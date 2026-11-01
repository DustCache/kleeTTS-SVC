@echo off
setlocal
title KleeStop
echo Stopping services on ports 9880 ^(TTS^) and 9001 ^(ASR, if used^) ...

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":9880" ^| findstr "LISTENING"') do (
    echo   kill TTS PID %%p
    taskkill /PID %%p /F >nul 2>&1
)
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":9001" ^| findstr "LISTENING"') do (
    echo   kill ASR PID %%p
    taskkill /PID %%p /F >nul 2>&1
)

echo Done.
pause
