@echo off
chcp 949 >nul
cd /d "%~dp0"

if "%~1"=="" (
  echo ============================================
  echo    캡컷 AI 편집기
  echo.
  echo   사용법: 촬영한 영상 파일을 마우스로 집어서
  echo           이 파일 위로 끌어다 놓으세요.
  echo.
  echo   자막 오타를 고치고 싶으면: 한 번 편집한 뒤 영상 옆에 생기는
  echo           같은 이름의 .srt 파일을 메모장으로 고치고, 영상을 다시 놓으세요.
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

REM 영상 옆에 같은 이름의 .srt(직접 고친 자막)가 있으면 그걸로 편집한다.
set "SIDESRT=%~dpn1.srt"
set "SRTOPT="
if exist "%SIDESRT%" (
  echo [자막] 고친 자막을 발견: %~n1.srt  ^(이 자막으로 편집합니다^)
)
if exist "%SIDESRT%" set "SRTOPT=--srt "%SIDESRT%""

echo 편집 시작: %~1
echo 영상 길이에 따라 시간이 걸립니다. 창을 닫지 마세요.
echo.
python -m autoedit.cli edit "%~1" -o output -v %SRTOPT%
if errorlevel 1 (
  echo.
  echo [오류] 편집 중 문제가 발생했습니다. 위 메시지를 확인하세요.
  pause
  exit /b 1
)

REM 처음 편집한 경우, 만들어진 자막을 영상 옆에 복사해 메모장으로 고칠 수 있게 한다.
if not exist "%SIDESRT%" if exist "output\%~n1.srt" (
  copy /y "output\%~n1.srt" "%SIDESRT%" >nul
  echo.
  echo [자막 수정 안내]
  echo   오타가 있으면 영상 옆의 "%~n1.srt" 파일을 메모장으로 열어 고친 다음,
  echo   이 영상을 다시 "편집하기.bat" 위로 끌어다 놓으면 고친 자막으로 다시 만듭니다.
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
