@echo off
chcp 65001 >nul
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    캡컷 AI 편집기
  echo ============================================
  echo.
  echo  사용법: 이 "편집하기.bat" 파일 위로
  echo          촬영한 영상 파일을 마우스로 끌어다 놓으세요.
  echo.
  pause
  exit /b 0
)

if not exist ".venv\Scripts\activate.bat" (
  echo [오류] 먼저 "설치.bat" 을 한 번 실행해 주세요.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo 편집을 시작합니다: %~1
echo (영상 길이에 따라 시간이 걸릴 수 있어요. 창을 닫지 마세요.)
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
echo    완료! 결과물은 output 폴더 안에 있습니다.
echo      - 완성 영상:  output\(영상이름)_edited.mp4
echo      - 자막:       output\(영상이름).srt
echo      - 숏츠:       output\shorts\ 폴더
echo ============================================
explorer "%~dp0output"
pause
