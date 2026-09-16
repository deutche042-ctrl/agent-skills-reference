#!/bin/bash

set -euo pipefail

entrypoint_log_icon() {
  case "$1" in
    debug) printf '%s' '🔍' ;;
    warn) printf '%s' '⚠️' ;;
    error) printf '%s' '❗' ;;
    *) printf '%s' 'ℹ️' ;;
  esac
}

entrypoint_log_level() {
  case "$1" in
    debug) printf '%s' 'DEBUG' ;;
    warn) printf '%s' ' WARN' ;;
    error) printf '%s' 'ERROR' ;;
    *) printf '%s' ' INFO' ;;
  esac
}

entrypoint_log() {
  local lifecycle="$1"
  local level="$2"
  local hierarchy="$3"
  local event="$4"
  local module="$5"
  local method="$6"
  local message="$7"
  shift 7
  local fields="" key value scope
  for key in session_id agent_id log_id tool_use_id; do
    case "${key}" in
      session_id) value="${SESSION_ID:-}" ;;
      agent_id) value="${AGENT_ID:-}" ;;
      log_id) value="${LOG_ID:-}" ;;
      tool_use_id) value="${TOOL_USE_ID:-}" ;;
    esac
    [ -z "${value}" ] && continue
    fields="${fields}${fields:+ }${key}=${value//$'\n'/\\n}"
  done
  if [ "${level}" != "info" ]; then
    fields="${fields}${fields:+ }level=${level}"
  fi
  for key in "$@"; do
    if [[ "${key}" == *=* ]]; then
      value="${key#*=}"
      fields="${fields}${fields:+ }${key%%=*}=${value//$'\n'/\\n}"
    fi
  done
  scope="${lifecycle}/entrypoint.sh/${module}"
  if [ -n "${method}" ] && [ "${method}" != "entrypoint.sh" ]; then
    scope="${scope}/${method}"
  fi
  if [ -n "${fields}" ]; then
    printf '[VM Shell] %s [%s] %s | %s\n' "${event}" "${scope}" "${message}" "${fields}"
  else
    printf '[VM Shell] %s [%s] %s\n' "${event}" "${scope}" "${message}"
  fi
}

entrypoint_log_lifecycle_signal() {
  local lifecycle="$1"
  local severity="$2"
  shift 2
  local event="log_message_reported"
  case "${lifecycle}:${severity}" in
    bootstrap:error) event="container_start_failed" ;;
    destroy:error) event="container_stop_failed" ;;
  esac
  entrypoint_log "${lifecycle}" "${severity}" "-" "${event}" bootstrap entrypoint.sh "$*" \
    "signal=${lifecycle}_${severity}"
}

# 重定输出到日志文件
if [ -n "${MCP_VM_SERVER_LOG_PATH:-}" ]; then
    touch "${MCP_VM_SERVER_LOG_PATH}"
    chown user:user "${MCP_VM_SERVER_LOG_PATH}"
    exec &> >(tee -a "${MCP_VM_SERVER_LOG_PATH}")
fi

PROFILE="${MCP_VM_PROFILE:-all}"
export MCP_VM_LOG_LIFECYCLE=bootstrap
ENTRYPOINT_START_SECONDS="${SECONDS}"
# 统一镜像入口：默认走 all，命中 ci profile 时尽早转发到专用入口。
case "${PROFILE}" in
  all)
    ;;
  ci)
    entrypoint_log bootstrap info "-" profile_selected bootstrap entrypoint.sh \
      "CI profile selected" "profile=ci"
    exec "${RUNTIME_PATH}/entrypoint_ci.sh" "$@"
    ;;
  *)
    entrypoint_log_lifecycle_signal bootstrap error \
      "unknown MCP_VM_PROFILE=${PROFILE}" >&2
    exit 1
    ;;
esac

normalize_wait_ports() {
  local wait_ports="${WAIT_PORTS:-8091}"
  local original_wait_ports="${WAIT_PORTS:-<empty>}"

  # all 模式下 nginx 默认等待 8091；如果启用了 CI server，再补上 9999。
  if [ "${ENABLE_CI_SERVER:-true}" = "true" ]; then
    case ",${wait_ports}," in
      *,9999,*)
        ;;
      *)
        wait_ports="${wait_ports},9999"
        ;;
    esac
  fi

  export WAIT_PORTS="${wait_ports}"
  entrypoint_log bootstrap info "--" wait_ports_configured runtime_layout \
    normalize_wait_ports "service wait ports configured" \
    "original=${original_wait_ports}" "configured=${WAIT_PORTS}"
}

normalize_wait_ports

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_INIT_DIR="${SCRIPT_DIR}/runtime_init"
RESOURCE_INIT_DIR="${RESOURCE_INIT_DIR:-/tmp/resource-init}"
RESOURCE_INIT_SUMMARY_OUTPUT=""

normalize_vm_generation() {
  case "${VM_GENERATION:-}" in
    ""|v1)
      export VM_GENERATION="v1"
      ;;
    v2)
      export VM_GENERATION="v2"
      ;;
    *)
      entrypoint_log_lifecycle_signal bootstrap error \
        "invalid VM_GENERATION=${VM_GENERATION}" >&2
      return 1
      ;;
  esac
}

configure_v2_layout_env() {
  local layout_env_json aio_runtime_dir browser_data_dir downloads_path
  layout_env_json="$(
    "${SCRIPT_DIR}/vm_runtime_hook" runtime-layout env \
      --generation v2 \
      --session-id "${SESSION_ID:-}" \
      --format json
  )" || return 1

  aio_runtime_dir="$(
    jq -er '.AIO_RUNTIME_DIR | select(type == "string" and length > 0)' \
      <<<"${layout_env_json}"
  )" || return 1
  browser_data_dir="$(
    jq -er '.BROWSER_DATA_DIR | select(type == "string" and length > 0)' \
      <<<"${layout_env_json}"
  )" || return 1
  downloads_path="$(
    jq -er '.DOWNLOADS_PATH | select(type == "string" and length > 0)' \
      <<<"${layout_env_json}"
  )" || return 1

  export AIO_RUNTIME_DIR="${aio_runtime_dir}"
  export BROWSER_DATA_DIR="${browser_data_dir}"
  export DOWNLOADS_PATH="${downloads_path}"
}

configure_resource_loader_bin_path() {
  export RESOURCE_LOADER_OVERRIDE_ENABLED="${RESOURCE_LOADER_OVERRIDE_ENABLED:-true}"
  case "${VM_GENERATION}" in
    v1)
      export RESOURCE_LOADER_BIN_PATH="/opt/vm/resource-loader/bin"
      ;;
    v2)
      export RESOURCE_LOADER_BIN_PATH="/home/user/vm/resource-loader/bin"
      ;;
  esac
}

normalize_vm_generation
configure_resource_loader_bin_path
case "${VM_GENERATION}" in
  v1)
    source "${RUNTIME_INIT_DIR}/common.sh"
    if ls /sandboxdata/data >/dev/null 2>&1; then
      export MCP_VM_STANDBY=0
    else
      export MCP_VM_STANDBY=1
    fi
    ;;
  v2)
    if configure_v2_layout_env; then
      :
    else
      configure_layout_status=$?
      entrypoint_log_lifecycle_signal bootstrap error \
        "configure v2 runtime layout env failed, status=${configure_layout_status}" >&2
      exit "${configure_layout_status}"
    fi
    source "${RUNTIME_INIT_DIR}/common.sh"
    if "${SCRIPT_DIR}/vm_runtime_hook" runtime-layout apply \
      --generation v2 \
      --phase bootstrap \
      --format compact; then
      :
    else
      apply_layout_status=$?
      entrypoint_log_lifecycle_signal bootstrap error \
        "apply v2 runtime layout failed, status=${apply_layout_status}" >&2
      exit "${apply_layout_status}"
    fi
    if [ -n "${SESSION_ID:-}" ]; then
      export MCP_VM_STANDBY=0
    else
      export MCP_VM_STANDBY=1
    fi
    ;;
esac
if [ "${VM_GENERATION}" = "v2" ] || [ "${MCP_VM_STANDBY}" = "0" ]; then
  export BROWSER_DOWNLOAD_DIR="${DOWNLOADS_PATH}"
else
  unset BROWSER_DOWNLOAD_DIR
fi

if [ "${UNSET_PROXY:-false}" = "true" ]; then
  unset PROXY PROXY_SERVER http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
  entrypoint_log bootstrap info "--" proxy_env_cleared proxy entrypoint.sh \
    "proxy environment cleared" "reason=unset_proxy"
fi

if [ "${MCP_VM_STANDBY}" = "1" ]; then
  STARTUP_MODE="standby"
else
  STARTUP_MODE="cold"
fi
entrypoint_log bootstrap info "-" container_start_started bootstrap entrypoint.sh \
  "container starting" \
  "startup_mode=${STARTUP_MODE}" \
  "generation=${VM_GENERATION}" \
  "profile=${PROFILE}"
entrypoint_log bootstrap info "--" resource_loader_path_selected runtime_layout \
  configure_resource_loader_bin_path "resource-loader path selected" \
  "generation=${VM_GENERATION}" \
  "path=${RESOURCE_LOADER_BIN_PATH}" \
  "override_enabled=${RESOURCE_LOADER_OVERRIDE_ENABLED}"

filter_user_package_paths() {
  local value="$1"
  shift
  local result=""
  local item excluded skip
  local items=()
  IFS=':' read -r -a items <<< "${value}"
  for item in "${items[@]}"; do
    [ -n "${item}" ] || continue
    skip=false
    for excluded in "$@"; do
      if [ "${item}" = "${excluded}" ]; then
        skip=true
        break
      fi
    done
    if [ "${skip}" = "true" ]; then
      continue
    fi
    if [ -z "${result}" ]; then
      result="${item}"
    else
      result="${result}:${item}"
    fi
  done
  printf '%s' "${result}"
}

configure_process_user_env() {
  export HOME="${RUNTIME_INIT_USER_HOME}"

  local path_rest node_path_rest
  path_rest="$(filter_user_package_paths "${PATH:-}" \
    "${RUNTIME_INIT_USER_HOME}/.npm-global/bin" \
    "${RUNTIME_INIT_USER_HOME}/.local/bin" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.npm-global/bin" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.local/bin")"
  node_path_rest="$(filter_user_package_paths "${NODE_PATH:-}" \
    "${RUNTIME_INIT_USER_HOME}/.npm-global/lib/node_modules" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.npm-global/lib/node_modules")"

  export NPM_CONFIG_PREFIX="${HOME}/.npm-global"
  export PYTHONUSERBASE="${HOME}/.local"
  export UV_TOOL_DIR="${PYTHONUSERBASE}/share/uv/tools"
  export UV_TOOL_BIN_DIR="${PYTHONUSERBASE}/bin"
  export PATH="${NPM_CONFIG_PREFIX}/bin:${PYTHONUSERBASE}/bin${path_rest:+:${path_rest}}"
  export NODE_PATH="${NPM_CONFIG_PREFIX}/lib/node_modules${node_path_rest:+:${node_path_rest}}"
  export XDG_CONFIG_HOME="${HOME}/.config"
  export XDG_CACHE_HOME="/runtime/cache/user"
  export NPM_CONFIG_CACHE="/runtime/cache/npm"
  export PIP_CACHE_DIR="/runtime/cache/pip"
  export UV_CACHE_DIR="/runtime/cache/uv"
  export GOCACHE="/runtime/cache/go-build"
  export PLAYWRIGHT_BROWSERS_PATH="/opt/vm/preinstall/ms-playwright"
  # Let pip auto-select the user site outside virtualenvs and the venv itself
  # inside virtualenvs. A global PIP_USER=1 makes every venv install fail.
  unset PIP_USER

  entrypoint_log bootstrap info "--" user_process_env_configured environment \
    configure_process_user_env "user process environment configured" \
    "generation=${VM_GENERATION}" "npm_prefix_configured=true" "python_user_base_configured=true"
}

configure_system_process_env() {
  local path_rest node_path_rest
  path_rest="$(filter_user_package_paths "${PATH:-}" \
    "${RUNTIME_INIT_USER_HOME}/.npm-global/bin" \
    "${RUNTIME_INIT_USER_HOME}/.local/bin" \
    "${RUNTIME_INIT_USER_HOME}/.fnm_shell/bin" \
    "${RUNTIME_INIT_USER_HOME}/gopath/bin" \
    "${RUNTIME_INIT_USER_HOME}/go/bin" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.npm-global/bin" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.local/bin")"
  node_path_rest="$(filter_user_package_paths "${NODE_PATH:-}" \
    "${RUNTIME_INIT_USER_HOME}/.npm-global/lib/node_modules" \
    "${RUNTIME_INIT_AGENT_MODE_WORKSPACE}/.npm-global/lib/node_modules")"

  export HOME="${RUNTIME_PATH}/home"
  export NPM_CONFIG_PREFIX="/opt/vm/preinstall/npm-global"
  export PYTHONUSERBASE="${HOME}/.local"
  export PATH="${path_rest}"
  export NODE_PATH="${node_path_rest}"
  export XDG_CACHE_HOME="/runtime/cache/system"
  export NPM_CONFIG_CACHE="/runtime/cache/npm-system"
  export PIP_CACHE_DIR="/runtime/cache/pip-system"
  export UV_CACHE_DIR="/runtime/cache/uv-system"
  export GOCACHE="/runtime/cache/go-build-system"
  export PLAYWRIGHT_BROWSERS_PATH="/opt/vm/preinstall/ms-playwright"
  unset PIP_USER XDG_CONFIG_HOME

  entrypoint_log bootstrap info "--" system_process_env_configured environment \
    configure_system_process_env "system process environment configured" \
    "npm_prefix_configured=true" "cache_scope=system"
}

sync_browser_proxy_server_env() {
	# TODO: 确认出网是否有配置。显式 Browser 出口优先，避免 GOST 被 Shell
	# proxy 覆盖；两者都缺失时由 runtime post-hook fail closed。
	if [ -n "${PROXY_SERVER:-}" ]; then
		entrypoint_log bootstrap info "--" browser_proxy_env_selected proxy \
			sync_browser_proxy_server_env "explicit browser proxy preserved" "source=proxy_server"
		return 0
	fi

	if [ -z "${PROXY:-}" ]; then
		entrypoint_log bootstrap info "--" browser_proxy_env_skipped proxy \
			sync_browser_proxy_server_env "browser proxy left unconfigured" "reason=proxy_unavailable"
		return 0
	fi

  export PROXY_SERVER="${PROXY}"
	entrypoint_log bootstrap info "--" browser_proxy_env_selected proxy \
		sync_browser_proxy_server_env "browser proxy selected from shell proxy" "source=proxy"
}

export_shell_http_proxy_env() {
  if [ -z "${PROXY:-}" ]; then
    entrypoint_log bootstrap info "--" shell_proxy_env_skipped proxy \
      export_shell_http_proxy_env "shell proxy export skipped" "reason=proxy_unavailable"
    return 0
  fi
  runtime_init_validate_proxy_url "${PROXY}"

  local no_proxy_value="localhost,127.0.0.1,::1"
  if [ -n "${NO_PROXY_DOMAINS:-}" ]; then
    no_proxy_value="${no_proxy_value},${NO_PROXY_DOMAINS}"
  fi
  runtime_init_validate_no_proxy_list "${no_proxy_value}"

  export http_proxy="${PROXY}"
  export https_proxy="${PROXY}"
  export HTTP_PROXY="${PROXY}"
  export HTTPS_PROXY="${PROXY}"
  export no_proxy="${no_proxy_value}"
  export NO_PROXY="${no_proxy_value}"
  entrypoint_log bootstrap info "--" shell_proxy_env_configured proxy \
    export_shell_http_proxy_env "shell proxy environment configured" \
    "no_proxy_configured=true"
}

start_official_npm_cli_install_async() {
  if [ "${MCP_VM_STANDBY}" != "0" ]; then
    entrypoint_log bootstrap info "--" npm_cli_install_skipped npm \
      start_official_npm_cli_install_async "official npm CLI installation skipped" \
      "reason=standby"
    return 0
  fi
  if [ -z "${MCP_VM_OFFICIAL_NPM_CLI_INSTALL_CONFIG_B64:-}" ]; then
    entrypoint_log bootstrap info "--" npm_cli_install_skipped npm \
      start_official_npm_cli_install_async "official npm CLI installation skipped" \
      "reason=config_absent"
    return 0
  fi
  (
    set +e
    RUNTIME_INIT_EMIT_STATUS_MARKERS=false bash "${RUNTIME_INIT_DIR}/official_npm_cli_install.sh"
    local install_status=$?
    if [ "${install_status}" -ne 0 ]; then
      entrypoint_log bootstrap warn "--" npm_cli_install_degraded npm \
        start_official_npm_cli_install_async "official npm CLI installation failed" \
        "exit_code=${install_status}"
    fi
    exit "${install_status}"
  ) &
  OFFICIAL_NPM_CLI_INSTALL_PID=$!
  entrypoint_log bootstrap info "--" npm_cli_install_submitted npm \
    start_official_npm_cli_install_async "official npm CLI installation submitted" \
    "pid=${OFFICIAL_NPM_CLI_INSTALL_PID}"
}

wait_official_npm_cli_install() {
  if [ -z "${OFFICIAL_NPM_CLI_INSTALL_PID:-}" ]; then
    return 0
  fi
  if wait "${OFFICIAL_NPM_CLI_INSTALL_PID}"; then
    return 0
  fi
  local wait_status=$?
  if [ "${wait_status}" -gt 128 ]; then
    entrypoint_log bootstrap warn "--" npm_cli_install_degraded npm \
      wait_official_npm_cli_install "official npm CLI installation wait interrupted" \
      "exit_code=${wait_status}"
    return 0
  fi
  entrypoint_log bootstrap warn "--" npm_cli_install_degraded npm \
    wait_official_npm_cli_install "official npm CLI installation failed; continuing startup" \
    "exit_code=${wait_status}"
  return 0
}

wait_service_startup_before_official_npm_cli_wait() {
  if [ -z "${OFFICIAL_NPM_CLI_INSTALL_PID:-}" ]; then
    return 0
  fi
  local health_url="http://127.0.0.1:${VM_SERVER_PORT}/vm/exec/api/v3/health"
  local timeout_seconds="${OFFICIAL_NPM_CLI_INSTALL_SERVICE_READY_TIMEOUT_SECONDS:-30}"
  local deadline=$((SECONDS + timeout_seconds))
  while [ "${SECONDS}" -lt "${deadline}" ]; do
    if curl -fsS --max-time 2 "${health_url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  entrypoint_log bootstrap warn "--" npm_cli_install_degraded npm \
    wait_service_startup_before_official_npm_cli_wait "service startup wait timed out before npm CLI installation wait" \
    "timeout_seconds=${timeout_seconds}"
  return 0
}

wait_vm_server_ready() {
  local health_url="http://127.0.0.1:${VM_SERVER_PORT}/vm/exec/api/v3/health"
  local timeout_seconds="${VM_SERVER_STARTUP_TIMEOUT_SECONDS:-60}"
  local deadline=$((SECONDS + timeout_seconds))

  while [ "${SECONDS}" -lt "${deadline}" ]; do
    if curl -fsS --max-time 2 "${health_url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  return 1
}

run_runtime_init_script() {
  local script_name="$1"
  local failure_severity="${2:-error}"
  local script_path="${RUNTIME_INIT_DIR}/${script_name}"
  entrypoint_log bootstrap info "--" runtime_init_script_started runtime_init \
    run_runtime_init_script "runtime init script starting" "script=${script_name}"
  if [ ! -f "${script_path}" ]; then
    entrypoint_log bootstrap error "--" runtime_init_script_failed runtime_init \
      run_runtime_init_script "runtime init script not found" "script=${script_name}" >&2
    exit 1
  fi
  local status=0
  if RUNTIME_INIT_EMIT_STATUS_MARKERS=false bash "${script_path}"; then
    return 0
  else
    status=$?
  fi
  entrypoint_log bootstrap "${failure_severity}" "--" runtime_init_script_failed runtime_init \
    run_runtime_init_script "runtime init script failed" \
    "script=${script_name}" "exit_code=${status}" >&2
  return "${status}"
}

run_runtime_init_script_best_effort() {
  local script_name="$1"
  if run_runtime_init_script "${script_name}" warn; then
    return 0
  fi
  entrypoint_log bootstrap warn "--" runtime_init_script_degraded runtime_init \
    run_runtime_init_script_best_effort "runtime init script failed; continuing startup" \
    "script=${script_name}"
  return 0
}

start_persistent_sync() {
  if [ "${MCP_VM_STANDBY}" != "0" ]; then
    entrypoint_log bootstrap info "--" persistent_restore_skipped persistence \
      start_persistent_sync "persistent restore skipped" "reason=standby"
    return 0
  fi
  if [ -z "${MCP_VM_PERSISTENT_SYNC_CONFIG_B64:-}" ]; then
    entrypoint_log bootstrap info "--" persistent_restore_skipped persistence \
      start_persistent_sync "persistent restore skipped" "reason=config_absent"
    return 0
  fi
  RUNTIME_INIT_EMIT_STATUS_MARKERS=false bash "${RUNTIME_INIT_DIR}/persistent_sync.sh" restore &
  PERSISTENT_SYNC_PID=$!
  entrypoint_log bootstrap info "--" persistent_restore_submitted persistence \
    start_persistent_sync "persistent restore submitted" "pid=${PERSISTENT_SYNC_PID}"
}

if [ "${MCP_VM_STANDBY}" = "0" ]; then
  run_runtime_init_script init_user_home.sh
  configure_process_user_env
  if "${SCRIPT_DIR}/vm_runtime_hook" workspace-init; then
    :
  else
    workspace_init_status=$?
    entrypoint_log_lifecycle_signal bootstrap error \
      "workspace init failed, status=${workspace_init_status}" >&2
    exit "${workspace_init_status}"
  fi
else
  entrypoint_log bootstrap info "--" session_init_deferred runtime_layout entrypoint.sh \
    "session initialization deferred to post-hook" "deferred_module=home_workspace"
fi
configure_system_process_env

resource_init_summary_output_path() {
	local mode="$2"
	printf '%s/%s_resource_init_summary.json' "${RESOURCE_INIT_DIR}" "${mode}"
}

run_resource_init_if_needed() {
	RESOURCE_INIT_SUMMARY_OUTPUT=""
	local manifest_path="${MCP_VM_RESOURCE_INIT_MANIFEST_PATH:-}"
	if [ -z "${manifest_path}" ] || [ ! -s "${manifest_path}" ]; then
		entrypoint_log bootstrap info "--" resource_init_skipped resource_init \
			run_resource_init_if_needed "resource init skipped" "reason=manifest_unavailable"
		return 0
	fi
	# manifest 是一次性输入。RETURN 覆盖正常返回，EXIT 覆盖 set -e 在命令替换等
	# 场景直接终止 shell；%q 将 local 路径固化进 trap，避免 EXIT 时变量已离开作用域。
	local cleanup_manifest_command
	printf -v cleanup_manifest_command \
		'trap - RETURN EXIT; rm -f -- %q || echo %q >&2' \
		"${manifest_path}" "resource init manifest cleanup failed: ${manifest_path}"
	trap "${cleanup_manifest_command}" RETURN EXIT

	local workspace
	workspace="$(jq -er '.work_dir' /run/mcp_vm_server/workspace_config.json 2>/dev/null || printf '%s' "${RUNTIME_INIT_WORKSPACE}")"
	mkdir -p "${RESOURCE_INIT_DIR}"
	if [ -L "${RESOURCE_INIT_DIR}" ]; then
		entrypoint_log_lifecycle_signal bootstrap error \
			"resource init dir must not be a symlink" >&2
		return 1
	fi
	chown root:root "${RESOURCE_INIT_DIR}"
	chmod 0700 "${RESOURCE_INIT_DIR}"
	local manifest_id summary_output
	manifest_id="$(resource-loader manifest-id --manifest "${manifest_path}")"
	summary_output="$(resource_init_summary_output_path "${manifest_id}" "entrypoint")"
	entrypoint_log bootstrap info "--" resource_init_started resource_init \
		run_resource_init_if_needed "resource initialization starting" \
		"manifest_id=${manifest_id}" "workspace_configured=true"
	local apply_status=0
	if resource-loader apply --manifest "${manifest_path}" --workspace "${workspace}" --mode entrypoint --summary-output "${summary_output}"; then
		:
	else
		apply_status=$?
	fi
	if [ "${apply_status}" -ne 0 ]; then
		entrypoint_log_lifecycle_signal bootstrap error \
			"resource init failed, status=${apply_status}" >&2
		return "${apply_status}"
	fi
	RESOURCE_INIT_SUMMARY_OUTPUT="${summary_output}"
	entrypoint_log bootstrap info "--" resource_init_succeeded resource_init \
		run_resource_init_if_needed "resource initialization completed" \
		"manifest_id=${manifest_id}"
}

configure_lark_cli_resource_path() {
	local asset_id="${LARK_CLI_ASSET_ID:-}"
	unset LARK_CLI_RESOURCE_PATH
	if [ -z "${asset_id}" ] || [ -z "${RESOURCE_INIT_SUMMARY_OUTPUT}" ]; then
		entrypoint_log bootstrap info "--" lark_cli_resource_fallback_selected lark_cli \
			configure_lark_cli_resource_path "lark CLI resource unavailable; using legacy chain" \
			"reason=resource_summary_unavailable"
		return 0
	fi
	if LARK_CLI_RESOURCE_PATH="$(resource-loader artifact-path --summary-output "${RESOURCE_INIT_SUMMARY_OUTPUT}" --asset-id "${asset_id}")"; then
		export LARK_CLI_RESOURCE_PATH
		entrypoint_log bootstrap info "--" lark_cli_resource_selected lark_cli \
			configure_lark_cli_resource_path "lark CLI resource selected" \
			"asset_id=${asset_id}" "resource_path=${LARK_CLI_RESOURCE_PATH}"
		return 0
	fi
	entrypoint_log bootstrap info "--" lark_cli_resource_fallback_selected lark_cli \
		configure_lark_cli_resource_path "lark CLI resource unavailable; using legacy chain" \
		"asset_id=${asset_id}" "reason=artifact_unavailable"
}

merge_browser_disable_features() {
  local features="${DISABLE_BROWSER_FEATURES:-}"
  local option_args="${BROWSER_COMMANDLINE_ARGS:-}"
  local positional_args=""
  features="${features//[[:space:]]/}"
  [ -z "${features}" ] && return 0

  if ! grep -Eq '^[A-Za-z0-9_,.:/<>-]+$' <<<"${features}"; then
    entrypoint_log bootstrap error "--" browser_feature_policy_rejected browser \
      merge_browser_disable_features "browser feature policy rejected" \
      "reason=invalid_feature_name" \
      "configured_bytes=${#features}" >&2
    return 1
  fi

  if [[ "${option_args}" == "-- "* ]]; then
    positional_args=" -- ${option_args#-- }"
    option_args=""
  elif [[ "${option_args}" == *" -- "* ]]; then
    positional_args=" -- ${option_args#* -- }"
    option_args="${option_args%% -- *}"
  fi

  if [[ "${option_args}" =~ (.*--disable-features=)([^[:space:]]+)(.*) ]]; then
    option_args="${BASH_REMATCH[1]}${BASH_REMATCH[2]},${features}${BASH_REMATCH[3]}"
  else
    option_args="${option_args:+${option_args} }--disable-features=${features}"
  fi
  BROWSER_COMMANDLINE_ARGS="${option_args}${positional_args}"
  export BROWSER_COMMANDLINE_ARGS
}

init_browser_config() {
  local start_marker="# >>> mcp_vm_server browser config start >>>"
  local end_marker="# <<< mcp_vm_server browser config end <<<"
  local tmp_file filtered_file
  if ! merge_browser_disable_features; then
    return 1
  fi
  local configured_features="${DISABLE_BROWSER_FEATURES:-}"
  configured_features="${configured_features//[[:space:]]/}"
  local configured_count=0
  if [ -n "${configured_features}" ]; then
    configured_count="$(awk -F ',' '{print NF}' <<<"${configured_features}")"
  fi
  entrypoint_log bootstrap info "--" browser_feature_policy_configured browser \
    init_browser_config "browser feature policy configured" \
    "configured_count=${configured_count}"
  export BROWSER_EXTRA_ARGS="${BROWSER_EXTRA_ARGS:-} --disable-sync --disable-component-update"
  tmp_file="$(mktemp)"
  filtered_file="$(mktemp)"
  touch /root/.bashrc
  awk -v start="${start_marker}" -v end="${end_marker}" '
    $0 == start { skip = 1; next }
    $0 == end { skip = 0; next }
    skip != 1 { print }
  ' /root/.bashrc > "${filtered_file}"
  cat "${filtered_file}" > "${tmp_file}"
  {
    echo "${start_marker}"
    printf 'export BROWSER_COMMANDLINE_ARGS=%q\n' "${BROWSER_COMMANDLINE_ARGS:-}"
    printf 'export BROWSER_EXTRA_ARGS=%q\n' "${BROWSER_EXTRA_ARGS}"
    echo "${end_marker}"
  } >> "${tmp_file}"
  mv "${tmp_file}" /root/.bashrc
  rm -f "${filtered_file}"
}

start_vm_runtime_hook() {
  if [ -z "${VM_RUNTIME_HOOK_INTERNAL_TOKEN:-}" ]; then
    VM_RUNTIME_HOOK_INTERNAL_TOKEN="$(od -An -N32 -tx1 /dev/urandom | tr -d ' \n')"
    export VM_RUNTIME_HOOK_INTERNAL_TOKEN
  fi

  "${SCRIPT_DIR}/vm_runtime_hook" --host 127.0.0.1 --port 10080 &
  VM_RUNTIME_HOOK_PID=$!
  entrypoint_log bootstrap info "--" runtime_hook_bootstrap_submitted runtime_hook \
    start_vm_runtime_hook "runtime hook process submitted" "pid=${VM_RUNTIME_HOOK_PID}"
}

if [ "${VM_GENERATION}" = "v1" ] || [ "${MCP_VM_STANDBY}" = "0" ]; then
  run_runtime_init_script ensure_cookie_dir_owner.sh
else
  entrypoint_log bootstrap info "--" session_init_deferred runtime_layout entrypoint.sh \
    "session initialization deferred to post-hook" "deferred_module=browser_cookie"
fi
if [ "${MCP_VM_STANDBY}" = "0" ]; then
  run_runtime_init_script init_shell_http_proxy.sh
  run_runtime_init_script ensure_data_dir_permission.sh

  # Experience 冷加载：失败时由 loader 保留旧版本或创建空目录，不阻断 VM 主任务。
  "${SCRIPT_DIR}/vm_runtime_hook" load-experience || entrypoint_log_lifecycle_signal bootstrap warn \
    "experience cold load failed (best-effort)"

  # 官方 + 个人 skills 冷加载：复用 Go 内核（root 身份、一次性进程）。
  # load_session_skills.sh 现在只负责把官方包解到 skills.tmp/official，真实落地由 Go commit；
  # 因此 entrypoint 不能直接调用该脚本，否则会先消费 workspace skills.zip，导致 sync-skills 无法 commit。
  "${SCRIPT_DIR}/vm_runtime_hook" sync-skills || entrypoint_log_lifecycle_signal bootstrap warn \
    "skills cold sync failed (best-effort)"
  ("${SCRIPT_DIR}/vm_runtime_hook" audit-skill-permissions || entrypoint_log_lifecycle_signal bootstrap warn \
    "skill permission audit failed (best-effort)") &
  SKILL_PERMISSION_AUDIT_PID=$!
  entrypoint_log bootstrap info "--" skills_permission_audit_submitted skills entrypoint.sh \
    "skill permission audit submitted" "pid=${SKILL_PERMISSION_AUDIT_PID}"

  run_resource_init_if_needed
  configure_lark_cli_resource_path
  run_runtime_init_script_best_effort init_lark_cli.sh
  run_runtime_init_script_best_effort rebuild_lark_cli.sh
else
  entrypoint_log bootstrap info "--" session_init_deferred runtime_layout entrypoint.sh \
    "session initialization deferred to post-hook" "deferred_module=user_session"
fi
export_shell_http_proxy_env
if [ "${VM_GENERATION}" = "v1" ] || [ "${MCP_VM_STANDBY}" = "0" ]; then
  run_runtime_init_script adapt_intranet.sh
else
  entrypoint_log bootstrap info "--" session_init_deferred runtime_layout entrypoint.sh \
    "session initialization deferred to post-hook" "deferred_module=app_log"
fi
start_official_npm_cli_install_async
start_persistent_sync
init_browser_config
start_vm_runtime_hook

RUNTIME_INIT_EMIT_STATUS_MARKERS=false bash "${RUNTIME_INIT_DIR}/start_hijack_proxy.sh" &
HIJACK_PROXY_INIT_PID=$!
entrypoint_log bootstrap info "--" hijack_proxy_bootstrap_submitted hijack_proxy entrypoint.sh \
  "hijack proxy bootstrap submitted" "pid=${HIJACK_PROXY_INIT_PID}"

# nginx
envsubst '${VM_SERVER_PORT} ${CI_PYTHON_SERVER_PORT}' < /tmp/nginx.mcp_vm_server.conf.template > /opt/gem/nginx/nginx.mcp_vm_server.conf

# 启动 aio & gem browser
sync_browser_proxy_server_env
entrypoint_log bootstrap info "--" aio_bootstrap_started aio entrypoint.sh \
  "starting AIO runtime"
/opt/gem/run.sh &
RUN_GEM_PID=$!
child_pid="${RUN_GEM_PID}"
entrypoint_log bootstrap info "--" aio_bootstrap_submitted aio entrypoint.sh \
  "AIO runtime process submitted" "pid=${RUN_GEM_PID}"


# 转发信号给子进程
FORWARDED_SIGNAL_NUMBER=0
forward_signal() {
  sig="$1"
  FORWARDED_SIGNAL_NUMBER="$2"
  entrypoint_log destroy info "-" container_stop_started bootstrap forward_signal \
    "container shutdown signal received" "signal=${sig}"
  if [ -n "${VM_RUNTIME_HOOK_PID:-}" ]; then
    kill "-$sig" "${VM_RUNTIME_HOOK_PID}" 2>/dev/null || true
  fi
  if [ -n "${PERSISTENT_SYNC_PID:-}" ]; then
    kill "-$sig" "${PERSISTENT_SYNC_PID}" 2>/dev/null || true
  fi
  if [ -n "${OFFICIAL_NPM_CLI_INSTALL_PID:-}" ]; then
    kill "-$sig" "${OFFICIAL_NPM_CLI_INSTALL_PID}" 2>/dev/null || true
  fi
  # /opt/gem/run.sh ends with `exec supervisord`, so child_pid becomes the
  # supervisord pid. Signal that pid directly and let supervisord stop programs.
  kill "-$sig" "$child_pid" 2>/dev/null || true
}

trap 'forward_signal TERM 15' SIGTERM
trap 'forward_signal INT 2'   SIGINT
trap 'forward_signal QUIT 3'  SIGQUIT

wait_service_startup_before_official_npm_cli_wait
wait_official_npm_cli_install
if ! wait_vm_server_ready; then
  entrypoint_log bootstrap error "--" vm_server_start_failed bootstrap entrypoint.sh \
    "VM server startup timed out" \
    "timeout_seconds=${VM_SERVER_STARTUP_TIMEOUT_SECONDS:-60}" >&2
  exit 1
fi
entrypoint_log bootstrap info "--" aio_bootstrap_succeeded aio entrypoint.sh \
  "AIO runtime ready"
entrypoint_log bootstrap info "-" container_start_succeeded bootstrap entrypoint.sh \
  "container ready" \
  "generation=${VM_GENERATION}" \
  "startup_mode=${STARTUP_MODE}" \
  "duration_ms=$(( (SECONDS - ENTRYPOINT_START_SECONDS) * 1000 ))"

set +e
wait "$RUN_GEM_PID"
wait_status=$?
if [ "$wait_status" -gt 128 ] && [ "${FORWARDED_SIGNAL_NUMBER}" -ne 0 ]; then
  # The first wait is interrupted by the trapped signal. Keep PID 1 alive until
  # supervisord finishes stopping its managed processes.
  wait "$RUN_GEM_PID"
  shutdown_status=$?
  expected_signal_status=$((128 + FORWARDED_SIGNAL_NUMBER))
  if [ "${shutdown_status}" -ne 0 ] && [ "${shutdown_status}" -ne "${expected_signal_status}" ]; then
    entrypoint_log_lifecycle_signal destroy error \
      "gem shutdown failed, status=${shutdown_status}, expected_status=${expected_signal_status}" >&2
  fi
  exit "${shutdown_status}"
fi
if [ "${wait_status}" -ne 0 ]; then
  entrypoint_log_lifecycle_signal runtime error \
    "gem exited unexpectedly, status=${wait_status}" >&2
fi
exit "$wait_status"
