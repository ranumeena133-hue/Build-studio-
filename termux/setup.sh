#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  Build Studio - Termux Setup
#  ek hi baar chalana hai. iske baad sirf `bs` command chalegi.
# ============================================================

set -e

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say()  { echo -e "${GREEN}==>${NC} $1"; }
warn() { echo -e "${YELLOW}!!${NC} $1"; }
die()  { echo -e "${RED}XX${NC} $1"; exit 1; }

echo ""
echo "=============================================="
echo "   Build Studio - Termux Setup"
echo "=============================================="
echo ""

# ---------- 1. zaroori packages ----------
say "Zaroori packages install kar rahe hain (git, rsync, curl)..."
pkg update -y >/dev/null 2>&1 || warn "pkg update me halki dikkat, aage badh rahe hain"
pkg install -y git rsync curl termux-services >/dev/null 2>&1 \
    || pkg install -y git rsync curl >/dev/null 2>&1 \
    || die "packages install nahi ho paye. Internet check karo."
say "Packages ho gaye."

# ---------- 2. storage permission ----------
if [ ! -d "$HOME/storage" ]; then
    say "Storage permission maang rahe hain... popup aaye to ALLOW dabana."
    termux-setup-storage
    sleep 3
fi

if [ ! -d "/storage/emulated/0" ]; then
    die "Phone ka storage nahi mila. 'termux-setup-storage' khud chala kar ALLOW dabao."
fi
say "Storage ka rasta mil gaya."

# ---------- 3. sawaal-jawab ----------
CONF="$HOME/.buildstudio.conf"
echo ""
echo "----------------------------------------------"
echo " Ab kuch cheezein poochhenge. Enter dabao to"
echo " bracket [] wali default value le li jayegi."
echo "----------------------------------------------"
echo ""

read -r -p "GitHub username [ranumeena133-hue]: " GH_USER
GH_USER="${GH_USER:-ranumeena133-hue}"

read -r -p "Repository ka naam [Build-studio-]: " GH_REPO
GH_REPO="${GH_REPO:-Build-studio-}"

read -r -p "Branch [main]: " GH_BRANCH
GH_BRANCH="${GH_BRANCH:-main}"

DEF_LOCAL="/storage/emulated/0/.BUILD STUDIO/NewProject3"
read -r -p "Phone ka folder [$DEF_LOCAL]: " LOCAL_DIR
LOCAL_DIR="${LOCAL_DIR:-$DEF_LOCAL}"

read -r -p "Repo ke andar folder (khaali = repo ki jad) [NewProject3]: " REPO_SUBDIR
REPO_SUBDIR="${REPO_SUBDIR-NewProject3}"

echo ""
echo "GitHub Token daalo (screen par dikhega nahi)."
echo "Banane ka tarika: GitHub > Settings > Developer settings >"
echo "Personal access tokens > Fine-grained > Contents: Read and write"
read -r -s -p "Token: " GH_TOKEN
echo ""

[ -z "$GH_TOKEN" ] && die "Token khaali hai. Bina token ke kaam nahi chalega."

# ---------- 4. folder bana do ----------
mkdir -p "$LOCAL_DIR" || die "Folder nahi bana: $LOCAL_DIR"
say "Phone ka folder taiyaar: $LOCAL_DIR"

WORK_DIR="$HOME/buildstudio-work"

# ---------- 5. config file likho ----------
cat > "$CONF" <<EOF
# Build Studio - Termux config
# ye file apne aap bani hai. haath se badalna ho to badal sakte ho.
GH_USER="$GH_USER"
GH_REPO="$GH_REPO"
GH_BRANCH="$GH_BRANCH"
GH_TOKEN="$GH_TOKEN"
LOCAL_DIR="$LOCAL_DIR"
REPO_SUBDIR="$REPO_SUBDIR"
WORK_DIR="$WORK_DIR"
WATCH_SECONDS=30
EOF
chmod 600 "$CONF"
say "Config save ho gayi: $CONF (sirf tum padh sakte ho)"

# ---------- 6. git ka naam-pata ----------
git config --global user.name  "$GH_USER"        >/dev/null 2>&1 || true
git config --global user.email "$GH_USER@users.noreply.github.com" >/dev/null 2>&1 || true
git config --global init.defaultBranch "$GH_BRANCH" >/dev/null 2>&1 || true
git config --global --add safe.directory "$WORK_DIR" >/dev/null 2>&1 || true

# ---------- 7. repo clone ----------
REMOTE="https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${GH_REPO}.git"

if [ -d "$WORK_DIR/.git" ]; then
    say "Repo pehle se hai, sirf naya remote laga rahe hain..."
    git -C "$WORK_DIR" remote set-url origin "$REMOTE"
    git -C "$WORK_DIR" fetch origin >/dev/null 2>&1 || warn "fetch me dikkat"
else
    say "Repo clone kar rahe hain..."
    rm -rf "$WORK_DIR"
    if ! git clone --branch "$GH_BRANCH" "$REMOTE" "$WORK_DIR" 2>/dev/null; then
        warn "Us branch se clone nahi hua, poora repo la rahe hain..."
        git clone "$REMOTE" "$WORK_DIR" || die "Clone fail. Token ya repo ka naam galat lag raha hai."
        git -C "$WORK_DIR" checkout -B "$GH_BRANCH"
    fi
fi
say "Repo taiyaar: $WORK_DIR"

# ---------- 8. bs command install ----------
BIN_DIR="$PREFIX/bin"
SCRIPT_SRC="$(cd "$(dirname "$0")" && pwd)/bs"

if [ -f "$SCRIPT_SRC" ]; then
    cp "$SCRIPT_SRC" "$BIN_DIR/bs"
    chmod +x "$BIN_DIR/bs"
    say "'bs' command install ho gayi."
else
    warn "bs script nahi mili ($SCRIPT_SRC ke paas). Use manually copy karna padega."
fi

echo ""
echo "=============================================="
echo -e "   ${GREEN}SAB TAIYAAR HAI BHAI${NC}"
echo "=============================================="
echo ""
echo "  bs pull    -> GitHub se laakar phone me daalo"
echo "  bs push    -> phone ka folder GitHub par chadhao"
echo "  bs watch   -> background me apne aap chalta rahe"
echo "  bs stop    -> background band karo"
echo "  bs status  -> kya-kya badla hai dekho"
echo "  bs log     -> background ka log dekho"
echo ""
echo "  Phone folder : $LOCAL_DIR"
echo "  Repo folder  : ${REPO_SUBDIR:-(repo ki jad)}"
echo ""
echo "Sabse pehle ye chalao:  bs pull"
echo ""
