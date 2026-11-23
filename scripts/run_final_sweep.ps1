$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'resolve_ssh_key.ps1')
$Key = Resolve-VirtuosoSshKey
$Generated = Join-Path $ProjectRoot 'results\generated'

New-Item -ItemType Directory -Force -Path $Generated | Out-Null

python (Join-Path $ProjectRoot 'src\python\sweep_sizes.py') `
    --host 192.168.44.128 `
    --user userone `
    --key $Key `
    --template (Join-Path $ProjectRoot 'circuit\spectre\fc_ota_fd_template.scs') `
    --config (Join-Path $ProjectRoot 'config\fd_size_sweep.json') `
    --output (Join-Path $Generated 'fd_cmfb_sweep_results.csv') `
    --work (Join-Path $Generated 'runs') `
    --remote-root /home/userone/codex_project_sweeps `
    --signal out `
    --negative-signal ym

if ($LASTEXITCODE -ne 0) {
    throw "W/L sweep failed with exit code $LASTEXITCODE"
}
