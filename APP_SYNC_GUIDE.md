# GitHub Folder Sync App — पूरा विकास गाइड (AI के लिए)

> यह फ़ाइल **किसी भी AI को पूरी दे दो** — यह AI को इस ऐप का पूरा कोड लिखने का
> सटीक, चरण-बद्ध, और पूर्ण निर्देश देती है। इस फ़ाइल में जो भी लिखा है उसे AI को
> **शब्द-शब्द, बिना बदले** पालन करना है। कोई भी requirement छोड़नी नहीं है।
>
> भाषा नोट: यह गाइड हिंदी (Devanagari) में है। **सारे code, file-name, function-name,
> API-endpoint अंग्रेज़ी में ही होंगे**। हिंदी सिर्फ़ निर्देश समझाने के लिए है।

---

## भाग 0 — इस गाइड को पढ़ने वाले AI के लिए शुरुआती काम

जब तुम (AI) यह फ़ाइल पढ़ो, तो **कोड लिखना शुरू करने से पहले** इंसान से ये ज़रूरी
सवाल पूछो (हर सवाल का जवाब लो, फिर ही आगे बढ़ो):

1. **ऐप का नाम** (App Display Name) क्या रखना है?
   उदाहरण: `GitSync`, `Folder Sync`, `Build Studio`.
2. **Package name** क्या रखना है? (नियम: छोटे अक्षर, बीच में `.`, जैसे
   `com.tumharaNaam.gitsync`)। अगर इंसान नहीं बताए तो `com.buildstudio.sync` मत
   रखना — नया, टकराव-रहित बनाओ और इंसान से पूछो।
3. इंसान **किस editor/वातावरण** में build करेगा? (Android Studio / AIDE / Termux).
   — इससे बताना होगा कि file-path और gradle सेटअप कैसे रखना है। यह गाइड मानता है
   कि **कोई भी तीसरा library/gradle dependency इस्तेमाल नहीं होगा**।
4. **Minimum Android version** कितना चाहिए? (पूछो; अगर पता नहीं तो `minSdk 24`
   मान लो।)
5. हर कितने समय में auto-sync चले? (पूछो; default 5 मिनट।)
6. क्या पहली बार जोड़ते समय **पूरे local फ़ोल्डर को GitHub पर भेजना** है या सिर्फ़
   नई/बदली हुई फ़ाइलें? (नीचे §9 का डिफ़ॉल्ट नियम समझाओ और पूछो।)

> जवाब आने के बाद ही कोड लिखना शुरू करो। नीचे की सारी spec में `{{APP_NAME}}`,
> `{{PACKAGE}}`, `{{MIN_SDK}}` की जगह इन जवाबों की value डाल दो।

---

## भाग 1 — ऐप क्या करता है (Goal)

यह एक Android ऐप है जो **किसी भी library का इस्तेमाल नहीं करती**। इसका पूरा काम:

- इंसान अपना **GitHub account** (Personal Access Token से) जोड़ता है, एक
  **repository** और उसकी **branch** चुनता है।
- इंसान अपने **फ़ोन की storage से कोई फ़ोल्डर** चुनता है (System के folder-picker से)।
- फिर यह ऐप उस फ़ोल्डर और GitHub repo के बीच **दो-तरफ़ा (two-way) sync** करता है:

  1. **फ़ोल्डर → GitHub (Push):** फ़ोल्डर में जो भी फ़ाइल/फ़ोल्डर हैं, नई बनी
     हो या बदली हो, वे GitHub repo में **सही जगह** (सही path/subfolder) पर पहुँच
     जाती हैं। जो फ़ाइल इंसान ने local में delete की, वह GitHub से भी delete हो
     जाती है।
  2. **GitHub → फ़ोल्डर (Pull):** अगर कोई दूसरा (जैसे कोई AI, या GitHub website पर)
     GitHub repo में कोई फ़ाइल **update** करे, **नई फ़ाइल बनाए**, या कोई **फ़ाइल
     delete** करे, तो वह बदलाव local फ़ोल्डर में **उसी सही जगह** पर आ जाता है
     (सही sub-folder खुद बन जाते हैं)।

- सब कुछ **atomic** हो — मतलब कोई भी फ़ाइल आधी नहीं लिखी जाएगी, आधी नहीं भेजी
  जाएगी। या तो पूरा काम होगा या पहले जैसा ही रहेगा (भाग 8 देखो)।
- सब कुछ **error-free** — कोई crash नहीं, token बिना पूछे लीक नहीं होता, sync में
  आधी फ़ाइल नहीं बिगड़ती।

**कौन-सा source of truth (किसकी बात माननी है)?** — नीचे भाग 9 में पूरा नियम लिखा
है। ध्यान रखो: यह **binary merge नहीं** कर सकती (क्योंकि कोई library नहीं)। अगर एक
ही फ़ाइल **दोनों तरफ़** बदल गई हो (conflict), तो नीचे दिए गए नियम से निपटो।

---

## भाग 2 — तकनीकी ज़रूरतें और मनाही (Do's & Don'ts)

### अनुमति (ALLOWED — सिर्फ़ यही) — ये सब Android में पहले से होते हैं, कोई library नहीं:
- `java.*` / `javax.*` (JDK क्लासेस)
- `android.*` framework क्लासेस
- `org.json` (JSONObject, JSONArray — Android में बिल्ट-इन है)
- `android.util.Base64` (base64 encode/decode के लिए, बिल्ट-इन)
- `java.security.MessageDigest` (SHA-1 hash)
- `java.net.HttpURLConnection` (नेटवर्क के लिए — Retrofit/OkHttp नहीं)
- `android.os.FileObserver`, `android.content.*`, `android.app.Service`,
  `android.app.Notification` आदि — सब framework के हैं।

### मनाही (NOT ALLOWED — कतई नहीं):
- ❌ कोई external Gradle dependency — न JGit, न OkHttp, न Retrofit, न Gson,
  न AndroidX/Jetpack libraries (jQuery, Volley सब बंद)।
- ❌ कोई NDK / native code।
- ❌ कोई paid API / key।

> अगर AI कोई library जोड़ना चाहे, तो **मना कर दो**। इस ऐप को बिना library चलाना
> ही पूरी चुनौती और पूरा मकसद है।

### नेटवर्क करने की बुनियादी विधि (हर request में):
- सब `HttpURLConnection` से, **background thread** पर (मुख्य/UI thread पर कभी
  नेटवर्क मत करो)।
- हर request में header डालो:
  - `Authorization: Bearer <TOKEN>` (या `token <TOKEN>` — fine-grained के लिए
    Bearer ठीक है)
  - `Accept: application/vnd.github+json`
  - `Content-Type: application/json` (जहाँ body है)
- यूनिक `User-Agent` हेडर डालना ज़रूरी है (GitHub बिना इसके 403 देता है)।
- Response code जाँचो: `2xx` = ठीक, `401` = token गलत, `403` = permission/rate-limit,
  `404` = नहीं मिला, `409/422` = conflict/stale (नीचे retry विधि)। Body का JSON
  `org.json` से पढ़ो। `error`/`message` फ़ील्ड user को दिखाओ।
- कोई भी network exception आए तो crash मत करो — catch करके log + दोबारा कोशिश।

---

## भाग 3 — प्रोजेक्ट फ़ाइलों की सूची (AI को ये सब बनाने हैं)

सारा कोड `{{PACKAGE}}` package में। उदाहरण के लिए package `com.gitsync.app` मान
लो, तो structure:

```
app/src/main/AndroidManifest.xml
app/src/main/java/{{PACKAGE}}/
    AppConfig.java            // ऐप-भर की constants (clientId आदि)
    SettingsStore.java        // SharedPreferences wrapper (token/username/repo/branch/path/state)
    BlobSha.java              // Git blob SHA-1 hash बनाने का काम
    LocalScanner.java         // फ़ोल्डर घूमकर local files की सूची + hash निकालना
    GitApi.java               // GitHub REST API के सारे calls (HttpURLConnection)
    DiffEngine.java           // local vs remote की तुलना, changes निकालना
    PushEngine.java           // local → GitHub एक atomic commit में भेजना
    PullEngine.java           // GitHub → local atomic write में उतारना
    SyncManager.java          // पूरी sync का orchestration + state save
    SyncService.java          // foreground service, auto-sync loop + FileObserver
    MainActivity.java         // मुख्य स्क्रीन (config + status + buttons)
    FolderPicker... (MainActivity में ही ACTION_OPEN_DOCUMENT_TREE से)
app/src/main/res/layout/
    activity_main.xml
    dialog_config.xml          // token/repo/branch भरने की dialog/activity
    item_file.xml              // log/sync-result list की एक row
app/src/main/res/values/
    strings.xml                // सारे user-visible शब्द (हिंदी default)
    colors.xml
    styles.xml                 // theme (Material नहीं, बेसिक Theme)
    dimens.xml (optional)
app/src/main/res/drawable/     // buttons/icon आदि (सरल vector/shape)
```

AI को **हर file का पूरा, compile-होने वाला कोड** देना है। नीचे हर class की ज़िम्मेदारी
और हर method का algorithm है। AI नीचे की विधि का पालन करके पूरा कोड लिखे।

> Manifest और resources में **किसी भी library/namespace** (`androidx.*`) का नाम नहीं
> आना चाहिए। Theme बेसिक `android:Theme.Material.Light` या custom हो।

---

## भाग 4 — AndroidManifest.xml

- `<uses-permission android:name="android.permission.INTERNET" />`
- Android 13+ के लिए
  `<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />`
  (runtime में भी माँगनी पड़ेगी — Android 13+ पर।)
- `<application>` में:
  - `android:label="{{APP_NAME}}"`
  - MainActivity को `LAUNCHER` activity बनाओ।
  - SyncService को `<service android:name=".SyncService" .../>` घोषित करो।
- Service `foregroundServiceType` (Android 14+) के लिए `dataSync` रखो, और
  `FOREGROUND_SERVICE` + `FOREGROUND_SERVICE_DATA_SYNC` permissions भी डालो।
- **Storage permission (READ/WRITE_EXTERNAL_STORAGE) की ज़रूरत नहीं** — फ़ोल्डर
  selection SAF (`ACTION_OPEN_DOCUMENT_TREE`) से होगा (भाग 6 देखो)। यही safest है।

---

## भाग 5 — सेटिंग्स कहाँ रखें (SettingsStore)

`SharedPreferences` में (file name `sync_cfg`) ये save करो:
- `username` (String) — repo का मालिक (owner)
- `repo` (String)
- `branch` (String) — default `main`
- `token` (String) — Personal Access Token
- `treeUri` (String) — चुने हुए फ़ोल्डर का `content://` Uri (SAF से)
- `autoSyncMinutes` (int, default 5)
- `lastSyncEpoch` (long)
- `syncMode`: `"two_way"` (डिफ़ॉल्ट) | `"push_only"` | `"pull_only"`
- और नीचे भाग 9 की **baseline/state** (अलग JSON file में, नीचे देखो)

> ⚠️ **सुरक्षा:** token को **कभी log मत करो**, कभी screen पर पूरा मत दिखाओ
> (dots में दिखाओ)। UI में एक "Show/Hide" हो सकता है पर default छिपा रहे।

---

## भाग 6 — फ़ोल्डर चुनना (SAF — Storage Access Framework)

कोई permission नहीं चाहिए, सिर्फ़ system picker:

```
Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
startActivityForResult(i, REQ_TREE);
```

`onActivityResult` में `data.getData()` से `treeUri` मिलेगा। `SettingsStore` में
`treeUri.toString()` save करो। अगर ऐप फिर खुलने पर चुना फ़ोल्डर न मिले
(SecurityException / FileNotFoundException) तो user को दोबारा चुनने को कहो और
`takePersistableUriPermission` मत भूलना:

```
getContentResolver().takePersistableUriPermission(uri,
        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
```

**फ़ोल्डर से files पढ़ना/लिखना SAF के ज़रिये ही:** `DocumentsContract` +
`ContentResolver` + `DocumentFile` क्लास से (सब framework में हैं, यह library नहीं):

- Root के लिए `DocumentFile.fromTreeUri(ctx, treeUri)`।
- `dir.listFiles()` से बच्चे, `f.isDirectory()`/`f.isFile()`, `f.getName()`,
  `f.getUri()`।
- File पढ़ना: `contentResolver.openInputStream(f.getUri())`।
- File लिखना: `contentResolver.openOutputStream(uri, "w")` — लेकिन atomic लिखने
  के लिए नीचे भाग 8 का तरीका अपनाओ।
- नया फ़ोल्डर बनाना: `parent.createDirectory(name)`।
- नई फ़ाइल बनाना: `parent.createFile("application/octet-stream", name)`।
- Delete: `DocumentFile.delete()` (यह भी atomic है)।

> **documentId / path बनाना:** किसी `DocumentFile` का repo-relative path निकालने
> के लिए `DocumentsContract.getDocumentId(uri)` के बाद path के ज़रिये **recursive
> walk** करो, या अपने LocalScanner में नीचे जाओ और हर file के सापेक्ष path
> (relative to root) खुद track करो। (SAF के तहत documentId कभी-कभी flatten होता
> है, इसलिए अपने walk से ही relative path रखना भरोसेमंद है।)

---

## भाग 7 — "एक फ़ाइल की पहचान" कैसे करें (Git blob SHA-1)

किसी फ़ाइल का असली बदलाव जानने के लिए तुम्हें सिर्फ़ उसके **content का hash**
चाहिए। GitHub जो hash इस्तेमाल करता है वही तुम local में बना सकते हो — इससे दोनों
तरफ़ की तुलना सटीक होती है, बिना किसी library के।

**Git blob SHA-1 का फ़ॉर्मूला** (हर file के लिए):

```
sha1(  "blob " + fileSizeInBytes + "\0" + fileContentBytes  )
```

यानी:
1. फ़ाइल की सारी bytes पढ़ो (length = N)।
2. एक नया SHA-1 `MessageDigest` लो।
3. पहले ASCII में string `"blob "` update करो, फिर ASCII में `N` (decimal) update
   करो, फिर एक null byte `0x00` update करो।
4. फिर पूरी file bytes update करो।
5. digest को hex string में बदलो (40 छोटे hex अक्षर)।

`BlobSha.java` में `static String ofFile(byte[] data)` और
`static String ofStream(InputStream in)` दोनों रखो। **यही hash GitHub के `sha` से
मेल खाना चाहिए** — तुलना इसी पर आधारित होगी।

> नोट: content ज़रूर binary-safe पढ़ो (सिर्फ़ text मत समझो)। इमेज/PDF भी sync होगी।

---

## भाग 8 — Atomic (पूरी-या-कुछ-नहीं) लिखना और भेजना

Atomic का मतलब: किसी भी वक़्त **फ़ाइल कभी आधी नहीं** होगी। अगर बीच में कुछ
फेल हो तो पहले जैसी ही रहे।

### 8.1 Local में file atomic उतारना (Pull)
SAF के ज़रिये तुम सीधे `openOutputStream` लिख सकते हो, लेकिन उससे आधी-लिखी फ़ाइल का
ख़तरा रहता है। इसलिए:

- नई लिखने से पहले पूरी content को पहले **memory buffer** में ले आओ (GitHub API
  base64 content देती है — नीचे)। 
- पहले content को एक **temporary file/uri** पर लिखो (जैसे उसी फ़ोल्डर में
  `.tmp_<random>`), पूरी तरह flush+close करो।
- फिर असली file पर **atomic replace** करो। SAF में atomic rename सीधे नहीं मिलता,
  इसलिए safe तरीका:
  1. नई content को असली `DocumentFile` में लिखने से पहले उसका पुराना content
     रखने के लिए backup बनाओ (या नई content को पहले temp uri पर पूरी लिखो),
  2. फिर असली uri में एक बार में (full buffer) लिखो और flush करो।
  3. अगर बीच में error आए तो backup से वापस लाओ / temp file delete कर दो, ताकि
     फ़ाइल आधी न रहे।
- वास्तव में आसान और भरोसेमंद तरीका: **हर file को नए content से तभी बदलो जब**
  (a) नई content **पूरी** buffer में तैयार हो, (b) `openOutputStream(uri,"wt")` से
  ट्रंकेट करके एक साथ पूरी लिखो और flush करो। बड़ी फ़ाइलों के लिए तुम `"w"` मोड में
  लिख सकते हो। — अगर यह process crash हो जाए तो आख़िरी बार लिखी गई ठीक होगी।
- सभी file operations **एक ही background worker** पर क्रम से करो (भाग 10) ताकि
  दो धागे एक ही फ़ाइल न छेड़ें।

### 8.2 GitHub पर atomic भेजना (Push)
GitHub पर कई फ़ाइलें बदलने का **सही atomic तरीका Git Data API** है — पूरा बदलाव
**एक ही commit** में। ऐसा कि बीच-बीच की हालत कभी दिखे ही नहीं:

1. सारे नए/बदले हुए contents के **blob** बनाओ (अलग-अलग POST)।
2. एक नया **tree** बनाओ जिसमें सारे entries हों (base_tree = पुराना tree)।
3. उस tree पर एक **commit** बनाओ (parent = current commit)।
4. फिर उस commit पर **branch ref update** करो।
   - यह एक ही atomic step है: ref या तो पूरा update होगा या नहीं।
   - अगर `409/422` (stale — बीच में किसी और ने push किया) आए तो नीचे भाग 9.6 की
     retry विधि से पूरी बात refresh करके दोबारा कोशिश करो (कभी force मत करो)।

### 8.3 पूरे sync-run का atomic होना
दो-तरफ़ा sync में local और remote अलग-अलग "systems" हैं, इसलिए दोनों एक साथ atomic
नहीं हो सकते। यहाँ atomic का मतलब है:
- **हर फ़ाइल-level operation atomic है** (ऊपर 8.1/8.2)।
- **State (baseline) सिर्फ़ तभी update होती है जब उस run के सारे local writes और
  remote commit सफल रहे।** अगर बीच में कोई फेल हुआ, तो state पुरानी रहे और अगले
  run में फिर से सही हो जाएगा (नीचे भाग 9 का rules देखो — वे naturally
  idempotent हैं)।

---

## भाग 9 — Sync का पूरा algorithm (DiffEngine + Push/Pull)

### 9.1 दो "snapshot" बनाओ
**Remote snapshot** — एक निश्चित commit पर:
- `GET /repos/{owner}/{repo}` → `default_branch` (अगर branch नहीं दिया)।
- `GET /repos/{owner}/{repo}/git/ref/heads/{branch}` → `object.sha` (commit sha C)।
- `GET /repos/{owner}/{repo}/commits/{C}` → `commit.tree.sha` (tree sha T)।
- `GET /repos/{owner}/{repo}/git/trees/{T}?recursive=1` → `tree[]`, हर entry का
  `path`, `type` ("blob"/"tree"), `mode`, `sha`। `truncated` flag जाँचो —
  अगर `true` हुआ तो इस run में push मत करो, बस user को बताओ (बहुत बड़े repo के
  लिए)। नतीजा: एक **map `remotePaths` = { path → sha }** (सिर्फ़ `type=="blob"`)।
- इस तरह **एक ही snapshot** पकड़ो — उसे बाद में compare के लिए रखो।

**Local snapshot**:
- चुने गए root `DocumentFile` से पूरा फ़ोल्डर walk करो।
- हर file का **relative path** (`a/b/c.txt`) और `BlobSha.ofFile(...)` hash निकालो।
- बड़ी फ़ाइलों के लिए पूरा पढ़ना भारी हो सकता है; फिर भी hash लेना ही पड़ेगा।
- नतीजा: map **`localPaths` = { path → blobSha }**। खाली फ़ोल्डर remote में नहीं
  जाते (Git फ़ोल्डर-track नहीं करता), यही सामान्य है।

**Baseline (पिछली सफल sync की हालत)** `localPaths` जैसी ही map है, पर सिर्फ़ वह
चीज़ जो पिछली बार दोनों तरफ़ **matching** थी। इसे **अलग से internal storage**
(`context.getFilesDir()/baseline.json`) में रखो (repo फ़ोल्डर के अंदर नहीं!):
```json
{ "commit": "C_last", "tree": "T_last",
  "files": { "a.txt": "sha1", "sub/b.png": "sha2" } }
```
Baseline मतलब: **वह सटीक हालत जिस पर local और remote दोनों राज़ी थे**। यही
conflict तय करने की कुंजी है।

### 9.2 हर path की तुलना (3 तरफ़ से)
हर path के लिए तीन मान:
- `L` = local hash (अगर मौजूद नहीं तो "ABSENT")
- `R` = remote sha (अगर नहीं तो "ABSENT")
- `B` = baseline hash (अगर baseline में नहीं तो "ABSENT")

तुलना के नियम:

| स्थिति | अर्थ | कार्य |
|---|---|---|
| L==R | दोनों एक जैसे | कुछ मत करो |
| R==B और L≠B | सिर्फ़ local बदला | **Push** (local को remote भेजो) |
| L==B और R≠B | सिर्फ़ remote बदला | **Pull** (remote को local लाओ) |
| L≠B और R≠B और L≠R | दोनों बदले (conflict) | **Conflict** — नीचे 9.5 |
| L मौजूद, R/B नहीं | local में नई फ़ाइल | **Push** (नई बनाओ) |
| R मौजूद, L/B नहीं | remote में नई फ़ाइल | **Pull** (local बनाओ) |
| B मौजूद, L नहीं, R मौजूद | local में delete हुई | **Push-delete** (remote से delete) |
| B मौजूद, R नहीं, L मौजूद | remote में delete हुई | **Pull-delete** (local delete) |
| B मौजूद, L और R दोनों नहीं | दोनों तरफ़ delete | सिर्फ़ baseline से हटाओ |
| L और R दोनों नए (B में नहीं) | दोनों तरफ़ नई | **Conflict** (कौन सही? → 9.5) |

इन्हें चार सूचियों में बाँटो:
`pushWrites[]` (नई/update), `pushDeletes[]`,
`pullWrites[]` (नई/update), `pullDeletes[]`, और `conflicts[]`।

> **पहली बार जब baseline खाली हो** (नया user): तुम्हें "पहली बार क्या होगा" तय
> करना है। डिफ़ॉल्ट नियम (§ नीचे): **local फ़ोल्डर पूरी तरह remote बन जाए** —
> यानी local की हर फ़ाइल push हो, और remote में जो फ़ाइल local में नहीं है वह भी
> pull होकर local में आ जाए, ताकि दोनों मिल जाएँ। पर अगर **एक ही path दोनों में
> अलग content** के साथ है और baseline खाली है, तो उसे **Conflict** मानो (क्योंकि
> पता नहीं कौन सही है) और user को पूछो। — इंसान से भाग 0 के सवाल 6 में यही तय
> करवाओ।

### 9.3 PushEngine (local → GitHub) — एक atomic commit
सिर्फ़ `pushWrites[]` और `pushDeletes[]` भेजो (conflicts नहीं):
1. Current commit C और tree T fetch करो (ऊपर 9.1 जैसा)।
2. **हर write-fाइल के लिए**: content base64 में, फिर
   `POST /repos/{owner}/{repo}/git/blobs` body:
   ```json
   { "content": "<base64>", "encoding": "base64" }
   ```
   → जवाब में `sha`। इसे save करो।
   (अगर फ़ाइल बहुत बड़ी हो और base64 GitHub की limit (~100MB) से ज़्यादा हो तो
   उसे छोड़ दो और error log करो — user को बताओ।)
3. एक tree entry-list बनाओ:
   - हर write के लिए: `{ "path": relPath, "mode": "100644", "type": "blob", "sha": "<blobSha>" }`
   - हर delete के लिए: `{ "path": relPath, "sha": null }`
   - कुल पहले वाले base tree में सब बदलाव।
4. `POST /repos/{owner}/{repo}/git/trees` body:
   ```json
   { "base_tree": "<T>", "tree": [ ...entries ] }
   ```
   → नया tree `T2`।
5. `POST /repos/{owner}/{repo}/git/commits` body:
   ```json
   { "message": "Sync from {{APP_NAME}}: <n> file(s)", "tree": "<T2>", "parents": ["<C>"] }
   ```
   → नया commit `C2`।
6. `PATCH /repos/{owner}/{repo}/git/refs/heads/{branch}` body:
   ```json
   { "sha": "<C2>", "force": false }
   ```
   - `200` → सफल, इस commit का tree/files नई baseline।
   - `409` / `422` (stale) → **पूरा run फिर से शुरू** (refresh करके)। कभी force=true
     मत भेजो। 3-5 बार कोशिश करो, फिर error।
7. सफल होने पर नई remote snapshot (tree C2/T2 और उसकी file→sha map) वापस दे दो।

> इस विधि से कई फ़ाइलों का बदलाव **एक ही atomic commit** में जाता है। कुछ भी फेल
> हो तो GitHub पर कोई आधा commit नहीं रहता।

### 9.4 PullEngine (GitHub → local) — atomic local writes
सिर्फ़ `pullWrites[]` और `pullDeletes[]` लाओ:
1. हर `pullWrites` file के लिए:
   `GET /repos/{owner}/{repo}/contents/{path}` (path को `URLEncoder` से percent-encode
   करो, `/` सुरक्षित छोड़ो)। जवाब:
   ```json
   { "content": "<base64 (newline वाली)>", "encoding": "base64", "size": <int> }
   ```
   base64 को clean करो (newlines हटाओ) और `android.util.Base64.decode` करो।
   Size मिलाओ (अगर decode हुई bytes की length != size तो error — फ़ाइल आधी मत
   लिखो)।
   → **atomic write** (भाग 8.1): पहले ज़रूरी parent folders बनाओ
   (`DocumentFile.createDirectory` recursively), फिर file content लिखो।
2. हर `pullDeletes` file के लिए: उसका `DocumentFile` ढूँढो और `.delete()` करो
   (अगर मौजूद हो)।
3. नई local map बनाओ (जो अब remote से मेल खाती है) और baseline के लिए लौटाओ।

### 9.5 Conflicts (टकराव) — बिना library binary-merge नहीं होता
Conflict का नियम (इंसान से भाग 0/सवाल में भी पूछा जाएगा), डिफ़ॉल्ट:
- **Conflict पर auto कुछ मत बदलो** — न local overwrite, न remote overwrite।
- दोनों version सुरक्षित रखो ताकि कुछ न छूटे:
  - local वाली फ़ाइल वहीं रहती है।
  - remote वाले नए content को उसी फ़ोल्डर में अलग नाम से save करो:
    `filename.CONFLICT.remote` (sub-folder के अंदर सही जगह)।
  - दोनों में मौजूद मूल फ़ाइल (local copy) छूती नहीं।
- Conflict को **log/list में दिखाओ** और status screen पर दिखाओ ताकि इंसान खुद तय
  करे (कौन सा रखना है — आगे के version के लिए बटन हो सकते हैं; minimum में सिर्फ़
  list dikhao)।
- Conflict वाले path को **baseline में मत बदलो** (वहाँ पुरानी B रहेगी) ताकि हर
  sync उसे फिर से conflict दिखाए और इंसान के फ़ैसले तक न छूटे।

> **syncMode** अगर user ने `push_only` किया हो तो pull steps स्किप करो; `pull_only`
> हो तो push steps स्किप करो। दो-तरफ़ा में दोनों। Conflicts सिर्फ़ `two_way` में
> देखे जाते हैं।

### 9.6 सामान्य "safe retry" विधि (idempotency)
पूरा design ऐसा रखो कि दोबारा चलाने पर कुछ ख़राब न हो (idempotent):
- Local write फिर से उसी content से करना → कोई फ़र्क नहीं (क्योंकि hash बदलता
  नहीं)।
- Push: अगर एक commit सफल हो गया पर जवाब न मिला, तो अगले run में compare से
  पता चलेगा कि remote पहले ही मैच कर रहा है → कुछ नहीं करना।
- Ref update stale (409/422) पर: refresh + full re-compare + retry (भाग 9.3.6)।
- Network exception पर: बीच का काम छोड़कर अगली बार फिर कोशिश; state सिर्फ़ तब
  save हो जब उस category के सारे काम सफल हों।

### 9.7 Sync-run का क्रम (SyncManager.runSync)
```
1. settings से सब पढ़ो (token/username/repo/branch/treeUri/mode)। अगर अधूरा → रुक जाओ, "configure first"।
2. validate+connect (GitApi.getRepo) — 401 पर साफ़ error।
3. remoteSnapshot लो (9.1)। अगर fetch फेल → return error, कुछ मत छुओ।
4. localSnapshot लो (9.1)।
5. baseline लो (internal JSON)।
6. DiffEngine.compare(...) → चार lists + conflicts (9.2)।
7. mode के हिसाब से:
   - अगर push काम है और mode पुश करता है:
        result = PushEngine.run(pushWrites, pushDeletes)   // atomic commit
        success → नई remote snapshot मिली; इसे अब "remote" मानो।
        fail → यहाँ रुको, error दो (pull मत करो, क्योंकि remote बदल चुका/अज्ञात)।
   - अगर pull काम है और mode पुल करता है:
        PullEngine.run(pullWrites, pullDeletes)            // atomic local
   - conflicts → 9.5 रखो (log + list)।
8. सफल होने पर **नई baseline** बनाओ:
   नई baseline.files = हर उस path का नया hash जो अब local और remote दोनों में
   एक जैसा है (i.e. जिन्हें push/pull किया गया और वे अब match), प्लस जो पहले से
   match थे। Conflict वाले path baseline से मत छुओ।
   → internal JSON में atomic write (temp + rename)।
9. lastSyncEpoch update, log update करो, UI को status भेजो।
```

---

## भाग 10 — threading और service (कभी दो धागे एक साथ नहीं)

- एक ही **`SyncService`** (foreground service) में एक ही worker logic।
- पूरा sync एक **एकल executor / HandlerThread** पर क्रम से चलता है
  (`ExecutorService singleThreadExecutor`), ताकि **एक समय में सिर्फ़ एक sync-run**
  हो। अगर run चल रहा हो और दोबारा शुरू करने को कहा जाए तो पुराने run को न रोककर
  उसके ख़त्म होने पर flag लगाओ कि "फिर चलाओ" (request coalescing)।
- **Auto-sync timer:** Service में एक `Handler` + सोया हुआ
  `alarm`/`Handler.postDelayed` हर `autoSyncMinutes` पर `runSync` बुलाए। (जब तक
  app/service ज़िंदा है। Screen बंद भी हो तो foreground service रहती है।)
- **FileObserver:** root folder पर `FileObserver` (framework) लगाओ; जब कोई local
  file बदले/create/delete हो तो short delay (2s) के बाद sync trigger करो। जब हम
  खुद pull से लिखें तो उसे ignore करने के लिए एक flag रखो (नहीं तो infinite loop
  बनेगा) — नीचे 10.1।
- हर बार network/write **UI thread पर मत करो** — सब background executor पर।
- UI को update करना `runOnUiThread` या `Handler(Looper.getMainLooper())` से।

### 10.1 Infinite-loop से बचाव (सबसे ज़रूरी!)
- जब PullEngine local में लिखता है तो FileObserver भड़कता है → दोबारा sync →
  push → फिर... हमेशा का loop। रोकने का तरीका:
  - PullEngine की सारी writes के दौरान `isApplyingRemote = true` flag set करो।
  - FileObserver callback में, अगर `isApplyingRemote` true हो तो event को ignore
    करो।
  - इसके अलावा, **compare हमेशा hash पर होता है** — अगर pull के बाद local hash
    remote जैसा है, तो अगला sync "कुछ बदला ही नहीं" कहेगा (L==R) और चुप रहेगा।
    यह hash-based compare ही असली loop-breaker है। इसलिए ऊपर का algorithm सही रखो।
- Push के बाद भी अगले sync में L और R match करते हैं → loop नहीं बनता।

---

## भाग 11 — GitApi.java — सारे REST endpoints (एक ही जगह)

हर method `HttpURLConnection` से। एक helper:
```java
JSONObject request(String method, String path, JSONObject body /*या null*/)
```
जो `https://api.github.com` + path पर जाता है, headers डालता है, body भेजता है,
status चेक करता है, जवाब JSON लौटाता है। Errors में GitHub का `message` निकालकर
फेंकता है।

कौन-से calls चाहिए (सब Git Data / Contents API — v3):

| काम | Method | Path |
|---|---|---|
| repo जानकारी | GET | `/repos/{owner}/{repo}` |
| branch ref का sha | GET | `/repos/{owner}/{repo}/git/ref/heads/{branch}` |
| commit की जानकारी | GET | `/repos/{owner}/{repo}/commits/{sha}` |
| पूरा tree (recursive) | GET | `/repos/{owner}/{repo}/git/trees/{sha}?recursive=1` |
| blob बनाना | POST | `/repos/{owner}/{repo}/git/blobs` |
| tree बनाना | POST | `/repos/{owner}/{repo}/git/trees` |
| commit बनाना | POST | `/repos/{owner}/{repo}/git/commits` |
| ref update | PATCH | `/repos/{owner}/{repo}/git/refs/heads/{branch}` |
| file content लाना | GET | `/repos/{owner}/{repo}/contents/{path}` |

नोट:
- Contents API `GET .../contents/{path}` **नई फ़ाइल (कभी file हो) में** base64 देती
  है — इसी से Pull में content मिलता है। जो path folder है उसके लिए contents list
  देता है — हमें चाहिए नहीं; हमारे पास तो tree-recursive से पूरा map है।
- Path में `/` रहने दो, बाकी special chars percent-encode करो।
- Response `truncated`/`size` फ़ील्ड जाँचो (भाग 9 देखो)।

---

## भाग 12 — UI (MainActivity + layouts) — सब हिंदी में

मुख्य स्क्रीन दिखाए (नीचे से ऊपर):
1. **Header:** ऐप का नाम `{{APP_NAME}}`, sync mode चिप (two-way/push/pull),
   last-sync समय।
2. **Configuration सेक्शन:**
   - GitHub Username (text)
   - Repo name (text)
   - Branch (text, default main)
   - Token (password field + show/hide)
   - चुना फ़ोल्डर (दिखाए path/name) + "📁 फ़ोल्डर चुनें" बटन
   - Auto-sync interval (dropdown/number)
   - Sync mode (radio: दो-तरफ़ा / सिर्फ़ push / सिर्फ़ pull)
   - "💾 सेव करें और टेस्ट" बटन → settings save + `GET repo` से validate, नतीजा
     toast/स्क्रीन पर।
3. **Actions:** बड़े बटन — "▶ अभी Sync करो", "⬆ सिर्फ़ भेजो", "⬇ सिर्फ़ लाओ",
   "🔄 बैकग्राउंड auto-sync चालू/बंद"।
4. **Status/Log list** (RecyclerView नहीं — Simple ListView या scroll TextView):
   हर run की lines जैसे:
   - `✓ 12:05:31 — भेजा: src/Main.java, res/strings.xml (2 फ़ाइलें)`
   - `✓ 12:05:31 — लाया: assets/img.png (1)`
   - `⚠ Conflict: config.json (local रखा, remote .CONFLICT.remote में)`
   - `✗ 12:06:00 — error: token invalid (401)`
   - (सिर्फ़ आख़िरी ~100 लाइनें रखो — memory save।)
5. Token कभी log/स्क्रीन पर पूरा नहीं।

Layouts: `activity_main.xml` में ScrollView + LinearLayout (कोई library widget नहीं,
सिर्फ़ `Button`, `EditText`, `TextView`, `RadioGroup`, `ProgressBar`, `ListView`)।
`styles.xml` में थीम `Theme.Material.Light` या बेसिक custom; सारे रंग `colors.xml`,
सारे शब्द `strings.xml` में (default Hindi, English strings भी डाल सकते हो)।

Foreground **notification** (SyncService): title `{{APP_NAME}}`, text `"Syncing…"` /
`"पिछली sync: HH:mm:ss"`, tap → MainActivity।

---

## भाग 13 — गलतियाँ/एज-केस जिन्हें AI ज़रूर संभाले

1. **Token गलत / ख़त्म (401):** साफ़ हिंदी error, settings reset न करो।
2. **Repo/branch नहीं मिला (404):** बताओ; branch नहीं तो default_branch से पूछो।
3. **Rate limit (403 + `X-RateLimit-Remaining: 0`):** बताओ "बहुत ज़्यादा calls,
   थोड़ी देर में दोबारा"। 
4. **फ़ाइल बहुत बड़ी:** contents API ~100MB limit; उससे बड़ी स्किप + warning।
5. **Binary फ़ाइल:** base64 में जाती है, atomic, कोई text-encoding मत लगाओ।
6. **खाली/गहरे nested फ़ोल्डर:** हर sub-folder push से पहले `DocumentFile.createDirectory`
   से बना; गहराई-पहले walk रखो।
7. **फ़ाइल नाम में `# % ? &` आदि:** path encode/decode सही करो।
8. **चुना फ़ोल्डर मिल न जाए** (SAF permission खो गई): user से दोबारा चुनने को
   कहो (भाग 6)।
9. **दो-तरफ़ा में कभी-कभी remote commit दूसरे push से बदल गया:** ref-update पर
   `409/422` → re-fetch + re-run (9.6)। force मत करो।
10. **कभी भी दो थ्रेड से एक फ़ाइल:** सब single executor पर (भाग 10)।
11. **App का lifecycle:** config बदलने पर service को रोक कर settings refresh।
12. **Token को कहीं (logs, notification, crash reports) मत छापो।**
13. **Activity recreate / rotation:** sync background में है इसलिए चलता रहे; UI
    fresh state pull करे।

---

## भाग 14 — AI को अंतिम जाँच सूची (सब code लिखने से पहले verify करो)

- [ ] कोई gradle dependency नहीं, सिर्फ़ framework classes।
- [ ] पूरा कोड `javac`-सही (types, imports, try/catch, no unused crash path)।
- [ ] Network सिर्फ़ background thread पर।
- [ ] हर file operation atomic (भाग 8)।
- [ ] Push पूरा **एक commit** में; ref update `force:false` + retry।
- [ ] Pull से पहले remote content **पूरी** buffer में, size जाँचकर।
- [ ] Baseline internal storage में, repo के अंदर नहीं।
- [ ] Infinite-loop का बचाव (FileObserver flag + hash-compare)।
- [ ] Conflict पर कुछ नहीं मिटता — दोनों versions सुरक्षित।
- [ ] Hindi strings, हर action का साफ़ feedback।
- [ ] Service foreground notification + auto-sync timer।
- [ ] SAF से folder pick + persistable permission।
- [ ] Android 13+ notification permission runtime माँगी।
- [ ] Manifest में service/foregroundServiceType सही।

---

## भाग 15 — Build कैसे करें (AI इंसान को ये बताएगा)

- **Android Studio:** project खोलो → Gradle sync (बिना किसी extra dependency) →
  Run। या `./gradlew assembleDebug` → APK `app/build/outputs/apk/debug/`.
- **AIDE (mobile):** folder import → Build → Run. (कोई extra "add library" मत करना।)
- **Termux:** `gradle assembleDebug` (अगर स्थापित हो) — भाग 0 के सवाल 3 के जवाब
  के मुताबिक बताओ।
- Test करते समय इंसान को एक छोटी test repo और छोटे फ़ोल्डर (कुछ text files +
  एक छोटी इमेज) से शुरू करने को कहो, फिर AI/GitHub से एक फ़ाइल बदलकर देखें कि वह
  सही जगह आती है या नहीं।

---

## अंतिम नोट

> इस गाइड का हर भाग तोड़-मरोड़ कर नहीं बदलना। AI, पूरा code पेश करने से पहले
> भाग 0 के सवाल पूछो, फिर ऊपर की सूची के हर class/फ़ाइल का पूरा, compile-होने
> वाला, atomic और error-safe Java/XML कोड लिखो। इंसान (या कोई AI) जब यह guide
> पढ़े, तो उसे पूरा ऐप मिल जाना चाहिए।
