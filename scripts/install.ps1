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
Write-Output '  recursion run --task "Say hello" --provider fixture'
Write-Output ""
Write-Output "The fixture provider starts no CLI. With only that provider, review has no"
Write-Output "second candidate, so the run is unreviewed and exits 2 unless"
Write-Output "review.accept_unreviewed is true. A live provider needs --allow-live."
Write-Output "See docs/USER-GUIDE.md."
