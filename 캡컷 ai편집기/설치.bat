@echo off
chcp 949 >nul
cd /d "%~dp0"
echo ============================================
echo    캡컷 AI 편집기 - 설치
echo ============================================
echo.

REM 파이썬 찾기: py 런처 우선 (Microsoft Store 가짜 별칭 제외)
set "PY="
py -3 --version >nul 2>nul && set "PY=py -3"
if not defined PY ( py --version >nul 2>nul && set "PY=py" )
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
echo.

REM 기존에 깨진 가상환경이 있으면 깨끗이 지우고 새로 만든다
if exist ".venv" (
  echo 기존 가상환경 정리 중...
  rmdir /s /q ".venv"
)
echo 가상환경 .venv 를 새로 만드는 중...
%PY% -m venv .venv

set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" (
  echo [오류] 가상환경 생성 실패. 파이썬을 다시 설치한 뒤 재시도하세요.
  pause
  exit /b 1
)

echo.
echo [1/3] 핵심 구성요소 설치 중 ... 무음컷 / 숏츠 / 브랜딩 + ffmpeg
"%VPY%" -m pip install --upgrade pip
"%VPY%" -m pip install pyyaml imageio-ffmpeg anthropic numpy
if errorlevel 1 (
  echo.
  echo [오류] 핵심 구성요소 설치 실패. 인터넷 연결을 확인하고 다시 시도하세요.
  pause
  exit /b 1
)

echo.
echo [2/3] 자막 AI 음성인식 구성요소 설치 중 ...
"%VPY%" -m pip install faster-whisper
if errorlevel 1 (
  echo.
  echo [참고] 자막 구성요소 설치 실패. 파이썬 최신버전 호환 문제일 수 있어요.
  echo        무음컷 / 숏츠 / 브랜딩은 정상 동작합니다.
)

echo.
echo [3/3] 자막 전용 글꼴 내려받는 중 ... (무료 OFL 글꼴)
"%VPY%" -m autoedit.fonts_install

echo.
echo 바탕화면에 "엣지 스튜디오" 바로가기를 만듭니다 ...
powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\엣지 스튜디오.lnk'); $s.TargetPath='%CD%\.venv\Scripts\pythonw.exe'; $s.Arguments='-m autoedit.studio'; $s.WorkingDirectory='%CD%'; $s.IconLocation='%SystemRoot%\System32\imageres.dll,186'; $s.Save()"

echo.
echo ============================================
echo    설치 완료!
echo    바탕화면의 "엣지 스튜디오" 를 더블클릭하세요.
echo    (예전 방식: "편집하기.bat" 위로 영상 끌어다 놓기도 그대로 됩니다)
echo ============================================
pause
