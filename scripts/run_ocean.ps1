param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$OceanScript
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'resolve_ssh_key.ps1')
$Key = Resolve-VirtuosoSshKey
$ResolvedScript = Resolve-Path -LiteralPath (Join-Path $ProjectRoot $OceanScript)

python (Join-Path $ProjectRoot 'src\python\remote_ocean.py') `
    --host 192.168.44.128 `
    --user userone `
    --key $Key `
    --ocean /opt/eda/cadence/IC251/tools/dfII/bin/ocean `
    $ResolvedScript.Path

if ($LASTEXITCODE -ne 0) {
    throw "OCEAN execution failed with exit code $LASTEXITCODE"
}
