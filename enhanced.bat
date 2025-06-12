@echo off
echo Starting Enhanced AI Scheduler with New Features...
echo.
echo ===================================================
echo Checking and installing required Python packages...
echo ===================================================

:: Check if pip is installed
where pip >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: pip is not installed or not in PATH.
    echo Please install Python with pip and try again.
    pause
    exit /b 1
)

:: Create a temporary requirements file
echo fastapi > requirements_temp.txt
echo uvicorn >> requirements_temp.txt
echo python-dotenv >> requirements_temp.txt
echo httpx >> requirements_temp.txt

:: Install required packages
echo Installing required packages...
pip install -r requirements_temp.txt
if %errorlevel% neq 0 (
    echo.
    echo Warning: There was an issue installing packages with pip.
    echo Trying with pip3...
    
    where pip3 >nul 2>nul
    if %errorlevel% neq 0 (
        echo Error: Neither pip nor pip3 could install the packages.
        echo Please manually install the required packages:
        echo pip install fastapi uvicorn python-dotenv httpx
        pause
        exit /b 1
    )
    
    pip3 install -r requirements_temp.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install required packages.
        echo Please manually install the required packages:
        echo pip install fastapi uvicorn python-dotenv httpx
        pause
        exit /b 1
    )
)

:: Clean up temporary file
del requirements_temp.txt

echo.
echo Starting backend server...
echo.

:: Start the Python backend server
start cmd /k "cd %~dp0 && python main.py"

:: Wait for the server to start
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

:: Open the HTML file in the default browser
echo Opening enhanced scheduler in your default browser...
start "" "htaml_enhanced.html"

echo.
echo Setup complete! The enhanced scheduler should now be running.
echo.
echo New features:
echo 1. Click on any day to see all appointments for that day
echo 2. Click on any appointment to cancel it
echo 3. Support for time range specification in events
echo.
echo If you encounter any issues:
echo 1. Check that port 8000 is not in use by another application
echo 2. Ensure you have Python 3.6+ installed
echo.
echo To close the application, close this window and the command prompt window that opened.
echo.
pause
