# 📦 Build Studio — File MCP Server

Ye MCP server **sandbox ke andar** hi chalta hai aur files ka poora management deta hai:
**banao ✍️ · padho 👀 · edit karo 🔧 · delete karo 🗑️ · move karo 📂 · list karo 📋**

Saari files `storage/` folder me rehti hain. Har file ka **Termux download command** bhi milta hai.

---

## 🔌 Server details

| Cheez | Value |
|---|---|
| MCP endpoint (Streamable HTTP) | `https://8000-i6lumd5n09qpyftoibzuf.e2b.app/mcp` |
| Token | `9rV6SEVUWJO9wd9_MMUAGb0n` |
| Health check | `https://8000-i6lumd5n09qpyftoibzuf.e2b.app/health` |

> 🔒 Har request me token chahiye — query me `?token=...` ya header `X-Token: ...`

---

## 📱 Termux se file download karna (sabse main cheez!)

**Pehli baar ye chalao** (storage permission + curl):

```bash
termux-setup-storage
pkg install -y curl
```

**Saari files ek saath (ZIP) phone me:**

```bash
curl -L "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/download/all?token=9rV6SEVUWJO9wd9_MMUAGb0n" -o /sdcard/Download/build-studio.zip
```

**Koi ek file phone me:**

```bash
curl -L "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/files/hello.txt?token=9rV6SEVUWJO9wd9_MMUAGb0n" -o /sdcard/Download/hello.txt
```

**Phone se server par upload:**

```bash
curl --data-binary @merifile.txt "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/upload/merifile.txt?token=9rV6SEVUWJO9wd9_MMUAGb0n"
```

**File delete:**

```bash
curl -X DELETE "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/files/purani.txt?token=9rV6SEVUWJO9wd9_MMUAGb0n"
```

**File list (JSON):**

```bash
curl -s "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/list?token=9rV6SEVUWJO9wd9_MMUAGb0n"
```

---

## 🛠️ MCP Tools (8 tools)

| Tool | Kaam |
|---|---|
| `write_file(path, content)` | Nayi file banao / overwrite karo |
| `append_file(path, content)` | File ke end me text jodo |
| `read_file(path)` | File ka text padho |
| `edit_file(path, old_text, new_text)` | Pehla match replace karo |
| `delete_file(path, recursive)` | File ya folder delete karo |
| `move_file(src, dst)` | Move / rename |
| `list_files(subdir)` | Saari files list karo |
| `download_link(path)` | Ready-made Termux curl command |

---

## 🔗 Kisi bhi MCP client me jodna (Claude Desktop, Cursor, etc.)

```json
{
  "mcpServers": {
    "build-studio": {
      "url": "https://8000-i6lumd5n09qpyftoibzuf.e2b.app/mcp",
      "headers": { "X-Token": "9rV6SEVUWJO9wd9_MMUAGb0n" }
    }
  }
}
```

---

## ▶️ Server chalana (sandbox ke andar)

```bash
cd /home/user/Build-studio-
MCP_TOKEN=9rV6SEVUWJO9wd9_MMUAGb0n \
PUBLIC_BASE=https://8000-i6lumd5n09qpyftoibzuf.e2b.app \
python3 mcp-server/server.py
```

Server `0.0.0.0:8000` par sunta hai. Token `MCP_TOKEN` env se badal sakte ho.
