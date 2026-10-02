# Prepares the local Windows machine for the next phase (FU-03/FU-04 experiments, then
# FU-01/02/05). Verifies base tools and installs the missing toolchains via winget.
# Human-run. See docs/v3/research-lane/NEXT-PHASE.md.
$ErrorActionPreference = 'Continue'

function Have($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }

Write-Output "== base tools =="
foreach ($c in 'python', 'git', 'node', 'wsl') {
  if (Have $c) { Write-Output "$c: present" } else { Write-Output "$c: MISSING" }
}

if (-not (Have 'winget')) {
  Write-Output "winget is required for automated installs. Install 'App Installer' from the Store, or install the tools manually."
  exit 2
}

Write-Output "== Java (Temurin 21 JDK) — required for TLA+/TLC (FU-03) =="
winget install --id EclipseAdoptium.Temurin.21.JDK -e --accept-source-agreements --accept-package-agreements

Write-Output "== Rust (rustup) — required for the FU-01 runtime experiment =="
winget install --id Rustlang.Rustup -e --accept-source-agreements --accept-package-agreements

Write-Output "== Go — required for the FU-01 runtime experiment =="
winget install --id GoLang.Go -e --accept-source-agreements --accept-package-agreements

Write-Output ""
Write-Output "== manual step: TLA+ tools =="
Write-Output "tla2tools.jar is not on winget. Fetch the pinned release from"
Write-Output "https://github.com/tlaplus/tlaplus/releases and place tla2tools.jar under tools/tlaplus/."
Write-Output ""
Write-Output "Reopen this shell (so PATH updates), then verify with:"
Write-Output "  python -X utf8 -B tools/check_next_phase.py"
