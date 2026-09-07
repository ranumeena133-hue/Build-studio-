# 📱 Gemini ko Apne Mobile Folder ka Access Do — Termux Setup (Poori Hindi Guide)

> Sirf mobile se — Gemini khud file **padhe, edit kare, nayi file banaye, file replace kare**. Sabse saral tarika, step-by-step Hindi me.

---

## 🧠 Pehle 30 second me samjho

- **Gemini CLI** = Google ka free wala terminal agent jo tumhare folder ke andar kaam karta hai.
- **Termux** = Android mobile ka terminal (Linux jaisa). Isi me Gemini CLI chalega.
- **"Folder ka access"** = jis folder me tum `gemini` likh kar enter karoge, Gemini **usi folder** me file bana/edit/replace kar sakta hai. Bas itna hi concept hai!
- **Atomic/safe** = kaam bigde to wapas lao. Iske liye **git** wala tarika sabse best hai (neeche Step 6 me).

> ⚠️ **Zaroori khabar (June 2026 ke baad):** Google ne Gemini CLI ka **free Google-login wala istemal band kar diya hai**. Ab **API key** lagti hai (Google AI Studio se banti hai, istemal ke hisaab se paisa lagta hai). Ghabrao mat — neeche Step 3 me key banana 2 minute ka kaam hai.

---

## 📦 Tumhe kya-kya chahiye

| Cheez | Kahan se |
|---|---|
| Android mobile | tumhara phone 🙂 |
| **Termux app (F-Droid wala)** | ⚠️ Play Store wala **mat** lena — purana hai, dikkat dega |
| Internet | Wi-Fi ya mobile data |
| Google account | API key banane ke liye |
| 500 MB khaali jagah | Node.js + Gemini ke liye |

---

## Step 0️⃣ — Termux install karo (sahi wala)

1. Mobile browser me jao: **https://f-droid.org**
2. F-Droid app download karke install karo.
3. F-Droid kholo → search karo **"Termux"** → install karo.
4. Termux kholo. Pehli baar thoda setup chalega, ruk jao.

> 💡 Play Store wala Termux purana aur band-pada hai. Hamesha **F-Droid wala** Termux use karo.

---

## Step 1️⃣ — Termux update + Node.js + Git install karo

Termux me ye commands **ek-ek karke** copy-paste karo (paste karne ke liye Termux me ungli dabaye rakho → **PASTE**):

```bash
pkg update && pkg upgrade -y
```

```bash
pkg install nodejs-lts git -y
```

Check karo sab sahi hai:

```bash
node -v
npm -v
```

- `node` ka version **v20 ya usse upar** aana chahiye (jaise `v22.x`). Agar hai → perfect, aage badho.

---

## Step 2️⃣ — Gemini CLI install karo (sabse easy tarika)

Termux ke liye **2 tarike** hain. Pehla wala sabse easy hai, wohi karo:

### ✅ Tarika A — Termux wala version (RECOMMENDED)

Ye version khaas Termux/Android ke liye bana hai — error sabse kam aate hain:

```bash
npm install -g @mmmbuto/gemini-cli-termux
```

Check karo:

```bash
gemini --version
```

Version number dikh gaya = install ho gaya 🎉

### 🔧 Tarika B — Google wala original (agar A kaam na kare)

```bash
npm install -g @google/gemini-cli --ignore-scripts
```

> `--ignore-scripts` isliye lagaya kyunki Termux me kuch package mobile par ban-te waqt (native build) fail hote hain. Ye lagane se install aage badh jata hai.

---

## Step 3️⃣ — API Key banao aur Termux me save karo

Free login band hai, to ab key chahiye. 2 minute ka kaam:

**3a. Key banao (browser me):**
1. Mobile browser me kholo: **https://aistudio.google.com/apikey**
2. Google account se login karo.
3. **"Create API key"** dabao → key copy kar lo (lambe aksharon wali).

**3b. Key ko Termux me hamesha ke liye save karo:**

```bash
echo 'export GEMINI_API_KEY="YAHAN-APNI-KEY-PASTE-KARO"' >> ~/.bashrc
```

> `YAHAN-APNI-KEY-PASTE-KARO` ki jagah apni asli key paste karna. `"` ke andar honi chahiye.

Phir Termux band karke dobara kholo, ya ye chalao:

```bash
source ~/.bashrc
```

Check karo key lagi ya nahi (poori key **nahi** dikhegi, bas khaali to nahi hai ye pata chalega):

```bash
echo $GEMINI_API_KEY | cut -c1-6
```

Agar 5-6 akshar dikhe → key set hai ✅

> 🔒 **Safety:** Ye key kisi ko mat bhejo, screenshot me mat dikhao. Ye tumhare paise se judi hai.

---

## Step 4️⃣ — Folder ka access do (yehi asli step hai ⭐)

Gemini ko folder ka access dene ka matlab bas itna hai: **us folder ke andar jaakar `gemini` chalao.**

**4a. Phone storage ki permission (ek baar):**

```bash
termux-setup-storage
```

- Ek popup aayega → **Allow** dabao.
- Ab tumhara phone storage yahan dikhega: `~/storage/shared/` (matlab `/sdcard/`)

**4b. Apna kaam wala folder banao:**

```bash
mkdir -p ~/storage/shared/my-project
cd ~/storage/shared/my-project
```

> `my-project` ki jagah kuch bhi naam rakh sakte ho, jaise `meri-website`. Ye folder tumhe phone ke **File Manager me bhi dikhega**, to file dekhna easy rahega.

**4c. Gemini start karo — bas!**

```bash
gemini
```

Pehli baar ye puchega:
- **Theme/color** pasand karo (jo marzi).
- **Trust this folder?** → **Yes** karo. (Yahi permission hai — Gemini ab isi folder me file bana/edit kar sakta hai.)

🎉 **Ho gaya!** Ab neeche wala box Gemini ka chat hai. Hindi me likho, kaam pao.

---

## Step 5️⃣ — Pehli baar Gemini se kaam karwao

Gemini chal raha hai, ab ye try karo (type karke Enter):

```
meri pehli website banao — index.html me mera naam likho
```

Gemini khud:
1. File banayega (`index.html`)
2. Tumse puchega **"Allow?"** → `Yes` karo
3. Kaam karke dikhayega

**Kuch kaam ke commands (Gemini ke andar):**

| Likhna hai | Matlab |
|---|---|
| `/help` | saare commands dekho |
| `/tools` | Gemini kya-kya kar sakta hai (file read/write/edit/shell) |
| `/quit` ya `Ctrl+C` do baar | bahar niklo |
| `!ls` | folder ki files dekho (bina bahar nikle) |

**Bahiar nikalne ke baad file check karo:**

```bash
ls
cat index.html
```

---

## Step 6️⃣ — Atomic / Safe kaam (bigde to wapas lao 🛡️)

Bhai tumne **atomic** bola — matlab kaam ya to poora ho, ya kuch bigde to **wapas undo** ho jaye. Iske 2 tarike:

### 🥇 Tarika 1 — Git wala (BEST, professional)

Folder me ek baar ye karo:

```bash
cd ~/storage/shared/my-project
git init
git add .
git commit -m "shuruat"
```

Ab Gemini se **koi bhi bada kaam karwane se pehle** Gemini ko ye bolo:

```
pehle git status dekho, phir kaam karo. kaam ke baad kya badla, wo batao.
```

Aur **agar kuch bigad jaye**, Gemini band karke (ya naye Termux session me) ye chalao:

```bash
cd ~/storage/shared/my-project
git status        # kya-kya badla, dekho
git diff          # andar kya change hua, dekho
git checkout .    # ❌ sab badlav WAPAS LO (undo)
```

| Command | Matlab |
|---|---|
| `git status` | kaunsi file badli |
| `git diff` | file ke andar kya badla |
| `git checkout .` | sab kuch pehle jaisa karo (powerful undo) |
| `git add . && git commit -m "sahi hai"` | jab kaam pasand aaye, use save (pakka) karo |

> 💡 **Golden rule:** Jab kaam sahi lage → `commit` kar lo. Jab bigde → `git checkout .` kar lo. Bas, atomic!

### 🥈 Tarika 2 — Backup wala (bina git, super simple)

Gemini ko kaam dene se pehle bolo:

```
pehle poori file ka backup banao (.bak naam se), phir edit karo
```

Ya khud backup le lo:

```bash
cp index.html index.html.bak
```

Bigad jaye to:

```bash
cp index.html.bak index.html
```

---

## 🗣️ Gemini ko aise bolo — ready-made Hindi prompts

Copy-paste karke apne hisaab se badal lo:

**📄 Nayi file banana:**
```
mere liye style.css banao — dark theme, mobile friendly
```

**✏️ File edit karna:**
```
index.html me heading ka rang laal kar do, baaki kuch mat chedo
```

**🔁 File replace karna:**
```
purani app.js hata kar nayi wali likh do jo button dabane par photo dikhaye. pehle backup bana lena.
```

**🔍 Pehle dekhna, phir karna (safe mode):**
```
pehle batao tum kya-kya badloge, bina change kiye. meri haan ke baad hi file chedna.
```

**🐞 Error theek karna:**
```
ye error aa raha hai: [yahan error paste karo]. file padh kar theek kar do.
```

**📦 Poora project samajhna:**
```
is folder ki saari files padh kar batao ye project kya karta hai, 5 line me
```

---

## 🚀 Roz ka istemal (daily routine)

Termux kholo → bas 2 command:

```bash
cd ~/storage/shared/my-project
gemini
```

Bas! Kaam karo, `/quit` se niklo.

**Gemini update karna (kabhi-kabhi):**

```bash
npm update -g @mmmbuto/gemini-cli-termux
```

---

## ⚙️ Extra setting (jab thoda expert ban jao)

- **Baar-baar "Allow?" puchta hai?** Gemini ke andar `/settings` me jaakar auto-approve dekh sakte ho. Lekin shuruat me **manual Allow hi rakho** — safe rehta hai, galat file nahi chedta.
- **Project ka rule batana hai?** Folder me `GEMINI.md` naam ki file banao aur usme likh do, jaise: `hamesha hindi me jawab do, bina puche file delete mat karo`. Gemini har baar use padhega.
- **Lambe kaam me Termux band ho jata hai?** Android 12+ me system Termux ko maar deta hai (phantom process killer). Phone ki **Settings → Battery → Termux → Unrestricted** kar do, aur bade kaam chhote-chhote hisson me karwao.

---

## 🆘 Dikkat aaye to — ilaaj table

| Dikkat | Ilaaj |
|---|---|
| `You need to install Termux for this module` error | Tarika A wala version install karo (`@mmmbuto/gemini-cli-termux`), isme ye theek hai |
| `node: command not found` | `pkg install nodejs-lts -y` dobara chalao |
| Install me `node-pty` / build error | `--ignore-scripts` lagakar install karo (Tarika B) |
| `API key not valid` / paise wala error | Key dobara check karo, `~/.bashrc` me sahi paste hui hai ya nahi; AI Studio me billing/key status dekho |
| Phone storage me folder nahi dikh raha | `termux-setup-storage` chalao + Allow dabao; phir `ls ~/storage/shared/` dekho |
| Gemini bahut paisa kha raha hai | Chhote kaam do, `pehle plan batao` bolo, badi file ek saath mat padhwao |
| `gemini: command not found` | Termux band karke kholo; phir bhi na mile to install wala command dobara chalao |
| Net slow / request atak rahi hai | Wi-Fi par jao; lambi chat me `/quit` karke nayi shuru karo (token kam lagega) |

---

## ⚡ Cheat-sheet — ek nazar me

```bash
# pehli baar setup
pkg update && pkg upgrade -y
pkg install nodejs-lts git -y
npm install -g @mmmbuto/gemini-cli-termux
termux-setup-storage
echo 'export GEMINI_API_KEY="APNI-KEY"' >> ~/.bashrc
source ~/.bashrc

# roz ka kaam
cd ~/storage/shared/my-project
gemini
```

---

## ✅ Aakhir me — 3 yaad rakhne wali baat

1. **Folder = access.** Jis folder me `gemini` chalaya, usi me wo kaam karega.
2. **Pehle backup/commit, phir kaam.** Bigde to `git checkout .` = sab wapas.
3. **Chhota bolo, clear bolo.** Hindi me bolo, koi dikkat nahi — Gemini Hindi samajhta hai.

*All the best bhai! 🚀 Koi step atke to uska error message copy karke Gemini se hi puchh lena — wo khud ilaaj bata dega.*
