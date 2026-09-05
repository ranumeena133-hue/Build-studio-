# Build Studio — Termux सेटअप की पूरी गाइड (A से Z तक)

बिना कोई ऐप बनाए, सिर्फ **Termux** से अपने फ़ोन का फ़ोल्डर और GitHub रिपॉज़िटरी को आपस में जोड़ो।

| | |
|---|---|
| **फ़ोन का फ़ोल्डर** | `/storage/emulated/0/.BUILD STUDIO/NewProject3` |
| **GitHub रिपॉज़िटरी** | `ranumeena133-hue/Build-studio-` |
| **ब्रांच** | `main` |

---

# भाग 1 — सबसे पहले ये समझ लो

तीन जगहें हैं, इन्हें दिमाग़ में बिठा लो:

```
   [ तुम्हारा फ़ोन ]                [ छुपी हुई कॉपी ]              [ GitHub ]
   .BUILD STUDIO/          <-->    ~/buildstudio-work    <-->    Build-studio-
   NewProject3/                    (असली git रिपॉज़िटरी)
```

बीच वाली "छुपी हुई कॉपी" तुम्हें हाथ नहीं लगानी। वो सिर्फ़ काम करने के लिए है।
तुम्हें बस फ़ोन वाले फ़ोल्डर से मतलब रखना है।

काम दो ही हैं:

- **`bs push`** = फ़ोन का सामान GitHub पर चढ़ाना
- **`bs pull`** = GitHub का सामान फ़ोन में उतारना

और एक जादू: **`bs watch`** = ये दोनों काम अपने आप, बैकग्राउंड में।

---

# भाग 2 — Termux इंस्टॉल करो

अगर Termux पहले से है तो ये भाग छोड़ दो।

Termux को **Play Store से मत लो** — वो पुराना है और उसमें ये सब नहीं चलेगा।

1. **F-Droid** से लो (सही तरीका): https://f-droid.org/packages/com.termux/
2. या **GitHub** से सीधा APK: https://github.com/termux/termux-app/releases
   (`termux-app_v0.118.x+github-debug_universal.apk` वाली फ़ाइल डाउनलोड करो)

इंस्टॉल करके Termux खोल लो। एक काली स्क्रीन खुलेगी जिसमें `$` का निशान होगा।
बस उसी में सारे कमांड टाइप करने हैं।

> **कमांड चलाना कैसे है?** कमांड कॉपी करो → Termux की स्क्रीन पर उंगली दबाए रखो →
> **Paste** दबाओ → फिर **Enter** दबाओ। बस।

---

# भाग 3 — पहली बार का सेटअप (सिर्फ़ एक बार)

## कदम 1 — GitHub का टोकन बनाओ

ये सबसे ज़रूरी कदम है। टोकन एक तरह का पासवर्ड है जिससे Termux तुम्हारे GitHub पर
फ़ाइल चढ़ा पाएगा।

1. फ़ोन के ब्राउज़र में GitHub खोलो और लॉगिन करो
2. ऊपर दाएँ अपनी फोटो दबाओ → **Settings**
3. सबसे नीचे तक जाओ → **Developer settings**
4. **Personal access tokens** → **Fine-grained tokens**
5. **Generate new token** दबाओ
6. अब ये चीज़ें भरो:

   | खाना | क्या करना है |
   |---|---|
   | Token name | कुछ भी लिख दो, जैसे `termux-sync` |
   | Expiration | `90 days` या `No expiration` |
   | Repository access | **Only select repositories** चुनो → `Build-studio-` चुनो |
   | Permissions → Repository permissions | नीचे **Contents** ढूँढो → **Read and write** करो |

   > ⚠️ **Contents: Read and write** ज़रूर करना। ये नहीं किया तो `bs push` फेल हो जाएगा।

7. सबसे नीचे **Generate token** दबाओ
8. अब जो लंबा सा कोड दिखेगा (`github_pat_...` से शुरू), उसे **कॉपी कर लो**

   > ⚠️ ये कोड सिर्फ़ **एक ही बार** दिखता है। पेज बंद किया तो दोबारा नहीं मिलेगा,
   > नया बनाना पड़ेगा। इसे किसी नोट ऐप में चिपका कर रख लो अभी।

## कदम 2 — git इंस्टॉल करो

Termux में ये चलाओ:

```bash
pkg install -y git
```

**क्या होगा:** Termux इंटरनेट से `git` डाउनलोड करके लगा देगा। थोड़ी देर लगेगी,
बहुत सारी लाइनें दौड़ेंगी। घबराना मत, ये सामान्य है।

## कदम 3 — स्क्रिप्ट डाउनलोड करो

```bash
git clone https://github.com/ranumeena133-hue/Build-studio-.git ~/bs-src
```

**क्या होगा:** तुम्हारी पूरी रिपॉज़िटरी `~/bs-src` नाम के फ़ोल्डर में उतर जाएगी।
इसी में `bs` वाली स्क्रिप्ट रखी है।

## कदम 4 — सेटअप चलाओ

```bash
bash ~/bs-src/termux/setup.sh
```

**अब क्या-क्या होगा, एक-एक करके:**

### (क) ज़रूरी सामान लगेगा
`git`, `rsync`, `curl` अपने आप इंस्टॉल हो जाएँगे। कुछ नहीं करना, बस देखते रहो।

### (ख) स्टोरेज की इजाज़त माँगेगा
स्क्रीन पर एक पॉपअप आएगा —
*"Allow Termux to access photos, media and files?"*
→ **ALLOW** दबाओ।

> ये नहीं किया तो Termux तुम्हारे `.BUILD STUDIO` फ़ोल्डर तक पहुँच ही नहीं पाएगा।

### (ग) अब सवाल पूछेगा

छह सवाल आएँगे। **हर सवाल के आगे `[ ]` कोष्ठक में सही जवाब पहले से लिखा है।**
सिर्फ़ **Enter** दबाते जाओ — वही जवाब ले लिया जाएगा।

| # | सवाल | पहले से भरा है | तुम्हें क्या करना है |
|---|---|---|---|
| 1 | GitHub username | `ranumeena133-hue` | बस **Enter** |
| 2 | Repository का नाम | `Build-studio-` | बस **Enter** |
| 3 | Branch | `main` | बस **Enter** |
| 4 | फ़ोन का फ़ोल्डर | `/storage/emulated/0/.BUILD STUDIO/NewProject3` | बस **Enter** |
| 5 | Repo के अंदर फ़ोल्डर | `NewProject3` | बस **Enter** |
| 6 | **Token** | कुछ नहीं | **यहाँ टोकन पेस्ट करो** फिर Enter |

> **टोकन दिखेगा नहीं!** जब टोकन पेस्ट करोगे तो स्क्रीन पर कुछ नहीं दिखेगा —
> न अक्षर, न तारे। ये जान-बूझकर है, सुरक्षा के लिए। पेस्ट करके सीधे **Enter** दबा दो।

### (घ) आख़िर में

- तुम्हारा फ़ोन वाला फ़ोल्डर बन जाएगा (अगर नहीं था तो)
- सेटिंग `~/.buildstudio.conf` में सेव हो जाएगी
- GitHub से रिपॉज़िटरी उतर आएगी
- **`bs` कमांड इंस्टॉल हो जाएगी**

आख़िर में हरे रंग में लिखा दिखेगा: **SAB TAIYAAR HAI BHAI**

बस, सेटअप ख़त्म। अब ये दोबारा कभी नहीं करना।

## कदम 5 — बैटरी सेटिंग बदलो (ये ज़रूरी है)

Android बैटरी बचाने के चक्कर में Termux को पीछे से मार देता है। रोकने के लिए:

**फ़ोन Settings → Apps → Termux → Battery → Unrestricted** (या "Don't optimize")

Xiaomi/Redmi वालों को एक और काम करना है:
**Settings → Apps → Termux → Autostart** चालू करो, और
हाल के ऐप्स में Termux पर नीचे खींच कर **ताला 🔒** लगा दो।

> ये नहीं किया तो `bs watch` थोड़ी देर बाद चुपचाप बंद हो जाएगा और तुम्हें पता भी नहीं चलेगा।

---

# भाग 4 — पहला असली इस्तेमाल

```bash
bs pull
```

**क्या होगा:** GitHub से सारी फ़ाइलें उतर कर तुम्हारे फ़ोन के फ़ोल्डर में आ जाएँगी।

स्क्रीन पर ऐसा कुछ दिखेगा:
```
==> PULL shuru - GitHub se phone me
  · Phone folder : /storage/emulated/0/.BUILD STUDIO/NewProject3
  · Files ab     : 4 (pehle 0 thi)
==> PULL ho gaya.
```

अब बैकग्राउंड चालू कर दो:

```bash
bs watch
```

**बस, हो गया।** अब जो भी फ़ाइल `.BUILD STUDIO/NewProject3` में डालोगे या बदलोगे,
वो **30 सेकंड के अंदर** अपने आप GitHub पर चढ़ जाएगी।

**काम करके देखो:**
```bash
echo "test" > "/storage/emulated/0/.BUILD STUDIO/NewProject3/test.txt"
```
30 सेकंड रुको, फिर `bs log` चलाओ — दिखेगा कि पुश हो गया।

---

# भाग 5 — हर कमांड का पूरा ब्यौरा

## `bs pull` — GitHub से फ़ोन में लाओ

```bash
bs pull
```

**अंदर क्या होता है:**
1. GitHub से नया सामान मँगाता है (`git fetch`)
2. छुपी हुई कॉपी को ताज़ा करता है
3. वहाँ से फ़ाइलें तुम्हारे फ़ोन के फ़ोल्डर में कॉपी करता है

**क्या दिखेगा:**
```
==> PULL shuru - GitHub se phone me
  · Phone folder : /storage/emulated/0/.BUILD STUDIO/NewProject3
  · Files ab     : 5 (pehle 3 thi)
==> PULL ho gaya.
```

> 🟢 **ये पूरी तरह सुरक्षित है।** तुम्हारे फ़ोन में जो अपनी अलग फ़ाइलें पड़ी हैं,
> वो **नहीं मिटेंगी**। सिर्फ़ GitHub वाली फ़ाइलें आकर जुड़ जाएँगी या पुरानी पर
> चढ़ जाएँगी। बेधड़क चलाओ।

**कब चलाओ:** जब किसी और जगह से (कंप्यूटर से या GitHub की वेबसाइट से) कुछ बदला हो।

---

## `bs push` — फ़ोन से GitHub पर भेजो

```bash
bs push
```

**अंदर क्या होता है:**
1. देखता है फ़ोन का फ़ोल्डर ख़ाली तो नहीं
2. फ़ोन की सारी फ़ाइलें छुपी कॉपी में डालता है
3. `git add` → `git commit` → `git push` करता है

**क्या दिखेगा:**
```
==> PUSH shuru - phone se GitHub par
  · 3 file badli hain:
     M    NewProject3/a.txt
     A    NewProject3/naya.txt
     D    NewProject3/purani.txt
==> PUSH ho gaya - 3 file GitHub par chadh gayi.
```

अक्षरों का मतलब: **M** = बदली, **A** = नई जुड़ी, **D** = मिटा दी गई

**कुछ नया न हो तो:**
```
  · Kuch naya nahi hai - sab pehle se hi GitHub par hai.
```

> 🔴 **ध्यान दो:** ये **मिरर** करता है। फ़ोन से फ़ाइल मिटाई तो GitHub से भी मिट जाएगी।
> ये जान-बूझकर रखा है ताकि दोनों जगह बिल्कुल एक जैसा रहे।

> 🟢 **बचाव भी है:** अगर फ़ोन का फ़ोल्डर ग़लती से ख़ाली हो गया, तो पुश **रुक जाएगा** —
> ताकि पूरी रिपॉज़िटरी ख़ाली न हो जाए। ये दिखेगा:
> `!! Phone ka folder khaali hai` / `· Kuch nahi bheja`

**छोटा रूप:** `bs up`

---

## `bs sync` — दोनों एक साथ

```bash
bs sync
```

पहले `pull` चलाता है, फिर `push`. यानी पहले GitHub का नया सामान ले आता है,
फिर तुम्हारा नया सामान भेज देता है।

**कब चलाओ:** जब कई दिन बाद खोला हो और पता न हो किधर क्या बदला है।

---

## `bs watch` — बैकग्राउंड में अपने आप ⭐

```bash
bs watch
```

**यही सबसे काम की चीज़ है।**

**अंदर क्या होता है:**
1. फ़ोन को सोने से रोकता है (wakelock)
2. पीछे चुपचाप चलता रहता है
3. **हर 30 सेकंड** में फ़ोन के फ़ोल्डर का "निशान" (fingerprint) बनाता है
4. निशान बदला = कुछ बदला = अपने आप `push` कर देता है

**क्या दिखेगा:**
```
==> Background chalu ho gaya (PID 1634)
  · Har 30 second me phone ka folder check hoga
  · Log dekhne ke liye : bs log
  · Band karne ke liye : bs stop
```

अब **Termux बंद कर सकते हो**, फ़ोन जेब में रख सकते हो। काम चलता रहेगा।

> 💡 **AI से जो `responsey` फ़ाइल मिले**, बस उसे `.BUILD STUDIO/NewProject3` में
> डाल दो — 30 सेकंड में अपने आप GitHub पर पहुँच जाएगी। कुछ टाइप करने की ज़रूरत नहीं।

**पहले से चल रहा हो तो:**
```
!! Background pehle se chal raha hai (PID 1634)
  · Band karna ho to: bs stop
```
दो बार चलाने से कोई नुक़सान नहीं, दूसरा चालू ही नहीं होगा।

**छोटा रूप:** `bs auto`

---

## `bs stop` — बैकग्राउंड बंद करो

```bash
bs stop
```

पीछे चल रहा काम रोक देता है और फ़ोन का wakelock भी हटा देता है।

```
==> Background band kar diya (PID 1634)
```

**कब चलाओ:** जब कुछ दिन इस्तेमाल न करना हो, या जब watch अटक गया लगे
(तब `bs stop` फिर `bs watch`)।

---

## `bs status` — हाल-चाल देखो

```bash
bs status
```

बिना कुछ बदले सिर्फ़ बताता है कि क्या चल रहा है।

**क्या दिखेगा:**
```
===== BUILD STUDIO - HAAL =====

  GitHub    : ranumeena133-hue/Build-studio- (main)
  Repo me   : NewProject3
  Phone me  : /storage/emulated/0/.BUILD STUDIO/NewProject3

  Phone folder : 12 files, 340K
  Background   : chal raha hai (PID 1634)

  Sab barabar hai - kuch bhejne ko nahi.
```

या अगर कुछ भेजना बाक़ी है:
```
  3 file GitHub se alag hai:
     M    NewProject3/a.txt
     A    NewProject3/naya.txt
```

> 🟢 ये सिर्फ़ **दिखाता** है, कुछ बदलता नहीं। बेधड़क जितनी बार चाहो चलाओ।

**छोटा रूप:** `bs st`

---

## `bs log` — लॉग देखो

```bash
bs log
```

आख़िरी 60 लाइनें दिखाता है — हर लाइन पर तारीख़ और समय लिखा होता है।

```
[05-09-2026 14:22:10] PUSH shuru - phone se GitHub par
[05-09-2026 14:22:14]   1 file badli hain:
[05-09-2026 14:22:15] PUSH ho gaya - 1 file GitHub par chadh gayi.
```

**कब चलाओ:** जब जानना हो कि बैकग्राउंड में क्या-क्या हुआ, या कुछ फेल हुआ तो क्यों।

---

## `bs config` — सेटिंग बदलो

```bash
bs config
```

वही छह सवाल दोबारा पूछेगा, पर अब `[ ]` में तुम्हारी **मौजूदा** सेटिंग दिखेगी।
जो नहीं बदलना उस पर बस **Enter** दबा दो।

| सवाल | कब बदलोगे |
|---|---|
| GitHub username | शायद कभी नहीं |
| Repository | दूसरी रिपॉज़िटरी पर जाना हो |
| Branch | दूसरी ब्रांच पर काम करना हो |
| फ़ोन का फ़ोल्डर | कोई और फ़ोल्डर सिंक करना हो |
| Repo के अंदर फ़ोल्डर | रिपॉज़िटरी में दूसरी जगह रखना हो |
| कितने सेकंड में चेक करे | watch तेज़/धीमा करना हो (डिफ़ॉल्ट 30) |
| नया टोकन | टोकन expire हो जाए (ख़ाली छोड़ोगे तो पुराना ही रहेगा) |

**छोटा रूप:** `bs conf`

---

## `bs help` — सारी कमांड की सूची

```bash
bs help
```

सिर्फ़ `bs` लिखने पर भी यही दिखेगा।

---

# भाग 6 — सारी कमांड एक नज़र में

| कमांड | छोटा रूप | क्या करता है | सुरक्षित? |
|---|---|---|---|
| `bs pull` | — | GitHub → फ़ोन | 🟢 हाँ, कुछ नहीं मिटेगा |
| `bs push` | `bs up` | फ़ोन → GitHub | 🔴 मिरर करता है (मिटाना भी) |
| `bs sync` | — | पहले pull, फिर push | 🔴 push वाली बात लागू |
| `bs watch` | `bs auto` | बैकग्राउंड चालू | 🔴 अपने आप push करेगा |
| `bs stop` | — | बैकग्राउंड बंद | 🟢 हाँ |
| `bs status` | `bs st` | हाल दिखाओ | 🟢 हाँ, सिर्फ़ दिखाता है |
| `bs log` | `bs logs` | लॉग दिखाओ | 🟢 हाँ |
| `bs config` | `bs conf` | सेटिंग बदलो | 🟢 हाँ |
| `bs help` | `bs` | सूची दिखाओ | 🟢 हाँ |

---

# भाग 7 — कुछ और काम की कमांड

अपना फ़ोल्डर देखो:
```bash
ls -la "/storage/emulated/0/.BUILD STUDIO/NewProject3"
```

फ़ोल्डर के अंदर चले जाओ:
```bash
cd "/storage/emulated/0/.BUILD STUDIO/NewProject3"
```

कितनी फ़ाइलें हैं गिनो:
```bash
find "/storage/emulated/0/.BUILD STUDIO/NewProject3" -type f | wc -l
```

अपनी सेटिंग देखो (टोकन छुपा कर):
```bash
grep -v TOKEN ~/.buildstudio.conf
```

watch चल रहा है या नहीं:
```bash
bs status
```

स्क्रिप्ट का नया version लो:
```bash
cd ~/bs-src && git pull && bash termux/setup.sh
```

---

# भाग 8 — कुछ अटक जाए तो

### `bs: command not found`
सेटअप पूरा नहीं हुआ था। दोबारा चलाओ:
```bash
bash ~/bs-src/termux/setup.sh
```

### `Clone fail. Token ya repo ka naam galat lag raha hai.`
टोकन ग़लत है या expire हो गया। नया टोकन बनाओ (भाग 3, कदम 1) फिर:
```bash
bs config
```

### `Push fail. Token ki 'Contents: Read and write' permission check karo.`
टोकन तो सही है पर उसमें लिखने की इजाज़त नहीं है।
GitHub पर टोकन की सेटिंग में जाकर **Contents** को **Read and write** करो।

### `Phone ka storage nahi mila`
```bash
termux-setup-storage
```
पॉपअप में **ALLOW** दबाओ।

### `GitHub se baat nahi ho payi (net check karo)`
इंटरनेट बंद है या कमज़ोर है। WiFi/डेटा देखो और दोबारा चलाओ।

### `Repo me 'NewProject3' naam ka folder abhi hai hi nahi`
रिपॉज़िटरी में वो फ़ोल्डर अभी बना ही नहीं। एक बार पुश कर दो, ख़ुद बन जाएगा:
```bash
bs push
```

### watch चुपचाप बंद हो गया
Android ने बैटरी बचाने के लिए मार दिया होगा।
1. भाग 3 का कदम 5 (बैटरी सेटिंग) करो
2. फिर:
```bash
bs stop
bs watch
```

### सब कुछ नए सिरे से करना है
```bash
bs stop
rm -rf ~/buildstudio-work ~/.buildstudio.conf
bash ~/bs-src/termux/setup.sh
```
> फ़ोन के फ़ोल्डर को कुछ नहीं होगा, सिर्फ़ सेटिंग और छुपी कॉपी मिटेगी।

---

# भाग 9 — याद रखने वाली बातें

1. **`bs pull` बेधड़क चलाओ** — तुम्हारी फ़ोन वाली अपनी फ़ाइलें कभी नहीं मिटेंगी।

2. **`bs push` मिरर करता है** — फ़ोन से मिटाई तो GitHub से भी मिटेगी। सोच कर मिटाना।

3. **ख़ाली फ़ोल्डर का बचाव है** — फ़ोन का फ़ोल्डर ख़ाली हो तो पुश रुक जाएगा,
   पूरी रिपॉज़िटरी ख़ाली नहीं होगी।

4. **टोकन सुरक्षित रखा है** — `~/.buildstudio.conf` में `chmod 600` के साथ,
   यानी सिर्फ़ तुम पढ़ सकते हो। उसे कभी GitHub पर कमिट मत करना।

5. **बैटरी सेटिंग ज़रूर बदलो** — वरना `bs watch` बीच में बंद होता रहेगा।

6. **रोज़ का तरीक़ा:** बस `bs watch` एक बार चला दो और भूल जाओ।
   फ़ाइल फ़ोल्डर में डालो, बाक़ी अपने आप।

---

# भाग 10 — सिर्फ़ कमांड चाहिए तो

पूरी कॉपी-पेस्ट वाली छोटी सूची अलग फ़ाइल में है: **[COMMANDS.md](COMMANDS.md)**

**बहुत जल्दी में हो? बस ये चार लाइनें:**

```bash
pkg install -y git
git clone https://github.com/ranumeena133-hue/Build-studio-.git ~/bs-src
bash ~/bs-src/termux/setup.sh
bs pull && bs watch
```
