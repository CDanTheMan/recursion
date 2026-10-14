# Create a virtualenv, install this checkout, and run recursion doctor.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = "python"
if ($env:PYTHON) {
    $python = $env:PYTHON
}

& $python -m venv .venv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\.venv\Scripts\python.exe -m pip install -e .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& .\.venv\Scripts\recursion.exe doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Output ""
Write-Output "Next steps:"
Write-Output "  .\.venv\Scripts\Activate.ps1"
Write-Output "  recursion --help"
Write-Output '  recursion run --task "Say hello"'
Write-Output ""
Write-Output "The shipped config enables fixture and fixture-b. Neither starts a CLI."
Write-Output "That run is reviewed by the other fixture and can finish without setting"
Write-Output "review.accept_unreviewed. Pinning one provider with --provider leaves no"
Write-Output "distinct reviewer. A live provider needs --allow-live."
Write-Output "See docs/USER-GUIDE.md."
