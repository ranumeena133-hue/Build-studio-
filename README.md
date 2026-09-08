# Build Studio 🏗️

Ye repo ek **File Management MCP Server** chalata hai jo is sandbox ke andar rehta hai —
files **create / edit / delete / move / list / download / upload** sab kuch.

| Cheez | Kahan |
|---|---|
| 🚀 **Server start karo** (naye session me) | `bash restart-server.sh` — **start_process tool se** (long-running), port `8000` |
| 📖 Server ki poori detail | [mcp-server/README.md](mcp-server/README.md) |
| 📁 Files ka folder | `storage/` |
| 📱 Termux user guide | [storage/TERMUX-GUIDE.md](storage/TERMUX-GUIDE.md) |
| 🔄 Sync system | Server har change ko GitHub par auto-push karta hai (`build-studio-files.zip` + `storage/`) |
| 🔑 Token | `restart-server.sh` me default hai (env `MCP_TOKEN` se badal sakte ho) |

## Naye chat/session me sabse pehla step:

1. `start_process` se chalao: `bash restart-server.sh` (cwd = repo root)
2. Port `8000` listen hone ka wait karo (`wait_for: port`)
3. Confirm: `curl -s http://127.0.0.1:8000/health` → `{"ok": true, ...}`
4. User ko bolo server live hai — Termux wale `getfiles`/`sendfile` commands waise hi chalenge
   (GitHub raw links kabhi nahi badalte)

## User ke liye quick facts:

- **Download (Termux):** `getfiles` command
- **Upload (Termux):** `sendfile file.pdf` → phir chat me "pull karo" → server `git pull` karega
- **Server → GitHub auto-sync:** har file change par ~5 sec me commit+push
- **e2b preview URL:** har session me badal sakta hai — Termux wale GitHub links hamesha same rehte hain
