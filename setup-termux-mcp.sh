#!/bin/bash
# =========================================================
#  MyAIFolder MCP — Termux one-command setup (Hindi)
#  Chalana:  bash setup-termux-mcp.sh
# =========================================================

echo "=== Step 1: Node.js check ==="
if ! command -v node >/dev/null 2>&1; then
  echo "Node nahi mila — install kar raha hu..."
  pkg update -y && pkg install nodejs-lts -y
fi
node -v

echo ""
echo "=== Step 2: MyAIFolder banao ==="
termux-setup-storage 2>/dev/null
mkdir -p ~/storage/shared/MyAIFolder
if [ ! -f ~/storage/shared/MyAIFolder/note.txt ]; then
  echo "Mera pehla note" > ~/storage/shared/MyAIFolder/note.txt
fi
ls ~/storage/shared/MyAIFolder/

echo ""
echo "=== Step 3: MCP server download (fixed wala) ==="
curl -sL -o ~/mcp-server.js https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07d91-build-studio/mcp-server-fixed.js
ls -la ~/mcp-server.js

echo ""
echo "=== Step 4: Server test (5 second) ==="
node ~/mcp-server.js &
SRV=$!
sleep 3
echo "Server ka jawab:"
curl -s -m 10 -X POST http://localhost:3000 -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"list_files","arguments":{}}}'
echo ""
kill $SRV 2>/dev/null
wait 2>/dev/null

echo ""
echo "=== Step 5: Gemini CLI se jodo (settings) ==="
mkdir -p ~/.gemini
if [ -f ~/.gemini/settings.json ]; then
  cp ~/.gemini/settings.json ~/.gemini/settings.json.bak
  echo "(purani settings ka backup: settings.json.bak)"
fi
cat > ~/.gemini/settings.json <<'EOF'
{
  "mcpServers": {
    "mera-server": {
      "httpUrl": "http://localhost:3000/mcp"
    }
  }
}
EOF
cat ~/.gemini/settings.json

echo ""
echo "==============================================="
echo "  HO GAYA BHAI! Ab 2 session me chalao:"
echo "  Session 1:  node ~/mcp-server.js"
echo "  Session 2:  cd ~/storage/shared/MyAIFolder && gemini"
echo "  Phir /tools me 4 tools dikhenge. Mauj karo!"
echo "==============================================="
