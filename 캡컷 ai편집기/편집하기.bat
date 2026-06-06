@echo off
REM ASCII-only content to avoid Korean codepage parsing issues on Windows.
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    CapCut AI Editor
  echo ============================================
  echo.
  echo  How to use: drag your recorded video file
  echo  and drop it onto THIS batch file.
  echo.
  pause
  exit /b 0
)

if not exist ".venv\Scripts\activate.bat" (
  echo [ERROR] Please run the SETUP batch file first.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo Editing: %~1
echo ^(This can take a while depending on video length. Do not close this window.^)
echo.
python -m autoedit.cli edit "%~1" -o output -v
if errorlevel 1 (
  echo.
  echo [ERROR] Editing failed. Please check the messages above.
  pause
  exit /b 1
)

echo.
echo ============================================
echo    DONE!  Results are in the "output" folder:
echo      - Final video : output\(name)_edited.mp4
echo      - Subtitles   : output\(name).srt
echo      - Shorts      : output\shorts\
echo ============================================
explorer "%~dp0output"
pause
