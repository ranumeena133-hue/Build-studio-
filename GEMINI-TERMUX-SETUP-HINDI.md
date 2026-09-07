# 🤖 AI ko DIRECT Local Folder ka Access — Mobile + Termux (₹0, Bina Card) — Hindi Guide

> AI **khud** tumhare folder me ghusega — file padhega, banayega, edit karega, replace karega. Tum bas Hindi me bologe. Aur kharcha? **₹0 — free key, bina credit card.**

---

## 🧠 Pehle 2 sach samjho (jhoothi ummeed nahi dunga)

1. **Bina key/login ke direct access namumkin hai.** Jo agent tumhare folder me kaam karega, use AI se baat karne ke liye *kuch to* chahiye. Gemini app (chat wali) tumhare folder ko khud nahi ched sakti — wo sirf baat karti hai.
2. **"API key" ka matlab PAISA nahi!** Google ki **FREE key** abhi bhi milti hai — bina card, bina billing, roz sekdon free requests (Flash models par). Bas **billing OFF** rakhna hai, paise kabhi nahi lagega.

> To hamara plan: **Termux me AI agent + Google ki FREE key (₹0)** = AI ko tumhare local folder ka poora access. Yehi ek asli tarika hai. Chal shuru karte hain! 🚀

---

## 📦 Kya-kya chahiye (sab free)

| Cheez | Kahan se |
|---|---|
| Android mobile + net | tumhara phone |
| **Termux (F-Droid wala)** | ⚠️ Play Store wala **mat** lena — https://f-droid.org se lo |
| Google account | free key banane ke liye |
| ~500 MB jagah | Node.js + agent ke liye |

---

## Step 1️⃣ — Termux taiyaar karo

Termux kholo, ye ek-ek karke paste karo (paste = ungli dabaye rakho → **PASTE**):

```bash
pkg update && pkg upgrade -y
```

```bash
pkg install nodejs-lts git -y
```

Check karo:

```bash
node -v
```

`v20` ya upar (jaise `v22.x`) aana chahiye. ✅

---

## Step 2️⃣ — AI agent install karo (Termux wala, easy)

```bash
npm install -g @mmmbuto/gemini-cli-termux
```

```bash
gemini --version
```

Version number dikha = ho gaya 🎉

> Ye khaas **Termux/Android ke liye bana** Gemini agent hai — normal wale me mobile par error aata hai, isme nahi. (Agar ye na chale to backup: `npm install -g @google/gemini-cli --ignore-scripts`)

---

## Step 3️⃣ — FREE key banao (₹0, bina card) ⭐

**3a. Browser me key banao (2 minute):**
1. Mobile browser me kholo: **https://aistudio.google.com/apikey**
2. Google login karo → **Create API Key** dabao → key copy kar lo.
3. ⚠️ **Billing/card KABHI mat jodo is project me!** Card jodte hi free quota **khatm** ho jata hai. Billing OFF = free forever.

**3b. Key + FREE model Termux me save karo:**

```bash
echo 'export GEMINI_API_KEY="YAHAN-APNI-KEY-PASTE-KARO"' >> ~/.bashrc
echo 'export GEMINI_MODEL="gemini-2.5-flash"' >> ~/.bashrc
source ~/.bashrc
```

> - `YAHAN-APNI-KEY-PASTE-KARO` ki jagah asli key paste karna.
> - **`GEMINI_MODEL` wali line sabse zaroori hai!** Agent default me Pro model mangta hai (jo paid hai). `gemini-2.5-flash` **free** hai — isliye ye line lagayi. Aur zyada free limit chahiye to `gemini-2.5-flash-lite` likh sakte ho.

Check karo:

```bash
echo $GEMINI_API_KEY | cut -c1-6
echo $GEMINI_MODEL
```

Dono me kuch dikha = perfect ✅

**Free me kitna milega?** (lagbhag, model ke hisaab se roz):
- `gemini-2.5-flash-lite` → ~1000 request/roz (sabse zyada free)
- `gemini-2.5-flash` → ~250 request/roz (thoda smart)
- Apna asli quota yahan dekho: **https://aistudio.google.com** → Usage/Limits

---

## Step 4️⃣ — Folder ka ACCESS do (yehi asli step hai ⭐⭐⭐)

```bash
termux-setup-storage
```

- Popup aaye → **Allow** dabao.

```bash
mkdir -p ~/storage/shared/my-project
cd ~/storage/shared/my-project
```

Ab agent chalao:

```bash
gemini
```

- Pehli baar theme puchega → jo marzi chuno.
- **"Trust this folder?"** → **Yes** karo.

🎉 **HO GAYA BHAI!** Ab AI ke paas tumhare `my-project` folder ka **poora access** hai — ye khud file bana/edit/replace kar sakta hai. Neeche wala box ab tumhara AI mazdoor hai, Hindi me hukam do!

---

## Step 5️⃣ — Pehla kaam karwao (access test karo)

Ye type karo, Enter dabao:

```
is folder me meri pehli website banao — index.html me mera naam likho
```

AI khud:
1. File banayega
2. Puchega **"Allow?"** → Yes karo
3. Kaam karke dikhayega

**Bahar nikalna ho to:** `/quit` likho (ya `Ctrl+C` do baar).

**Access PROOF dekho** (nikalne ke baad):

```bash
ls
cat index.html
```

AI ne file bana di = access mil gaya ✅

---

## 🗣️ AI se aise hukam do — ready prompts

**📄 Nayi file:**
```
mere liye style.css banao — dark theme, mobile friendly
```

**✏️ Edit (baaki mat chedna):**
```
index.html padho, sirf heading ka rang laal kar do, baaki kuch mat chedo
```

**🔁 Replace (pehle backup):**
```
app.js ka backup app.js.bak me banao, phir usko naye se likh do jo button dabane par photo dikhaye
```

**🔍 Safe mode (pehle plan):**
```
pehle batao kya-kya badloge bina change kiye. meri haan ke baad hi file chedna.
```

**🐞 Error fix:**
```
ye error aa raha hai: [error paste karo]. file padh kar khud theek kar do.
```

**📦 Poora project samajhna:**
```
is folder ki saari files padh kar 5 line me batao ye project kya karta hai
```

---

## Step 6️⃣ — Atomic / Safe (bigde to wapas 🛡️)

**Folder me ek baar ye karo:**

```bash
cd ~/storage/shared/my-project
git init
git add .
git commit -m "shuruat"
```

**AI se bada kaam karwane se PEHLE, AI ko bolo:**

```
pehle git status dekho, phir kaam karo. kaam ke baad kya badla wo batao.
```

**Agar AI ne kuch bigad diya** (agent band karke ya naye session me):

```bash
cd ~/storage/shared/my-project
git diff       # AI ne kya-kya badla, dekho
git checkout . # ❌ sab WAPAS — ek command me pehle jaisa
```

**Kaam pasand aaya to pakka karo:**

```bash
git add . && git commit -m "sahi hai"
```

> 💡 Golden rule: **pehle commit, phir AI ka kaam.** Bigde → `git checkout .` Bas, atomic!

---

## ⚙️ Baar-baar "Allow?" se tang ho? (Auto mode)

Shuruat me manual **Allow** hi rakho (safe). Jab bharosa ho jaye, tab agent aise chalao:

```bash
gemini --yolo
```

- `--yolo` = AI bina puche kaam karega. Fast, lekin **sirf tab jab git safe-point bana rakha ho!**

---

## 🚀 Roz ka routine (2 commands)

```bash
cd ~/storage/shared/my-project
gemini
```

Kaam karo → `/quit` se niklo. Bas!

**Free quota bachane ke 3 fund-e:**
1. Chhote-chhote kaam do, ek saath poora project mat banwao.
2. Lambi chat bhari lage to `/quit` karke nayi shuru karo.
3. Quota khatm ho jaye to `GEMINI_MODEL` ko `gemini-2.5-flash-lite` kar do (sabse zyada free) — ya agle din tak ruko (roz reset hota hai).

---

## 🆘 Dikkat aaye to — ilaaj table

| Dikkat | Ilaaj |
|---|---|
| `You need to install Termux for this module` | Termux wala agent install karo: `npm install -g @mmmbuto/gemini-cli-termux` |
| `gemini: command not found` | Termux band karke kholo; phir bhi na mile to install dobara chalao |
| `401 / API key not valid` | Key galat paste hui — Step 3b dobara karo, `"` ke andar poori key honi chahiye |
| `429 / quota exceeded` | Roz ki free limit khatm — Lite model lagao ya kal try karo; AI Studio me quota dekho |
| Paise katne ka darr | AI Studio project me **billing OFF** rakho, card mat jodo — free me paise NAHI lagte |
| `node: command not found` | `pkg install nodejs-lts -y` dobara chalao |
| Storage folder nahi dikh raha | `termux-setup-storage` + Allow; phir `ls ~/storage/shared/` |
| Lambe kaam me Termux band ho jata hai | Battery setting me Termux = **Unrestricted** karo; kaam tukdo me karwao |
| AI bevakoofi kar raha hai | Flash model Pro se halka hai — chhote, saaf hukam do; "pehle plan batao" bolo |

---

## 🆓 Dusre FREE AI Tools — DeepSeek (coding ka raja 👑)

Gemini ke alawa **2 aur bilkul free raste** hain. Dono me AI ko direct folder access milta hai, dono me **koi card nahi** lagta:

| Tool | Free me kya milta | Coding quality | Key/Card |
|---|---|---|---|
| **Gemini Flash** (upar wala) | roz ~250-1000 requests, permanent free | Good 👍 | Free key, no card |
| **DeepSeek** (official) | **5 million tokens free**, 30 din tak | Excellent 🏆 | Free key, no card |
| **OpenRouter free** | roz **50 requests**, `:free` models | Model par depend | Free key, no card |

### 🏆 Tarika 1 — DeepSeek + Aider (RECOMMENDED for coding)

DeepSeek coding me duniya me top par hai, aur naye account par **5M tokens free** milte hain (koi card nahi) [1](https://costgoat.com/pricing/deepseek-api). Aider ek terminal agent hai jo DeepSeek se chalta hai aur **khud git commit bhi karta hai** (atomic built-in!).

**Step A — Aider install karo (ek baar):**

```bash
pkg install python git -y
pip install aider-chat
```

```bash
aider --version
```

Version dikha = ho gaya ✅

**Step B — DeepSeek free key banao (2 minute):**
1. Browser me kholo: **https://platform.deepseek.com**
2. Email se **Sign Up** karo → login karo.
3. **API Keys** me jao → **Create** dabao → key copy kar lo. (5M free tokens account me khud jud jate hain, 30 din ke liye.)
4. Termux me save karo:

```bash
echo 'export DEEPSEEK_API_KEY="YAHAN-APNI-KEY-PASTE-KARO"' >> ~/.bashrc
source ~/.bashrc
```

**Step C — Folder ka access do + chalao:**

```bash
cd ~/storage/shared/my-project
aider --model deepseek/deepseek-chat
```

- Pehli baar puchega to **Yes** karo.
- 🎉 **Ab DeepSeek ke paas tumhare folder ka direct access hai!** Hindi me bolo, wo khud file banayega/edit karega.

**Aider me kaam ke commands:**

| Likhna hai | Matlab |
|---|---|
| `/add index.html` | is file par kaam karo (AI ko do) |
| `/diff` | AI ne kya badla, dekho |
| `/undo` | aakhri badlav wapas lo |
| `/commit` | kaam pakka save karo |
| `/help` | saare commands |
| `Ctrl+C` | bahar niklo |

> 💡 Aider **khud git commit karta hai** — matlab har badlav ka safe-point auto banta hai. Isse zyada atomic kya hoga!

**DeepSeek se baat (phone app, bina key):** Sirf chat karni ho (bina folder access) to **DeepSeek app** (Play Store) bilkul free hai, file upload ke saath — wahi copy-paste wala loop chalega.

### 🎁 Tarika 2 — OpenRouter FREE models (roz 50 requests, bina card)

OpenRouter par bahut saare `:free` models milte hain (DeepSeek, Qwen, Gemma jaise — lineup badalti rehti hai). Naye account par **roz 50 requests free, koi card nahi** [2](https://ask-coreai.com/blog/openrouter-free-models-2026-limits-catches).

**Step A — Free key + free model chuno:**
1. Browser me kholo: **https://openrouter.ai** → email/GitHub se signup (card nahi mangta).
2. **Keys** page → key banao → copy karo.
3. **Models** page kholo → **free filter** lagao → jo free model pasand aaye uska **ID copy** karo (jaise `deepseek/deepseek-v3.2:free` — naam badalte rehte hain, wahan se taaza copy karna).

**Step B — Termux me chalao:**

```bash
echo 'export OPENROUTER_API_KEY="YAHAN-APNI-KEY-PASTE-KARO"' >> ~/.bashrc
source ~/.bashrc
cd ~/storage/shared/my-project
aider --model openrouter/WAHAN-SE-COPIED-MODEL-ID
```

> ⚠️ 50/roz wali limit me **fail hue request bhi gine jate hain**, to soch-samajh kar bhejo. Quota khatm = agle din reset.

### 🤔 Kaunsa chunu? (seedhi salah)

- **Roz thoda-thoda, permanent free** → Gemini Flash (upar wala main tarika)
- **Coding ka best result, 30 din tak free** → DeepSeek 🏆
- **Model badal-badal kar experiment** → OpenRouter free
- 30 din baad DeepSeek khatm ho to tension nahi — DeepSeek paid bhi duniya ka sabse sasta hai, ya Gemini free par wapas aa jao.

---

## 🔌 Apna MCP Server Agent se Jodo (Gemini CLI + MCP)

Tumne MCP server bana liya — ab use **agent se jodna** hai. Rule yaad rakho: **server = taala 🔒, agent = chaabi 🔑**. Dono same phone (Termux) me chalenge, tab AI tumhare server ke through file read/write karega.

### Step A — Apna server test karo (Termux me)

Pehle dekho server akela chalta hai ya nahi (apni file ka naam lagao):

```bash
node ~/mcp-server.js
```

- Koi error na aaye (bas ruk jaye / log dikhe) = sahi hai. `Ctrl+C` se band karo.
- Error aaye to pehle wahi theek karo — bina chalte server ke agent nahi judega.

Deep test (server jawab deta hai ya nahi):

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | node ~/mcp-server.js
```

JSON jawab aaya = server ekdum sahi ✅

### Step B — Gemini CLI ko server se jodo

Settings file banao/kholo:

```bash
mkdir -p ~/.gemini
nano ~/.gemini/settings.json
```

Ye paste karo (**path apne hisaab se badalna** — apna path dekhne ke liye `pwd` aur `ls` chalao):

```json
{
  "mcpServers": {
    "mera-server": {
      "command": "node",
      "args": ["/data/data/com.termux/files/home/mcp-server.js"],
      "cwd": "/data/data/com.termux/files/home/storage/shared/my-project",
      "timeout": 30000
    }
  }
}
```

> ⚠️ `~` mat likho — **poora path** likho (`/data/data/com.termux/files/home/...`). Save: `Ctrl+O`, Enter, `Ctrl+X`.

### Step C — Test karo

```bash
cd ~/storage/shared/my-project
gemini
```

1. `/tools` likho → tumhare server ke tools dikhne chahiye (jaise `read_file`, `write_file` — jo naam tumne rakhe).
2. Ye bolo:

```
MCP server ke tool se mere folder ki files ki list dikhao
```

```
MCP se index.html padh kar uski pehli 5 line batao
```

3. Phir write test:

```
MCP se hello.txt banao aur usme mera naam likho
```

Bahar nikal kar check: `cat hello.txt` — naam dikha = **MCP read+write dono chal rahe!** 🎉

### Step D — Agar tumhara server HTTP wala hai

```bash
node ~/mcp-server.js
```

- Port note karo (jaise 3000). Ye Termux me **chalta rehne do** (naya session kholo: Termux me left-swipe → New Session).
- Settings me ye lagao:

```json
{
  "mcpServers": {
    "mera-server": {
      "httpUrl": "http://localhost:3000/mcp"
    }
  }
}
```

> Port apna lagao. Phir Step C jaisa test karo.

### 🆘 MCP jude nahi? Ilaaj

| Dikkat | Ilaaj |
|---|---|
| `/tools` me server ke tools nahi dikh rahe | `settings.json` me comma/brace check karo; server ka path 100% sahi likho; `gemini` restart karo |
| `MCP server failed to start` | Step A me server akela chalao — jo error aaye wahi asli dikkat hai |
| `node: command not found` | `pkg install nodejs-lts -y` |
| HTTP wala connect nahi ho raha | Server wala session chal raha hai na? Port sahi hai? `httpUrl` me `/mcp` laga hai? |
| Tool chalta hai par file nahi milti | `cwd` me sahi folder ka poora path likho |

### 🔒 Security — bahut zaroori!

- MCP server ko **kabhi public tunnel (ngrok/pinggy/link) par mat kholo** — koi bhi duniya me tumhari file padh/mita sakta hai!
- Sirf **localhost + apne agent** se use karo. Bas.

### 🧪 Mujhse (chat wale AI) server test karwana ho?

Server ka code repo me `mcp-server.js` naam se daal do (ya yahin chat me paste kar do) — main use yahan chala kar read/write ka full test karke report de dunga!

---

## ⚡ Cheat-sheet — ek nazar me

```bash
# ==== PEHLI BAAR ====
pkg update && pkg upgrade -y
pkg install nodejs-lts git -y
npm install -g @mmmbuto/gemini-cli-termux
termux-setup-storage
echo 'export GEMINI_API_KEY="APNI-FREE-KEY"' >> ~/.bashrc
echo 'export GEMINI_MODEL="gemini-2.5-flash"' >> ~/.bashrc
source ~/.bashrc
mkdir -p ~/storage/shared/my-project

# ==== ROZ ====
cd ~/storage/shared/my-project
gemini

# ==== DEEPSeek (coding best) ====
pip install aider-chat
echo 'export DEEPSEEK_API_KEY="APNI-FREE-KEY"' >> ~/.bashrc
source ~/.bashrc
cd ~/storage/shared/my-project
aider --model deepseek/deepseek-chat

# ==== OPENROUTER FREE (roz 50) ====
echo 'export OPENROUTER_API_KEY="APNI-FREE-KEY"' >> ~/.bashrc
source ~/.bashrc
cd ~/storage/shared/my-project
aider --model openrouter/FREE-MODEL-ID-YAHAN
```

---

## 💬 Bilkul bina-key wala backup (agar key hi nahi banani)

Agar tumhe **koi key nahi** chahiye — to AI khud file nahi ched payega, lekin **baat karke** kaam ho jayega:

1. `pkg install termux-api -y` + F-Droid se **Termux:API** app lo.
2. File AI ko dikhao: `cat index.html | termux-clipboard-set` → Gemini app me paste + bolo.
3. AI ka code copy karo → `termux-clipboard-get > index.html` → file me save.
4. Paste se pehle `git commit` (safe), bigde to `git checkout .`

---

## ✅ Aakhir me — 3 baat yaad rakho

1. **Jis folder me `gemini` chalaya = AI ka access usi me.** Yahi poora concept hai.
2. **FREE key = ₹0.** Billing OFF rakho, card mat jodo, free quota roz reset hota hai.
3. **Pehle `git commit`, phir AI ka kaam.** Bigde to `git checkout .` = sab wapas.

*All the best bhai! 🚀 Access milne ke baad pehla kaam karwa kar mujhe batana kaisa laga — aur koi error aaye to message yahin bhej dena!*
