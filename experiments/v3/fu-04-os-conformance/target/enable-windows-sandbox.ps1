<#
enable-windows-sandbox.ps1 — FU-04 OS-conformance Windows side (destructive Windows traces).

REQUIRES ELEVATION + REBOOT; not executed by any agent.

This file is documented and staged only. No agent runs it, and it is not part of any gate.
Windows Sandbox enablement and the reboot are human-gated (AGENTS.md hard rule 8).

What it does
  1. Enables the optional Windows feature `Containers-DisposableClientVM` (Windows Sandbox).
  2. Reports whether a reboot is required.
  3. Provides `Start-SandboxTrace` to launch Windows Sandbox from a .wsb config for destructive
     Windows traces. Each launch is a fresh, disposable guest: mutations do not persist.

Fallback
  If Windows Sandbox is unavailable (edition, policy, or nested virtualization limits), a
  Hyper-V generation-2 VM with a checkpoint/undo disk is the alternative disposable Windows
  target. Hyper-V also requires elevation and a reboot.

Human checklist
  - [ ] Confirm the destructive trace is authorized for this target.
  - [ ] Run this script from an elevated (Administrator) PowerShell.
  - [ ] Reboot when prompted.
  - [ ] Re-run to confirm the feature reports Enabled and no reboot pending.
  - [ ] Launch a disposable guest and run the destructive Windows trace inside it only.
#>
#Requires -RunAsAdministrator
[CmdletBinding()]
param(
    [switch]$Enable,
    [switch]$Status,
    [string]$ConfigPath
)

$ErrorActionPreference = 'Stop'
$FeatureName = 'Containers-DisposableClientVM'

function Get-SandboxStatus {
    $feature = Get-WindowsOptionalFeature -Online -FeatureName $FeatureName
    [pscustomobject]@{
        FeatureName = $FeatureName
        State       = $feature.State
        Elevation   = ([Security.Principal.WindowsPrincipal] `
            [Security.Principal.WindowsIdentity]::GetCurrent()
        ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
}

function Enable-Sandbox {
    Write-Host "Enabling $FeatureName ..."
    $result = Enable-WindowsOptionalFeature -Online -FeatureName $FeatureName -All
    if ($result.RestartNeeded) {
        Write-Warning 'REBOOT REQUIRED before Windows Sandbox can run. Reboot is human-gated.'
    } else {
        Write-Host 'Feature enabled; no reboot reported. Windows Sandbox is ready.'
    }
    $result
}

function Start-SandboxTrace {
    param([Parameter(Mandatory)][string]$ConfigPath)
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "Sandbox config not found: $ConfigPath"
    }
    # Each launch is a fresh disposable guest; nothing written inside persists after close.
    Write-Host "Launching disposable Windows Sandbox: $ConfigPath"
    Start-Process -FilePath "$env:SystemRoot\System32\WindowsSandbox.exe" -ArgumentList $ConfigPath
}

if ($Enable) { Enable-Sandbox; Get-SandboxStatus }
elseif ($ConfigPath) { Start-SandboxTrace -ConfigPath $ConfigPath }
else { Get-SandboxStatus }
