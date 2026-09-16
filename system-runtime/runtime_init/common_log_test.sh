#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON_SH="${SCRIPT_DIR}/common.sh"

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_contains() {
  local output="$1"
  local expected="$2"
  [[ "${output}" == *"${expected}"* ]] || fail "expected output to contain ${expected@Q}, got ${output@Q}"
}

assert_not_contains() {
  local output="$1"
  local unexpected="$2"
  [[ "${output}" != *"${unexpected}"* ]] || fail "expected output not to contain ${unexpected@Q}, got ${output@Q}"
}

run_status() {
  local markers_enabled="$1"
  local operation_script="$2"
  local status="$3"
  local message="$4"

  RUNTIME_INIT_EMIT_STATUS_MARKERS="${markers_enabled}" \
    RUNTIME_INIT_LOG_SCRIPT_NAME="${operation_script}" \
    bash -euo pipefail -c '
      source "$1"
      runtime_init_emit_status "$2" "$3"
    ' _ "${COMMON_SH}" "${status}" "${message}"
}

entrypoint_output="$(run_status false init_user_home.sh success "user home initialized")"
assert_contains "${entrypoint_output}" "[VM Shell] user_home_init_succeeded"
assert_contains "${entrypoint_output}" "user_home_init_succeeded"
assert_contains "${entrypoint_output}" "[bootstrap/init_user_home.sh/user_home]"
assert_not_contains "${entrypoint_output}" "agent_id="
assert_not_contains "${entrypoint_output}" "__RUNTIME_INIT_STATUS__="
assert_not_contains "${entrypoint_output}" "__RUNTIME_INIT_MESSAGE__="

post_hook_output="$(run_status true init_lark_cli.sh skipped "lark cli installation skipped")"
assert_contains "${post_hook_output}" "[VM Shell] lark_cli_init_skipped"
assert_contains "${post_hook_output}" "lark_cli_init_skipped"
assert_contains "${post_hook_output}" "[bootstrap/init_lark_cli.sh/lark_cli]"
assert_contains "${post_hook_output}" "__RUNTIME_INIT_STATUS__=skipped"
assert_contains "${post_hook_output}" "__RUNTIME_INIT_MESSAGE__=lark cli installation skipped"

printf 'PASS: runtime init logs identify the script and business node\n'
