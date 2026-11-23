#!/usr/bin/env bash
set -euo pipefail

# Run once inside the RedHat VM as the desktop user who owns the Cadence setup.
# It installs only the dedicated public key beside this script and records the
# Cadence command paths visible from a login shell.

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
public_key_file="${script_dir}/virtuoso_vm_ed25519.pub"
status_file="${script_dir}/virtuoso_guest_status.env"

if [[ ! -r "${public_key_file}" ]]; then
  printf 'Missing public key: %s\n' "${public_key_file}" >&2
  exit 2
fi

target_user="$(id -un)"
target_home="$(getent passwd "${target_user}" | cut -d: -f6)"
if [[ -z "${target_home}" || ! -d "${target_home}" ]]; then
  printf 'Cannot resolve home directory for %s\n' "${target_user}" >&2
  exit 3
fi

ssh_dir="${target_home}/.ssh"
authorized_keys="${ssh_dir}/authorized_keys"
install -d -m 700 "${ssh_dir}"
touch "${authorized_keys}"
chmod 600 "${authorized_keys}"

public_key="$(tr -d '\r\n' < "${public_key_file}")"
if ! grep -Fqx -- "${public_key}" "${authorized_keys}"; then
  printf '%s\n' "${public_key}" >> "${authorized_keys}"
fi

restorecon -R "${ssh_dir}" >/dev/null 2>&1 || true

find_login_command() {
  local command_name="$1"
  TERM=dumb NO_COLOR=1 bash -lc "command -v ${command_name} 2>/dev/null" 2>/dev/null \
    | grep '^/' \
    | tail -n 1 \
    || true
}

ocean_path="$(find_login_command ocean)"
spectre_path="$(find_login_command spectre)"
virtuoso_path="$(find_login_command virtuoso)"

status_tmp="${status_file}.tmp.$$"
{
  printf 'SSH_USER=%s\n' "${target_user}"
  printf 'SSH_HOST=%s\n' "$(hostname -f 2>/dev/null || hostname)"
  printf 'SSH_HOME=%s\n' "${target_home}"
  printf 'OCEAN_PATH=%s\n' "${ocean_path}"
  printf 'SPECTRE_PATH=%s\n' "${spectre_path}"
  printf 'VIRTUOSO_PATH=%s\n' "${virtuoso_path}"
  printf 'CREATED_UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "${status_tmp}"
mv -f "${status_tmp}" "${status_file}"

printf 'SSH authorization installed for %s.\n' "${target_user}"
printf 'Environment report: %s\n' "${status_file}"
if [[ -z "${ocean_path}" ]]; then
  printf 'Note: ocean is not visible in a login shell; Cadence setup sourcing is still required.\n'
fi
