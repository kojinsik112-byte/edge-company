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

if not exist ".venv\Scripts\activate.bat" (
  echo [오류] 먼저 "설치.bat" 을 한 번 실행해 주세요.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo 편집 시작: %~1
echo 영상 길이에 따라 시간이 걸립니다. 창을 닫지 마세요.
echo.
python -m autoedit.cli edit "%~1" -o output -v
if errorlevel 1 (
  echo.
  echo [오류] 편집 중 문제가 발생했습니다. 위 메시지를 확인하세요.
  pause
  exit /b 1
)

echo.
echo ============================================
echo    완료! 결과는 output 폴더에 있습니다.
echo      - 완성 영상은 output 폴더 안의 _edited.mp4
echo      - 자막은 .srt 파일
echo      - 숏츠는 output\shorts\ 폴더
echo ============================================
explorer "%~dp0output"
pause
