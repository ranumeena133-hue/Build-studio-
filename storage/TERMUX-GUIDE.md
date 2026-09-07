# 📱 BUILD STUDIO — TERMUX COMPLETE GUIDE

> **Ye ek baar ka setup hai — hamesha ke liye.**
> Iske baad sirf 2 command yaad rakhni hai: `getfiles` (download) aur `sendfile` (upload)

---

## 🧠 SYSTEM KAISA KAAM KARTA HAI (30 second me samjho)

```
        ☁️  SERVER (Build Studio sandbox)
                 ⬇️ getfiles          ⬆️ sendfile + "pull karo"
        📱 TUMHARA PHONE (Termux)      🐙 GITHUB (sabki files yahan)
```

- Server par files ka **main folder**: `storage/`
- Har change **GitHub par auto-sync** hota hai
- Phone me laane ke liye **`getfiles`** — hamesha fresh files
- Phone se bhejne ke liye **`sendfile`** + chat me **"pull karo"** bolna

---

# 🚀 PART 1: FIRST TIME SETUP (sirf ek baar)

### Step 1️⃣ — Storage permission

Termux kholo aur ye chalao:

```bash
termux-setup-storage
```

> 📲 Ek **popup** aayega — **"Allow"** dabao.
> Ye isliye zaroori hai taaki files tumhare **Download folder** me aa jaayen.
> (Agar popup na aaye to tension mat lo — shayad pehle hi permission hai)

---

### Step 2️⃣ — Zaroori apps install

```bash
pkg update -y && pkg upgrade -y
pkg install -y curl unzip gh
```

> Ye 4 cheezein install hoti hain:
> `curl` = download karne ke liye · `unzip` = ZIP kholne ke liye · `gh` = GitHub upload ke liye

---

### Step 3️⃣ — GitHub login (one-time, sabse important!)

```bash
gh auth login
```

Ab ye options chunno (arrow keys + Enter):

| Sawal | Jawab |
|---|---|
| What account...? | **GitHub.com** |
| Preferred protocol...? | **HTTPS** |
| Authenticate Git...? | **Y** (ya Enter) |
| How to authenticate? | **Login with a web browser** |

Ab ek **8-digit code** dikhega (jaise `XXXX-XXXX`) — **usko note kar lo** 📝

Phir:
1. Termux khud browser kholega (na khole to code ke saath link dikhega, wo kholo)
2. Browser me apne **GitHub account** me login karo (agar already login ho to best)
3. Wahan **code daalo**
4. **Authorize github** (neela button) dabao
5. Termux me `✓ Logged in as ranumeena133-hue` dikhega ✅

> 🔐 Ye tumhare **apne GitHub account** ki login hai — poori tarah safe hai.
> Ye **sirf ek baar** karni hai — hamesha ke liye set ho jayega.

---

### Step 4️⃣ — Build Studio ki shortcut commands install

```bash
curl -sL "https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/termux-setup.sh" | bash
```

Ye do **magic commands** bana dega:
- 📥 **`getfiles`** — server ki saari files phone me
- 📤 **`sendfile`** — phone ki file server par

```
✅ Setup complete! Do command mile:
   getfiles            -> server ki files phone me laao
   sendfile <file>     -> phone ki file server par bhejo
```

---

# ✅ SETUP COMPLETE! 🎉

## Ab check karo — pehla download:

```bash
getfiles
```

Output aisa aayega:

```
📥 Build Studio ki files aa rahi hain...
✅ DONE! Files yahan hain: /sdcard/Download/build-studio/
README.txt
demo.md
hello.txt
notes
termux-commands.txt
```

📁 Phone me path: **Internal Storage → Download → build-studio → storage**

---

# 📖 PART 2: DAILY USE COMMANDS (yaad rakhne wali)

### 📥 Server ki saari files phone me (fresh copy):

```bash
getfiles
```

> Jab bhi main naye files banau/add karau — bas ye dobara chalao. **Links kabhi nahi badalte.**

### 📤 Phone ki file server par bhejo:

```bash
sendfile /sdcard/Download/merifile.pdf
```

- Koi bhi file: pdf, jpg, mp3, docx, zip... kuch bhi
- **Subfolder** me bhejna ho: `sendfile photo.jpg pics`
- Upload ke baad **chat me bolo "pull karo"** → main server le lunga ✅

### 📥 Sirf ek file chahiye (bina ZIP ke):

```bash
curl -L "https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/storage/demo.md" -o /sdcard/Download/demo.md
```

> (file ke naam ke hisaab se last part badal dena)

### 📤 Bina Termux ke (phone BROWSER se upload):

Is link ko browser me kholo:
**https://github.com/ranumeena133-hue/Build-studio-/upload/arena/01a07dfe-build-studio/storage**

→ **Choose your files** → file chuno → **Commit changes** dabao → chat me bolo **"pull karo"**

### 📂 Server par kaunsi files hain ye dekho (browser me):

**https://github.com/ranumeena133-hue/Build-studio-/tree/arena/01a07dfe-build-studio/storage**

---

# 💬 PART 3: CHAT KE SIMPLE WORDS (Build Studio bhi se)

Chat me bas ye bolo — baaki sab automatic:

| Tum bolo | Hoga kya |
|---|---|
| **"file banao ... "** | Server par nayi file banegi |
| **"file edit karo"** | Server par file badlegi |
| **"file delete karo"** | Delete ho jayegi |
| **"pull karo"** | GitHub par uploaded files server par aa jayengi |
| **"file dikhao"** | File ka content dikhega |

Har change ke baad bas **`getfiles`** chalao — fresh files phone me! 🔁

---

# 🚑 PART 4: PROBLEM AAYE TO (Troubleshooting)

### ❌ `getfiles` chalaya par "permission denied" aaya
```bash
termux-setup-storage
```
chalao, Allow karo, phir `getfiles` dobara.

### ❌ `sendfile` bola "pehle GitHub login karo"
```bash
gh auth login
```
(Part 1, Step 3 jaise hi — browser code wala)

### ❌ `unzip: command not found`
```bash
pkg install -y unzip
```

### ❌ Download me sirf 86 bytes aaye / koi error file aayi
Matlab tumne **galat URL** use kiya. Termux me **SIRF** ye URLs chalenge:
- ✅ `raw.githubusercontent.com/...` (downloads)
- ✅ `github.com/...` (upload page)
- ❌ `8000-...e2b.app` — **ye SIRF Arena chat ke preview window ke liye hai, Termux me KABHI nahi chalega!**

### ❌ `sendfile` me "file nahi mili"
File ka **poora path** do — pehle `ls /sdcard/Download/` chala ke sahi naam dekho.

### ❌ Kuch bhi samajh na aaye
Bas chat me bolo: **"bhai termux me ye error aa raha hai: [error paste karo]"** 😄

---

# 📋 PART 5: QUICK REFERENCE CARD (screenshot le lo! 📸)

```bash
# ── FIRST TIME (ek baar) ──────────────────
termux-setup-storage
pkg update -y && pkg install -y curl unzip gh
gh auth login
curl -sL "https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/termux-setup.sh" | bash

# ── DAILY (hamesha) ───────────────────────
getfiles                          # 📥 saari files phone me
sendfile file.pdf                 # 📤 file server par
sendfile file.pdf folder          # 📤 subfolder me

# ── KABHI KABHI ───────────────────────────
ls /sdcard/Download/build-studio/storage/    # files dekho
unzip -o /sdcard/Download/build-studio-files.zip -d /sdcard/Download/build-studio/
```

---

## 🔗 IMPORTANT LINKS

| Kya | Link |
|---|---|
| 📂 Files dekho | https://github.com/ranumeena133-hue/Build-studio-/tree/arena/01a07dfe-build-studio/storage |
| 📤 Upload (browser) | https://github.com/ranumeena133-hue/Build-studio-/upload/arena/01a07dfe-build-studio/storage |
| ⚡ Setup script | https://raw.githubusercontent.com/ranumeena133-hue/Build-studio-/arena/01a07dfe-build-studio/termux-setup.sh |

---

*Build Studio File MCP Server ki taraf se 💙 — commands badalne par ye guide bhi update ho jayegi, bas `getfiles` chalate rehna!*
