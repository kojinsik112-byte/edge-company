@echo off
chcp 65001 >nul
title 엣지컴퍼니 A/S 도움 창구 - 시험판
set "PHPX=%~dp0php\php.exe"
set "PHPD=-c "%~dp0php\php.ini" -d extension_dir="%~dp0php\ext""
cd /d "%~dp0app"
if not exist "data\as.sqlite" (
  echo 처음이라 시연 데이터를 만드는 중...
  "%PHPX%" %PHPD% seed_demo.php
)
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8091/demo.php'"
echo.
echo 시험판이 켜졌습니다(앞서 넣은 내용 그대로): http://127.0.0.1:8091/demo.php
echo 끝나면 이 검은 창을 닫으세요. 닫으면 시험판도 꺼집니다.
echo.
"%PHPX%" %PHPD% -S 127.0.0.1:8091 -t "%~dp0app" "%~dp0app\router.php"
