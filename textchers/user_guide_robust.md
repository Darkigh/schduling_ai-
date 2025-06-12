# Gemini-Powered AI Scheduler - User Guide (Robust Version)

## Overview

This enhanced AI scheduler uses Google's Gemini API to understand natural language requests and automatically create calendar appointments. The application features robust error handling and fallback mechanisms to ensure reliability.

## Features

- **Natural Language Understanding**: Powered by Google's Gemini AI to understand scheduling requests
- **Automatic Calendar Creation**: Extracts event details and creates calendar appointments
- **Intelligent Date Parsing**: Understands relative dates (today, tomorrow, next Monday) and specific dates
- **Robust Fallback Mechanism**: Automatically falls back to rule-based parsing if AI analysis fails
- **Detailed Logging**: Logs all operations for easy troubleshooting
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
   - Double-click `run_app_gemini_robust.bat`
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

1. **Check the log file**:
   - Look at `gemini_scheduler.log` in the project folder for detailed error information
   - This will help identify if there are issues with the Gemini API

2. **Check your API key**:
   - Ensure your Gemini API key is correctly set in the `.env` file
   - Verify the API key is active and has not expired

3. **Dependency issues**:
   - If the automatic installation fails, manually install the required packages:
   ```
   pip install fastapi uvicorn google-generativeai python-dotenv httpx
   ```

4. **Port conflicts**:
   - Ensure port 8000 is not in use by another application
   - If needed, modify the port in `main_gemini_robust.py`

5. **Browser issues**:
   - If the browser doesn't open automatically, manually open `htaml.html`
   - Ensure JavaScript is enabled in your browser

6. **Fallback mode**:
   - If the Gemini API is unavailable, the application will automatically fall back to direct parsing
   - You'll still be able to schedule events, but with less natural language understanding

## Technical Details

The application consists of:

- **Backend**: FastAPI server that processes requests using Gemini API with robust error handling
- **Frontend**: HTML/CSS/JavaScript interface with FullCalendar integration
- **Gemini Integration**: Natural language processing for scheduling requests
- **Fallback Logic**: Rule-based parsing as a backup mechanism
- **Logging System**: Detailed logging for troubleshooting

## Privacy Note

Your scheduling data is processed locally and is not stored on any external servers. The only external communication is with the Gemini API to process your natural language requests.
