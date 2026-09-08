#!/data/data/com.termux/files/usr/bin/bash
# ============================================================================
# survey.sh - phone storage ka naksha. READ ONLY (kuch move/delete nahi hota).
#   usage: bash survey.sh [outfile]
# Default out: <shared>/Download/BuildStudio/storage-map.txt
# `bhai map` isi ko chalata hai (tasks/0003-storage-map.json bhi).
# Android portability: find -printf na support ho to stat-based fallback lagta hai.
# ============================================================================
set -u
SH="${BHAI_SHARED:-$HOME/storage/shared}"
[ -d "$SH" ] || SH="/sdcard"
# IMPORTANT: Termux me ~/storage/shared ek SYMLINK hai -> `find $SH` usme ghusta hi nahi.
# isliye physical path me convert karte hain (pwd -P, POSIX, har device par chalta hai).
if [ -d "$SH" ]; then
  R=$(cd "$SH" 2>/dev/null && pwd -P 2>/dev/null) && [ -n "$R" ] && SH="$R"
fi
SH="${SH%/}"; [ -n "$SH" ] || SH=/sdcard
BIG_MB=${BIG_MB:-20}          # 'biggest files' ka threshold
OUT="${1:-$SH/Download/BuildStudio/storage-map.txt}"
mkdir -p "$(dirname "$OUT")" 2>/dev/null

# T <seconds> <cmd...>  ->  time-bounded, errors chup, kabhi crash nahi
T() { local t=${1:-90}; shift; timeout "$t" "$@" 2>/dev/null; }
# N <cmd...> -> line count
N() { local n; n=$(T 45 "$@" | wc -l); printf '%s' "${n:-0}"; }

size_lines() {                 # size_lines <find expr...> -> "bytes<TAB>path"
  local out
  # \( ... \) zaroori hai: warna `A -o B -printf` me -printf sirf B branch par lagta hai
  out=$(T 150 find "$SH" \( "$@" \) -type f -printf '%s\t%p\n' | sort -rn | head -40)
  if [ -z "${out//[[:space:]]/}" ]; then
    out=$(T 180 find "$SH" \( "$@" \) -type f -print | head -400 | while IFS= read -r f; do
            s=$(T 10 stat -c '%s' "$f"); [ -n "$s" ] && printf '%s\t%s\n' "$s" "$f"
          done | sort -rn | head -40)
  fi
  printf '%s\n' "$out"
}

MB() { awk -F'\t' '$1>0{printf "  %8.1f MB  %s\n", $1/1048576, $2}'; }

{
  echo "# bhai storage map"
  echo "# generated: $(date '+%F %T %Z')"
  echo "# root: $SH"
  echo
  echo "## device"
  if command -v getprop >/dev/null 2>&1; then
    echo "  model   : $(T 5 getprop ro.product.model)"
    echo "  brand   : $(T 5 getprop ro.product.manufacturer)"
    echo "  android : $(T 5 getprop ro.build.version.release) (sdk $(T 5 getprop ro.build.version.sdk))"
  fi
  echo "  kernel  : $(uname -s -r -m)"
  echo "  termux  : $(command -v pkg >/dev/null 2>&1 && T 25 dpkg -l | tail -n +6 | wc -l || echo '?') pkgs installed"
  echo
  echo "## free space"
  T 10 df -h "$SH" | tail -1 | sed 's/^/  /'
  echo
  echo "## top-level of shared storage"
  printf '%-14s %9s %8s  %s\n' FOLDER SIZE FILES LAST-MODIFIED
  for d in DCIM Pictures Movies Download Documents Music Notifications Podcasts Ringtones Alarms Android WhatsApp Telegram, X Docs Google Chrome; do
    p="$SH/$d"; [ -d "$p" ] || continue
    sz=$(T 60 du -sh "$p" | cut -f1)
    n=$(N find "$p" -type f)
    mt=$(T 5 stat -c '%y' "$p" | cut -d. -f1)
    printf '%-14s %9s %8s  %s\n' "$d" "${sz:-?}" "$n" "${mt:-?}"
  done
  echo
  echo "## biggest files (>${BIG_MB}MB, top 20)"
  size_lines -size +"${BIG_MB}M" | head -20 | MB
  echo
  echo "## files by extension (top 14 by count)"
  T 75 find "$SH" -type f | sed 's/.*\///' | awk -F. 'NF>1 && length($NF)<9 {print tolower($NF)}' \
    | sort | uniq -c | sort -rn | head -14 | sed 's/^/  /'
  echo
  echo "## media breakdown per folder"
  for d in DCIM Pictures Download Movies WhatsApp Telegram; do
    p="$SH/$d"; [ -d "$p" ] || continue
    printf '  %-10s img=%-6s video=%-6s png=%-6s audio=%s\n' "$d" \
      "$(N find "$p" -iname '*.jpg' -o -iname '*.jpeg')" \
      "$(N find "$p" -iname '*.mp4' -o -iname '*.mkv' -o -iname '*.3gp')" \
      "$(N find "$p" -iname '*.png' -o -iname '*.webp')" \
      "$(N find "$p" -iname '*.mp3' -o -iname '*.m4a')"
  done
  echo
  echo "## camera vs screenshots (organising ke liye)"
  printf '  %-26s %s\n' "DCIM/Camera"            "$(N find "$SH/DCIM/Camera" -type f)"
  printf '  %-26s %s\n' "Pictures/Screenshots"    "$(N find "$SH/Pictures/Screenshots" -type f)"
  printf '  %-26s %s\n' "Screenshot"              "$(N find "$SH/Screenshot" -type f)"
  echo
  echo "## junk / temp (delete candidates - main LIST dunga, 'haan' bolo tabhi delete hoga)"
  size_lines -name '*.tmp' -o -name '*.partial' -o -name '*.log' -o -name '*.crdownload' -o -name '.*.swp' | head -20 \
    | awk -F'\t' '$1>0{printf "  %10s B  %s\n", $1, $2}'
  echo
  echo "## Download me 1 saal se purane (archive candidates)"
  T 60 find "$SH/Download" -type f -mtime +365 | head -40 | sed 's/^/  /'
  echo
  echo "## same-size pairs in DCIM (duplicate shak - confirm karke hi hataunga)"
  dup=$(T 75 find "$SH/DCIM" -type f -size +100k -printf '%s\t%p\n' | sort -n)
  if [ -z "${dup//[[:space:]]/}" ]; then
    dup=$(T 90 find "$SH/DCIM" -type f -size +100k -print | head -300 | while IFS= read -r f; do
            s=$(T 10 stat -c '%s' "$f"); [ -n "$s" ] && printf '%s\t%s\n' "$s" "$f"
          done | sort -n)
  fi
  printf '%s\n' "$dup" | awk -F'\t' 'c[$1]++==1{printf "  [%s B]:\n",$1} c[$1]>1{printf "    %s\n",$2}' | head -30
  echo
  echo "## termux home"
  T 40 du -sh "$HOME" 2>/dev/null | sed 's/^/  /'
  echo
  echo "# AGENT NOTE: yeh padhke main tumhare liye safe task banaunga."
  echo "# Koi bhi delete/trash task 'confirm' field ke saath aayega - bina word type kiye nahi chalega."
} > "$OUT" 2>/dev/null

BYTES=$(wc -c < "$OUT" 2>/dev/null || echo 0)
echo "storage-map written: $OUT (${BYTES} bytes)"
[ "$BYTES" -gt 40 ] && sed -n '1,34p' "$OUT"
exit 0
