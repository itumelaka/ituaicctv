@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "PROJECT_ROOT=%%~fI"

set "BACKEND_DIR=%PROJECT_ROOT%\backend"
set "LOG_DIR=%BACKEND_DIR%\data\task-logs"
set "LOG_FILE=%LOG_DIR%\monitor_person_all.log"

set "PYTHON_EXE=%PROJECT_ROOT%\.venv312\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=%PROJECT_ROOT%\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" set "PYTHON_EXE=python"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ================================================== >> "%LOG_FILE%"
echo Run started: %date% %time% >> "%LOG_FILE%"
echo Python exe: %PYTHON_EXE% >> "%LOG_FILE%"

cd /d "%PROJECT_ROOT%"
"%PYTHON_EXE%" "%BACKEND_DIR%\scripts\monitor_person_all_once.py" >> "%LOG_FILE%" 2>&1

echo Exit code: %ERRORLEVEL% >> "%LOG_FILE%"
echo Run ended: %date% %time% >> "%LOG_FILE%"

endlocal
exit /b 0
