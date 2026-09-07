# 📦 Mera Termux MCP Server — Setup Card (Verified ✅)

> Arena par live test kiya hua — ye setup sahi hai!

## 🔧 Server Info

| Cheez | Detail |
|---|---|
| Type | HTTP MCP server (JSON-RPC 2.0) |
| Port | 3000 (localhost only 🔒) |
| AI access folder | `/data/data/com.termux/files/home/storage/shared/MyAIFolder` |
| Server file | `~/mcp-server.js` (Node.js, zero external library) |
| Test status | ✅ 10/12 pass original, **6/6 pass fixed version** |

## 🛠️ Tools (4)

| Tool | Kaam | Arguments |
|---|---|---|
| `list_files` | Folder ki files ki list | — |
| `read_file` | File padhta hai | `path` |
| `write_file` | Nayi file / update | `path`, `content` |
| `delete_file` | File mitata hai | `path` |

## 🚀 Start / Stop (tmux se — recommended)

```bash
# tmux nahi hai to pehli baar:
pkg install tmux -y

# Server start (background me chalta rahega):
tmux new-session -d -s mcp 'node ~/mcp-server.js'

# Server dekhna ho:
tmux attach -t mcp
# (bahar: Ctrl+B phir D)

# Server band karna:
tmux kill-session -t mcp
```

## 🧪 MCP Client se baat

```
POST http://localhost:3000
Content-Type: application/json
```

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
```

Phir `tools/list` → `tools/call`. (Auto test ke liye repo me `test-mcp.sh` hai.)

## 🔌 Gemini CLI se jodna

`~/.muse/settings.json`:

```json
{
  "mcpServers": {
    "mera-server": {
      "httpUrl": "http://localhost:3000/mcp"
    }
  }
}
```

(Ya bas `bash setup-termux-mcp.sh` chala do — sab automatic!)

## ⚠️ Zaroori Notes

1. **Fixed wali file use karo!** `mcp-server-fixed.js` me security chhed band hai. Original me `../` wali chaal se bahar file ban sakti thi — fixed me **100% blocked** (test karke prove kiya).
2. Server **sirf localhost** par — public tunnel par kabhi mat kholo.
3. **Koi login/password nahi** — sirf apne phone ke liye safe hai.
4. `ROOT_DIR` badalna ho to file me 6th line edit karo.
5. Test report: `GEMINI-TERMUX-SETUP-HINDI.md` me MCP section dekho.

---
*Last verified: Arena live test — read/write/edit/delete sab OK ✅*
