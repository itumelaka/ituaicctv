@echo off
set PROJECT_ROOT=C:\Users\burnk\OneDrive\Documents-assets\ai-cctv-detection
set BACKEND_DIR=%PROJECT_ROOT%\backend
set PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe
set LOG_DIR=%BACKEND_DIR%\data\task-logs

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

cd /d "%BACKEND_DIR%"

echo ============================== >> "%LOG_DIR%\monitor_person.log"
echo Run started: %DATE% %TIME% >> "%LOG_DIR%\monitor_person.log"

"%PYTHON_EXE%" scripts\monitor_person_once.py >> "%LOG_DIR%\monitor_person.log" 2>&1

echo Exit code: %ERRORLEVEL% >> "%LOG_DIR%\monitor_person.log"
echo Run ended: %DATE% %TIME% >> "%LOG_DIR%\monitor_person.log"

exit /b %ERRORLEVEL%
