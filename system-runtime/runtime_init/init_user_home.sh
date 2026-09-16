#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

user_home="${RUNTIME_INIT_USER_HOME}"
runtime_cache_root="${RUNTIME_CACHE_ROOT:-/runtime/cache}"

if [ "${VM_GENERATION}" = "v2" ]; then
  "${RUNTIME_INIT_RUNTIME_PATH}/vm_runtime_hook" runtime-layout apply \
    --generation v2 \
    --phase runtime \
    --group user_home \
    --format compact
  runtime_init_success "v2 user home layout ensured"
fi

ensure_user_dir() {
  local path="$1"
  local mode="$2"

  runtime_init_assert_not_symlink "${path}" "managed user directory must not be symlink"
  runtime_init_run_privileged mkdir -p "${path}" || runtime_init_failed "create directory failed: ${path}"
  runtime_init_run_privileged chown user:user "${path}" || runtime_init_failed "chown directory failed: ${path}"
  runtime_init_run_privileged chmod "${mode}" "${path}" || runtime_init_failed "chmod directory failed: ${path}"
}

seed_user_file_if_missing() {
  local source_path="$1"
  local target_path="$2"

  runtime_init_assert_not_symlink "${target_path}" "managed user file must not be symlink"
  if [ -e "${target_path}" ]; then
    runtime_init_log "preserve existing user file: ${target_path}"
    return 0
  fi
  if [ -f "${source_path}" ]; then
    runtime_init_run_privileged install -o user -g user -m 0644 "${source_path}" "${target_path}" ||
      runtime_init_failed "seed user file failed: ${target_path}"
    return 0
  fi
  runtime_init_run_privileged touch "${target_path}" || runtime_init_failed "create user file failed: ${target_path}"
  runtime_init_run_privileged chown user:user "${target_path}" || runtime_init_failed "chown user file failed: ${target_path}"
  runtime_init_run_privileged chmod 0644 "${target_path}" || runtime_init_failed "chmod user file failed: ${target_path}"
}

runtime_init_log "start user home initialization, home=${user_home}"
runtime_init_assert_not_symlink "${user_home}" "user home must not be symlink"
runtime_init_assert_dir "${user_home}" "user home must be directory"
if ! runtime_init_path_is_healthy "${user_home}"; then
  runtime_init_failed "user home is not healthy: ${user_home}"
fi

# Only change the mount root itself. Existing persisted contents are never
# recursively chowned or removed.
runtime_init_run_privileged chown user:user "${user_home}" || runtime_init_failed "chown user home failed"
runtime_init_run_privileged chmod 0755 "${user_home}" || runtime_init_failed "chmod user home failed"

ensure_user_dir "${user_home}/.npm-global" 0755
ensure_user_dir "${user_home}/.local" 0755
ensure_user_dir "${user_home}/.config" 0700
ensure_user_dir "${user_home}/.doubao" 0755
ensure_user_dir "${user_home}/.doubao/agent_mode" 0755
if [ "${VM_GENERATION}" = "v2" ]; then
  ensure_user_dir "${user_home}/.doubao/agent_mode/workspace" 0755
fi

ensure_user_dir "${runtime_cache_root}" 0755
ensure_user_dir "${runtime_cache_root}/user" 0755
ensure_user_dir "${runtime_cache_root}/npm" 0755
ensure_user_dir "${runtime_cache_root}/pip" 0755
ensure_user_dir "${runtime_cache_root}/uv" 0755
ensure_user_dir "${runtime_cache_root}/go-build" 0755

seed_user_file_if_missing "/opt/gem/bashrc" "${user_home}/.bashrc"
seed_user_file_if_missing "/etc/skel/.profile" "${user_home}/.profile"
seed_user_file_if_missing "/etc/skel/.bash_logout" "${user_home}/.bash_logout"

runtime_init_success "user home initialized"
