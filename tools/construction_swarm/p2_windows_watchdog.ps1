[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9._-]{1,128}$')]
    [string] $Distro,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ $_.StartsWith('/') -and $_.Length -le 4096 -and $_ -notmatch "[`0`r`n]" })]
    [string] $LinuxRepository,

    [Parameter(Mandatory = $true)]
    [ValidateScript({ $_.StartsWith('/') -and $_.Length -le 4096 -and $_ -notmatch "[`0`r`n]" })]
    [string] $Config,

    [switch] $DryRun
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# Keep every value as a distinct argv element. This wrapper never evaluates a
# command string and never accepts a credential or token parameter.
$wslArguments = @(
    '-d', $Distro,
    '--cd', $LinuxRepository,
    '--exec',
    'python3', '-X', 'utf8', '-B',
    '-m', 'tools.construction_swarm.p2_host_lifecycle',
    'run', '--config', $Config
)

if ($DryRun) {
    [ordered]@{
        executable = 'wsl.exe'
        argument_list = $wslArguments
        contains_credentials = $false
    } | ConvertTo-Json -Depth 3 -Compress
    exit 0
}

& wsl.exe @wslArguments
exit $LASTEXITCODE
