@echo off
chcp 949 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  call "%~dp0설치.bat"
  exit /b
)
echo 다운로드 엔진 최신화 중... (유튜브 구조 변경 대응)
".venv\Scripts\python.exe" -m pip install -U "yt-dlp[default,deno]" imageio-ffmpeg --disable-pip-version-check
echo.
echo 업데이트 완료. [실행.bat]으로 다시 실행하세요.
pause
