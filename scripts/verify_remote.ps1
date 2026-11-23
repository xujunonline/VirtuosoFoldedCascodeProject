$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
. (Join-Path $PSScriptRoot 'resolve_ssh_key.ps1')
$Key = Resolve-VirtuosoSshKey

python (Join-Path $ProjectRoot 'src\python\verify_connection.py') `
    --host 192.168.44.128 `
    --user userone `
    --key $Key

if ($LASTEXITCODE -ne 0) {
    throw "Remote verification failed with exit code $LASTEXITCODE"
}
