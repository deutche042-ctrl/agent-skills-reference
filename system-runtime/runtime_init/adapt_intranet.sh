#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

app_log_dir="/opt/tiger/toutiao/log/app"

if [ "${VM_GENERATION}" = "v2" ]; then
  result="$(
    "${RUNTIME_INIT_RUNTIME_PATH}/vm_runtime_hook" runtime-layout apply \
      --generation v2 \
      --phase runtime \
      --group app_log \
      --format compact
  )"
  printf '%s\n' "${result}"
  if [[ "${result}" == *"skipped=app.log"* ]]; then
    runtime_init_skipped "v2 app log layout skipped"
  fi
  runtime_init_success "v2 app log layout reconciled"
fi

runtime_init_log "start adapt intranet, app_log_dir=${app_log_dir}"
if [ ! -e "${app_log_dir}" ]; then
  runtime_init_log "app log dir is absent, skip adapt intranet: ${app_log_dir}"
  runtime_init_skipped "app log dir is absent"
fi
if ! runtime_init_path_is_healthy "${app_log_dir}"; then
  runtime_init_log "app log dir is not healthy, skip adapt intranet: ${app_log_dir}"
  runtime_init_skipped "app log dir is not healthy"
fi
runtime_init_assert_not_symlink "${app_log_dir}" "app log dir must not be symlink"
runtime_init_assert_dir "${app_log_dir}" "app log dir must be directory"

stage_start_ms="$(runtime_init_now_ms)"
# Do not follow symlinks under the log dir. The target is an intranet runtime
# log directory; symlink entries are intentionally left untouched.
if ! runtime_init_run_privileged find "${app_log_dir}" -xdev ! -type l \( ! -user user -o ! -group user \) -exec chown user:user {} +; then
  runtime_init_log "chown app log dir failed, continue: ${app_log_dir}"
fi
runtime_init_log_duration_ms "chown_app_log_dir_user" "${stage_start_ms}"

owner="$(runtime_init_path_owner "${app_log_dir}" || true)"
runtime_init_log "adapt intranet finished, app_log_dir=${app_log_dir}, owner=${owner:-unknown}"
runtime_init_success "intranet adapted"
