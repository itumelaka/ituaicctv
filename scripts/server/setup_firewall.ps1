#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Setup Windows Firewall rule for ITU AI CCTV Backend (port 8000, LAN only).

.DESCRIPTION
    Allows inbound TCP traffic on port 8000 from private/LAN networks only.
    Blocks access from public networks (internet).
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RuleName    = "ITU AI CCTV Backend (Port 8000 LAN)"
$Port        = 8000
$Description = "Allow LAN access to ITU AI CCTV FastAPI backend on port $Port"

Write-Host ""
Write-Host "======================================================"
Write-Host "  ITU AI CCTV Backend - Firewall Setup"
Write-Host "======================================================"
Write-Host ""

# Remove existing rule with same name
$existing = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing rule '$RuleName'..."
    Remove-NetFirewallRule -DisplayName $RuleName
}

# Create new inbound rule — LAN profile only (Private), not Public
New-NetFirewallRule `
    -DisplayName $RuleName `
    -Description $Description `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort $Port `
    -Action Allow `
    -Profile Private `
    -Enabled True | Out-Null

Write-Host "Firewall rule created:" -ForegroundColor Green
Write-Host "  Name    : $RuleName"
Write-Host "  Port    : $Port (TCP Inbound)"
Write-Host "  Profile : Private (LAN only — not Public/internet)"
Write-Host ""
Write-Host "Verify with:"
Write-Host "  Get-NetFirewallRule -DisplayName '$RuleName' | Format-List"
Write-Host ""

# Show server's LAN IP
$lanIp = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {
    $_.PrefixOrigin -ne "WellKnown" -and $_.IPAddress -notlike "127.*"
} | Select-Object -First 1).IPAddress

if ($lanIp) {
    Write-Host "This server's LAN IP: $lanIp" -ForegroundColor Cyan
    Write-Host "Set backend URL in GitHub Pages dashboard to:"
    Write-Host "  http://${lanIp}:$Port" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Done."
