---
title: Recursion v3 design-foundation deterministic validation procedure
status: active-campaign-gate-procedure
last-updated: 2026-09-03
---

# Recursion v3 design-foundation deterministic validation procedure

This file owns the exact reproducible local procedure for the documentation campaign's
machine-checkable gates. It changes no repository or external state. Run it from the target
worktree in PowerShell after committing the candidate; a clean tree is required so `HEAD` names
the exact reviewed bytes. The recorded output MUST include `candidate=<40-hex>`.

A bare `git diff --check` on a clean tree is insufficient because it compares an empty working
diff. This procedure checks the complete starting-baseline-to-candidate range. External URLs and
source applicability are inspectable gates in [SOURCE-REGISTER.md](SOURCE-REGISTER.md), not
silently treated as link-check success.

```powershell
$ErrorActionPreference = 'Stop'
$baseline = '672081fc1874ab9b7a41a14ca61adc60ecd71c95'
$candidate = (git rev-parse HEAD).Trim()
$root = (Resolve-Path 'docs/v3').Path

if ($candidate -notmatch '^[0-9a-f]{40}$') { throw 'candidate is not a full commit' }
if ((git branch --show-current).Trim() -ne 'codex/v3-design-foundation') {
  throw 'wrong branch'
}
git merge-base --is-ancestor 6543840cfd4dd1d7f49ce58b55e8357cdf3b37be $candidate
if ($LASTEXITCODE) { throw 'required ancestor missing' }
if (git status --porcelain) { throw 'worktree is not clean' }

$changed = @(git diff --name-only $baseline $candidate)
$outside = @($changed | Where-Object { $_ -notlike 'docs/v3/*' })
if ($outside) { throw "out-of-bound paths: $($outside -join ', ')" }
$diffCheck = @(git diff --check $baseline $candidate)
if ($LASTEXITCODE -or $diffCheck) { $diffCheck; throw 'candidate-range diff check failed' }
"candidate=$candidate"
"CHANGED_PATH_AND_DIFF_PASS count=$($changed.Count)"

$registry = Get-Content -Raw (Join-Path $root 'CLAIM-REGISTRY.json') | ConvertFrom-Json
$ledgerLines = Get-Content (Join-Path $root $registry.canonicalLedger)
$rows = for ($i = 0; $i -lt $ledgerLines.Count; $i++) {
  if ($ledgerLines[$i] -match '^\| ([A-Z][A-Z0-9]*-[0-9]{3}) \|') {
    [pscustomobject]@{ Id = $Matches[1]; Line = $i + 1 }
  }
}
$errors = [System.Collections.Generic.List[string]]::new()
foreach ($d in ($rows | Group-Object Id | Where-Object Count -gt 1)) {
  $errors.Add("duplicate row $($d.Name)")
}
$known = @{}
foreach ($row in $rows) { $known[$row.Id] = $true }
$expected = @{}
foreach ($range in $registry.ranges) {
  foreach ($n in $range.start..$range.end) {
    $id = '{0}-{1:D3}' -f $range.prefix, $n
    if ($expected.ContainsKey($id)) { $errors.Add("overlapping range $id") }
    $expected[$id] = $true
    if (-not $known.ContainsKey($id) -and $range.reserved -notcontains $n) {
      $errors.Add("registered id without row $id")
    }
  }
  foreach ($reserved in $range.reserved) {
    $id = '{0}-{1:D3}' -f $range.prefix, [int]$reserved
    if ($known.ContainsKey($id)) { $errors.Add("reserved id has row $id") }
  }
}
foreach ($id in $known.Keys) {
  if (-not $expected.ContainsKey($id)) { $errors.Add("row outside registry $id") }
  if ($id -notmatch $registry.idPattern) { $errors.Add("malformed row $id") }
}

$activeFiles = Get-ChildItem $root -Recurse -File | Where-Object {
  $_.Extension -in '.md', '.json' -and $_.FullName -notmatch '[\\/]archive[\\/]'
}
$foreignPatterns = @($registry.foreignRegistries | ForEach-Object {
  [regex]::new($_.idPattern)
})
$refRegex = [regex]::new($registry.referencePattern)
foreach ($file in $activeFiles) {
  $lines = Get-Content $file.FullName
  for ($i = 0; $i -lt $lines.Count; $i++) {
    foreach ($match in $refRegex.Matches($lines[$i])) {
      $id = $match.Groups[1].Value
      if ($registry.literalExclusions.value -contains $id -or $known.ContainsKey($id)) {
        continue
      }
      $foreign = $false
      foreach ($pattern in $foreignPatterns) {
        if ($pattern.IsMatch($id)) { $foreign = $true; break }
      }
      if (-not $foreign) {
        $relative = [IO.Path]::GetRelativePath($root, $file.FullName)
        $errors.Add("unknown reference $id at $($relative):$($i + 1)")
      }
    }
  }
}
if ($errors.Count) { $errors | Sort-Object -Unique; throw 'claim registry failed' }
"CLAIM_REGISTRY_PASS rows=$($rows.Count) expected=$($expected.Count)"

function Test-Sequence($path, $pattern, $prefix, $start, $end, $width, $label) {
  $ids = @()
  foreach ($line in (Get-Content $path)) {
    if ($line -match $pattern) { $ids += $Matches[1] }
  }
  $wanted = foreach ($n in $start..$end) {
    if ($width) { $prefix + $n.ToString("D$width") } else { $prefix + $n }
  }
  $dupes = $ids | Group-Object | Where-Object Count -gt 1
  $missing = $wanted | Where-Object { $_ -notin $ids }
  $extra = $ids | Where-Object { $_ -notin $wanted }
  if ($dupes -or $missing -or $extra -or $ids.Count -ne $wanted.Count) {
    throw "$label sequence failed"
  }
  "$label=$($ids.Count)"
}

Test-Sequence 'docs/v3/R1-R17-EVIDENCE.md' '^## (R[0-9]+) —' 'R' 1 17 0 'R_LANES'
Test-Sequence 'docs/v3/AUTONOMOUS-PLANNING.md' '^\| (APQ-[0-9]{2}) \|' 'APQ-' 1 18 2 'APQ_TRACE'
Test-Sequence 'docs/v3/M1A-AUTONOMOUS-PLANNING.md' '^\| (F-M1A-[0-9]{3}) \|' 'F-M1A-' 1 23 3 'M1A_FIXTURES'
Test-Sequence 'docs/v3/M1A-AUTONOMOUS-PLANNING.md' '^\| (M1A-[0-9]{2}) [^|]*\|' 'M1A-' 1 6 2 'M1A_DAG'
Test-Sequence 'docs/v3/M1A-FIXTURE-ORACLES.md' '^\| `(F-M1A-[0-9]{3})` \|' 'F-M1A-' 1 23 3 'M1A_ORACLES'
Test-Sequence 'docs/v3/AUTONOMOUS-PLANNING-CAMPAIGN.md' '^\| (GATE-V3DF-[0-9]{2}) \|' 'GATE-V3DF-' 1 24 2 'CAMPAIGN_GATES'
Test-Sequence 'docs/v3/SOURCE-REGISTER.md' '^\| `(SRC-V3-[0-9]{3})` \|' 'SRC-V3-' 1 51 3 'SOURCE_RECORDS'
Test-Sequence 'docs/v3/SOURCE-REGISTER.md' '^\| (R[0-9]+) \| `SRC-V3-' 'R' 1 17 0 'SOURCE_LANE_COVERAGE'

$sourceLines = Get-Content 'docs/v3/SOURCE-REGISTER.md'
$sourceIds = @($sourceLines | ForEach-Object {
  if ($_ -match '^\| `(SRC-V3-[0-9]{3})` \|') { $Matches[1] }
})
$coverageLines = @($sourceLines | Where-Object { $_ -match '^\| R(?:[1-9]|1[0-7]) \|' })
$sourceCoverageErrors = foreach ($line in $coverageLines) {
  foreach ($match in [regex]::Matches($line, 'SRC-V3-[0-9]{3}')) {
    if ($match.Value -notin $sourceIds) { "unknown coverage source $($match.Value)" }
  }
}
if ($sourceCoverageErrors) { $sourceCoverageErrors; throw 'source lane coverage failed' }
"SOURCE_LANE_LINKS_PASS lanes=$($coverageLines.Count)"

$oracleLines = Get-Content 'docs/v3/M1A-FIXTURE-ORACLES.md'
$commandIds = @($oracleLines | ForEach-Object {
  if ($_ -match '^\| `([a-z][a-z0-9-]+)` \| `(?:owner|head|arm|worker|verifier|kernel-fixture-gate)') {
    $Matches[1]
  }
})
$errorIds = @($oracleLines | ForEach-Object {
  if ($_ -match '^\| `(E-[A-Z0-9-]+)` \|') { $Matches[1] }
})
if ($commandIds.Count -ne 17 -or ($commandIds | Sort-Object -Unique).Count -ne 17) {
  throw 'closed command alphabet failed'
}
if ($errorIds.Count -ne 26 -or ($errorIds | Sort-Object -Unique).Count -ne 26) {
  throw 'closed error registry failed'
}
"M1A_CLOSED_ALPHABETS_PASS commands=$($commandIds.Count) errors=$($errorIds.Count)"

function Get-GfmSlugs($path) {
  $slugs = @{}
  $counts = @{}
  foreach ($line in (Get-Content $path)) {
    if ($line -notmatch '^#{1,6}\s+(.+?)\s*#*$') { continue }
    $slug = $Matches[1].ToLowerInvariant()
    $slug = $slug -replace '<[^>]+>', ''
    $slug = $slug -replace '[^\p{L}\p{N}\s_-]', ''
    $slug = $slug -replace '\s', '-'
    if ($counts.ContainsKey($slug)) {
      $counts[$slug] += 1
      $slug = "$slug-$($counts[$slug])"
    } else { $counts[$slug] = 0 }
    $slugs[$slug] = $true
  }
  return $slugs
}

$linkErrors = [System.Collections.Generic.List[string]]::new()
$linkRegex = [regex]'\[[^\]]*\]\((?<target>[^)]+)\)'
$slugCache = @{}
foreach ($file in ($activeFiles | Where-Object Extension -eq '.md')) {
  $text = Get-Content -Raw $file.FullName
  # Code examples can contain regex fragments that resemble Markdown links; only prose links
  # participate in the documentation-link gate.
  $text = [regex]::Replace($text, '(?ms)^```.*?^```[ \t]*$', '')
  foreach ($match in $linkRegex.Matches($text)) {
    $target = $match.Groups['target'].Value.Trim()
    if ($target.StartsWith('<') -and $target.EndsWith('>')) {
      $target = $target.Substring(1, $target.Length - 2)
    }
    if ($target -match '^(https?|mailto|data):') { continue }
    $parts = $target -split '#', 2
    $targetPath = ($parts[0] -split '\s+"', 2)[0]
    $fragment = if ($parts.Count -eq 2) { [Uri]::UnescapeDataString($parts[1]) } else { '' }
    $resolved = if ([string]::IsNullOrWhiteSpace($targetPath)) {
      $file.FullName
    } else {
      [IO.Path]::GetFullPath((Join-Path -Path $file.DirectoryName -ChildPath ([Uri]::UnescapeDataString($targetPath))))
    }
    if (-not (Test-Path -LiteralPath $resolved)) {
      $linkErrors.Add("missing file $target in $($file.FullName)")
      continue
    }
    if ($fragment -and [IO.Path]::GetExtension($resolved) -eq '.md') {
      if (-not $slugCache.ContainsKey($resolved)) { $slugCache[$resolved] = Get-GfmSlugs $resolved }
      if (-not $slugCache[$resolved].ContainsKey($fragment)) {
        $linkErrors.Add("missing anchor $target in $($file.FullName)")
      }
    }
  }
}
if ($linkErrors.Count) { $linkErrors | Sort-Object -Unique; throw 'relative links failed' }
"RELATIVE_LINKS_PASS files=$(($activeFiles | Where-Object Extension -eq '.md').Count)"

$scanFiles = Get-ChildItem $root -Recurse -File | Where-Object {
  $_.FullName -notmatch '[\\/]archive[\\/]'
}
$patterns = [ordered]@{
  private_key = '-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'
  aws_access = '(?<![A-Z0-9])(?:AKIA|ASIA)[A-Z0-9]{16}(?![A-Z0-9])'
  github_token = '(?<![A-Za-z0-9_])(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})(?![A-Za-z0-9_])'
  slack_token = '(?<![A-Za-z0-9])xox[baprs]-[A-Za-z0-9-]{10,}(?![A-Za-z0-9])'
  openai_style_token = '(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}(?![A-Za-z0-9])'
  bearer_value = '(?i)\bBearer\s+[A-Za-z0-9._~+/-]{20,}={0,2}'
  credential_assignment = '(?i)\b(?:api[_-]?key|client[_-]?secret|password|access[_-]?token)\s*[:=]\s*["''][^"'']{8,}["'']'
  credential_url = '(?i)https?://[^/\s:@]+:[^/\s@]+@'
  windows_user_path = '(?i)\b[A-Z]:[\\/]+Users[\\/]+[^\\/\s]+'
  unix_user_path = ('(?i)(?:^|[\s"''])(?:/{0}/|/{1}/)[^/\s"'']+' -f 'home', 'Users')
  private_canary_value = '(?i)\bprivate[-_ ]canary[-_ ](?:id|name|identity)\s*[:=]\s*["'']?[^"''\s|]{3,}'
}
$findings = @()
foreach ($file in $scanFiles) {
  $text = Get-Content -Raw $file.FullName
  foreach ($entry in $patterns.GetEnumerator()) {
    if ([regex]::IsMatch($text, $entry.Value)) {
      $findings += "$($entry.Key):$([IO.Path]::GetRelativePath($root, $file.FullName))"
    }
  }
}
if ($findings) { $findings | Sort-Object -Unique; throw 'privacy/secret scan failed' }
"SECRET_CREDENTIAL_PRIVATE_CANARY_PATH_SCAN_PASS files=$($scanFiles.Count)"

python -u scripts/tests/recursion-v2-mvp.test.py
if ($LASTEXITCODE) { throw 'v2 regression umbrella failed' }
'V2_REGRESSION_PASS'
```

The campaign may run the expensive v2 umbrella before the final receipt commit and then rerun
the fast documentation portion after a receipt-only commit, provided the receipt commit changes
only documentation and records the exact earlier test candidate. Any semantic/source/oracle
change after the test requires the full umbrella again. Final completion additionally requires
the independent Terra receipt, its dissent disposition, a final clean tree, and a manual check
that no unavailable route/verifier/source/counter is described as pass or zero.
