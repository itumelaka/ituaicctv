#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup Windows Task Scheduler for ITU AI CCTV multi-camera person monitor.

.DESCRIPTION
    Creates a scheduled task that runs the multi-camera person monitor
    every 5 minutes. Uses the hidden VBS launcher to avoid CMD popup.

    The task runs under the SYSTEM account so it continues even when
    no user is logged in.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$VbsScript   = Join-Path $ProjectRoot "backend\scripts\run_monitor_person_all_once_hidden.vbs"
$TaskName    = "ITU AI CCTV Person Monitor"
$IntervalMin = 5

Write-Host ""
Write-Host "======================================================"
Write-Host "  ITU AI CCTV - Task Scheduler Setup"
Write-Host "======================================================"
Write-Host "Project root : $ProjectRoot"
Write-Host "VBS script   : $VbsScript"
Write-Host "Interval     : every $IntervalMin minutes"
Write-Host ""

if (-not (Test-Path $VbsScript)) {
    Write-Error "VBS launcher not found: $VbsScript"
    exit 1
}

# Remove existing task
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task '$TaskName'..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Action: run wscript.exe with the hidden VBS launcher
$Action = New-ScheduledTaskAction `
    -Execute "wscript.exe" `
    -Argument "`"$VbsScript`"" `
    -WorkingDirectory $ProjectRoot

# Trigger: repeat every 5 minutes, starting now, indefinitely
$Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes $IntervalMin) -Once -At (Get-Date)

# Settings: run whether user logged on or not, do not store password
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 4) `
    -MultipleInstances IgnoreNew `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable

# Principal: SYSTEM account — runs without user login
$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "ITU AI CCTV multi-camera person monitor. Runs every $IntervalMin minutes." | Out-Null

Write-Host "Task registered: '$TaskName'" -ForegroundColor Green
Write-Host ""
Write-Host "The task is currently DISABLED for safety."
Write-Host "Enable it when you are ready to start monitoring:"
Write-Host ""
Write-Host "  Enable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "Other useful commands:"
Write-Host "  Get-ScheduledTask -TaskName '$TaskName' | Select-Object TaskName, State"
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName'"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'   # run immediately"
Write-Host "  Disable-ScheduledTask -TaskName '$TaskName' # pause monitoring"
Write-Host ""

# Leave disabled — operator enables when ready
Disable-ScheduledTask -TaskName $TaskName | Out-Null
Write-Host "Task is installed and ready. Enable when ready to start." -ForegroundColor Yellow
Write-Host ""
Write-Host "Monitor log will be written to:"
Write-Host "  $ProjectRoot\backend\data\task-logs\monitor_person_all.log"
Write-Host ""
Write-Host "Done."
