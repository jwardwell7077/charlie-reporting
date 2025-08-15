@echo off
echo Charlie Reporting - Email Test
echo ================================

echo Activating virtual environment...
call "C:\Users\jward\Documents\GitHub\charlie-reporting\.venv\Scripts\activate.bat"

echo.
echo Changing to demo directory...
cd /d "C:\Users\jward\Documents\GitHub\charlie-reporting\demo\run_scripts"

echo.
echo Running email test...
python manual_test.py

echo.
echo Running quick email test...
python quick_email_test.py

echo.
echo Test complete. Press any key to exit...
pause
