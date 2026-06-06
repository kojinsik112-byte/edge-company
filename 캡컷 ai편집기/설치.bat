@echo off
REM ASCII-only content to avoid Korean codepage parsing issues on Windows.
cd /d "%~dp0"
echo ============================================
echo    CapCut AI Editor - SETUP
echo ============================================
echo.

REM Find Python: py launcher first, then python (skip Microsoft Store stub).
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY ( py --version >nul 2>nul && set "PY=py" )
if not defined PY ( python --version >nul 2>nul && set "PY=python" )

if not defined PY (
  echo [ERROR] Python was not found.
  echo.
  echo   1^) Install Python from https://www.python.org/downloads/
  echo   2^) Check "Add python.exe to PATH" on the first install screen.
  echo   3^) Run this file again.
  echo.
  pause
  exit /b 1
)
echo Python found: %PY%
echo.

echo Creating virtual environment ^(.venv^) ...
%PY% -m venv .venv
call .venv\Scripts\activate.bat

echo.
echo [1/2] Installing core components ^(silence-cut / shorts / branding + ffmpeg^) ...
python -m pip install --upgrade pip
pip install pyyaml imageio-ffmpeg
if errorlevel 1 (
  echo.
  echo [ERROR] Failed to install core components. Check your internet and retry.
  pause
  exit /b 1
)

echo.
echo [2/2] Installing subtitle component ^(AI speech-to-text^) ...
pip install faster-whisper
if errorlevel 1 (
  echo.
  echo [NOTE] Subtitle component failed to install ^(Python version compatibility^).
  echo        That is OK - silence-cut / shorts / intro-outro-BGM still work fine.
)

echo.
echo ============================================
echo    SETUP COMPLETE
echo.
echo    Next: drag your recorded video file
echo    onto the EDIT batch file in this folder.
echo ============================================
pause
