@echo off
setlocal

for %%P in (8000 5500) do (
  for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%%P ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
    echo Stopped process %%a on port %%P
  )
)

echo Done.
endlocal
