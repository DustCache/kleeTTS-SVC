@echo off
chcp 65001 >nul
cd /d C:\GPT-SoVITS-local
set HF_ENDPOINT=https://hf-mirror.com
set PATH=C:\gpt-sovits-venv\Scripts;%PATH%
echo Starting Klee TTS API on http://127.0.0.1:9880 ...
C:\gpt-sovits-venv\Scripts\python.exe api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer_klee.yaml
pause
