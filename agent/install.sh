#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# Build Studio -> Termux "bhai agent" bootstrap
# Phone par sirf YEHI EK command chalaao (koi API key nahi, koi account nahi):
#
#   git clone --depth 1 -b arena/01a08283-build-studio \
#     https://github.com/ranumeena133-hue/Build-studio-.git ~/.bhai/repo \
#   && bash ~/.bhai/repo/agent/install.sh
#
# Repo PUBLIC hai, isliye clone me koi token nahi lagta.
# ============================================================================
set -u

BOLD=$(printf '\033[1m'); DIM=$(printf '\033[2m'); R=$(printf '\033[0m')
ok()   { printf "  ${BOLD}\033[32mok\033[0m %s\n" "$1"; }
warn() { printf "  ${BOLD}\033[33m!!\033[0m %s\n" "$1"; }
say()  { printf "  ${DIM}%s${R}\n" "$1"; }

HERE=$(cd "$(dirname "$0")" && pwd)          # ~/.bhai/repo/agent
REPO=$(cd "$HERE/.." && pwd)                 # ~/.bhai/repo
BHAIDIR=$(dirname "$REPO")                   # ~/.bhai
echo "${BOLD}bhai agent install${R}  (repo: $REPO)"

# ---- 0. Termux? -------------------------------------------------------------
if [ ! -d /data/data/com.termux ]; then
  warn "Yeh Termux nahi lagta. Script Android Termux ke liye hai; phir bhi try kar rahe hain."
fi

mkdir -p "$BHAIDIR/upload" "$BHAIDIR/out" "$BHAIDIR/trash" "$BHAIDIR/logs"
ok "dirs ready ($BHAIDIR)"

# ---- 1. deps (best effort; offline ho to skip) ------------------------------
if command -v pkg >/dev/null 2>&1; then
  have_any=0
  command -v git >/dev/null 2>&1 || have_any=1
  command -v python3 >/dev/null 2>&1 || have_any=1
  if [ "$have_any" = 1 ]; then
    say "pkg install -y git python termux-api  (net chahiye)"
    pkg install -y git python termux-api >/dev/null 2>&1 \
      || warn "pkg fail (offline?). Manual: pkg install git python"
  else
    say "git + python3 already present - pkg skip"
  fi
fi
command -v git >/dev/null 2>&1 || { warn "git missing - install karke dobara chalao"; exit 1; }
if ! command -v python3 >/dev/null 2>&1; then
  warn "python3 missing -> pkg install python -y ; phir dobara: bash $HERE/install.sh"
  exit 1
fi
ok "python $(python3 -c 'import sys;print(sys.version.split()[0])')"

# ---- 2. shared storage permission ------------------------------------------
if [ ! -d "$HOME/storage/shared" ]; then
  warn "phone storage mount nahi hai. YEH chalao (permission dialog aayega, Allow dabao):"
  echo "      termux-setup-storage"
  echo "  phir Termux app poori band karke dobara kholo."
else
  ok "storage shared: $HOME/storage/shared -> $(readlink -f "$HOME/storage/shared" 2>/dev/null)"
fi

# ---- 3. link the `bhai` command --------------------------------------------
chmod +x "$REPO/agent/bhai" 2>/dev/null
BIN=""
for cand in "${PREFIX:-/data/data/com.termux/files/usr}/bin" "$HOME/.local/bin"; do
  if [ -d "$cand" ] && [ -w "$cand" ]; then BIN="$cand"; break; fi
done
[ -n "$BIN" ] || { mkdir -p "$HOME/.local/bin"; BIN="$HOME/.local/bin"; }
ln -sf "$REPO/agent/bhai" "$BIN/bhai"
export PATH="$BIN:$PATH"          # is script ke andar bhi `bhai` chale
ok "command ready: $BIN/bhai -> agent/bhai"
if ! grep -qxF "export PATH=\"$BIN:\$PATH\"" "$HOME/.bashrc" 2>/dev/null; then
  echo "export PATH=\"$BIN:\$PATH\"" >> "$HOME/.bashrc" 2>/dev/null \
    && say "PATH me add kiya ($HOME/.bashrc) - naya session kholo ya: source ~/.bashrc" \
    || say "note: $BIN ko PATH me khud add kar lena"
fi

# ---- 4. self-consistent config (origin url + current branch) --------------
URL=$(git -C "$REPO" remote get-url origin 2>/dev/null || echo "")
BR=$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
[ -n "$URL" ] || URL="https://github.com/ranumeena133-hue/Build-studio-.git"
CFG="$BHAIDIR/config"
: > "$CFG"
{
  echo "REPO_URL=$URL"
  echo "BRANCH=$BR"
  echo "SHARED=$HOME/storage/shared"
  echo "MAX_MB=150"
  echo "WATCH_SEC=30"
  echo "NOTIFY=1"
} >> "$CFG"
ok "config: $CFG  (branch $BR)"

# ---- 5. first sync ---------------------------------------------------------
echo
say "bhai doctor:"
bhai doctor || true
echo
say "hello-check (ek chhota safe demo task):"
bhai hello || true
echo
echo "${BOLD}Ab aage:${R}"
echo "  bhai sync        - mere naye instructions uthaake lagaao"
echo "  bhai watch       - chhodo hi mat: har 30s me auto-sync (agent mode)"
echo "  bhai up <file>   - apni file mujhe bhejo (main edit kar dunga)"
echo "  bhai report      - jo hua uska paste-ready summary (mujhe paste karo)"
echo "  Ya Arena chat me bas Hindi/Eng me bolo: 'Download ke 500M se bade video DCIM me shift karo'"
