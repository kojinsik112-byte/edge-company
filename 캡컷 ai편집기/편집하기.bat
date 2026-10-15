@echo off
chcp 949 >nul
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    캡컷 AI 편집기
  echo.
  echo   사용법: 촬영한 영상 파일을 마우스로 집어서
  echo           이 파일 위로 끌어다 놓으세요.
  echo ============================================
  pause
  exit /b 0
)

REM venv의 파이썬을 직접 호출 (activate 의존 X, Microsoft Store 가짜 python 회피)
set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" (
  echo [오류] 설치가 없거나 깨졌습니다.
  echo        이 폴더에서 "설치.bat" 을 먼저 실행하세요.
  pause
  exit /b 1
)

set "CFG="
if exist "config.yaml" set "CFG=-c config.yaml"

set "DESKTOP="
for /f "usebackq tokens=2,*" %%A in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop`) do set "DESKTOP=%%B"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Desktop"

set "OUT=%DESKTOP%\캡컷_완성본\%~n1"
if not exist "%OUT%" mkdir "%OUT%"

echo 편집 시작: %~1
echo 결과 저장 위치: %OUT%
echo (영상 길이에 따라 시간이 걸립니다. 진행률이 움직이면 정상입니다. 창을 닫지 마세요.)
echo.
"%VPY%" -m autoedit.cli edit "%~1" -o "%OUT%" %CFG% -v
if errorlevel 1 (
  echo.
  echo [오류] 편집 중 문제가 발생했습니다. 위 메시지를 확인하세요.
  echo        (Python was not found 라고 떴다면 "설치.bat" 을 다시 실행하세요.)
  pause
  exit /b 1
)

echo.
echo ============================================
echo    완료! 결과는 바탕화면의
echo    "캡컷_완성본\%~n1" 폴더에 있습니다.
echo ============================================
explorer "%OUT%"
pause
