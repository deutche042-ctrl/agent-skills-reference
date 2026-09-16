#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${SCRIPT_DIR}/init_shell_http_proxy.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

run_target() {
  env \
    VM_GENERATION=v1 \
    PROXY="${PROXY_VALUE:-}" \
    NO_PROXY_DOMAINS="${NO_PROXY_VALUE:-}" \
    UNSET_PROXY="${UNSET_PROXY_VALUE:-false}" \
    bash "${TARGET}"
}

PROXY_VALUE="http://proxy.example:8080"
NO_PROXY_VALUE="example.com,*.internal.example"
output="$(run_target)"
grep -q '__RUNTIME_INIT_STATUS__=success' <<<"${output}" ||
  fail "valid proxy did not succeed"
grep -q '__RUNTIME_INIT_MESSAGE__=shell proxy configuration validated' <<<"${output}" ||
  fail "valid proxy returned unexpected message"

PROXY_VALUE=""
NO_PROXY_VALUE=""
output="$(run_target)"
grep -q '__RUNTIME_INIT_STATUS__=skipped' <<<"${output}" ||
  fail "empty proxy did not skip"

PROXY_VALUE="not-a-proxy"
if run_target >"${TEST_ROOT}/invalid.out" 2>"${TEST_ROOT}/invalid.err"; then
  fail "invalid proxy succeeded"
fi
grep -q '__RUNTIME_INIT_STATUS__=failed' "${TEST_ROOT}/invalid.err" ||
  fail "invalid proxy did not report failure"

PROXY_VALUE="http://proxy.example:8080"
NO_PROXY_VALUE="bad entry"
if run_target >"${TEST_ROOT}/invalid-no-proxy.out" 2>"${TEST_ROOT}/invalid-no-proxy.err"; then
  fail "invalid no-proxy list succeeded"
fi
grep -q '__RUNTIME_INIT_STATUS__=failed' "${TEST_ROOT}/invalid-no-proxy.err" ||
  fail "invalid no-proxy list did not report failure"

if grep -Eq '\.bashrc|runtime_init_replace_managed_block' "${TARGET}"; then
  fail "proxy validation script still accesses .bashrc"
fi

echo "init_shell_http_proxy tests passed"
