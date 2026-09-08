#!/usr/bin/env python3
"""Build Studio — File Management MCP Server

Ye server isi sandbox ke andar chalta hai. Saari files `storage/` folder me rehti hain.

Endpoints:
  MCP (streamable HTTP) : POST   /mcp                          (header: X-Token)
  Upload web page       : GET    /                             (browser file-manager UI)
  File download         : GET    /files/{path}?token=...
  File delete           : DELETE /files/{path}?token=...
  File upload (raw)     : POST   /upload/{path}?token=...
  Saari files ZIP       : GET    /download/all?token=...
  Listing (JSON)        : GET    /list?token=...
  Force GitHub sync     : POST   /sync?token=...
  Health check          : GET    /health                       (no token)
"""

from __future__ import annotations

import io
import os
import secrets
import shutil
import subprocess
import threading
import time
import zipfile
from collections import deque
from datetime import datetime
from pathlib import Path

import uvicorn
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, JSONResponse, Response

from mcp.server.fastmcp import FastMCP

# ---------------- Config ----------------
REPO_ROOT = Path(__file__).resolve().parent.parent
STORAGE = REPO_ROOT / "storage"
STORAGE.mkdir(parents=True, exist_ok=True)

TOKEN = os.environ.get("MCP_TOKEN", "9rV6SEVUWJO9wd9_MMUAGb0n")
PORT = int(os.environ.get("PORT", "8000"))
BASE_URL = os.environ.get("PUBLIC_BASE", f"http://localhost:{PORT}").rstrip("/")
BRANCH = os.environ.get("GIT_BRANCH", "arena/01a07dfe-build-studio")
RAW_BASE = f"https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/{BRANCH}"
AUTO_SYNC = os.environ.get("AUTO_SYNC", "1") == "1"

MAX_UPLOAD = 100 * 1024 * 1024  # 100 MB

# Security / speed tuning (env se badal sakte ho)
RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "300"))      # max requests/IP/minute
AUTH_MAX = int(os.environ.get("AUTH_MAX", "5"))            # itne galat token par...
LOCKOUT_SECS = int(os.environ.get("LOCKOUT_SECS", "600"))  # ...itne sec ke liye IP ban
START_TIME = time.time()
STATS = {"total": 0, "blocked": 0, "auth_fail": 0}

mcp = FastMCP(
    "build-studio-files",
    instructions=(
        "Build Studio file server — files 'storage/' folder me rehti hain. "
        "Tools se file banao, padho, edit karo, delete karo, move karo, list karo. "
        "Har change GitHub repo me auto-sync hota hai (Termux download links wahi se hain)."
    ),
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
    json_response=True,
)


# ---------------- GitHub auto-sync ----------------
_sync_timer: threading.Timer | None = None
_sync_lock = threading.Lock()


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-c", "user.name=Build Studio", "-c", "user.email=agent@arena.ai", *args],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=120,
    )


def _do_sync() -> None:
    """Zip refresh + git commit + push (background thread me)."""
    if not AUTO_SYNC:
        return
    if not _sync_lock.acquire(blocking=False):
        return
    try:
        with zipfile.ZipFile(REPO_ROOT / "build-studio-files.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(STORAGE.rglob("*")):
                if p.is_file():
                    z.write(p, arcname=_rel(p))  # zip me seedha files, storage/ folder nahi
        _git("pull", "--rebase", "--autostash", "origin", BRANCH)
        _git("add", "-A")
        c = _git("commit", "-m", f"auto-sync: storage update {datetime.now():%Y-%m-%d %H:%M}")
        if c.returncode == 0 and "nothing to commit" not in c.stdout:
            p = _git("push", "origin", BRANCH)
            print(f"[sync] GitHub push: {'OK' if p.returncode == 0 else p.stderr[:200]}")
    except Exception as e:  # noqa: BLE001
        print("[sync] error:", e)
    finally:
        _sync_lock.release()


def schedule_sync(delay: float = 4.0) -> None:
    """Debounced sync — lagataar changes me sirf ek commit hoga."""
    global _sync_timer
    if not AUTO_SYNC:
        return
    if _sync_timer is not None:
        _sync_timer.cancel()
    _sync_timer = threading.Timer(delay, _do_sync)
    _sync_timer.daemon = True
    _sync_timer.start()


# ---------------- Helpers ----------------
class ServerError(Exception):
    pass


def _safe(rel: str, *, allow_root: bool = False) -> Path:
    rel = (rel or "").strip().replace("\\", "/").lstrip("/")
    if rel in ("", "."):
        if allow_root:
            return STORAGE
        raise ServerError("File ka naam do (sirf '/' allowed nahi)")
    p = (STORAGE / rel).resolve()
    if p != STORAGE and STORAGE not in p.parents:
        raise ServerError(f"'{rel}' storage ke bahar jaata hai ('..' allowed nahi)")
    return p


def _rel(p: Path) -> str:
    return p.relative_to(STORAGE).as_posix()


def _raw(path: str) -> str:
    return f"{RAW_BASE}/storage/{path}"


def _err(e: Exception) -> str:
    return f"ERROR: {e}"


# ---------------- ZIP cache (speed) ----------------
_zip_cache: dict = {"sig": None, "data": b""}


def _zip_signature():
    return tuple(
        (str(p), p.stat().st_mtime_ns, p.stat().st_size)
        for p in sorted(STORAGE.rglob("*"))
        if p.is_file()
    )


def build_zip() -> bytes:
    """Sirf tab banata hai jab files badli hon — warna cache se turant. (fast!)"""
    sig = _zip_signature()
    if _zip_cache["sig"] == sig:
        return _zip_cache["data"]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STORAGE.rglob("*")):
            if p.is_file():
                z.write(p, arcname=_rel(p))
    _zip_cache["sig"] = sig
    _zip_cache["data"] = buf.getvalue()
    return _zip_cache["data"]


# ---------------- MCP Tools ----------------
@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create a new file in storage (or overwrite an existing one) with the given text content."""
    try:
        p = _safe(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        schedule_sync()
        return f"OK: 'storage/{_rel(p)}' likh di gayi ({len(content)} chars) — GitHub sync ho raha hai"
    except Exception as e:
        return _err(e)


@mcp.tool()
def append_file(path: str, content: str) -> str:
    """Append text to the end of a file in storage (creates the file if it does not exist)."""
    try:
        p = _safe(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(content)
        schedule_sync()
        return f"OK: 'storage/{_rel(p)}' me {len(content)} chars add hue"
    except Exception as e:
        return _err(e)


@mcp.tool()
def read_file(path: str) -> str:
    """Read and return the text content of a file in storage."""
    try:
        p = _safe(path)
        if not p.is_file():
            return f"ERROR: 'storage/{path}' nahi mili"
        try:
            return p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return (
                f"ERROR: 'storage/{path}' text file nahi hai "
                f"(binary, {p.stat().st_size:,} bytes) — download link se le lo."
            )
    except Exception as e:
        return _err(e)


@mcp.tool()
def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Edit a file in storage: replace the FIRST occurrence of old_text with new_text."""
    try:
        p = _safe(path)
        if not p.is_file():
            return f"ERROR: 'storage/{path}' nahi mili"
        content = p.read_text(encoding="utf-8")
        count = content.count(old_text)
        if count == 0:
            return "ERROR: old_text file me nahi mila"
        p.write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        schedule_sync()
        return f"OK: 'storage/{_rel(p)}' edit ho gayi ({count} match the, pehla replace kiya)"
    except Exception as e:
        return _err(e)


@mcp.tool()
def delete_file(path: str, recursive: bool = False) -> str:
    """Delete a file (or a folder — set recursive=true) from storage."""
    try:
        p = _safe(path)
        if p == STORAGE:
            return "ERROR: poora storage root delete nahi kar sakte"
        if not p.exists():
            return f"ERROR: 'storage/{path}' nahi mili"
        if p.is_dir():
            if not recursive:
                return f"ERROR: '{path}' folder hai — recursive=true bhejo"
            shutil.rmtree(p)
        else:
            p.unlink()
        schedule_sync()
        return f"OK: 'storage/{_rel(p)}' delete ho gayi"
    except Exception as e:
        return _err(e)


@mcp.tool()
def move_file(src: str, dst: str) -> str:
    """Move/rename a file or folder inside storage."""
    try:
        s = _safe(src)
        d = _safe(dst)
        if not s.exists():
            return f"ERROR: 'storage/{src}' nahi mili"
        d.parent.mkdir(parents=True, exist_ok=True)
        s.rename(d)
        schedule_sync()
        return f"OK: 'storage/{_rel(s)}' -> 'storage/{_rel(d)}'"
    except Exception as e:
        return _err(e)


@mcp.tool()
def list_files(subdir: str = ".") -> str:
    """List all files and folders in storage (recursively), optionally under a subfolder."""
    try:
        base = _safe(subdir, allow_root=True)
        if not base.exists():
            return f"ERROR: 'storage/{subdir}' nahi mili"
        lines = []
        for p in sorted(base.rglob("*")):
            r = _rel(p)
            if p.is_dir():
                lines.append(r + "/")
            else:
                lines.append(f"{r}  ({p.stat().st_size:,} bytes)")
        if not lines:
            return "(storage khaali hai)"
        n = sum(1 for l in lines if not l.endswith("/"))
        return f"storage/ me {n} files hain:\n" + "\n".join(lines)
    except Exception as e:
        return _err(e)


@mcp.tool()
def pull_github() -> str:
    """Pull latest files from the GitHub repo into the server (files uploaded via GitHub web UI will appear here)."""
    try:
        r = _git("pull", "--rebase", "--autostash", "origin", BRANCH)
        out = (r.stdout + r.stderr).strip()
        schedule_sync(delay=1.0)
        files = "\n".join(f"  - {p.relative_to(STORAGE)}" for p in sorted(STORAGE.rglob('*')) if p.is_file())
        return f"GitHub pull: {'OK' if r.returncode == 0 else 'FAIL'}\n{out}\n\nAbhi server par files:\n{files}"
    except Exception as e:
        return _err(e)


@mcp.tool()
def download_link(path: str) -> str:
    """Return a ready-to-run Termux/curl command that downloads this file straight to a phone's Download folder."""
    try:
        p = _safe(path)
        if not p.is_file():
            return f"ERROR: 'storage/{path}' nahi mili"
        r = _rel(p)
        cmd = f'curl -L "{_raw(r)}" -o /sdcard/Download/{p.name}'
        return f"Termux me ye run karo:\n{cmd}"
    except Exception as e:
        return _err(e)


# ---------------- Upload web page (phone browser ke liye) ----------------
PAGE = """<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Studio — File Manager</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:680px;margin:20px auto;padding:0 14px;background:#0f172a;color:#e2e8f0}
 h1{font-size:1.25rem} a{color:#7dd3fc;text-decoration:none}
 #drop{border:2px dashed #475569;border-radius:14px;padding:34px 14px;text-align:center;cursor:pointer;transition:.2s}
 #drop.over{border-color:#4ade80;background:#14532d22}
 button{background:#2563eb;color:#fff;border:0;border-radius:8px;padding:9px 16px;font-size:1rem;margin:4px}
 .del{background:#dc2626;padding:5px 10px;font-size:.85rem}
 .row{display:flex;justify-content:space-between;gap:8px;align-items:center;padding:9px 6px;border-bottom:1px solid #1e293b}
 .sz{color:#94a3b8;font-size:.85rem;white-space:nowrap}
 #msg{color:#4ade80;min-height:1.4em} #bar{height:6px;background:#1e293b;border-radius:3px;overflow:hidden;display:none}
 #bar div{height:100%;background:#4ade80;width:0;transition:.3s}
</style></head><body>
<h1>📤 Build Studio — File Manager</h1>
<p>Apne phone ki file pick karo → seedha server par upload ho jayegi. Upload ke baad wo <b>GitHub repo me bhi sync</b> ho jayegi (Termux <code>getfiles</code> se bhi milegi).</p>
<div id="drop">📱 <b>Tap karo</b> ya file yahan drag karo<br><small>(ek saath kai files select kar sakte ho)</small></div>
<input id="fi" type="file" multiple hidden>
<div id="bar"><div></div></div>
<p id="msg"></p>
<h3>📂 Server par files:</h3>
<div id="list">loading...</div>
<p><a href="/list?token=TOKEN">JSON list</a> · <a href="/download/all?token=TOKEN">sab ZIP</a> · <a href="/health">health</a></p>
<script>
const T="TOKEN", drop=document.getElementById("drop"), fi=document.getElementById("fi"),
 msg=document.getElementById("msg"), bar=document.getElementById("bar"), inner=bar.firstElementChild;
drop.onclick=()=>fi.click();
drop.ondragover=e=>{e.preventDefault();drop.classList.add("over")};
drop.ondragleave=()=>drop.classList.remove("over");
drop.ondrop=e=>{e.preventDefault();drop.classList.remove("over");up(e.dataTransfer.files)};
fi.onchange=()=>up(fi.files);
async function up(files){
  if(!files.length)return; bar.style.display="block";
  let ok=0;
  for(let i=0;i<files.length;i++){
    inner.style.width=((i)/files.length*100)+"%";
    const r=await fetch("/upload/"+encodeURIComponent(files[i].name)+"?token="+T,{method:"POST",body:files[i]});
    if(r.ok)ok++; else msg.textContent="❌ "+files[i].name+" upload fail ("+r.status+")";
  }
  inner.style.width="100%"; setTimeout(()=>{bar.style.display="none";inner.style.width="0"},600);
  msg.textContent="✅ "+ok+" file(s) upload ho gayi! GitHub sync ho raha hai...";
  fi.value=""; loadList();
}
async function del(p){ if(!confirm("Delete: "+p+" ?"))return;
  await fetch("/files/"+p+"?token="+T,{method:"DELETE"}); loadList(); }
async function loadList(){
  const d=await (await fetch("/list?token="+T)).json();
  document.getElementById("list").innerHTML = d.files.length
    ? d.files.map(f=>`<div class="row"><span>${f.type==="dir"?"📁":"📄"} ${f.path}</span><span><span class="sz">${f.size!=null?f.size+" B":""}</span> ${f.type==="file"?`<a href="${f.url}">⬇️</a>`:""} <button class="del" onclick="del('${f.path}')">🗑️</button></span></div>`).join("")
    : "<i>khaali hai</i>";
}
loadList();
</script></body></html>"""


@mcp.custom_route("/", methods=["GET"])
async def home(request: Request) -> HTMLResponse:
    return HTMLResponse(PAGE.replace("TOKEN", TOKEN))


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    n = sum(1 for p in STORAGE.rglob("*") if p.is_file())
    return JSONResponse(
        {
            "ok": True,
            "files": n,
            "time": datetime.now().isoformat(timespec="seconds"),
            "uptime_sec": int(time.time() - START_TIME),
            "requests": STATS["total"],
            "blocked": STATS["blocked"],
        }
    )


@mcp.custom_route("/list", methods=["GET"])
async def list_json(request: Request) -> JSONResponse:
    items = []
    for p in sorted(STORAGE.rglob("*")):
        items.append(
            {
                "path": _rel(p),
                "type": "dir" if p.is_dir() else "file",
                "size": p.stat().st_size if p.is_file() else None,
                "url": _url(_rel(p)) if p.is_file() else None,
            }
        )
    return JSONResponse({"count": len(items), "files": items})


def _url(path: str) -> str:
    return f"{BASE_URL}/files/{path}?token={TOKEN}"


@mcp.custom_route("/files/{path:path}", methods=["GET", "DELETE"])
async def file_ops(request: Request) -> Response:
    try:
        p = _safe(request.path_params["path"])
    except ServerError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if request.method == "DELETE":
        if not p.exists():
            return JSONResponse({"error": "file nahi mili"}, status_code=404)
        try:
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
            schedule_sync()
            return JSONResponse({"ok": True, "deleted": _rel(p)})
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)

    if not p.is_file():
        return JSONResponse({"error": "file nahi mili"}, status_code=404)
    return FileResponse(p, filename=p.name)


@mcp.custom_route("/upload/{path:path}", methods=["POST"])
async def upload(request: Request) -> JSONResponse:
    try:
        p = _safe(request.path_params["path"])
    except ServerError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    body = await request.body()
    if len(body) > MAX_UPLOAD:
        return JSONResponse({"error": "file 100MB se badi hai"}, status_code=413)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(body)
    schedule_sync()
    return JSONResponse(
        {"ok": True, "saved": _rel(p), "size": len(body), "raw": _raw(_rel(p))}
    )


@mcp.custom_route("/sync", methods=["POST"])
async def sync_now(request: Request) -> JSONResponse:
    schedule_sync(delay=0.5)
    return JSONResponse({"ok": True, "msg": "GitHub sync shuru"})


@mcp.custom_route("/pull", methods=["POST"])
async def pull_now(request: Request) -> JSONResponse:
    r = _git("pull", "--rebase", "--autostash", "origin", BRANCH)
    schedule_sync(delay=1.0)
    return JSONResponse(
        {
            "ok": r.returncode == 0,
            "output": (r.stdout + r.stderr).strip()[-500:],
            "files": sorted(str(p.relative_to(STORAGE)) for p in STORAGE.rglob("*") if p.is_file()),
        }
    )


@mcp.custom_route("/download/all", methods=["GET"])
async def download_all(request: Request) -> Response:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Response(
        build_zip(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="build-studio-files-{stamp}.zip"'
        },
    )


# ---------------- Security Guard + App ----------------
class Guard(BaseHTTPMiddleware):
    """Rate limit + brute-force lockout + timing-safe auth + security headers."""
    EXEMPT = {"/", "/health"}

    def __init__(self, app):
        super().__init__(app)
        self.hits: dict[str, deque] = {}
        self.fails: dict[str, deque] = {}

    def _prune(self, dq: deque, now: float, window: float) -> None:
        while dq and now - dq[0] > window:
            dq.popleft()

    async def dispatch(self, request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = time.time()

        # -- rate limit (har request, har IP par) --
        dq = self.hits.setdefault(ip, deque())
        self._prune(dq, now, 60)
        if len(dq) >= RATE_LIMIT:
            STATS["blocked"] += 1
            return JSONResponse(
                {"error": "too many requests — thoda ruk ke try karo"},
                status_code=429, headers={"Retry-After": "30"},
            )
        dq.append(now)

        # -- brute-force lockout --
        fq = self.fails.get(ip)
        if fq:
            self._prune(fq, now, LOCKOUT_SECS)
            if len(fq) >= AUTH_MAX:
                STATS["blocked"] += 1
                return JSONResponse(
                    {"error": f"bahut galat tries — {LOCKOUT_SECS//60} min ke liye blocked"},
                    status_code=403, headers={"Retry-After": str(LOCKOUT_SECS)},
                )

        # -- auth (timing-safe) --
        if request.url.path not in self.EXEMPT:
            auth_header = request.headers.get("authorization", "")
            given = (
                request.query_params.get("token")
                or request.headers.get("x-token")
                or auth_header.removeprefix("Bearer ").strip()
            )
            if not given or not secrets.compare_digest(given.encode(), TOKEN.encode()):
                STATS["auth_fail"] += 1
                fq = self.fails.setdefault(ip, deque())
                fq.append(now)
                left = AUTH_MAX - len(fq)
                return JSONResponse(
                    {"error": f"invalid/missing token ({max(left,0)} try baaki, phir IP ban)"},
                    status_code=401,
                )

        resp = await call_next(request)
        STATS["total"] += 1
        # -- security headers --
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path not in {"/files", "/download/all"} and not request.url.path.startswith("/files/"):
            resp.headers["Cache-Control"] = "no-store"
        return resp


from starlette.middleware.gzip import GZipMiddleware  # noqa: E402

app = mcp.streamable_http_app()
app.add_middleware(GZipMiddleware, minimum_size=500)   # chhota+tez transfer
app.add_middleware(Guard)


if __name__ == "__main__":
    print(f"* Storage       : {STORAGE}")
    print(f"* MCP endpoint  : {BASE_URL}/mcp")
    print(f"* Upload page   : {BASE_URL}/")
    print(f"* Health check  : {BASE_URL}/health")
    print(f"* Auto-sync     : {'ON (' + BRANCH + ')' if AUTO_SYNC else 'OFF'}")
    uvicorn.run(
        app, host="0.0.0.0", port=PORT,
        log_level=os.environ.get("LOG_LEVEL", "warning"),
        access_log=os.environ.get("ACCESS_LOG", "0") == "1",
    )
