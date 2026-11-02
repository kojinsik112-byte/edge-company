@echo off
chcp 65001 >nul
title 엣지컴퍼니 A/S 도움 창구 - 시험판
set "PHPX=%~dp0php\php.exe"
set "PHPD=-c "%~dp0php\php.ini" -d extension_dir="%~dp0php\ext""
cd /d "%~dp0app"
echo 시연 데이터를 지금 시각 기준으로 새로 만드는 중...
"%PHPX%" %PHPD% seed_demo.php
if errorlevel 1 goto err
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8091/demo.php'"
echo.
echo 시험판이 켜졌습니다: http://127.0.0.1:8091/demo.php
echo 시연이 끝나면 이 검은 창을 닫으세요. 닫으면 시험판도 꺼집니다.
echo.
"%PHPX%" %PHPD% -S 127.0.0.1:8091 -t "%~dp0app" "%~dp0app\router.php"
goto end
:err
echo.
echo 시연 데이터를 만들지 못했습니다. 위 메시지를 확인해 주세요.
pause
:end
