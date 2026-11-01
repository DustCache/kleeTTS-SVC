@echo off
setlocal enabledelayedexpansion
title KleeVoice - Install
cd /d "%~dp0"

echo ============================================================
echo   KleeVoice installer  (TTS: GPT-SoVITS + SVC: DDSP-Reflow)
echo ============================================================
echo.

REM ---------- 1) locate Python 3.10/3.11 ----------
set "PY="
where py >nul 2>&1
if %errorlevel%==0 (
    py -3.10 -c "import sys" >nul 2>&1
    if !errorlevel!==0 set "PY=py -3.10"
)
if not defined PY (
    where python >nul 2>&1
    if !errorlevel!==0 (
        for /f "delims=" %%v in ('python -c "import sys;print(sys.version_info[1])" 2^>nul') do set "PYVER=%%v"
        if "!PYVER!"=="10" set "PY=python"
        if "!PYVER!"=="11" set "PY=python"
    )
)
if not defined PY (
    echo [ERROR] Python 3.10 / 3.11 not found.
    echo         Install from https://www.python.org/downloads/  ^(tick "Add to PATH"^)
    pause
    exit /b 1
)
echo [1/4] Python launcher: %PY%
%PY% -c "import sys;print('      version',sys.version.split()[0])"

REM ---------- 2) detect GPU -> torch wheel index ----------
set "TORCH_INDEX=https://download.pytorch.org/whl/cpu"
set "GPUNAME="
for /f "delims=" %%i in ('nvidia-smi --query-gpu=name --format=csv,noheader 2^>nul') do (
    if not defined GPUNAME set "GPUNAME=%%i"
)
if defined GPUNAME (
    echo [2/4] GPU detected: !GPUNAME!
    echo !GPUNAME! | findstr /i "RTX 50 RTX50 B100 B200" >nul
    if !errorlevel!==0 (
        set "TORCH_INDEX=https://download.pytorch.org/whl/cu128"
        echo       Blackwell class -^> torch cu128
    ) else (
        set "TORCH_INDEX=https://download.pytorch.org/whl/cu121"
        echo       NVIDIA GPU -^> torch cu121
    )
) else (
    echo [2/4] No NVIDIA GPU detected -^> CPU wheels
    echo       WARNING: CPU inference is very slow for both TTS and SVC.
)

REM ---------- 3) TTS venv ----------
echo.
echo [3/4] Setting up TTS environment (.venv-tts) ...
if not exist ".venv-tts\Scripts\python.exe" (
    %PY% -m venv .venv-tts || goto :fail
)
call ".venv-tts\Scripts\activate.bat"
python -m pip install --upgrade pip -q
python -m pip install torch torchaudio --index-url %TORCH_INDEX% || goto :fail
python -m pip install -r requirements-tts.txt || goto :fail
python -m pip install "numpy==1.26.4" || goto :fail
python -c "import torch,numpy;print('      torch',torch.__version__,'cuda',torch.cuda.is_available(),'| numpy',numpy.__version__)"
call ".venv-tts\Scripts\deactivate.bat"
echo       TTS env OK.

REM ---------- 4) SVC venv ----------
echo.
echo [4/4] Setting up SVC environment (.venv-svc) ...
if not exist ".venv-svc\Scripts\python.exe" (
    %PY% -m venv .venv-svc || goto :fail
)
call ".venv-svc\Scripts\activate.bat"
python -m pip install --upgrade pip -q
python -m pip install torch torchaudio --index-url %TORCH_INDEX% || goto :fail
python -m pip install -r requirements-svc.txt
if !errorlevel! neq 0 (
    echo.
    echo [WARN] Some SVC requirements failed ^(most likely fairseq^).
    echo        Retry after installing MSVC Build Tools, or see README "fairseq".
)
python -c "import torch,numpy;print('      torch',torch.__version__,'cuda',torch.cuda.is_available(),'| numpy',numpy.__version__)"
call ".venv-svc\Scripts\deactivate.bat"

echo.
echo ============================================================
echo   Install finished.
echo.
echo   NEXT: put the model files in place ^(see README "模型文件"^):
echo     TTS\GPT_weights_v2\klee-e60.ckpt
echo     TTS\SoVITS_weights_v2\klee_e24_s600.pth
echo     SVC\exp\reflow-klee\model_108000.pt
echo   and the pretrained models:
echo     TTS\GPT_SoVITS\pretrained_models\  ^(bert + hubert^)
echo     TTS\GPT_SoVITS\text\G2PWModel\     ^(chinese g2p^)
echo     SVC\pretrain\                      ^(contentvec / rmvpe / pc_nsf_hifigan^)
echo.
echo   Then run:  start_tts.cmd   ^(TTS, port 9880^)
echo              svc_convert.cmd ^<in_dir^> ^<out_dir^> [key]
echo ============================================================
pause
exit /b 0

:fail
echo.
echo [ERROR] Installation aborted. See the message above.
pause
exit /b 1
