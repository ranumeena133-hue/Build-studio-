# 📦 Build Studio — File MCP Server

Ye MCP server **sandbox ke andar** hi chalta hai aur files ka poora management deta hai:
**banao ✍️ · padho 👀 · edit karo 🔧 · delete karo 🗑️ · move karo 📂 · list karo 📋**

Saari files `storage/` folder me rehti hain.

---

## 📱 Termux se download karna (GitHub raw links — sabse reliable!)

Files har change ke baad is repo me push hoti hain, isliye ye links **phone se direct** kaam karte hain:

**Pehli baar (Termux me):**
```bash
termux-setup-storage
pkg install -y curl
```

**Koi ek file (jaise demo.md):**
```bash
curl -L "https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/storage/demo.md" -o /sdcard/Download/demo.md
```

**Saari files ek ZIP me:**
```bash
curl -L "https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/build-studio-files.zip" -o /sdcard/Download/build-studio-files.zip
```

> ZIP ko extract karne ke liye: `pkg install -y unzip && unzip build-studio-files.zip -d /sdcard/Download/build-studio/`

**Poora repo hi chahiye to (code + files sab):**
```bash
curl -L "https://github.com/ranumeena133-hue/Build-studio-/archive/refs/heads/arena/01a07dfe-build-studio.zip" -o /sdcard/Download/build-studio-repo.zip
```

---

## 📤 Phone se UPLOAD karna (files server par bhejna)

**Phone ke browser me ye kholo:** https://8000-i6lumd5n09qpyftoibzuf.e2b.app

- File pick / drag karo → upload!
- Upload hote hi file **GitHub repo me auto-sync** ho jayegi (sabko milegi)
- Wahi page se **delete** bhi kar sakte ho 🗑️

(Termux/curl se bhi upload ho sakta hai: `curl --data-binary @file.txt "https://8000-....e2b.app/upload/file.txt?token=..."` — par yaad rahe, ye e2b URL curl se block hai; browser hi use karo.)

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
| `download_link(path)` | Ready-made download command |

---

## 🔌 Server details (sandbox/preview ke andar ke liye)

| Cheez | Value |
|---|---|
| MCP endpoint (Streamable HTTP) | `https://8000-i6lumd5n09qpyftoibzuf.e2b.app/mcp` |
| Token | (env `MCP_TOKEN` me hai — chat me diya gaya hai) |
| Health check | `https://8000-i6lumd5n09qpyftoibzuf.e2b.app/health` |

> ⚠️ Ye e2b URL **browser preview** ke liye hai — curl/Termux se is par request karo ge to
> preview-gate ka chhota error (86 bytes) milega. Termux ke liye upar wale **GitHub raw links** use karo.
>
> 🔒 Har request me token chahiye — query me `?token=...` ya header `X-Token: ...`

---

## ▶️ Server chalana (sandbox ke andar)

```bash
cd /home/user/Build-studio-
MCP_TOKEN=<token> PUBLIC_BASE=https://8000-i6lumd5n09qpyftoibzuf.e2b.app python3 mcp-server/server.py
```

Server `0.0.0.0:8000` par sunta hai. Token `MCP_TOKEN` env se set hota hai.
