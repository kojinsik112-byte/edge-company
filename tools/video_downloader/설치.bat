@echo off
chcp 949 >nul
cd /d "%~dp0"
echo ============================================
echo    엣지컴퍼니 유튜브 영상 추출기 - 설치
echo ============================================
echo.

set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY ( python --version >nul 2>nul && set "PY=python" )
if not defined PY (
  echo [오류] 파이썬을 찾을 수 없습니다.
  echo   1^) https://www.python.org/downloads/ 에서 설치
  echo   2^) 첫 화면 "Add python.exe to PATH" 체크
  echo   3^) 설치 후 이 파일을 다시 실행
  pause
  exit /b 1
)
echo 파이썬 발견: %PY%

if not exist ".venv\Scripts\python.exe" (
  echo 가상환경 .venv 만드는 중...
  %PY% -m venv .venv
)
set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" (
  echo [오류] 가상환경 생성 실패. 파이썬을 다시 설치한 뒤 재시도하세요.
  pause
  exit /b 1
)

echo.
echo 다운로드 엔진(yt-dlp + deno) + ffmpeg 설치 중... (1~3분)
"%VPY%" -m pip install --upgrade pip --disable-pip-version-check -q
"%VPY%" -m pip install -U "yt-dlp[default,deno]" imageio-ffmpeg --disable-pip-version-check
if errorlevel 1 (
  echo.
  echo [오류] 설치 실패. 인터넷 연결을 확인하고 다시 실행하세요.
  pause
  exit /b 1
)
"%VPY%" -c "import imageio_ffmpeg; imageio_ffmpeg.get_ffmpeg_exe()"

echo.
echo ============================================
echo   설치 완료!  이제 [실행.bat]을 더블클릭하세요.
echo ============================================
pause
