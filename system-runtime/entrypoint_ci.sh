#! /usr/bin/env bash

init_http_proxy() {
  if [ "${UNSET_PROXY:-false}" = "true" ]; then
    echo "UNSET_PROXY=true, clear proxy environment"
    unset PROXY PROXY_SERVER http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
    return 0
  fi
  # 如果传入了PROXY环境变量，则使用PROXY作为代理
  if [ -n "${PROXY:-}" ]; then
    echo "PROXY=${PROXY}, init_http_proxy"
    echo "export http_proxy=\"${PROXY}\"" >> ~/.bashrc
    echo "export https_proxy=\"${PROXY}\"" >> ~/.bashrc
    echo "export HTTP_PROXY=\"${PROXY}\"" >> ~/.bashrc
    echo "export HTTPS_PROXY=\"${PROXY}\"" >> ~/.bashrc
    echo "export no_proxy=\"localhost,127.0.0.1,::1\"" >> ~/.bashrc

    . ~/.bashrc
  fi
}

RUNTIME_INIT_EMIT_STATUS_MARKERS=false bash "${RUNTIME_PATH}/runtime_init/init_user_home.sh"
init_http_proxy

# ci profile 约定直接对外监听 8080，不复用底包中的 9999 默认值。
export CI_PYTHON_SERVER_PORT="8080"
echo "entrypoint(ci): forcing CI_PYTHON_SERVER_PORT=${CI_PYTHON_SERVER_PORT}"

cd ${RUNTIME_PATH}
PY_ARGS="$@"
echo "PY_ARGS=$PY_ARGS"

if [ "${ENABLE_CI_SERVER:-true}" != "true" ]; then
  echo "Skip starting python server because ENABLE_CI_SERVER=${ENABLE_CI_SERVER}"
  exit 0
fi

# 使用gosu，以user用户启动进程 且 继承当前进程的 ulimit fd上限（1024 -> 2048）
# 暂时不使用 supervisord
exec gosu user env \
  HOME="${RUNTIME_PATH}/home" \
  XDG_CACHE_HOME="/runtime/cache/system" \
  /opt/python3.12/bin/python3.12 ${RUNTIME_PATH}/python_server/start_server.py "$@"
