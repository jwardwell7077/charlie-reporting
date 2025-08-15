@echo off
REM activate_env.bat
REM Activate the virtual environment and run commands

set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%.venv
set PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

REM Check if virtual environment exists
if not exist "%PYTHON_EXE%" (
    echo Error: Virtual environment not found at %VENV_PATH%
    echo Please create virtual environment first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
call "%VENV_PATH%\Scripts\activate.bat"

REM Set environment variables
set PYTHONPATH=%SCRIPT_DIR%src;%SCRIPT_DIR%tests
if exist "%SCRIPT_DIR%.env" (
    echo Loading environment variables from .env
    for /f "tokens=1,2 delims==" %%a in ('type "%SCRIPT_DIR%.env" ^| findstr /v "^#" ^| findstr "="') do (
        set "%%a=%%b"
    )
)

REM Run command if provided
if "%~1"=="" (
    echo Virtual environment activated. Python path: %PYTHON_EXE%
    echo You can now run Python commands or integration tests.
    cmd /k
) else (
    echo Running: %*
    %*
)
