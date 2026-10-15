@echo off
chcp 949 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call "%~dp0설치.bat"
echo ============================================
echo    유튜브 주소 하나로 숏츠 만들기
echo    (1080p 다운로드 - 캡컷 AI 편집기 재가공)
echo ============================================
echo.
set "URL="
set /p "URL=유튜브 주소 붙여넣기(마우스 오른쪽 클릭) 후 Enter: "
if not defined URL exit /b 0
".venv\Scripts\python.exe" yt_downloader.py "%URL%" -q 1080 --edit
echo.
echo 편집은 새로 뜬 창에서 진행됩니다. 완료되면 바탕화면 캡컷_완성본 폴더가 열립니다.
pause
