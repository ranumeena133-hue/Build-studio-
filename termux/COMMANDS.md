# SAARE COMMAND — bas copy karo aur chala do

---

## STEP 1 — Pehli baar (sirf ek baar chalana hai)

Termux kholo. Ye teeno line ek-ek karke copy karke chalao:

```bash
pkg install -y git
```

```bash
git clone https://github.com/ranumeena133-hue/Build-studio-.git ~/bs-src
```

```bash
bash ~/bs-src/termux/setup.sh
```

Ab setup tumse sawaal poochhega. Har sawaal par **sirf Enter dabate jao**
(default value pehle se sahi bhari hai), sirf **token** wala sawaal aaye
tab token paste karna.

> Popup aaye "Allow Termux to access files" → **ALLOW** dabana.

---

## STEP 2 — Sabse pehla kaam

```bash
bs pull
```

Ye GitHub se files laakar tumhare phone ke folder me daal dega.

---

## STEP 3 — Background chalu karo (roz ka kaam)

```bash
bs watch
```

Bas. Ab jo bhi file `.BUILD STUDIO/NewProject3` me daaloge, wo apne aap
GitHub par chadh jayegi. Ye ek baar chalao aur bhool jao.

---

# ROZ KAAM AANE WALE COMMAND

Haath se GitHub par chadhana ho:
```bash
bs push
```

GitHub se laana ho:
```bash
bs pull
```

Dono ek saath (pehle laao, phir chadhao):
```bash
bs sync
```

Background chalu karo:
```bash
bs watch
```

Background band karo:
```bash
bs stop
```

Haal-chaal dekho (kya alag hai):
```bash
bs status
```

Background ka log dekho:
```bash
bs log
```

Setting ya token badlo:
```bash
bs config
```

Saare command ki list:
```bash
bs help
```

---

# CHHOTE RASTE (short cut)

Ye bhi wahi kaam karte hain, bas chhote hain:

```bash
bs up
```
`bs push` jaisa hi

```bash
bs st
```
`bs status` jaisa hi

```bash
bs auto
```
`bs watch` jaisa hi

---

# KAAM KI DO-CHAAR AUR CHEEZEIN

Apne folder me kya-kya hai dekho:
```bash
ls -la "/storage/emulated/0/.BUILD STUDIO/NewProject3"
```

Folder ke andar chale jao:
```bash
cd "/storage/emulated/0/.BUILD STUDIO/NewProject3"
```

Kitni files hain ginti karo:
```bash
find "/storage/emulated/0/.BUILD STUDIO/NewProject3" -type f | wc -l
```

Ek test file banakar dekho watch kaam kar raha hai ya nahi:
```bash
echo "test" > "/storage/emulated/0/.BUILD STUDIO/NewProject3/test.txt"
```
(30 second ruko, phir `bs log` chalao — dikhega ki push ho gaya)

Apni setting dekho (token chhupa kar):
```bash
grep -v TOKEN ~/.buildstudio.conf
```

Background chal raha hai ya nahi:
```bash
bs status
```

---

# KUCH ATAK JAYE TO

**`bs: command not found` aa raha hai:**
```bash
bash ~/bs-src/termux/setup.sh
```

**Storage nahi mil raha:**
```bash
termux-setup-storage
```
(popup me ALLOW dabao)

**Token galat / expire ho gaya:**
```bash
bs config
```

**Background chup ho gaya, dobara chalu karo:**
```bash
bs stop
bs watch
```

**Sab kuch naye sire se karna hai:**
```bash
bs stop
rm -rf ~/buildstudio-work ~/.buildstudio.conf
bash ~/bs-src/termux/setup.sh
```

**Script ka naya version lena hai:**
```bash
cd ~/bs-src && git pull && bash termux/setup.sh
```

---

# YAAD RAKHNE WALI 3 BAATEIN

1. **`bs pull` surakshit hai** — tumhari phone wali extra files nahi mitegi. Bina dare chalao.
2. **`bs push` mirror karta hai** — phone se file hatai to GitHub se bhi hategi.
3. **Battery setting zaroor badlo**, warna `bs watch` beech me band ho jayega:
   Phone Settings → Apps → **Termux** → Battery → **Unrestricted**
