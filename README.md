# MeraPaisa — Personal Finance Tracker (single file, 100% offline)

Ek professional, mobile-app style personal finance tracker — **poora app ek hi HTML file me**.
Koi server nahi, koi login nahi, koi internet nahi. Sirf `index.html` kholo aur chal jayega.

---

## App kholne ke links

**1. Abhi, bina kisi setup ke (public link — kisi bhi phone/browser me kholo):**

```
https://htmlpreview.github.io/?https://github.com/ranumeena133-hue/Build-studio-/blob/arena/35308669-build-studio/index.html
```

**2. Permanent saaf link (GitHub Pages) — ek baar enable karna hai:**

Repo me jaake `Settings → Pages → Build and deployment → Source: "GitHub Actions"` chuno.
Phir link ye hoga (har push pe auto-update):

```
https://ranumeena133-hue.github.io/Build-studio-/
```

**3. Apne phone/laptop me offline file:**

`index.html` download karo (GitHub pe file kholke **⤓ Download raw file**), phir browser se kholo —
internet band hone pe bhi poora app chalega.

---

## Kaise chalayein

**Option 1 — seedha phone/laptop me:**
`index.html` file ko browser me kholo (double-click / "Open with browser"). Bas.

**Option 2 — offline carry karo:**
File ko pendrive / phone storage me rakho. Airport mode me bhi poora chalega — charts, saving, sab.
Phone me "Add to Home Screen" karo to app jaisa icon ban jayega.

## Andar kya hai

| Tab | Kya karta hai |
|---|---|
| 🏠 **होम** | Is mahine ki bachat, aay/kharach, budget progress bar, goals (progress ring), recent transactions, 6-mahine ka savings trend (SVG sparkline) |
| 📈 **पोर्टफोलियो** | Holdings (share / mutual fund / sona / FD / PPF / cash), invested vs aaj ka moolya, P&L ₹ aur %, allocation donut chart, best performer |
| ➕ **+** | Lene-den ka entry: aay/kharach toggle, 9+5 category chips, tareekh, note |
| 📊 **रिपोर्ट** | 6 mahine ka aay-vs-kharach bar chart, mahina-wise category breakdown (progress bars), savings rate, avg monthly spend, insights |
| 👤 **प्रोफ़ाइल** | Naam/number/avatar, **हिंदी ↔ English** toggle, **light/dark** theme, monthly budget, JSON backup download/restore, demo reset, "sab khali karo" |

Extra: toast notifications, bottom-sheet modals, delete confirmation, empty-state screens, Indian number format (₹1,20,000), ek dum smooth animations — sab pure vanilla JS + CSS, **koi library nahi, koi CDN nahi**.

## Aapka data kahan rehta hai?

Sirf **usi browser ki `localStorage`** me — kisi server pe nahi jaata. Isliye:
- Incognito/private mode me data save nahi rahega
- Browser ka cache/data clear karne se data ja sakta hai → **mahine me ek baar Profile → "Baithak download karein"** (JSON backup) se backup le lo
- Phone badla? Nayi device pe wahi JSON file "Restore" kar do — sab wapas

## Apna naam / brand lagana ho?

`index.html` kholo, JS ke top pe `CONFIG` block hai:

```js
const CONFIG = {
  brand: 'MeraPaisa',        // English naam
  brandHi: 'मेरा पैसा',       // Hindi naam
  symbol: '₹',
  locale: 'en-IN',
  version: '1.0.0',
  storeKey: 'merapaisa.v1'   // localStorage key
};
```

Bas `brand` / `brandHi` badal do — header, title, footer aur About section sab jagah naam update ho jayega.
Rang badalne ke liye file ke top pe CSS variables hain (`--green`, `--green-2`, `--green-3`, `--r` waghairah).

## Demo data

Pehli baar kholne pe 6 mahine ka sample data + 7 holdings + 3 goals aata hai, taaki charts bhare-bhare dikhein.
**Profile → "Demo data reset karein"** se wapas aa jaata hai. Apna data shuru karne ke liye:
**Profile → "Sab khali karein"** (pehle backup le lena).

## Notes

- Yeh ek **personal tracker** hai. Yeh koi nivesh salaah nahi deta, kisi yojana ka jhaansa nahi deta aur koi return nahi dilata.
- Isme **koi referral / level commission / recharge / "daily earning" system nahi hai** — jaanbujhkar. Aisi cheezein India me BUDS Act 2019 aur PCMCS Act 1978 ke tahat illegal hain.
- Sab kuch aapke browser me chalta hai, to yeh kisi bhi device pe, bina internet, bina account — safe rehta hai.
