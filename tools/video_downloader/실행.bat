@echo off
chcp 949 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo 처음 실행이라 설치부터 진행합니다...
  call "%~dp0설치.bat"
  if not exist ".venv\Scripts\python.exe" exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0yt_downloader.py"
