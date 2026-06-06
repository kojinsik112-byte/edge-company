@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo    캡컷 AI 편집기 - 설치
echo ============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [오류] 파이썬이 설치되어 있지 않습니다.
  echo.
  echo  1) https://www.python.org/downloads/ 에서 파이썬을 받으세요.
  echo  2) 설치 첫 화면에서 "Add Python to PATH" 를 꼭 체크하세요!
  echo  3) 설치 후 이 "설치.bat" 을 다시 실행하세요.
  echo.
  pause
  exit /b 1
)

echo 가상환경(.venv)을 만듭니다...
python -m venv .venv
call .venv\Scripts\activate.bat

echo.
echo 필요한 프로그램을 설치합니다. (처음엔 몇 분 걸릴 수 있어요)
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo [오류] 설치 중 문제가 발생했습니다. 인터넷 연결을 확인하고 다시 시도하세요.
  pause
  exit /b 1
)

echo.
echo ============================================
echo    설치 완료!
echo.
echo    이제 "편집하기.bat" 파일 위로
echo    촬영한 영상을 마우스로 끌어다 놓으면
echo    자동 편집이 시작됩니다.
echo ============================================
pause
