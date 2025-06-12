from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
import re
from datetime import datetime, timedelta
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow your front‑end (localhost:8000 →  http://localhost:5500 or whichever you serve HTML from)
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

@app.post("/schedule", response_model=list[Task])
async def schedule(req: ScheduleRequest):
    # Use direct parsing method
    logger.info("Using direct parsing method")
    return parse_tasks_directly(req.prompt)

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
