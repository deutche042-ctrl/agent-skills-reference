#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON="${SCRIPT_DIR}/common.sh"
ENTRYPOINT="${SCRIPT_DIR}/../entrypoint.sh"
DOCKERFILE="${SCRIPT_DIR}/../Dockerfile"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

mkdir -p "${TEST_ROOT}/bin"
cat >"${TEST_ROOT}/bin/jq" <<'EOF'
#!/bin/bash
exit 1
EOF
chmod +x "${TEST_ROOT}/bin/jq"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

run_common() {
  env -i \
    PATH="${TEST_ROOT}/bin:/usr/bin:/bin" \
    "$@" \
    bash -c '
      source "$1"
      printf "%s|%s|%s|%s|%s\n" \
        "${VM_GENERATION}" \
        "${AIO_RUNTIME_DIR-<unset>}" \
        "${BROWSER_DATA_DIR}" \
        "${DOWNLOADS_PATH}" \
        "${RUNTIME_INIT_WORKSPACE}"
    ' _ "${COMMON}"
}

v1_output="$(run_common VM_GENERATION=v1 SESSION_ID=session-v1)"
v1_expected="v1|<unset>|/home/user/.config/browser|/home/user/.super_doubao/super-doubao-runtime/workspace/Downloads|/home/user/.super_doubao/super-doubao-runtime/workspace"
[ "${v1_output}" = "${v1_expected}" ] ||
  fail "v1 layout mismatch: ${v1_output}"

v2_output="$(
  run_common \
    VM_GENERATION=v2 \
    SESSION_ID=session-v2 \
    AIO_RUNTIME_DIR=/runtime/aio \
    BROWSER_DATA_DIR=/runtime/aio/app-data/browser \
    DOWNLOADS_PATH=/home/user/Downloads
)"
v2_expected="v2|/runtime/aio|/runtime/aio/app-data/browser|/home/user/Downloads|/home/user/.doubao/agent_mode/workspace/.sessions/session-v2"
[ "${v2_output}" = "${v2_expected}" ] ||
  fail "v2 layout mismatch: ${v2_output}"

if run_common \
  VM_GENERATION=v2 \
  AIO_RUNTIME_DIR=/runtime/aio \
  BROWSER_DATA_DIR=/runtime/aio/app-data/browser \
  >"${TEST_ROOT}/missing.out" 2>"${TEST_ROOT}/missing.err"; then
  fail "v2 common.sh accepted a missing DOWNLOADS_PATH"
fi
grep -q "DOWNLOADS_PATH must be initialized by entrypoint for v2" "${TEST_ROOT}/missing.err" ||
  fail "missing v2 DOWNLOADS_PATH error is unclear"

if run_common VM_GENERATION=v3 >"${TEST_ROOT}/invalid.out" 2>"${TEST_ROOT}/invalid.err"; then
  fail "common.sh accepted an invalid VM_GENERATION"
fi
grep -q "invalid VM_GENERATION=v3" "${TEST_ROOT}/invalid.err" ||
  fail "invalid generation error is unclear"

env_selectors="$(
  sed -n '/^configure_v2_layout_env()/,/^}/p' "${ENTRYPOINT}" |
    grep -Eo '\.[A-Z_][A-Z0-9_]*' |
    tr -d '.' |
    sort -u
)"
expected_selectors="$(printf '%s\n' AIO_RUNTIME_DIR BROWSER_DATA_DIR DOWNLOADS_PATH | sort)"
[ "${env_selectors}" = "${expected_selectors}" ] ||
  fail "entrypoint v2 env selectors mismatch: ${env_selectors}"

grep -q 'RESOURCE_LOADER_BIN_PATH=/opt/vm/resource-loader/bin' "${DOCKERFILE}" ||
  fail "Dockerfile default resource-loader bin path must remain v1-compatible"
resource_loader_bin_function="$(sed -n '/^configure_resource_loader_bin_path()/,/^}/p' "${ENTRYPOINT}")"
grep -q 'export RESOURCE_LOADER_BIN_PATH="/opt/vm/resource-loader/bin"' <<<"${resource_loader_bin_function}" ||
  fail "entrypoint does not preserve resource-loader bin path for v1"
grep -q 'export RESOURCE_LOADER_BIN_PATH="/home/user/vm/resource-loader/bin"' "${ENTRYPOINT}" ||
  fail "entrypoint does not switch resource-loader bin path for v2"
grep -q '^configure_resource_loader_bin_path$' "${ENTRYPOINT}" ||
  fail "entrypoint does not apply generation-specific resource-loader bin path"

generation_branch="$(sed -n '/^case "${VM_GENERATION}" in$/,/^esac$/p' "${ENTRYPOINT}")"
v1_branch="$(sed -n '/^  v1)$/,/^    ;;$/p' <<<"${generation_branch}")"
v2_branch="$(sed -n '/^  v2)$/,/^    ;;$/p' <<<"${generation_branch}")"

grep -q 'ls /sandboxdata/data' <<<"${v1_branch}" ||
  fail "v1 no longer uses the legacy data mount standby check"
if grep -q 'runtime-layout' <<<"${v1_branch}"; then
  fail "v1 branch invokes the v2 runtime-layout CLI"
fi
grep -q 'configure_v2_layout_env' <<<"${v2_branch}" ||
  fail "v2 branch does not load centralized layout env"
grep -q -- '--phase bootstrap' <<<"${v2_branch}" ||
  fail "v2 branch does not apply bootstrap layout"
grep -q -- '--format compact' <<<"${v2_branch}" ||
  fail "v2 branch does not emit compact bootstrap layout output"
grep -q 'SESSION_ID' <<<"${v2_branch}" ||
  fail "v2 branch does not derive standby from SESSION_ID"
if grep -q '/sandboxdata/data' <<<"${v2_branch}"; then
  fail "v2 branch still derives standby from the data mount"
fi
grep -q 'if \[ "${VM_GENERATION}" = "v2" \] || \[ "${MCP_VM_STANDBY}" = "0" \]; then' "${ENTRYPOINT}" ||
  fail "entrypoint does not guard the AIO browser download directory"
grep -q 'export BROWSER_DOWNLOAD_DIR="${DOWNLOADS_PATH}"' "${ENTRYPOINT}" ||
  fail "entrypoint does not align the configured AIO browser download directory"

user_env_function="$(sed -n '/^configure_process_user_env()/,/^}/p' "${ENTRYPOINT}")"
system_env_function="$(sed -n '/^configure_system_process_env()/,/^}/p' "${ENTRYPOINT}")"
grep -q 'export XDG_CONFIG_HOME="${HOME}/.config"' <<<"${user_env_function}" ||
  fail "user process env does not restore XDG_CONFIG_HOME under HOME"
if grep -q 'export PIP_USER=' <<<"${user_env_function}"; then
  fail "user process env still forces pip user installs"
fi
grep -q 'unset PIP_USER' <<<"${user_env_function}" ||
  fail "user process env does not clear inherited PIP_USER"
grep -q 'unset PIP_USER XDG_CONFIG_HOME' <<<"${system_env_function}" ||
  fail "system process env does not clear user-only pip and XDG settings"
grep -q '"${RUNTIME_INIT_USER_HOME}/.fnm_shell/bin"' <<<"${system_env_function}" ||
  fail "system process env does not filter the user fnm path"

echo "runtime layout shell tests passed"
