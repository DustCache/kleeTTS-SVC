@echo off
setlocal
title KleeSVC
cd /d "%~dp0SVC"

if not exist "..\.venv-svc\Scripts\python.exe" (
    echo [ERROR] .venv-svc not found. Run install.cmd first.
    pause
    exit /b 1
)

if "%~1"=="" goto :usage
if "%~2"=="" goto :usage

set "KEY=%~3"
if "%KEY%"=="" set "KEY=0"

echo [SVC] model : exp/reflow-klee/model_108000.pt
echo [SVC] input : %~1
echo [SVC] output: %~2
echo [SVC] key   : %KEY% semitones
echo.

..\.venv-svc\Scripts\python.exe batch_infer.py -m exp/reflow-klee/model_108000.pt -i "%~1" -o "%~2" -d auto -k %KEY%

echo.
echo [SVC] done. Converted vocals are in: %~2
echo       Mix with instrumental:  ..\tools\mix_cover.py
pause
exit /b 0

:usage
echo Usage:
echo   svc_convert.cmd ^<input_dir^> ^<output_dir^> [key_semitones]
echo.
echo   input_dir  : folder with vocal .wav files (44.1 kHz recommended)
echo   output_dir : folder for converted vocals
echo   key        : semitone shift. 0 = keep pitch (female song)
echo                +12 = one octave up (male song -^> child voice)
echo.
echo Example:
echo   svc_convert.cmd D:\songs\vocals D:\songs\vocals_klee 12
pause
exit /b 1
