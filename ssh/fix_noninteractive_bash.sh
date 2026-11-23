#!/usr/bin/env bash
set -euo pipefail

bashrc="${HOME}/.bashrc"
banner_line='/home/userone/.bashrc_encrypted'
guarded_line='if [[ $- == *i* ]]; then /home/userone/.bashrc_encrypted; fi'

if grep -Fqx -- "${guarded_line}" "${bashrc}"; then
  printf 'Non-interactive guard already installed.\n'
  exit 0
fi

if ! grep -Fqx -- "${banner_line}" "${bashrc}"; then
  printf 'Expected banner line was not found; no change made.\n' >&2
  exit 2
fi

backup="${bashrc}.codex-backup-20260719"
if [[ ! -e "${backup}" ]]; then
  cp -p -- "${bashrc}" "${backup}"
fi

awk -v old="${banner_line}" -v replacement="${guarded_line}" \
  '{ if ($0 == old) print replacement; else print $0 }' \
  "${bashrc}" > "${bashrc}.codex-tmp"
chmod --reference="${bashrc}" "${bashrc}.codex-tmp"
mv -f -- "${bashrc}.codex-tmp" "${bashrc}"

printf 'Updated %s; backup: %s\n' "${bashrc}" "${backup}"
