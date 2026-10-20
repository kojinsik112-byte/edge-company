# 주관사 공고 감시 — 윈도우 작업 스케줄러 등록 (본부장 PC · PowerShell에서 1회 실행)
#   cd <저장소>\jugansa\watch ; powershell -ExecutionPolicy Bypass -File .\register_watch.ps1
# 시각은 watch_config.json "times" (기본 09:00 · 12:00 · 15:00 · 18:00). 바꾸면 다시 실행.
# 끄기: Get-ScheduledTask EdgeNoticeWatch_* | Disable-ScheduledTask   · 지우기: Unregister-ScheduledTask EdgeNoticeWatch_* -Confirm:$false
$here = $PSScriptRoot
$cfg = Get-Content "$here\watch_config.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$py = (Get-Command python).Source
Get-ScheduledTask -TaskName "EdgeNoticeWatch_*" -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
foreach ($t in $cfg.times) {
  $name = "EdgeNoticeWatch_" + ($t -replace ":", "")
  $act = New-ScheduledTaskAction -Execute $py -Argument "`"$here\notice_watch.py`"" -WorkingDirectory $here
  $trg = New-ScheduledTaskTrigger -Daily -At $t
  $set = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15)
  Register-ScheduledTask -TaskName $name -Action $act -Trigger $trg -Settings $set -Description "주관사 모집공고 감시(카페 검색 → 새 글 카톡)" | Out-Null
  Write-Host "등록: $name ($t)"
}
Write-Host "첫 실행은 알림 폭탄 방지를 위해: python `"$here\notice_watch.py`" --init"
