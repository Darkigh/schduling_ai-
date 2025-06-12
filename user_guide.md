# Gemini-Powered AI Scheduler - User Guide

## Overview

This enhanced AI scheduler uses Google's Gemini API to understand natural language requests and automatically create calendar appointments. The application can interpret a wide variety of scheduling requests and convert them into calendar events.

## Features

- **Natural Language Understanding**: Powered by Google's Gemini AI to understand scheduling requests
- **Automatic Calendar Creation**: Extracts event details and creates calendar appointments
- **Intelligent Date Parsing**: Understands relative dates (today, tomorrow, next Monday) and specific dates
- **Fallback Mechanism**: Uses rule-based parsing as a backup if AI analysis fails
- **One-Click Setup**: Batch file automatically installs dependencies and starts the application

## Setup Instructions

1. **Get a Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create or sign in to your Google account
   - Create an API key
   - Copy the API key

2. **Set Your API Key**:
   - Open the `.env` file in the project folder
   - Replace `your-api-key-here` with your actual Gemini API key
   - Save the file

3. **Run the Application**:
   - Double-click `run_app_gemini.bat`
   - This will automatically:
     - Install required dependencies
     - Start the backend server
     - Open the scheduler in your default browser

## Using the Scheduler

1. **Enter scheduling requests in natural language**:
   - "Schedule a meeting with John tomorrow at 2 PM"
   - "Lunch with Sarah on Friday at noon"
   - "Dentist appointment next Tuesday at 10 AM"
   - "Gym workout every Monday at 7 AM"

2. **View your schedule**:
   - All scheduled events appear on the calendar
   - You can switch between month, week, and day views
   - Export your calendar as a PNG image using the download button

## Troubleshooting

If you encounter issues:

1. **Check your API key**:
   - Ensure your Gemini API key is correctly set in the `.env` file
   - Verify the API key is active and has not expired

2. **Dependency issues**:
   - If the automatic installation fails, manually install the required packages:
   ```
   pip install fastapi uvicorn google-generativeai python-dotenv httpx
   ```

3. **Port conflicts**:
   - Ensure port 8000 is not in use by another application
   - If needed, modify the port in `main_gemini.py`

4. **Browser issues**:
   - If the browser doesn't open automatically, manually open `htaml.html`
   - Ensure JavaScript is enabled in your browser

## Technical Details

The application consists of:

- **Backend**: FastAPI server that processes requests using Gemini API
- **Frontend**: HTML/CSS/JavaScript interface with FullCalendar integration
- **Gemini Integration**: Natural language processing for scheduling requests
- **Fallback Logic**: Rule-based parsing as a backup mechanism

## Privacy Note

Your scheduling data is processed locally and is not stored on any external servers. The only external communication is with the Gemini API to process your natural language requests.
