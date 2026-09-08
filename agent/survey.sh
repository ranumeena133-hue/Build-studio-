#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# survey.sh - phone storage ka naksha banao. READ ONLY. Kuch move/delete nahi.
# Output: <shared>/Download/BuildStudio/storage-map.txt
# `bhai map` isi ko chalata hai; tasks/0003-storage-map.json bhi.
# Portability: Android ke find/stat par -printf na mile to fallback use hota hai.
# ============================================================================
set -u
SH="${BHAI_SHARED:-$HOME/storage/shared}"
[ -d "$SH" ] || SH="/sdcard"
OUT="${1:-$SH/Download/BuildStudio/storage-map.txt}"
mkdir -p "$(dirname "$OUT")" 2>/dev/null
T() { timeout "${2:-90}" "$@" 2>/dev/null; }   # time-bounded, never crash

size_lines() {         # $1 = find args...  -> "bytes<TAB>path" lines
  local out
  out=$(T find "$SH" -type f "$@" -printf '%s\t%p\n' 120 | sort -rn | head -40)
  if [ -z "$out" ]; then
    out=$(T find "$SH" -type f "$@" -print 150 | head -300 | while IFS= read -r f; do
             s=$(T stat -c '%s' "$f" 8); [ -n "$s" ] && printf '%s\t%s\n' "$s" "$f"
           done | sort -rn | head -40)
  fi
  printf '%s\n' "$out"
}

{
  echo "# bhai storage map"
  echo "# generated: $(date '+%F %T %Z')"
  echo
  echo "## device"
  if command -v getprop >/dev/null 2>&1; then
    echo "  model  : $(getprop ro.product.model)"
    echo "  android: $(getprop ro.build.version.release) (sdk $(getprop ro.build.version.sdk))"
    echo "  brand  : $(getprop ro.product.manufacturer)"
  fi
  uname -a | sed 's/^/  /'
  echo "  termux pkg count: $(T dpkg -l 20 | tail -n +6 | wc -l)"
  echo
  echo "## free space"
  df -h "$SH" | tail -2 | sed 's/^/  /'
  echo
  echo "## top-level of /sdcard"
  printf '%-14s %9s %9s  %s\n' FOLDER SIZE "FILES" "LAST-MOD"
  for d in DCIM Pictures Movies Download Documents Music Notifications Podcasts Alarms Ringtones Android WhatsApp Telegram; do
    p="$SH/$d"
    [ -d "$p" ] || continue
    n=$(T find "$p" -type f 90 | wc -l)
    sz=$(T du -sh "$p" 90 | cut -f1)
    mt=$(T stat -c '%y' "$p" 8 | cut -d. -f1)
    printf '%-14s %9s %9s  %s\n' "$d" "${sz:-?}" "$n" "${mt:-?}"
  done
  echo
  echo "## biggest files (>20MB, top 20)"
  size_lines -size +20M | head -20 | awk -F'\t' '$1>0{printf "  %8.1f MB  %s\n", $1/1048576, $2}'
  echo
  echo "## files by extension (top 14)"
  T find "$SH" -type f 150 | sed 's/.*\///' | awk -F. 'NF>1{print tolower($NF)}' | sort | uniq -c | sort -rn | head -14 | sed 's/^/  /'
  echo
  echo "## media breakdown"
  for d in DCIM Pictures Download Movies WhatsApp Telegram; do
    p="$SH/$d"; [ -d "$p" ] || continue
    j=$(T find "$p" -iname '*.jpg' -o -iname '*.jpeg' 60 | wc -l)
    v=$(T find "$p" -iname '*.mp4' -o -iname '*.mkv' -o -iname '*.3gp' 60 | wc -l)
    g=$(T find "$p" -iname '*.png' -o -iname '*.webp' 60 | wc -l)
    a=$(T find "$p" -iname '*.mp3' -o -iname '*.m4a' 60 | wc -l)
    printf '  %-10s img=%-6s video=%-6s png/webp=%-6s audio=%s\n' "$d" "$j" "$v" "$g" "$a"
  done
  echo
  echo "## screenshots vs camera (organise karne laayak)"
  printf '  %-28s %s\n' "Screenshot/" "$(T find "$SH/Screenshot" -type f 60 | wc -l)"
  printf '  %-28s %s\n' "Pictures/Screenshots" "$(T find "$SH/Pictures/Screenshots" -type f 60 | wc -l)"
  printf '  %-28s %s\n' "DCIM/Camera" "$(T find "$SH/DCIM/Camera" -type f 60 | wc -l)"
  echo
  echo "## junk / temp (delete candidates - main PUCHH ke hi delete karunga)"
  size_lines -name '*.tmp' -o -name '*.partial' -o -name '*.log' -o -name '.*.swp' | head -20 | awk -F'\t' '$1>0{printf "  %9s B  %s\n", $1, $2}'
  echo
  echo "## very old files in Download (>365 din) - archive candidates"
  T find "$SH/Download" -type f -mtime +365 90 | head -40 | sed 's/^/  /'
  echo
  echo "## same-size pairs (duplicate shak)"
  T find "$SH/DCIM" "$SH/Pictures" "$SH/Download" -type f -size +100k 90 >/dev/null
  { T find "$SH/DCIM" -type f -size +100k -printf '%s\t%p\n' 90; } | sort -n | awk -F'\t' 'c[$1]++==1{print "  same size " $1 "B:"} c[$1]>1{print "    " $2}' | head -30
  echo
  echo "## termux home"
  du -sh "$HOME" 2>/dev/null | sed 's/^/  /'
  echo
  echo "# AGENT NOTE: yeh file padhke main tumhare liye safe task banaunga."
  echo "# kuch bhi delete karne se pehle main list dunga, tum 'haan' bolo tabhi hoga."
} > "$OUT" 2>/dev/null

BYTES=$(wc -c < "$OUT" 2>/dev/null || echo 0)
echo "storage-map written: $OUT (${BYTES} bytes)"
[ "$BYTES" -gt 40 ] && sed -n '1,28p' "$OUT"
exit 0
