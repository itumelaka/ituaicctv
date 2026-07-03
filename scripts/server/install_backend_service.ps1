#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Install ITU AI CCTV Backend as a Windows Service using NSSM.

.DESCRIPTION
    Installs the FastAPI backend as a Windows Service that starts automatically
    when the server boots. Requires NSSM to be installed.

    Download NSSM: https://nssm.cc/download
    After downloading, place nssm.exe in C:\nssm\ or add it to PATH.

.NOTES
    Run this script as Administrator.
    Run from any location — it detects the project root automatically.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Paths ---
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$BackendDir  = Join-Path $ProjectRoot "backend"
$ServiceName = "ITUAICCTVBackend"
$DisplayName = "ITU AI CCTV Backend"
$Port        = 8000

Write-Host ""
Write-Host "======================================================"
Write-Host "  ITU AI CCTV Backend - Windows Service Installer"
Write-Host "======================================================"
Write-Host "Project root : $ProjectRoot"
Write-Host "Backend dir  : $BackendDir"
Write-Host ""

# --- Detect Python ---
$PythonExe = Join-Path $ProjectRoot ".venv312\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
}
if (-not (Test-Path $PythonExe)) {
    $PythonExe = (Get-Command python -ErrorAction SilentlyContinue)?.Source
}
if (-not $PythonExe) {
    Write-Error "Python not found. Install Python 3.12 and create a virtual environment first."
    exit 1
}
Write-Host "Python       : $PythonExe"

# --- Detect NSSM ---
$NssmExe = $null
$CandidatePaths = @(
    "C:\nssm\nssm.exe",
    "C:\nssm\win64\nssm.exe",
    "C:\tools\nssm\nssm.exe",
    (Get-Command nssm -ErrorAction SilentlyContinue)?.Source
)
foreach ($path in $CandidatePaths) {
    if ($path -and (Test-Path $path)) { $NssmExe = $path; break }
}
if (-not $NssmExe) {
    Write-Host ""
    Write-Host "ERROR: NSSM not found." -ForegroundColor Red
    Write-Host "Download NSSM from: https://nssm.cc/download" -ForegroundColor Yellow
    Write-Host "Extract and place nssm.exe at: C:\nssm\nssm.exe" -ForegroundColor Yellow
    exit 1
}
Write-Host "NSSM         : $NssmExe"

# --- Check .env exists ---
$EnvFile = Join-Path $BackendDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host ""
    Write-Host "WARNING: backend\.env not found." -ForegroundColor Yellow
    Write-Host "Copy backend\.env.example to backend\.env and fill in credentials." -ForegroundColor Yellow
    Write-Host "The service will still be installed but may not work correctly." -ForegroundColor Yellow
}

# --- Remove existing service if present ---
$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host ""
    Write-Host "Existing service found. Stopping and removing..." -ForegroundColor Yellow
    & $NssmExe stop $ServiceName confirm
    & $NssmExe remove $ServiceName confirm
    Start-Sleep -Seconds 2
}

# --- Install service ---
Write-Host ""
Write-Host "Installing service '$DisplayName'..."

& $NssmExe install $ServiceName $PythonExe "-m uvicorn app.main:app --host 0.0.0.0 --port $Port"
& $NssmExe set $ServiceName AppDirectory $BackendDir
& $NssmExe set $ServiceName DisplayName $DisplayName
& $NssmExe set $ServiceName Description "ITU AI CCTV FastAPI backend. Dashboard: https://itumelaka.github.io/ituaicctv/"
& $NssmExe set $ServiceName Start SERVICE_AUTO_START

# Restart on failure
& $NssmExe set $ServiceName AppRestartDelay 10000
& $NssmExe set $ServiceName AppThrottle 30000

# Log stdout and stderr
$LogDir = Join-Path $BackendDir "data\service-logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
& $NssmExe set $ServiceName AppStdout (Join-Path $LogDir "backend_stdout.log")
& $NssmExe set $ServiceName AppStderr (Join-Path $LogDir "backend_stderr.log")
& $NssmExe set $ServiceName AppRotateFiles 1
& $NssmExe set $ServiceName AppRotateSeconds 86400
& $NssmExe set $ServiceName AppRotateBytes 5242880

# --- Start service ---
Write-Host ""
Write-Host "Starting service..."
& $NssmExe start $ServiceName

Start-Sleep -Seconds 3

$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -eq "Running") {
    Write-Host ""
    Write-Host "Service is running." -ForegroundColor Green
    Write-Host "Backend URL  : http://localhost:$Port"
    Write-Host "API docs     : http://localhost:$Port/docs"
    Write-Host "Dashboard UI : http://localhost:$Port/dashboard-ui"
    Write-Host ""
    Write-Host "Open GitHub Pages dashboard and set Backend URL to:"
    Write-Host "  http://<this-server-ip>:$Port" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Service may not have started correctly. Check logs:" -ForegroundColor Yellow
    Write-Host "  $LogDir"
    Write-Host "Or run: Get-Service -Name $ServiceName"
}

Write-Host ""
Write-Host "Done."
