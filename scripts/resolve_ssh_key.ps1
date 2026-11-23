function Resolve-VirtuosoSshKey {
    $candidates = @()

    if ($env:VIRTUOSO_SSH_KEY) {
        $candidates += $env:VIRTUOSO_SSH_KEY
    }

    $candidates += (Join-Path $env:USERPROFILE '.ssh\virtuoso_vm_ed25519')

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    throw @"
SSH private key not found. Set VIRTUOSO_SSH_KEY or place the key at:
  $env:USERPROFILE\.ssh\virtuoso_vm_ed25519
Do not store the private key on an exFAT project drive because exFAT has no NTFS ACLs.
"@
}
