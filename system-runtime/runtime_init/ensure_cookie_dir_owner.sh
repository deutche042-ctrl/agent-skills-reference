#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

if [ "${VM_GENERATION}" = "v2" ]; then
  "${RUNTIME_INIT_RUNTIME_PATH}/vm_runtime_hook" runtime-layout apply \
    --generation v2 \
    --phase runtime \
    --group browser_cookie \
    --format compact
  runtime_init_success "v2 browser cookie layout ensured"
fi

# Keep browser profile directories writable for the user process. The cookie
# mount may not be ready yet, so common.sh guards that path with health checks.
runtime_init_log "start ensure cookie and browser profile owner"
runtime_init_ensure_cookie_root

runtime_init_success "cookie dir owner ensured"
