<#
.SYNOPSIS
    Quick health check for ITU AI CCTV on this Windows Server.
#>

$Port    = 8000
$BaseUrl = "http://localhost:$Port"

Write-Host ""
Write-Host "======================================================"
Write-Host "  ITU AI CCTV Backend - Server Health Check"
Write-Host "======================================================"
Write-Host ""

# 1. Service status
$svc = Get-Service -Name "ITUAICCTVBackend" -ErrorAction SilentlyContinue
if ($svc) {
    $color = if ($svc.Status -eq "Running") { "Green" } else { "Red" }
    Write-Host "Windows Service  : $($svc.Status)" -ForegroundColor $color
} else {
    Write-Host "Windows Service  : Not installed" -ForegroundColor Yellow
}

# 2. Port listening
$listening = Test-NetConnection -ComputerName localhost -Port $Port -InformationLevel Quiet -ErrorAction SilentlyContinue
$portColor = if ($listening) { "Green" } else { "Red" }
Write-Host "Port $Port (TCP)  : $(if ($listening) { 'Listening' } else { 'Not listening' })" -ForegroundColor $portColor

# 3. Health endpoint
try {
    $health = Invoke-RestMethod -Uri "$BaseUrl/health" -TimeoutSec 5
    Write-Host "GET /health      : $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "GET /health      : Failed - $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Dashboard summary
try {
    $summary = Invoke-RestMethod -Uri "$BaseUrl/dashboard/summary" -TimeoutSec 5
    Write-Host "GET /dashboard   : ok — cameras $($summary.cameras_enabled)/$($summary.cameras_total) enabled, events $($summary.events.total_events)" -ForegroundColor Green
} catch {
    Write-Host "GET /dashboard   : Failed" -ForegroundColor Red
}

# 5. Scheduled task
$task = Get-ScheduledTask -TaskName "ITU AI CCTV Person Monitor" -ErrorAction SilentlyContinue
if ($task) {
    $taskColor = if ($task.State -eq "Ready" -or $task.State -eq "Running") { "Green" } elseif ($task.State -eq "Disabled") { "Yellow" } else { "Red" }
    Write-Host "Task Scheduler   : $($task.State)" -ForegroundColor $taskColor
} else {
    Write-Host "Task Scheduler   : Not installed" -ForegroundColor Yellow
}

# 6. Firewall rule
$fw = Get-NetFirewallRule -DisplayName "ITU AI CCTV Backend (Port 8000 LAN)" -ErrorAction SilentlyContinue
if ($fw) {
    $fwColor = if ($fw.Enabled -eq "True") { "Green" } else { "Yellow" }
    Write-Host "Firewall rule    : $($fw.Enabled)" -ForegroundColor $fwColor
} else {
    Write-Host "Firewall rule    : Not found" -ForegroundColor Yellow
}

# 7. LAN IP
$lanIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.PrefixOrigin -ne "WellKnown" -and $_.IPAddress -notlike "127.*"
} | Select-Object -First 1).IPAddress

Write-Host ""
if ($lanIp) {
    Write-Host "LAN IP           : $lanIp"
    Write-Host "Set backend URL to: http://${lanIp}:$Port" -ForegroundColor Cyan
}

# 8. Monitor log
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$LogFile     = Join-Path $ProjectRoot "backend\data\task-logs\monitor_person_all.log"

if (Test-Path $LogFile) {
    $lastWrite = (Get-Item $LogFile).LastWriteTime
    $ageMin    = [int]((Get-Date) - $lastWrite).TotalMinutes
    $logColor  = if ($ageMin -le 10) { "Green" } elseif ($ageMin -le 60) { "Yellow" } else { "Red" }
    Write-Host "Monitor log      : Last updated $ageMin min ago ($($lastWrite.ToString('yyyy-MM-dd HH:mm')))" -ForegroundColor $logColor
} else {
    Write-Host "Monitor log      : Not found (scheduler may not have run yet)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Dashboard: https://itumelaka.github.io/ituaicctv/"
Write-Host ""
