#!/data/data/com.termux/files/usr/bin/bash
# ================================================
#  Build Studio — Termux setup (SIRF EK BAAR chalao)
#  Iske baad hamesha bas ye type karna:  getfiles
# ================================================
set -e

# storage permission check
if [ ! -w /sdcard/Download ]; then
  echo "📁 Pehle storage permission chahiye — ye chalao: termux-setup-storage"
  echo "   (popup aayega, Allow dabao) — phir ye script dobara chalao"
  exit 1
fi

# unzip ho to theek, nahi to install
command -v unzip >/dev/null 2>&1 || pkg install -y unzip

# 'getfiles' shortcut banao
mkdir -p "$PREFIX/bin"
cat > "$PREFIX/bin/getfiles" << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
BASE="https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio"
echo "📥 Build Studio ki files aa rahi hain..."
curl -sL "$BASE/build-studio-files.zip" -o /sdcard/Download/build-studio-files.zip
unzip -o /sdcard/Download/build-studio-files.zip -d /sdcard/Download/build-studio/ >/dev/null
echo ""
echo "✅ DONE! Files yahan hain: /sdcard/Download/build-studio/"
ls /sdcard/Download/build-studio/storage/
SCRIPT
chmod +x "$PREFIX/bin/getfiles"

echo ""
echo "✅ Setup complete!"
echo "   Ab hamesha bas ye type karo:  getfiles"
