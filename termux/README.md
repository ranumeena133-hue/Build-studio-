# Build Studio — Termux Sync

Bina koi app banaye, **sirf Termux** se apne phone ka folder aur GitHub repo ko aapas me jodo.

**Phone ka folder:** `/storage/emulated/0/.BUILD STUDIO/NewProject3`
**GitHub repo:** `ranumeena133-hue/Build-studio-`

Do kaam hote hain:

1. **`bs pull`** — GitHub se laakar phone ke folder me daal deta hai
2. **`bs push`** — phone ka pura folder GitHub par chadha deta hai

Aur **`bs watch`** — background me chalta rehta hai, jaise hi phone me kuch badla, apne aap GitHub par chadha deta hai.

---

## Pehli baar ka setup (ek hi baar)

Termux kholo aur ye 3 line chalao:

```bash
pkg install -y git
git clone https://github.com/ranumeena133-hue/Build-studio-.git ~/bs-src
bash ~/bs-src/termux/setup.sh
```

Setup khud hi:
- `git`, `rsync`, `curl` install karega
- storage permission maangega (popup aaye to **ALLOW** dabana)
- tumse username, repo, folder aur token poochhega
- `bs` command install kar dega

### GitHub Token kahan se laun?

1. GitHub kholo → **Settings** → **Developer settings**
2. **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
3. Repository access → **Only select repositories** → `Build-studio-` chuno
4. Permissions → **Contents: Read and write** ← ye zaroori hai
5. Generate dabao, token copy kar lo (sirf ek baar dikhta hai)

---

## Roz ka istemaal

| Command | Kya karta hai |
|---|---|
| `bs pull` | GitHub → phone (nayi/badli files aa jayengi) |
| `bs push` | phone → GitHub (commit + push apne aap) |
| `bs sync` | pehle pull, phir push |
| `bs watch` | **background me chalu** — apne aap push karta rahega |
| `bs stop` | background band |
| `bs status` | kya-kya alag hai, dikhata hai |
| `bs log` | background ka log |
| `bs config` | setting ya token badlo |
| `bs help` | ye list |

### Sabse pehli baar
```bash
bs pull
```

### Aage se bas ye
```bash
bs watch
```
Ek baar chala do aur bhool jao. Jo bhi file `.BUILD STUDIO/NewProject3` me daaloge ya badloge,
30 second ke andar GitHub par pahunch jayegi.

---

## Kaam kaise karta hai

- Ek chhupi hui copy `~/buildstudio-work` me rehti hai — wahi asli git repo hai
- **Push**: phone ka folder → us copy me → `git add` → `git commit` → `git push`
- **Pull**: `git fetch` → us copy se → phone ka folder
- **Watch**: har 30 second me phone ke folder ka "nishaan" (fingerprint) banata hai.
  Nishaan badla = kuch badla = push kar do

**AI se jo `responsey` file milegi**, use bas `.BUILD STUDIO/NewProject3` me daal do —
watch chalu hai to wo apne aap GitHub par chadh jayegi.

---

## Zaroori baatein

**Push me delete bhi chalta hai** — phone se file hatai to GitHub se bhi hat jayegi.
Ye jaan-boojh kar rakha hai taki dono jagah ek jaisa rahe.

**Pull surakshit hai** — GitHub se aane wali files aa jayengi, par phone ki apni extra
files nahi mitegi. Isliye bina dare `bs pull` chala sakte ho.

**Phone folder khaali ho to push nahi hoga** — galti se pura repo khaali na ho jaye,
iska bachav rakha hai.

**Token surakshit hai** — `~/.buildstudio.conf` me `chmod 600` ke saath rehta hai
(sirf tum padh sakte ho). Use kabhi GitHub par commit mat karna.

**Watch band ho jaye to?** Android battery bachane ke liye Termux ko maar deta hai.
Bachne ke liye:
- Phone Settings → Apps → Termux → Battery → **Unrestricted / Don't optimize**
- Termux notification me **Acquire wakelock** dabao

**Speed badalni ho?** `bs config` chalao aur second badal do (default 30).

---

## Kuch atak jaye to

| Dikkat | Ilaaj |
|---|---|
| `Clone fail` | Token galat hai ya expire ho gaya → `bs config` |
| `Push fail` | Token me **Contents: Read and write** nahi hai |
| `Storage nahi mila` | `termux-setup-storage` chalao, ALLOW dabao |
| `bs: command not found` | `bash ~/bs-src/termux/setup.sh` dobara chalao |
| Watch chup ho gaya | `bs log` dekho, phir `bs stop && bs watch` |
| Repo me folder nahi mila | Pehle `bs push` chalao, folder khud ban jayega |
