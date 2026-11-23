$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Manifest = Join-Path $ProjectRoot 'MANIFEST.sha256'

$files = Get-ChildItem -LiteralPath $ProjectRoot -Recurse -File | Where-Object {
    $_.FullName -ne $Manifest -and
    $_.FullName -notlike (Join-Path $ProjectRoot '.git\*') -and
    $_.FullName -notlike (Join-Path $ProjectRoot '.secrets\*') -and
    $_.FullName -notlike '*\__pycache__\*' -and
    $_.FullName -notlike (Join-Path $ProjectRoot 'pdk\pdk_device_report.txt') -and
    $_.FullName -notlike (Join-Path $ProjectRoot 'docs\Codex完整聊天记录_*') -and
    $_.FullName -notlike '*\spectre.stdout.log' -and
    $_.FullName -notlike '*\spectre.stderr.log'
} | Sort-Object FullName

$lines = foreach ($file in $files) {
    $relative = $file.FullName.Substring($ProjectRoot.Length + 1).Replace('\', '/')
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    "$hash  $relative"
}

$lines | Set-Content -LiteralPath $Manifest -Encoding utf8
Write-Output "Wrote $Manifest with $($lines.Count) entries."

