@echo off
chcp 949 >nul
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    자막 수정 반영 ^(오타 고친 뒤^)
  echo.
  echo   1^) output 폴더의 (이름).srt 를 메모장으로 열어
  echo      오타를 고치고 저장하세요.
  echo   2^) 그런 다음 원래 영상 파일을 이 파일 위로
  echo      끌어다 놓으면 자막이 다시 반영됩니다.
  echo ============================================
  pause
  exit /b 0
)

if not exist ".venv\Scripts\activate.bat" (
  echo [오류] 먼저 "설치.bat" 을 실행해 주세요.
  pause
  exit /b 1
)

if not exist "output\%~n1_clean.mp4" (
  echo [오류] output 폴더에 %~n1_clean.mp4 가 없습니다.
  echo        먼저 "편집하기.bat" 으로 한 번 편집해야 합니다.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo 수정된 자막을 반영하는 중: %~n1
echo.
python -m autoedit.cli reburn "output\%~n1_clean.mp4" "output\%~n1.srt" -o output -v
if errorlevel 1 (
  echo.
  echo [오류] 처리 중 문제가 발생했습니다. 위 메시지를 확인하세요.
  pause
  exit /b 1
)

echo.
echo ============================================
echo    완료! output 폴더에서 수정된 영상을 확인하세요.
echo ============================================
explorer "%~dp0output"
pause
