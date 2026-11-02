@echo off
setlocal
title KleeVoice - Doctor
cd /d "%~dp0"

echo KleeVoice doctor - collecting environment info...
echo.

set "FOUND=0"

if exist ".venv-tts\Scripts\python.exe" (
    echo ===== TTS environment =====
    ".venv-tts\Scripts\python.exe" check_env.py --role tts
    set "FOUND=1"
)

if exist ".venv-svc\Scripts\python.exe" (
    echo.
    echo ===== SVC environment =====
    ".venv-svc\Scripts\python.exe" check_env.py --role svc
    set "FOUND=1"
)

if "%FOUND%"=="0" (
    echo [WARN] No venv found - run install.cmd first.
    echo        Falling back to system python:
    echo.
    python check_env.py
)

echo.
echo Copy everything above when asking for help.
echo Save it to a file:  doctor.cmd ^> report.txt
pause
