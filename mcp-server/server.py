#!/usr/bin/env python3
"""Build Studio — File Management MCP Server

Ye server isi sandbox ke andar chalta hai. Saari files `storage/` folder me rehti hain.

Endpoints:
  MCP (streamable HTTP) : POST /mcp                    (header: X-Token)
  File download         : GET    /files/{path}?token=...
  File delete           : DELETE /files/{path}?token=...
  File upload (raw)     : POST   /upload/{path}?token=...
  Saari files ZIP       : GET    /download/all?token=...
  Listing (JSON)        : GET    /list?token=...
  Health check          : GET    /health               (no token)
  Help page             : GET    /                     (no token)
"""

from __future__ import annotations

import io
import os
import shutil
import zipfile
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

MAX_UPLOAD = 100 * 1024 * 1024  # 100 MB

mcp = FastMCP(
    "build-studio-files",
    instructions=(
        "Build Studio file server — files 'storage/' folder me rehti hain. "
        "Tools se file banao, padho, edit karo, delete karo, move karo, list karo. "
        "Har file ka ready-made Termux/curl download command bhi mil sakta hai (download_link)."
    ),
    host="0.0.0.0",
    port=PORT,
    stateless_http=True,
    json_response=True,
)


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


def _url(path: str) -> str:
    return f"{BASE_URL}/files/{path}?token={TOKEN}"


def _err(e: Exception) -> str:
    return f"ERROR: {e}"


# ---------------- MCP Tools ----------------
@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create a new file in storage (or overwrite an existing one) with the given text content."""
    try:
        p = _safe(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"OK: 'storage/{_rel(p)}' likh di gayi ({len(content)} chars)"
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
                f"(binary, {p.stat().st_size:,} bytes) — download_link tool se download karo."
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
def download_link(path: str) -> str:
    """Return a ready-to-run Termux/curl command that downloads this file straight to a phone's Download folder."""
    try:
        p = _safe(path)
        if not p.is_file():
            return f"ERROR: 'storage/{path}' nahi mili"
        r = _rel(p)
        cmd = f"curl -L '{_url(r)}' -o /sdcard/Download/{p.name}"
        return f"Termux me ye run karo (pehli baar: termux-setup-storage):\n{cmd}"
    except Exception as e:
        return _err(e)


# ---------------- HTTP Routes ----------------
HELP_HTML = """<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Build Studio File MCP Server</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;background:#0f172a;color:#e2e8f0}
 code,pre{background:#1e293b;border-radius:6px;padding:2px 6px;overflow-x:auto;display:block;padding:12px}
 a{color:#7dd3fc} h1{font-size:1.4rem} .t{color:#fbbf24}
</style></head><body>
<h1>📦 Build Studio — File MCP Server <span style="color:#4ade80">chalu hai</span></h1>
<p>Ye server sandbox ke andar chal raha hai. MCP endpoint: <code>POST /mcp</code></p>
<p>Har request me token chahiye: <code>?token=&lt;TOKEN&gt;</code> ya header <code>X-Token: &lt;TOKEN&gt;</code></p>
<h3>Termux se download</h3>
<pre># sab files ek zip me
curl -L "https://&lt;HOST&gt;/download/all?token=&lt;TOKEN&gt;" -o /sdcard/Download/build-studio.zip

# koi ek file
curl -L "https://&lt;HOST&gt;/files/hello.txt?token=&lt;TOKEN&gt;" -o /sdcard/Download/hello.txt</pre>
<h3>Termux se upload</h3>
<pre>curl --data-binary @merifile.txt "https://&lt;HOST&gt;/upload/merifile.txt?token=&lt;TOKEN&gt;"</pre>
<h3>File delete</h3>
<pre>curl -X DELETE "https://&lt;HOST&gt;/files/purani.txt?token=&lt;TOKEN&gt;"</pre>
<p><a href="/health">/health</a> · README me poori detail hai.</p>
</body></html>"""


@mcp.custom_route("/", methods=["GET"])
async def help_page(request: Request) -> HTMLResponse:
    return HTMLResponse(HELP_HTML)


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    n = sum(1 for p in STORAGE.rglob("*") if p.is_file())
    return JSONResponse(
        {"ok": True, "files": n, "time": datetime.now().isoformat(timespec="seconds")}
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
    return JSONResponse(
        {"ok": True, "saved": _rel(p), "size": len(body), "url": _url(_rel(p))}
    )


@mcp.custom_route("/download/all", methods=["GET"])
async def download_all(request: Request) -> Response:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(STORAGE.rglob("*")):
            if p.is_file():
                z.write(p, arcname=_rel(p))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Response(
        buf.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="build-studio-files-{stamp}.zip"'
        },
    )


# ---------------- Auth + App ----------------
class TokenAuth(BaseHTTPMiddleware):
    EXEMPT = {"/", "/health"}

    async def dispatch(self, request, call_next):
        if request.url.path in self.EXEMPT:
            return await call_next(request)
        auth_header = request.headers.get("authorization", "")
        given = (
            request.query_params.get("token")
            or request.headers.get("x-token")
            or auth_header.removeprefix("Bearer ").strip()
        )
        if given != TOKEN:
            return JSONResponse(
                {"error": "invalid/missing token — ?token=... ya X-Token header bhejo"},
                status_code=401,
            )
        return await call_next(request)


app = mcp.streamable_http_app()
app.add_middleware(TokenAuth)


if __name__ == "__main__":
    print(f"* Storage       : {STORAGE}")
    print(f"* MCP endpoint  : {BASE_URL}/mcp")
    print(f"* Health check  : {BASE_URL}/health")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
