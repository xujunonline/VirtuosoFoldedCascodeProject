$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot

python -m py_compile `
    (Join-Path $ProjectRoot 'src\python\psfascii_metrics.py') `
    (Join-Path $ProjectRoot 'src\python\sweep_sizes.py') `
    (Join-Path $ProjectRoot 'src\python\remote_ocean.py') `
    (Join-Path $ProjectRoot 'src\python\verify_connection.py')

python -m unittest discover -s (Join-Path $ProjectRoot 'tests') -v

if ($LASTEXITCODE -ne 0) {
    throw "Tests failed with exit code $LASTEXITCODE"
}

python (Join-Path $ProjectRoot 'src\python\verify_manifest.py')

if ($LASTEXITCODE -ne 0) {
    throw "Manifest verification failed with exit code $LASTEXITCODE"
}
