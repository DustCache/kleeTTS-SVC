@echo off
setlocal
title KleeTTS
cd /d "%~dp0TTS"

if not exist "..\.venv-tts\Scripts\python.exe" (
    echo [ERROR] .venv-tts not found. Run install.cmd first.
    pause
    exit /b 1
)

netstat -ano 2>nul | findstr ":9880" | findstr "LISTENING" >nul
if %errorlevel%==0 (
    echo [TTS] port 9880 already listening - skip.
    pause
    exit /b 0
)

set "HF_ENDPOINT=https://hf-mirror.com"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUTF8=1"

echo [TTS] starting Klee TTS API on 0.0.0.0:9880 ...
echo [TTS] config: configs/tts_infer_klee.yaml
echo [TTS] keep this window open; close it to stop.
echo.
..\.venv-tts\Scripts\python.exe api_v2.py -a 0.0.0.0 -p 9880 -c configs/tts_infer_klee.yaml

echo.
echo [TTS] process exited.
pause
