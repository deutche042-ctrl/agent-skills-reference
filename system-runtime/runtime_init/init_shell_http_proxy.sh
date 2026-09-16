#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

if [ "${UNSET_PROXY:-false}" = "true" ]; then
  PROXY=""
fi

if [ -z "${PROXY:-}" ]; then
  runtime_init_log "PROXY is empty, skip init_shell_http_proxy"
  runtime_init_skipped "proxy is not configured"
fi
runtime_init_validate_proxy_url "${PROXY}"

no_proxy_value="localhost,127.0.0.1,::1"
if [ -n "${NO_PROXY_DOMAINS:-}" ]; then
  runtime_init_log "NO_PROXY_DOMAINS is configured, append to no_proxy"
  no_proxy_value="${no_proxy_value},${NO_PROXY_DOMAINS}"
fi
runtime_init_validate_no_proxy_list "${no_proxy_value}"

runtime_init_success "shell proxy configuration validated"
