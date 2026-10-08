@echo off
chcp 949 >nul
cd /d "%~dp0"
REM ============================================
REM   엣지 스튜디오 (AI 영상 자동편집) 실행
REM   창이 뜨면 영상을 끌어다 놓으세요.
REM ============================================

set "PYW="
if exist ".venv\Scripts\pythonw.exe" set "PYW=.venv\Scripts\pythonw.exe"
if not defined PYW ( where pyw >nul 2>nul && set "PYW=pyw -3" )
if not defined PYW ( where pythonw >nul 2>nul && set "PYW=pythonw" )

if not defined PYW (
  echo [오류] 파이썬을 찾을 수 없습니다. 먼저 "설치.bat" 을 실행하세요.
  pause
  exit /b 1
)

start "" %PYW% -m autoedit.studio
exit /b 0
