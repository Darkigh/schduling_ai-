"""
Enhanced AI Scheduler with Gemini API Integration
This module handles natural language processing for scheduling using Google's Gemini API.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
import re
from datetime import datetime, timedelta
import calendar
from typing import List, Dict, Any, Optional
import os

# Import Gemini API
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not found in environment variables. Using placeholder.")
    GEMINI_API_KEY = "your-api-key-here"  # Placeholder, will be replaced by user

genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScheduleRequest(BaseModel):
    prompt: str

class Task(BaseModel):
    name: str
    start_time: str
    end_time: str
    date: str

class GeminiChatAnalyzer:
    """
    Class for analyzing chat messages using Google's Gemini API
    """
    
    def __init__(self):
        """Initialize the Gemini Chat Analyzer"""
        # Configure the model
        self.model = genai.GenerativeModel('gemini-pro')
        logger.info("Gemini Chat Analyzer initialized")
    
    def analyze_message(self, message: str) -> Dict[str, Any]:
        """
        Analyze a chat message to extract scheduling information
        
        Args:
            message: The user's message
            
        Returns:
            Dict containing extracted information
        """
        logger.info(f"Analyzing message with Gemini: {message}")
        
        # Create the prompt for Gemini
        prompt = self._create_analysis_prompt(message)
        
        try:
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Parse the response
            result = self._parse_gemini_response(response.text)
            logger.info(f"Gemini analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            # Return a basic result on error
            return {
                "success": False,
                "error": str(e),
                "event_name": None,
                "date": None,
                "start_time": None,
                "duration": None
            }
    
    def _create_analysis_prompt(self, message: str) -> str:
        """
        Create a prompt for the Gemini model
        
        Args:
            message: The user's message
            
        Returns:
            Formatted prompt string
        """
        # Base prompt with instructions
        prompt = """
You are an AI assistant that extracts scheduling information from user messages.
Analyze the following message and extract details about events or appointments.

USER MESSAGE: "{message}"

Extract the following information in JSON format:
- event_name: The name or title of the event
- date: The date of the event (YYYY-MM-DD format, use today's date if not specified)
- start_time: The start time (HH:MM format, 24-hour)
- duration: Duration in minutes (default to 60 if not specified)

If information is missing or unclear, set the corresponding field to null.
Respond ONLY with the JSON object, no additional text.
"""
        
        # Format the prompt with the actual message
        return prompt.format(message=message)
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the response from Gemini API
        
        Args:
            response_text: The text response from Gemini
            
        Returns:
            Dict containing extracted information
        """
        try:
            # Try to extract JSON from the response
            # First, look for JSON-like structure
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                # Parse the JSON
                result = json.loads(json_str)
                
                # Add success flag
                result["success"] = True
                return result
            else:
                # If no JSON found, try to extract information using regex
                return self._extract_with_regex(response_text)
                
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from Gemini response: {response_text}")
            return self._extract_with_regex(response_text)
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "event_name": None,
                "date": None,
                "start_time": None,
                "duration": None
            }
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract information using regex as a fallback
        
        Args:
            text: The text to extract from
            
        Returns:
            Dict containing extracted information
        """
        result = {
            "success": True,
            "event_name": None,
            "date": None,
            "start_time": None,
            "duration": None
        }
        
        # Extract event name
        event_match = re.search(r'event_name["\s:]+([^",\n]+)', text)
        if event_match:
            result["event_name"] = event_match.group(1).strip()
            
        # Extract date
        date_match = re.search(r'date["\s:]+([^",\n]+)', text)
        if date_match:
            date_str = date_match.group(1).strip()
            if date_str.lower() not in ['null', 'none']:
                result["date"] = date_str
                
        # Extract start time
        time_match = re.search(r'start_time["\s:]+([^",\n]+)', text)
        if time_match:
            time_str = time_match.group(1).strip()
            if time_str.lower() not in ['null', 'none']:
                result["start_time"] = time_str
                
        # Extract duration
        duration_match = re.search(r'duration["\s:]+(\d+)', text)
        if duration_match:
            result["duration"] = int(duration_match.group(1))
            
        return result

# Initialize the Gemini Chat Analyzer
gemini_analyzer = GeminiChatAnalyzer()

@app.post("/schedule", response_model=List[Task])
async def schedule(req: ScheduleRequest):
    """
    Process scheduling requests using Gemini API with fallback to direct parsing
    """
    prompt = req.prompt
    logger.info(f"Received scheduling request: {prompt}")
    
    try:
        # First try with Gemini API
        logger.info("Attempting to analyze with Gemini API")
        analysis_result = gemini_analyzer.analyze_message(prompt)
        
        if analysis_result.get("success", False):
            # Convert Gemini analysis to tasks
            tasks = convert_analysis_to_tasks(analysis_result, prompt)
            
            # If Gemini successfully created tasks, return them
            if tasks:
                logger.info(f"Gemini created {len(tasks)} tasks")
                return tasks
        
        # If Gemini failed or didn't create tasks, fall back to direct parsing
        logger.info("Falling back to direct parsing")
        return parse_tasks_directly(prompt)
        
    except Exception as e:
        logger.error(f"Error in schedule endpoint: {str(e)}")
        # Fall back to direct parsing on any error
        logger.info("Falling back to direct parsing due to error")
        return parse_tasks_directly(prompt)

def convert_analysis_to_tasks(analysis: Dict[str, Any], original_prompt: str) -> List[Dict[str, Any]]:
    """
    Convert Gemini analysis result to tasks
    
    Args:
        analysis: The analysis result from Gemini
        original_prompt: The original user prompt
        
    Returns:
        List of task dictionaries
    """
    tasks = []
    
    # Check if we have the minimum required information
    if not (analysis.get("event_name") and analysis.get("date")):
        return []
    
    # Get event details
    event_name = analysis.get("event_name", "Untitled Event")
    date = analysis.get("date")
    
    # Handle start time
    start_time = None
    if analysis.get("start_time"):
        # Convert 24-hour time to 12-hour format with AM/PM
        try:
            hours, minutes = map(int, analysis["start_time"].split(":"))
            if hours >= 12:
                period = "PM"
                if hours > 12:
                    hours -= 12
            else:
                period = "AM"
                if hours == 0:
                    hours = 12
            
            start_time = f"{hours}:{minutes:02d} {period}"
        except:
            # If conversion fails, try to extract time from original prompt
            time_pattern = r"(\d+):?(\d*)\s*(AM|PM|am|pm)"
            time_match = re.search(time_pattern, original_prompt, re.IGNORECASE)
            if time_match:
                hours = time_match.group(1)
                minutes = time_match.group(2) or "00"
                period = time_match.group(3).upper()
                start_time = f"{hours}:{minutes} {period}"
            else:
                # Default to noon
                start_time = "12:00 PM"
    else:
        # Try to extract time from original prompt
        time_pattern = r"(\d+):?(\d*)\s*(AM|PM|am|pm)"
        time_match = re.search(time_pattern, original_prompt, re.IGNORECASE)
        if time_match:
            hours = time_match.group(1)
            minutes = time_match.group(2) or "00"
            period = time_match.group(3).upper()
            start_time = f"{hours}:{minutes} {period}"
        else:
            # Default to noon
            start_time = "12:00 PM"
    
    # Calculate end time based on duration
    duration_minutes = analysis.get("duration", 60)
    end_time = calculate_end_time_from_12h(start_time, duration_minutes)
    
    # Create task
    task = {
        "name": event_name,
        "start_time": start_time,
        "end_time": end_time,
        "date": date
    }
    
    tasks.append(task)
    return tasks

def calculate_end_time_from_12h(start_time_str: str, duration_minutes: int) -> str:
    """
    Calculate end time based on 12-hour format start time and duration in minutes
    
    Args:
        start_time_str: Start time in 12-hour format (e.g., "2:30 PM")
        duration_minutes: Duration in minutes
        
    Returns:
        End time in 12-hour format
    """
    # Parse start time
    time_parts = start_time_str.split()
    time = time_parts[0]
    period = time_parts[1]
    
    hours, minutes = map(int, time.split(':'))
    
    # Convert to 24-hour for calculation
    if period == "PM" and hours < 12:
        hours += 12
    elif period == "AM" and hours == 12:
        hours = 0
    
    # Calculate total minutes
    total_minutes = hours * 60 + minutes + duration_minutes
    
    # Convert back to hours and minutes
    end_hours = total_minutes // 60
    end_minutes = total_minutes % 60
    
    # Convert back to 12-hour format
    if end_hours >= 12:
        end_period = "PM"
        if end_hours > 12:
            end_hours -= 12
    else:
        end_period = "AM"
        if end_hours == 0:
            end_hours = 12
    
    return f"{end_hours}:{end_minutes:02d} {end_period}"

def parse_tasks_directly(prompt):
    """
    Method to directly parse tasks from the prompt without using external APIs
    """
    logger.info(f"Direct parsing prompt: {prompt}")
    tasks = []
    
    # Parse date from prompt
    date_str = parse_date_from_prompt(prompt)
    
    # Enhanced pattern matching for common scheduling patterns
    lunch_pattern = r"lunch with (\w+).*?(\d+):?(\d*)\s*(AM|PM|am|pm)"
    gym_pattern = r"gym.*?(\d+):?(\d*)\s*(AM|PM|am|pm)"
    class_pattern = r"class\s+(\w+).*?(\d+):?(\d*)\s*(AM|PM|am|pm)"
    meeting_pattern = r"meet(?:ing)?\s+(?:with)?\s*(\w+).*?(\d+):?(\d*)\s*(AM|PM|am|pm)"
    
    # Duration pattern
    duration_pattern = r"for\s+(\d+)\s+hour"
    duration_match = re.search(duration_pattern, prompt, re.IGNORECASE)
    default_duration = 1  # Default duration in hours
    if duration_match:
        default_duration = int(duration_match.group(1))
    
    # Try to match lunch pattern
    lunch_match = re.search(lunch_pattern, prompt, re.IGNORECASE)
    if lunch_match:
        person = lunch_match.group(1)
        start_hour = int(lunch_match.group(2))
        start_min = lunch_match.group(3) or "00"
        start_ampm = lunch_match.group(4).upper()
        
        # Calculate end time based on duration
        end_time = calculate_end_time(start_hour, int(start_min), start_ampm, default_duration)
        
        tasks.append({
            "name": f"Lunch with {person}",
            "start_time": f"{start_hour}:{start_min.zfill(2)} {start_ampm}",
            "end_time": end_time,
            "date": date_str
        })
    
    # Try to match gym pattern
    gym_match = re.search(gym_pattern, prompt, re.IGNORECASE)
    if gym_match:
        start_hour = int(gym_match.group(1))
        start_min = gym_match.group(2) or "00"
        start_ampm = gym_match.group(3).upper()
        
        # Calculate end time based on duration
        end_time = calculate_end_time(start_hour, int(start_min), start_ampm, default_duration)
        
        tasks.append({
            "name": "Gym workout",
            "start_time": f"{start_hour}:{start_min.zfill(2)} {start_ampm}",
            "end_time": end_time,
            "date": date_str
        })
    
    # Try to match class pattern
    class_match = re.search(class_pattern, prompt, re.IGNORECASE)
    if class_match:
        class_num = class_match.group(1)
        start_hour = int(class_match.group(2))
        start_min = class_match.group(3) or "00"
        start_ampm = class_match.group(4).upper()
        
        # Calculate end time based on duration
        end_time = calculate_end_time(start_hour, int(start_min), start_ampm, default_duration)
        
        tasks.append({
            "name": f"Class {class_num}",
            "start_time": f"{start_hour}:{start_min.zfill(2)} {start_ampm}",
            "end_time": end_time,
            "date": date_str
        })
    
    # Try to match meeting pattern
    meeting_match = re.search(meeting_pattern, prompt, re.IGNORECASE)
    if meeting_match:
        person = meeting_match.group(1)
        start_hour = int(meeting_match.group(2))
        start_min = meeting_match.group(3) or "00"
        start_ampm = meeting_match.group(4).upper()
        
        # Calculate end time based on duration
        end_time = calculate_end_time(start_hour, int(start_min), start_ampm, default_duration)
        
        tasks.append({
            "name": f"Meeting with {person}",
            "start_time": f"{start_hour}:{start_min.zfill(2)} {start_ampm}",
            "end_time": end_time,
            "date": date_str
        })
    
    # If no patterns matched, create a generic task based on the prompt
    if not tasks:
        # Extract time if available, otherwise default to noon
        time_pattern = r"(\d+):?(\d*)\s*(AM|PM|am|pm)"
        time_match = re.search(time_pattern, prompt, re.IGNORECASE)
        
        if time_match:
            start_hour = int(time_match.group(1))
            start_min = time_match.group(2) or "00"
            start_ampm = time_match.group(3).upper()
            
            # Calculate end time based on duration
            end_time = calculate_end_time(start_hour, int(start_min), start_ampm, default_duration)
        else:
            # Default to noon if no time found
            start_hour = 12
            start_min = "00"
            start_ampm = "PM"
            end_time = "1:00 PM"
        
        # Use the first few words of the prompt as the task name
        words = prompt.split()
        task_name = " ".join(words[:min(5, len(words))])
        
        tasks.append({
            "name": task_name,
            "start_time": f"{start_hour}:{start_min.zfill(2)} {start_ampm}",
            "end_time": end_time,
            "date": date_str
        })
    
    logger.info(f"Direct parsing created {len(tasks)} tasks: {tasks}")
    return tasks

def parse_date_from_prompt(prompt):
    """
    Enhanced date parsing to support various date formats
    """
    prompt_lower = prompt.lower()
    today = datetime.now()
    
    # Check for "today"
    if "today" in prompt_lower:
        return today.strftime("%Y-%m-%d")
    
    # Check for "tomorrow"
    if "tomorrow" in prompt_lower:
        tomorrow = today + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    # Check for "next week"
    if "next week" in prompt_lower:
        next_week = today + timedelta(days=7)
        return next_week.strftime("%Y-%m-%d")
    
    # Check for day names (Monday, Tuesday, etc.)
    days_of_week = {
        "monday": 0, "mon": 0,
        "tuesday": 1, "tue": 1, "tues": 1,
        "wednesday": 2, "wed": 2,
        "thursday": 3, "thu": 3, "thurs": 3,
        "friday": 4, "fri": 4,
        "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6
    }
    
    for day_name, day_num in days_of_week.items():
        if day_name in prompt_lower:
            # Calculate days until the next occurrence of this day
            current_day_num = today.weekday()
            days_until = (day_num - current_day_num) % 7
            if days_until == 0:  # If it's the same day, assume next week
                days_until = 7
            target_date = today + timedelta(days=days_until)
            return target_date.strftime("%Y-%m-%d")
    
    # Check for "next" followed by day name
    next_day_pattern = r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)"
    next_day_match = re.search(next_day_pattern, prompt_lower)
    if next_day_match:
        day_name = next_day_match.group(1)
        day_num = days_of_week.get(day_name)
        if day_num is not None:
            current_day_num = today.weekday()
            days_until = (day_num - current_day_num) % 7
            if days_until == 0:  # If it's the same day, use next week
                days_until = 7
            target_date = today + timedelta(days=days_until + 7)  # Add extra week for "next"
            return target_date.strftime("%Y-%m-%d")
    
    # Check for month/day format (e.g., "May 20")
    month_names = {
        "january": 1, "jan": 1,
        "february": 2, "feb": 2,
        "march": 3, "mar": 3,
        "april": 4, "apr": 4,
        "may": 5,
        "june": 6, "jun": 6,
        "july": 7, "jul": 7,
        "august": 8, "aug": 8,
        "september": 9, "sep": 9, "sept": 9,
        "october": 10, "oct": 10,
        "november": 11, "nov": 11,
        "december": 12, "dec": 12
    }
    
    for month_name, month_num in month_names.items():
        month_pattern = rf"{month_name}\s+(\d+)(?:st|nd|rd|th)?"
        month_match = re.search(month_pattern, prompt_lower)
        if month_match:
            day = int(month_match.group(1))
            year = today.year
            # If the date is in the past, assume next year
            if month_num < today.month or (month_num == today.month and day < today.day):
                year += 1
            # Validate day is within month's range
            _, last_day = calendar.monthrange(year, month_num)
            if 1 <= day <= last_day:
                return f"{year}-{month_num:02d}-{day:02d}"
    
    # Check for MM/DD or MM-DD format
    date_pattern = r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?"
    date_match = re.search(date_pattern, prompt)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        year = today.year
        if date_match.group(3):
            year_str = date_match.group(3)
            if len(year_str) == 2:
                year = 2000 + int(year_str)
            else:
                year = int(year_str)
        # Validate month and day
        if 1 <= month <= 12:
            _, last_day = calendar.monthrange(year, month)
            if 1 <= day <= last_day:
                return f"{year}-{month:02d}-{day:02d}"
    
    # Check for YYYY-MM-DD format
    iso_date_pattern = r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})"
    iso_match = re.search(iso_date_pattern, prompt)
    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        day = int(iso_match.group(3))
        # Validate month and day
        if 1 <= month <= 12:
            _, last_day = calendar.monthrange(year, month)
            if 1 <= day <= last_day:
                return f"{year}-{month:02d}-{day:02d}"
    
    # Default to tomorrow if no date is found
    tomorrow = today + timedelta(days=1)
    return tomorrow.strftime("%Y-%m-%d")

def calculate_end_time(start_hour, start_min, start_ampm, duration_hours):
    """
    Calculate end time based on start time and duration
    """
    # Convert to 24-hour format for calculation
    if start_ampm == "PM" and start_hour < 12:
        start_hour += 12
    elif start_ampm == "AM" and start_hour == 12:
        start_hour = 0
    
    # Calculate end time
    end_hour = start_hour + duration_hours
    end_min = start_min
    
    # Convert back to 12-hour format
    if end_hour >= 12:
        end_ampm = "PM"
        if end_hour > 12:
            end_hour -= 12
    else:
        end_ampm = "AM"
        if end_hour == 0:
            end_hour = 12
    
    return f"{end_hour}:{end_min:02d} {end_ampm}"

# Add this for Windows compatibility
if __name__ == "__main__":
    uvicorn.run("main_gemini:app", host="0.0.0.0", port=8000, reload=True)
