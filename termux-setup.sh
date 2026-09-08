#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Build Studio — Termux setup (SIRF EK BAAR chalao)
#  Iske baad:
#    getfiles          -> server ki saari files phone me
#    sendfile file.pdf -> phone ki file server par
# ================================================
set -e

# 'getfiles' shortcut (download)
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/getfiles" << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
BASE="https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio"
command -v unzip >/dev/null 2>&1 || pkg install -y unzip
echo "📥 Build Studio ki files aa rahi hain..."
curl -sL "$BASE/build-studio-files.zip" -o /sdcard/Download/build-studio-files.zip
unzip -o /sdcard/Download/build-studio-files.zip -d /sdcard/Download/build-studio/ >/dev/null
echo ""
echo "✅ DONE! Files yahan hain: /sdcard/Download/build-studio/"
ls /sdcard/Download/build-studio/
SCRIPT

# 'sendfile' shortcut (upload)
cat > "$PREFIX/bin/sendfile" << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
# Usage: sendfile <file> [subfolder]
command -v gh >/dev/null 2>&1 || { echo "❌ pehle ye chalao: pkg install -y gh ; phir: gh auth login"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "❌ pehle GitHub login karo: gh auth login"; exit 1; }
F="$1"
[ -f "$F" ] || { echo "❌ file nahi mili: $F"; exit 1; }
DEST="${2:-}"
NAME="$(basename "$F")"
TARGET="storage/${DEST:+$DEST/}$NAME"
echo "📤 Upload ho rahi hai: $NAME -> $TARGET ..."
if gh api --method PUT "repos/ranumeena133-hue/Build-studio-/contents/$TARGET" \
     -f message="termux upload: $NAME" \
     -f content="$(base64 -w0 "$F")" --jq .content.size >/dev/null 2>&1; then
  echo ""
  echo "✅ UPLOAD HO GAYI: $TARGET"
  echo "   👉 Ab chat me bolo: \"pull karo\" — file server par aa jayegi!"
else
  echo "❌ upload fail (file 100MB se badi to nahi?)"
fi
SCRIPT

chmod +x "$PREFIX/bin/getfiles" "$PREFIX/bin/sendfile"

echo ""
echo "✅ Setup complete! Do command mile:"
echo "   getfiles            -> server ki files phone me laao"
echo "   sendfile <file>     -> phone ki file server par bhejo"
echo ""
echo "ℹ️  sendfile pehli baar chalane par agar login maange:"
echo "   pkg install -y gh"
echo "   gh auth login        (browser se login, one-time)"
