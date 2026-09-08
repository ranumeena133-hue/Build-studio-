#!/usr/bin/env bash
# ================================================
#  Build Studio — File MCP Server STARTER
#  Naye chat/session me agent ye ek command chalaye:
#      bash restart-server.sh
#  (start_process tool se, long-running — bash me nahi)
#  Dependencies khud install ho jaati hain agar nahi hain.
# ================================================
set -e
cd "$(dirname "$0")"

# 1) Dependencies check + auto-install
if ! python3 -c "import mcp, uvicorn" 2>/dev/null; then
  echo "[setup] mcp/uvicorn install ho rahe hain (30-60 sec)..."
  pip3 install --quiet --break-system-packages 'mcp<2' uvicorn
  echo "[setup] install OK"
fi

# 2) Config (env se override kar sakte ho)
export MCP_TOKEN="${MCP_TOKEN:-9rV6SEVUWJO9wd9_MMUAGb0n}"
export GIT_BRANCH="${GIT_BRANCH:-arena/01a07dfe-build-studio}"
export PUBLIC_BASE="${PUBLIC_BASE:-http://localhost:8000}"
export LOG_LEVEL="${LOG_LEVEL:-warning}"

echo "[start] Build Studio File MCP Server"
echo "[start] storage : $PWD/storage"
echo "[start] branch  : $GIT_BRANCH"
echo "[start] port    : 8000 (0.0.0.0)"
echo "[start] MCP     : <BASE>/mcp  |  upload page: /  |  health: /health"

# 3) Server chalu (foreground — start_process me chalana)
exec python3 mcp-server/server.py
