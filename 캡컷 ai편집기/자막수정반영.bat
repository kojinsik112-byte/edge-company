@echo off
chcp 949 >nul
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    자막 수정 반영 ^(오타 고친 뒤^)
  echo.
  echo   1^) 바탕화면 "캡컷_완성본\(이름)" 폴더의
  echo      (이름).srt 를 메모장으로 열어 오타를 고쳐 저장
  echo   2^) 그런 다음 원래 영상 파일을 이 파일 위로 드래그
  echo ============================================
  pause
  exit /b 0
)

set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" (
  echo [오류] 설치가 없거나 깨졌습니다. "설치.bat" 을 먼저 실행하세요.
  pause
  exit /b 1
)

set "DESKTOP="
for /f "usebackq tokens=2,*" %%A in (`reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop`) do set "DESKTOP=%%B"
if not defined DESKTOP set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\Desktop"

set "OUT=%DESKTOP%\캡컷_완성본\%~n1"

if not exist "%OUT%\%~n1_clean.mp4" (
  echo [오류] %OUT%\%~n1_clean.mp4 가 없습니다.
  echo        먼저 "편집하기.bat" 으로 한 번 편집해야 합니다.
  pause
  exit /b 1
)

echo 수정된 자막을 반영하는 중: %~n1
echo.
"%VPY%" -m autoedit.cli reburn "%OUT%\%~n1_clean.mp4" "%OUT%\%~n1.srt" -o "%OUT%" -v
if errorlevel 1 (
  echo.
  echo [오류] 처리 중 문제가 발생했습니다. 위 메시지를 확인하세요.
  pause
  exit /b 1
)

echo.
echo ============================================
echo    완료! 바탕화면 "캡컷_완성본\%~n1" 폴더를 확인하세요.
echo ============================================
explorer "%OUT%"
pause
