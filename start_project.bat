@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_EXE=C:\Users\Aayush\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if not exist "%PYTHON_EXE%" (
  set "PYTHON_EXE=python"
)

echo Using Python: %PYTHON_EXE%
"%PYTHON_EXE%" -m ensurepip --upgrade >nul 2>&1
"%PYTHON_EXE%" -m pip install --upgrade pip
"%PYTHON_EXE%" -m pip install -r requirements.txt

for /f "tokens=5" %%p in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do set "BACKEND_PID=%%p"
for /f "tokens=5" %%p in ('netstat -aon ^| findstr :5500 ^| findstr LISTENING') do set "FRONTEND_PID=%%p"

if defined BACKEND_PID (
  echo Backend already running on port 8000 (PID: %BACKEND_PID%)
) else (
  start "FitBuddy Backend" cmd /k ""%PYTHON_EXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000"
)

if defined FRONTEND_PID (
  echo Frontend already running on port 5500 (PID: %FRONTEND_PID%)
) else (
  start "FitBuddy Frontend" cmd /k ""%PYTHON_EXE%" -m http.server 5500"
)

echo.
echo Servers ready:
echo   Frontend: http://localhost:5500
echo   Backend:  http://127.0.0.1:8000
endlocal
