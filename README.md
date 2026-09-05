# Build Studio — GitHub फाइल सिंक ऐप

बिलकुल सिंपल Android ऐप। सिर्फ **Java + XML**, **कोई भी बाहरी library नहीं** (न Retrofit, न OkHttp, न AndroidX)।
जो कुछ इस्तेमाल हुआ है वो Android में पहले से मौजूद है — `HttpURLConnection`, `Base64`, `org.json`.

## ये ऐप करती क्या है

आपके GitHub अकाउंट की एक फाइल (जैसे `responsey.txt`) और आपके फोन की एक फाइल — इन दोनों के बीच आना-जाना:

1. **GitHub से लाओ (Download)** — repo वाली फाइल उठाकर फोन में आपकी बताई हुई जगह पर रख देती है।
   फोल्डर नहीं है तो खुद बना लेती है।
2. **GitHub पर भेजो (Upload)** — फोन वाली फाइल उठाकर उसी repo में update कर देती है।
   अगर repo में फाइल पहले से है तो उसका `sha` लेकर update करती है, नहीं है तो नई बना देती है।

दोनों काम **background service (`SyncService`)** में होते हैं — यानी स्क्रीन बंद कर दो या ऐप पीछे कर दो, काम चलता रहेगा।
ऊपर notification में status दिखता रहता है।

## फाइलें कौन-कौन सी हैं

| फाइल | काम |
|---|---|
| `MainActivity.java` | एक ही स्क्रीन — सेटिंग्स भरो और दो बटन दबाओ |
| `SyncService.java` | background में download / upload का असली काम |
| `GitHubApi.java` | GitHub Contents API से बात करना (GET और PUT) |
| `Settings.java` | token, username, repo, रास्ता — सब SharedPreferences में सेव |
| `res/layout/activity_main.xml` | स्क्रीन का डिज़ाइन |
| `res/values/strings.xml` | सारे शब्द (हिंदी में) |

## चलाने का तरीका

### 1. GitHub Token बनाओ
- GitHub → Settings → Developer settings → Personal access tokens
- **Fine-grained token** बनाओ, अपनी repo चुनो, और **Contents: Read and write** परमिशन दो
- (या Classic token में `repo` scope चुन लो)
- token copy कर लो — वो सिर्फ एक बार दिखता है

### 2. प्रोजेक्ट खोलो
- Android Studio में इस फोल्डर को खोलो → **Run** दबाओ
- या टर्मिनल से: `./gradlew assembleDebug` (APK मिलेगा `app/build/outputs/apk/debug/` में)

### 3. ऐप में भरो
| खाना | क्या डालना है |
|---|---|
| GitHub Token | `ghp_...` वाला token |
| यूज़रनेम | `ranumeena133-hue` |
| Repository | `Build-studio-` |
| ब्रांच | `main` |
| Repo में रास्ता | `responsey.txt` |
| फोन में जगह | `/storage/emulated/0/Download/BuildStudio/responsey.txt` |

फिर **सेटिंग्स सेव करो** दबाओ। एक बार भरने के बाद दोबारा भरने की ज़रूरत नहीं।

### 4. बटन दबाओ
- नीला वाला पहला बटन → GitHub से फाइल आकर फोन में गिर जाएगी
- दूसरा बटन → फोन की फाइल GitHub पर चढ़ जाएगी

नीचे लॉग वाले डिब्बे में हर कदम हिंदी में दिखता रहेगा।

## ज़रूरी बातें

- **Android 10 और ऊपर**: `Download/` फोल्डर में लिखना ठीक चलता है। कोई दूसरी जगह चाहिए तो
  ऐप का अपना फोल्डर इस्तेमाल करना बेहतर रहेगा।
- **Android 9 और नीचे**: पहली बार ऐप storage परमिशन माँगेगी — "Allow" कर देना।
- Token फोन के अंदर SharedPreferences में सेव होता है। फोन किसी और को मत देना, और token को
  कभी GitHub पर commit मत करना।
- बड़ी फाइलें (100 MB से ऊपर) GitHub Contents API सपोर्ट नहीं करता।

## परमिशन क्यों चाहिए

- `INTERNET` — GitHub से बात करने के लिए
- `FOREGROUND_SERVICE` — background में काम चलाने के लिए
- `WRITE/READ_EXTERNAL_STORAGE` — पुराने Android में फाइल लिखने-पढ़ने के लिए
- `POST_NOTIFICATIONS` — Android 13+ में status notification दिखाने के लिए
