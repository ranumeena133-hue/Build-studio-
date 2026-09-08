#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# diag.sh - Termux + pkg + network ki halat patta karta hai (READ ONLY).
#   usage: bash diag.sh [outfile]
# Output: <shared>/Download/BuildStudio/termux-diag.txt
# जब `pkg install` fail ho (mirror dead / purani Termux) ya agent sync na ho,
# yeh file mujhe bhejo - 30 second me exact wajah batla dunga.
# ============================================================================
set -u
OUT="${1:-$HOME/storage/shared/Download/BuildStudio/termux-diag.txt}"
mkdir -p "$(dirname "$OUT")" 2>/dev/null
T() { local t=${1:-15}; shift; timeout "$t" "$@" 2>&1; }
P="${PREFIX:-/data/data/com.termux/files/usr}"

{
  echo "# bhai termux diag"
  echo "# $(date '+%F %T %Z')"
  echo
  echo "## device"
  if command -v getprop >/dev/null 2>&1; then
    echo "  model      : $(T 5 getprop ro.product.model)"
    echo "  android    : $(T 5 getprop ro.build.version.release) (sdk $(T 5 getprop ro.build.version.sdk))"
    echo "  abi        : $(T 5 getprop ro.product.cpu.abi)"
  fi
  echo "  termux app : $(T 5 getprop -v '' 2>/dev/null; dumpsys package com.termux 2>/dev/null | grep -m1 versionName || echo '?')"
  echo "  kernel     : $(uname -s -r -m)"
  echo "  termux data: $(T 20 du -sh "$P" | cut -f1)"
  echo
  echo "## tools available"
  for c in git python3 pip curl wget tar sed awk grep find du df timeout proot dash; do
    printf '  %-7s %s\n' "$c" "$(command -v $c || echo MISSING)"
  done
  echo
  echo "## apt / pkg state  (yahi aksar kharab hota hai)"
  echo "  pkg script : $(command -v pkg || echo MISSING)"
  SRC="$P/etc/apt/sources.list"
  [ -f "$SRC" ] || SRC="$P/lib/apt/sources.list"
  echo "  sources    : $SRC"
  [ -f "$SRC" ] && sed 's/^/    /' "$SRC" || echo "    (file nahi mila)"
  echo "  lists date : $(T 10 ls -l "$P/var/lib/apt/lists" 2>/dev/null | awk 'NR>1{print $6,$7,$8}' | head -1)"
  echo "  lists size : $(T 15 du -sh "$P/var/lib/apt/lists" 2>/dev/null | cut -f1)"
  echo "  lock       : $(ls "$P/var/lib/dpkg/lock" 2>/dev/null && echo 'lock file hai (dusra pkg chal raha?)' || echo free)"
  echo "  dpkg db    : $(T 15 grep -c '^Package:' "$P/var/lib/dpkg/status" 2>/dev/null)"
  echo
  echo "## network -> termux mirror + github"
  for U in https://packages.termux.dev/apt/termux-main/dists/stable/Release \
           https://mirror.fcix.net/termux/termux-main/dists/stable/Release \
           https://codeload.github.com/ranumeena133-hue/Build-studio-/tar.gz/refs/heads/arena/01a08283-build-studio \
           https://github.com; do
    if command -v curl >/dev/null 2>&1; then
      R=$(T 20 curl -s -o /dev/null -w '%{http_code} %{time_total}s' --max-time 18 "$U")
    elif command -v wget >/dev/null 2>&1; then
      R=$(T 20 wget -S --spider -q --timeout=18 "$U" && echo "200(wget)")
    else
      R=$(T 20 python3 -c "import urllib.request,ssl,time;u='$U';s=time.time();r=urllib.request.urlopen(u,timeout=18);print(r.status, round(time.time()-s,1),'s, KB=',round(len(r.read())/1024))" 2>&1 | tail -1)
    fi
    printf '  %-8s %s\n' "$(printf '%s' "$U" | sed 's|https://||;s|/.*||' | cut -c1-8)" "${R:-no tool}"
  done
  echo "  dns        : $(T 8 getprop net.dns1) / $(T 8 getprop net.dns2)  resolve: $(T 8 python3 -c "import socket;print(socket.gethostbyname('packages.termux.dev'))" 2>&1 | tail -1)"
  echo
  echo "## space (pkg install ke liye ~200MB chahiye hota hai)"
  T 10 df -h "$HOME" | tail -2 | sed 's/^/  /'
  echo
  echo "## last pkg/apt errors (agar cache me hon)"
  for f in "$P"/../tmp/*.log "$HOME"/.npm/_logs/*; do [ -f "$f" ] && { echo "  -- $f"; tail -5 "$f" | sed 's/^/    /'; }; done
  T 20 dmesg 2>/dev/null | tail -3 | sed 's/^/  /'
  echo
  echo "## agent state"
  echo "  bhai       : $(command -v bhai || ls "$P/bin/bhai" 2>/dev/null || echo 'PATH me nahi')"
  echo "  cfg        : $(cat "$HOME/.bhai/config" 2>/dev/null | tr '\n' ' ')"
  echo "  repo dir   : $(ls "$HOME/.bhai/repo" 2>/dev/null | tr '\n' ' ')"
  echo "  log tail   :"; tail -12 "$HOME/.bhai/logs/bhai.log" 2>/dev/null | sed 's/^/    /'
  echo
  echo "# FIX hints (main is file ko padhke exact command dunga):"
  echo "#  A) lists purani    -> pkg update && pkg upgrade -y"
  echo "#  B) mirror dead     -> termux-change-repo  (ya: echo 'deb https://packages.termux.dev/apt/termux-main stable main' > \$PREFIX/etc/apt/sources.list)"
  echo "#  C) Termux purana   -> F-Droid/GitHub se update karo (Play Store wala Termux dead hai)"
  echo "#  D) lock atka       -> pkill -f apt ; rm -f \$PREFIX/var/lib/dpkg/lock ; dpkg --configure -a"
  echo "#  E) kuch na chale   -> git ki zarurat hi nahi: bhai config SYNC_MODE=http"
} > "$OUT" 2>/dev/null

echo "termux-diag written: $OUT ($(wc -c < "$OUT" 2>/dev/null || echo 0) bytes)"
sed -n '1,30p' "$OUT" 2>/dev/null
exit 0
