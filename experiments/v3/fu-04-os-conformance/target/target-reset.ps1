<#
target-reset.ps1 — FU-04 OS-conformance disposable Linux target reset.

What this does
  Resets ONLY the disposable WSL2 distro named `Debian`:
    1. wsl --unregister Debian          (destroys that distro's rootfs; frees the disk)
    2. wsl --install -d Debian --no-launch   (reinstalls a clean Debian, stays stopped)
  Nothing else on the host is touched. It never modifies other distros.

Idempotent
  If `Debian` is not registered, the unregister step is skipped and only the install runs.
  Re-running the script on a fresh target simply re-installs if needed.

Dry run / -WhatIf
  The script supports PowerShell's common -WhatIf:
      pwsh -File target-reset.ps1 -WhatIf
  With -WhatIf (or -Confirm:$false) no destructive action is performed; the commands that
  WOULD run are printed. Use -DryRun for the same behavior in a fully explicit form.

WARNING
  `wsl --unregister Debian` DESTROYS the disposable Linux target and everything inside it.
  It does not affect Windows, the host filesystem, or any other WSL distro. Run it only on
  the target that is explicitly marked disposable.

  Do NOT run this against a distro you care about. This script is documented, not auto-run:
  no agent executes it without an explicit Owner task.
#>
[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'High')]
param(
    [string]$Distro = 'Debian',
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

function Invoke-Wsl {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $rendered = 'wsl ' + ($Arguments -join ' ')
    Write-Host "  > $rendered"
    & wsl.exe @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "wsl failed ($LASTEXITCODE): $rendered"
    }
}

$registered = (& wsl.exe --list --quiet) |
    ForEach-Object { $_.Trim().Trim([char]0) } |
    Where-Object { $_ -ne '' }

$present = $registered -contains $Distro

Write-Host "Disposable Linux target: $Distro"
Write-Host "Currently registered:    $present"
Write-Host "Mode:                    $(if ($DryRun) { 'DRY RUN (no changes)' } else { 'LIVE (destructive to the disposable target only)' })"

if ($present) {
    $action = "Unregister disposable distro '$Distro' (destroys its rootfs)"
    if ($DryRun) {
        Write-Host "[DryRun] would run: wsl --unregister $Distro"
    } elseif ($PSCmdlet.ShouldProcess($Distro, $action)) {
        Invoke-Wsl @('--unregister', $Distro)
    } else {
        Write-Host "Skipped unregister (WhatIf/Confirm)."
    }
} else {
    Write-Host "Distro '$Distro' is not registered; skipping unregister (idempotent)."
}

$installAction = "Install a clean '$Distro' and leave it stopped"
if ($DryRun) {
    Write-Host "[DryRun] would run: wsl --install -d $Distro --no-launch"
} elseif ($PSCmdlet.ShouldProcess($Distro, $installAction)) {
    Invoke-Wsl @('--install', '-d', $Distro, '--no-launch')
} else {
    Write-Host "Skipped install (WhatIf/Confirm)."
}

Write-Host "Done. Verify with: wsl --list --verbose"
