#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Remove ITU AI CCTV Backend Windows Service.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$NssmExe     = $null
$CandidatePaths = @(
    "C:\nssm\nssm.exe",
    "C:\nssm\win64\nssm.exe",
    "C:\tools\nssm\nssm.exe",
    (Get-Command nssm -ErrorAction SilentlyContinue)?.Source
)
foreach ($path in $CandidatePaths) {
    if ($path -and (Test-Path $path)) { $NssmExe = $path; break }
}

$ServiceName = "ITUAICCTVBackend"

$existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if (-not $existing) {
    Write-Host "Service '$ServiceName' not found. Nothing to remove."
    exit 0
}

Write-Host "Stopping service '$ServiceName'..."
if ($NssmExe) {
    & $NssmExe stop $ServiceName confirm
    Start-Sleep -Seconds 2
    & $NssmExe remove $ServiceName confirm
} else {
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    sc.exe delete $ServiceName
}

Write-Host "Service removed."
