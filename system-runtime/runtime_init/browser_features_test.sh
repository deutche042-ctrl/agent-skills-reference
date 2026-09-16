#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTRYPOINT="${SCRIPT_DIR}/../entrypoint.sh"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEST_ROOT}"' EXIT

sed -n '/^merge_browser_disable_features()/,/^}/p' "${ENTRYPOINT}" >"${TEST_ROOT}/functions.sh"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

run_merge() {
  local commandline="$1"
  local features="$2"
  env \
    BROWSER_COMMANDLINE_ARGS="${commandline}" \
    DISABLE_BROWSER_FEATURES="${features}" \
    bash -c '
      source "$1"
      entrypoint_log() {
        printf "%s\n" "$*" >&2
      }
      merge_browser_disable_features || exit $?
      printf "%s" "${BROWSER_COMMANDLINE_ARGS}"
    ' _ "${TEST_ROOT}/functions.sh"
}

output="$(run_merge '--foo --disable-features=BaseA,BaseB --bar' 'RuntimeA,RuntimeB')"
[ "${output}" = '--foo --disable-features=BaseA,BaseB,RuntimeA,RuntimeB --bar' ] ||
  fail "did not append configured features: ${output}"

output="$(run_merge '--foo --bar' 'RuntimeA')"
[ "${output}" = '--foo --bar --disable-features=RuntimeA' ] ||
  fail "did not add a missing disable-features argument: ${output}"

output="$(run_merge '--disable-features=BaseA' '')"
[ "${output}" = '--disable-features=BaseA' ] ||
  fail "empty configured features changed arguments: ${output}"

grep -q 'printf .*BROWSER_COMMANDLINE_ARGS:-' "${ENTRYPOINT}" ||
  fail "entrypoint does not tolerate an unset BROWSER_COMMANDLINE_ARGS"
grep -q -- '--disable-component-update' "${ENTRYPOINT}" ||
  fail "entrypoint does not disable component updates"
unset_output="$(env -u BROWSER_COMMANDLINE_ARGS bash -u -c 'printf "%q" "${BROWSER_COMMANDLINE_ARGS:-}"')"
[ "${unset_output}" = "''" ] ||
  fail "unset BROWSER_COMMANDLINE_ARGS did not render as an empty shell value: ${unset_output}"

output="$(run_merge '--disable-features=BaseA' ' RuntimeA, RuntimeB ')"
[ "${output}" = '--disable-features=BaseA,RuntimeA,RuntimeB' ] ||
  fail "configured whitespace was not removed: ${output}"

output="$(run_merge '--foo -- https://example.com/' 'RuntimeA')"
[ "${output}" = '--foo --disable-features=RuntimeA -- https://example.com/' ] ||
  fail "did not insert configured features before option terminator: ${output}"

output="$(run_merge '--disable-features=BaseA -- https://example.com/' 'RuntimeA')"
[ "${output}" = '--disable-features=BaseA,RuntimeA -- https://example.com/' ] ||
  fail "did not merge configured features before option terminator: ${output}"

if run_merge '--disable-features=BaseA' 'RuntimeA,Bad;Feature' \
  >"${TEST_ROOT}/invalid.out" 2>"${TEST_ROOT}/invalid.err"; then
  fail "invalid configured features succeeded"
fi
grep -q 'browser_feature_policy_rejected' "${TEST_ROOT}/invalid.err" ||
  fail "invalid configured features returned an unclear error"

echo "browser feature tests passed"
