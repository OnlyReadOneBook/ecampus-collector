# Attend Watch — 작업 스케줄러가 conhost --headless 로 띄운다. 30분마다, 그리고 시간표상 수업 10분 전·2분 뒤
# (월·수 09:00 컴퓨터네트워크1, 화·목 09:00 알고리즘·15:00 데이터베이스, 2026-2학기 구글 캘린더 「[수업]」 기준 1031 확인).
# 수업 시간 직전 트리거는 쿨다운을 무시한다(-Class). LLM 없이 미이수 차시만 센다.
# 미이수가 있고 출석이 이미 돌고 있지 않으면 Claude 루틴 online-lecture-attend 를 띄워 본인인증·출석을 맡긴다.
# 같은 미이수로 Claude 를 매번 다시 띄우지 않도록 마지막 실행 뒤 2시간은 건너뛴다.
param([switch]$Class)
$ErrorActionPreference = 'Continue'
$log = 'C:\Users\Public\RoutineRunner\logs\attend-watch.log'
$stamp = 'C:\Users\Public\RoutineRunner\attend-watch.last-launch'
function L($m) { Add-Content -LiteralPath $log -Value ("{0} {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm'), $m) -Encoding UTF8 }
$busy = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | ? { $_.CommandLine -match 'attend\.py' }
if ($busy) { L "skip: attend.py 실행 중"; exit 0 }
if (Get-ScheduledTask -TaskName 'Routine online-lecture-attend' -EA SilentlyContinue | ? State -eq 'Running') { L "skip: 출석 루틴 실행 중"; exit 0 }
$env:PYTHONUTF8 = '1'
Set-Location -LiteralPath 'C:\Users\rlfjr\ecampus-collector'
git pull -q --ff-only 2>$null
$out = & .venv\Scripts\python.exe attend.py --check 2>&1 | Out-String
$rc = $LASTEXITCODE
$lines = ($out -split "`n" | ? { $_ -match '^미이수|^PENDING|실패' }) -join ' / '
if ($rc -eq 0) { L "none: $lines"; exit 0 }
if ($rc -ne 10) { L "error rc=${rc}: $($out.Trim() -replace '\s+',' ')"; exit 0 }
if (-not $Class -and (Test-Path $stamp) -and ((Get-Date) - (Get-Item $stamp).LastWriteTime).TotalHours -lt 2) { L "pending(쿨다운): $lines"; exit 0 }
Set-Content -LiteralPath $stamp -Value (Get-Date -Format o)
L "launch: $lines"
Start-ScheduledTask -TaskName 'Routine online-lecture-attend'
