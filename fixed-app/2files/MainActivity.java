package com.tool;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.DocumentsContract;
import android.util.Base64;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ToggleButton;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {

    private static final int REQ_TREE = 1001;
    private static final String PREFS = "sync_cfg";
    private static final String BASELINE_FILE = "sync_baseline.json";

    private SharedPreferences prefs;
    private EditText etUser, etRepo, etBranch, etToken;
    private TextView tvFolder, tvLogs;
    private ToggleButton btnAutoSync;

    private ExecutorService executor = Executors.newSingleThreadExecutor();
    private Handler mainHandler = new Handler(Looper.getMainLooper());
    private Handler autoSyncHandler = new Handler(Looper.getMainLooper());

    private volatile boolean isSyncing = false;
    private volatile boolean activityGone = false;

    private Runnable autoSyncRunnable = new Runnable() {
        @Override public void run() {
            if (activityGone) return;
            if (btnAutoSync != null && btnAutoSync.isChecked()) {
                startSync();
                autoSyncHandler.postDelayed(this, 30000); // 30 seconds
            }
        }
    };

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);

        etUser   = findViewById(R.id.etUsername);
        etRepo   = findViewById(R.id.etRepo);
        etBranch = findViewById(R.id.etBranch);
        etToken  = findViewById(R.id.etToken);
        tvFolder = findViewById(R.id.tvSelectedFolder);
        tvLogs   = findViewById(R.id.tvLogs);
        btnAutoSync = findViewById(R.id.btnAutoSync);

        loadSettings();

        findViewById(R.id.btnPickFolder).setOnClickListener(v -> pickFolder());
        findViewById(R.id.btnSaveConfig).setOnClickListener(v -> saveSettings());
        findViewById(R.id.btnSyncNow).setOnClickListener(v -> startSync());

        btnAutoSync.setOnCheckedChangeListener((CompoundButton buttonView, boolean isChecked) -> {
            if (activityGone) return;
            if (isChecked) {
                log("Auto-sync 30s चालू किया गया।");
                autoSyncHandler.removeCallbacks(autoSyncRunnable);
                autoSyncHandler.post(autoSyncRunnable);
            } else {
                log("Auto-sync बंद किया गया।");
                autoSyncHandler.removeCallbacks(autoSyncRunnable);
            }
        });
    }

    private void pickFolder() {
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        startActivityForResult(i, REQ_TREE);
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQ_TREE && resultCode == RESULT_OK && data != null) {
            Uri treeUri = data.getData();
            if (treeUri == null) {
                Toast.makeText(this, "कोई फ़ोल्डर नहीं चुना गया।", Toast.LENGTH_SHORT).show();
                return;
            }
            try {
                getContentResolver().takePersistableUriPermission(treeUri,
                        Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            } catch (SecurityException e) {
                // persistable permission na mile to bhi chalta hai
            }
            prefs.edit().putString("treeUri", treeUri.toString()).apply();
            tvFolder.setText("Selected: " + readableTreeName(treeUri));
            log("फ़ोल्डर चुना गया।");
        }
    }

    private String readableTreeName(Uri treeUri) {
        try {
            String id = DocumentsContract.getTreeDocumentId(treeUri);
            int idx = Math.max(id.lastIndexOf('/'), id.lastIndexOf(':'));
            return idx >= 0 ? id.substring(idx + 1) : id;
        } catch (Exception e) {
            return treeUri.toString();
        }
    }

    private void loadSettings() {
        etUser.setText(prefs.getString("user", ""));
        etRepo.setText(prefs.getString("repo", ""));
        etBranch.setText(prefs.getString("branch", "main"));
        etToken.setText(prefs.getString("token", ""));
        String uriStr = prefs.getString("treeUri", null);
        if (uriStr != null) tvFolder.setText("Selected: " + readableTreeName(Uri.parse(uriStr)));
    }

    private void saveSettings() {
        prefs.edit()
             .putString("user",   etUser.getText().toString().trim())
             .putString("repo",   etRepo.getText().toString().trim())
             .putString("branch", etBranch.getText().toString().trim())
             .putString("token",  etToken.getText().toString().trim())
             .apply();
        Toast.makeText(this, "डिटेल्स सेव हो गईं", Toast.LENGTH_SHORT).show();
    }

    private void log(final String msg) {
        mainHandler.post(() -> {
            if (activityGone || tvLogs == null) return;
            String cur = tvLogs.getText() != null ? tvLogs.getText().toString() : "";
            tvLogs.setText(msg + "\n" + cur);
        });
    }

    private void startSync() {
        if (isSyncing) {
            log("Sync पहले से चल रहा है...");
            return;
        }
        String user = prefs.getString("user", "");
        String repo = prefs.getString("repo", "");
        String branch = prefs.getString("branch", "main");
        String token = prefs.getString("token", "");
        String uriStr = prefs.getString("treeUri", null);

        if (user.isEmpty() || repo.isEmpty() || token.isEmpty() || uriStr == null) {
            log("कृपया पहले सारी डिटेल्स भरें और फ़ोल्डर चुनें!");
            return;
        }

        isSyncing = true;
        executor.execute(() -> {
            try {
                log("🔄 Sync शुरू हो रहा है...");
                new SyncRun(user, repo, branch, token, Uri.parse(uriStr)).runSync();
            } catch (Exception e) {
                log("❌ Error: " + e.getMessage());
            } finally {
                isSyncing = false;
                log("----------------------------------------");
            }
        });
    }

    @Override protected void onDestroy() {
        activityGone = true;
        autoSyncHandler.removeCallbacks(autoSyncRunnable);
        executor.shutdownNow();
        super.onDestroy();
    }

    // ====================================================================
    // Git API helper (sirf framework + org.json)
    // ====================================================================
    class GitApi {
        final String user, repo, token;
        GitApi(String u, String r, String t) { user = u; repo = r; token = t; }

        // non-2xx par ApiError (code ke saath) throw karta hai
        JSONObject requestCode(String method, String path, JSONObject body) throws Exception {
            String base = "https://api.github.com/repos/" + user + "/" + repo;
            URL url = new URL(base + path);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod(method);
            conn.setConnectTimeout(20000);
            conn.setReadTimeout(30000);
            conn.setRequestProperty("Authorization", "Bearer " + token);
            conn.setRequestProperty("Accept", "application/vnd.github+json");
            conn.setRequestProperty("User-Agent", "ranu-meena-sync");

            if (body != null) {
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "application/json");
                OutputStream os = conn.getOutputStream();
                try {
                    os.write(body.toString().getBytes(StandardCharsets.UTF_8));
                } finally {
                    os.close();
                }
            }

            int code = conn.getResponseCode();
            InputStream is = (code >= 200 && code < 300) ? conn.getInputStream() : conn.getErrorStream();
            String res = "";
            if (is != null) {
                try {
                    ByteArrayOutputStream baos = new ByteArrayOutputStream();
                    byte[] buf = new byte[1024];
                    int len;
                    while ((len = is.read(buf)) != -1) baos.write(buf, 0, len);
                    res = baos.toString("UTF-8");
                } finally {
                    is.close();
                }
            }
            conn.disconnect();

            if (code >= 400) {
                throw new ApiError(code, res);
            }
            return res.isEmpty() ? new JSONObject() : new JSONObject(res);
        }
    }

    class ApiError extends Exception {
        final int code;
        ApiError(int code, String res) { super(res == null || res.isEmpty() ? "HTTP " + code : res); this.code = code; }
    }

    // ====================================================================
    // Sync engine — 3-way diff, deletion + conflict aware
    // ====================================================================
    class SyncRun {
        final GitApi api;
        final String branch;
        final Uri rootUri;
        final String rootDocId;

        Map<String, String> remoteSha = new HashMap<>();
        Map<String, String> localHash = new HashMap<>();
        Map<String, Uri>   localUri  = new HashMap<>();
        Map<String, String> baseline = new HashMap<>();
        List<String> skippedPush = new ArrayList<>();

        SyncRun(String u, String r, String b, String t, Uri root) {
            api = new GitApi(u, r, t);
            branch = b;
            rootUri = root;
            rootDocId = DocumentsContract.getTreeDocumentId(root);
        }

        void runSync() throws Exception {
            log("GitHub से स्थिति ले रहे हैं...");
            JSONObject refRes = api.requestCode("GET", "/git/refs/heads/" + branch, null);
            String commitSha = refRes.getJSONObject("object").getString("sha");
            JSONObject commitRes = api.requestCode("GET", "/commits/" + commitSha, null);
            String baseTreeSha = commitRes.getJSONObject("commit").getJSONObject("tree").getString("sha");
            JSONObject treeRes = api.requestCode("GET", "/git/trees/" + baseTreeSha + "?recursive=1", null);

            JSONArray arr = treeRes.getJSONArray("tree");
            for (int i = 0; i < arr.length(); i++) {
                JSONObject it = arr.getJSONObject(i);
                if ("blob".equals(it.getString("type"))) {
                    remoteSha.put(it.getString("path"), it.getString("sha"));
                }
            }

            log("लोकल फ़ोल्डर स्कैन कर रहे हैं...");
            scanLocal(rootDocId, "");
            loadBaseline();

            List<String> pushWrites = new ArrayList<>();
            List<String> pushDeletes = new ArrayList<>();
            List<String> pullWrites = new ArrayList<>();
            List<String> pullDeletes = new ArrayList<>();
            List<String> conflicts = new ArrayList<>();

            Set<String> union = new LinkedHashSet<>(localHash.keySet());
            union.addAll(remoteSha.keySet());
            union.addAll(baseline.keySet());

            for (String p : union) {
                String L = localHash.get(p);
                String R = remoteSha.get(p);
                String B = baseline.get(p);

                if (L != null && L.equals(R)) {
                    if (B == null) baseline.put(p, L);
                } else if (L != null && L.equals(B) && R == null) {
                    pullDeletes.add(p);
                } else if (L != null && L.equals(B) && R != null) {
                    pullWrites.add(p);
                } else if (R != null && R.equals(B) && L != null) {
                    pushWrites.add(p);
                } else if (R != null && R.equals(B) && L == null) {
                    pushDeletes.add(p);
                } else if (L == null && B == null && R != null) {
                    pullWrites.add(p);
                } else if (R == null && B == null && L != null) {
                    pushWrites.add(p);
                } else if (L == null && R == null && B != null) {
                    baseline.remove(p);
                } else {
                    conflicts.add(p);
                }
            }

            boolean pushNeeded = !pushWrites.isEmpty() || !pushDeletes.isEmpty();
            boolean pullNeeded = !pullWrites.isEmpty() || !pullDeletes.isEmpty();

            if (pushNeeded) {
                log("⬆ " + (pushWrites.size() + pushDeletes.size()) + " बदलाव GitHub पर भेज रहे हैं...");
                JSONArray treeEntries = new JSONArray();

                // file-vs-dir conflict detect: koi path doosre path ka prefix na ho
                java.util.Set<String> allP = new java.util.HashSet<>();
                for (String p : pushWrites) allP.add(p);
                for (String p : pushDeletes) allP.add(p);

                for (String p : pushWrites) {
                    if (!isValidTreePath(p) || isPrefixConflict(p, allP)) {
                        skippedPush.add(p);
                        continue;
                    }
                    byte[] data = readBytes(localUri.get(p));
                    JSONObject blob = new JSONObject();
                    blob.put("content", Base64.encodeToString(data, Base64.NO_WRAP));
                    blob.put("encoding", "base64");
                    JSONObject blobRes = api.requestCode("POST", "/git/blobs", blob);

                    JSONObject e = new JSONObject();
                    e.put("path", p);
                    e.put("mode", "100644");
                    e.put("type", "blob");
                    e.put("sha", blobRes.getString("sha"));
                    treeEntries.put(e);
                }
                for (String p : pushDeletes) {
                    if (!isValidTreePath(p)) {
                        skippedPush.add(p);
                        continue;
                    }
                    JSONObject e = new JSONObject();
                    e.put("path", p);
                    e.put("mode", "100644");
                    e.put("type", "blob");
                    e.put("sha", JSONObject.NULL);
                    treeEntries.put(e);
                }

                boolean pushCanCommit = treeEntries.length() > 0;
                if (!pushCanCommit) {
                    for (String s : skippedPush)
                        log("⚠ Skip (kharab path): " + s);
                    log("✓ कोई valid बदलाव नहीं बचा, push छोड़ा गया।");
                    skippedPush.clear();
                }
                if (pushCanCommit) {

                JSONObject treeBody = new JSONObject();
                treeBody.put("base_tree", baseTreeSha);
                treeBody.put("tree", treeEntries);
                JSONObject newTree = api.requestCode("POST", "/git/trees", treeBody);

                JSONObject commitBody = new JSONObject();
                commitBody.put("message", "Sync by sync-app: " + pushWrites.size() + " write, " + pushDeletes.size() + " delete");
                commitBody.put("tree", newTree.getString("sha"));
                JSONArray parents = new JSONArray().put(commitSha);
                commitBody.put("parents", parents);
                JSONObject newCommit = api.requestCode("POST", "/git/commits", commitBody);

                JSONObject refBody = new JSONObject();
                refBody.put("sha", newCommit.getString("sha"));
                refBody.put("force", false);
                try {
                    api.requestCode("PATCH", "/git/refs/heads/" + branch, refBody);
                } catch (ApiError er) {
                    if (er.code == 409 || er.code == 422) {
                        throw new Exception("Repo aur kisi ne beech me badal diya (409). कृपया Sync दोबारा दबाएँ।");
                    }
                    throw er;
                }

                for (String p : pushWrites) baseline.put(p, localHash.get(p));
                for (String p : pushDeletes) baseline.remove(p);
                log("✓ Push सफल (" + pushWrites.size() + " फ़ाइल, " + pushDeletes.size() + " डिलीट)");
                } // close if(pushCanCommit)
            } // close if(pushNeeded)

            if (pullNeeded) {
                log("⬇ " + (pullWrites.size() + pullDeletes.size()) + " बदलाव local में ला रहे हैं...");
                for (String p : pullDeletes) {
                    deleteLocal(p);
                    baseline.remove(p);
                }
                for (String p : pullWrites) {
                    // Branch-independent pull: git blob API se content lao (sha ke through).
                    // Isse kisi bhi branch par 404 nahi aata (contents API default branch use karta tha).
                    String sha = remoteSha.get(p);
                    JSONObject f = api.requestCode("GET", "/git/blobs/" + sha, null);
                    String b64 = f.getString("content").replace("\n", "").replace("\r", "");
                    byte[] data = Base64.decode(b64, Base64.DEFAULT);
                    writeFileAtomic(p, data);
                    baseline.put(p, sha);
                }
                log("✓ Pull सफल");
            }

            for (String c : conflicts) {
                log("⚠ Conflict (छोड़ा गया): " + c +
                        " — local bhi aur remote bhi badla hai. Koi bhi side overwrite nahi hui.");
            }

            saveBaseline();
            if (!pushNeeded && !pullNeeded && conflicts.isEmpty()) {
                log("✓ फ़ाइलें पहले से Sync हैं। कोई बदलाव नहीं।");
            }
        }

        private Uri docUri(String docId) {
            return DocumentsContract.buildDocumentUriUsingTree(rootUri, docId);
        }

        // GitHub tree API valid path check (no empty/dot/dotdot/control segments, no slash edges)
        private boolean isValidTreePath(String p) {
            if (p == null || p.isEmpty()) return false;
            if (p.startsWith("/") || p.endsWith("/")) return false;
            for (String s : p.split("/")) {
                if (s.isEmpty() || s.equals(".") || s.equals("..")) return false;
                for (int i = 0; i < s.length(); i++) {
                    if (s.charAt(i) < 32) return false;
                }
            }
            return true;
        }

        // agar 'a/b.txt' doosre 'a' se takra raha ho (file-vs-dir) to skip
        private boolean isPrefixConflict(String p, java.util.Set<String> all) {
            String prefix = p;
            int idx;
            while ((idx = prefix.lastIndexOf('/')) > 0) {
                prefix = prefix.substring(0, idx);
                if (all.contains(prefix)) return true;
            }
            return false;
        }

        private String findChildId(String parentDocId, String name) throws Exception {
            Uri listUri = DocumentsContract.buildChildDocumentsUriUsingTree(rootUri, parentDocId);
            String[] proj = {
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE
            };
            Cursor c = getContentResolver().query(listUri, proj, null, null, null);
            try {
                while (c != null && c.moveToNext()) {
                    String display = c.getString(c.getColumnIndex(DocumentsContract.Document.COLUMN_DISPLAY_NAME));
                    if (name.equals(display)) {
                        return c.getString(c.getColumnIndex(DocumentsContract.Document.COLUMN_DOCUMENT_ID));
                    }
                }
            } finally {
                if (c != null) c.close();
            }
            return null;
        }

        private String ensureDir(String parentDocId, String name) throws Exception {
            String ex = findChildId(parentDocId, name);
            if (ex != null) return ex;
            Uri created = DocumentsContract.createDocument(getContentResolver(), docUri(parentDocId),
                    DocumentsContract.Document.MIME_TYPE_DIR, name);
            if (created == null) throw new Exception("फ़ोल्डर नहीं बन सका: " + name);
            return DocumentsContract.getDocumentId(created);
        }

        private void writeFileAtomic(String path, byte[] data) throws Exception {
            String[] seg = path.split("/");
            if (seg.length == 0) return;
            String dirId = rootDocId;
            for (int i = 0; i < seg.length - 1; i++) {
                dirId = ensureDir(dirId, seg[i]);
            }
            String fileName = seg[seg.length - 1];
            String existing = findChildId(dirId, fileName);
            Uri target;
            if (existing != null) {
                target = docUri(existing);
            } else {
                Uri created = DocumentsContract.createDocument(getContentResolver(), docUri(dirId),
                        "application/octet-stream", fileName);
                if (created == null) throw new Exception("फ़ाइल नहीं बन सकी: " + path);
                target = created;
            }
            OutputStream os = getContentResolver().openOutputStream(target, "wt");
            if (os == null) throw new Exception("write नहीं खुला: " + path);
            try {
                os.write(data);
                os.flush();
            } finally {
                os.close();
            }
        }

        private void deleteLocal(String path) {
            try {
                deleteByPath(rootDocId, path.split("/"), 0);
            } catch (Exception e) {
                log("⚠ local file delete error: " + path + " — " + e.getMessage());
            }
        }

        private void deleteByPath(String dirId, String[] seg, int i) throws Exception {
            if (i >= seg.length) return;
            String child = findChildId(dirId, seg[i]);
            if (child == null) return;
            if (i == seg.length - 1) {
                DocumentsContract.deleteDocument(getContentResolver(), docUri(child));
            } else {
                deleteByPath(child, seg, i + 1);
            }
        }

        // build/machine-generated folders jo sync me nahi jaane chahiye
        private final String[] SKIP_DIRS = {
            ".git", ".gradle", "build", ".idea", ".cxx", ".externalNativeBuild",
            "node_modules", "captures", "kotlin"
        };
        // system junk files (dotfiles like .gitignore source file ko nahi skip karte)
        private final String[] SKIP_FILES = {
            ".DS_Store", "Thumbs.db", "Desktop.ini"
        };

        private boolean shouldSkipDir(String name) {
            if (name == null) return false;
            for (String s : SKIP_DIRS) {
                if (s.equalsIgnoreCase(name)) return true;
            }
            return false;
        }

        private boolean shouldSkipFile(String name) {
            if (name == null) return false;
            for (String s : SKIP_FILES) {
                if (s.equalsIgnoreCase(name)) return true;
            }
            String lower = name.toLowerCase();
            // build outputs / apk koi source nahi hote
            if (lower.endsWith(".apk")) return true;
            return false;
        }

        private void scanLocal(String dirDocId, String currentPath) {
            Uri listUri = DocumentsContract.buildChildDocumentsUriUsingTree(rootUri, dirDocId);
            String[] proj = {
                    DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                    DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                    DocumentsContract.Document.COLUMN_MIME_TYPE
            };
            Cursor c = null;
            try {
                c = getContentResolver().query(listUri, proj, null, null, null);
                while (c != null && c.moveToNext()) {
                    String id = c.getString(c.getColumnIndex(DocumentsContract.Document.COLUMN_DOCUMENT_ID));
                    String name = c.getString(c.getColumnIndex(DocumentsContract.Document.COLUMN_DISPLAY_NAME));
                    String mime = c.getString(c.getColumnIndex(DocumentsContract.Document.COLUMN_MIME_TYPE));
                    if (name == null) continue;

                    String newPath = currentPath.isEmpty() ? name : currentPath + "/" + name;
                    Uri childUri = docUri(id);
                    if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                        // build/machine dirs ko skip (sirf source folders sync)
                        if (shouldSkipDir(name)) continue;
                        scanLocal(id, newPath);
                    } else {
                        // junk/build files ko skip
                        if (shouldSkipFile(name)) continue;
                        try {
                            byte[] data = readBytes(childUri);
                            localUri.put(newPath, childUri);
                            localHash.put(newPath, gitBlobSha(data));
                        } catch (Exception ex) {
                            log("⚠ पढ़ नहीं सके: " + newPath + " — " + ex.getMessage());
                        }
                    }
                }
            } catch (Exception e) {
                log("⚠ folder scan error: " + currentPath + " — " + e.getMessage());
            } finally {
                if (c != null) c.close();
            }
        }

        private byte[] readBytes(Uri uri) throws Exception {
            InputStream is = getContentResolver().openInputStream(uri);
            if (is == null) throw new Exception("फ़ाइल खुली नहीं: " + uri);
            try {
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                byte[] buf = new byte[8192];
                int len;
                while ((len = is.read(buf)) != -1) baos.write(buf, 0, len);
                return baos.toByteArray();
            } finally {
                is.close();
            }
        }


        private File baselineFile() {
            return new File(getFilesDir(), BASELINE_FILE);
        }

        private void loadBaseline() {
            File f = baselineFile();
            if (!f.exists()) return;
            try {
                FileInputStream in = new FileInputStream(f);
                byte[] data;
                try {
                    ByteArrayOutputStream b = new ByteArrayOutputStream();
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) != -1) b.write(buf, 0, n);
                    data = b.toByteArray();
                } finally {
                    in.close();
                }
                JSONObject root = new JSONObject(new String(data, "UTF-8"));
                if (root.has("files")) {
                    JSONObject files = root.getJSONObject("files");
                    Iterator<String> it = files.keys();
                    while (it.hasNext()) {
                        String k = it.next();
                        baseline.put(k, files.getString(k));
                    }
                }
            } catch (Exception e) {
                baseline.clear();
            }
        }

        private void saveBaseline() {
            File f = baselineFile();
            try {
                JSONObject files = new JSONObject();
                for (Map.Entry<String, String> e : baseline.entrySet()) files.put(e.getKey(), e.getValue());
                JSONObject root = new JSONObject();
                root.put("files", files);
                byte[] data = root.toString().getBytes("UTF-8");

                File tmp = new File(f.getParentFile(), BASELINE_FILE + ".tmp");
                FileOutputStream out = new FileOutputStream(tmp);
                try {
                    out.write(data);
                    out.flush();
                } finally {
                    out.close();
                }
                if (!tmp.renameTo(f)) {
                    f.delete();
                    tmp.renameTo(f);
                }
            } catch (Exception e) {
                log("⚠ baseline save error: " + e.getMessage());
            }
        }

        private String gitBlobSha(byte[] data) {
            try {
                MessageDigest md = MessageDigest.getInstance("SHA-1");
                String header = "blob " + data.length + "\0";
                md.update(header.getBytes(StandardCharsets.US_ASCII));
                md.update(data);
                byte[] d = md.digest();
                StringBuilder sb = new StringBuilder();
                for (byte b : d) sb.append(String.format("%02x", b));
                return sb.toString();
            } catch (Exception e) {
                return "";
            }
        }
    }
}
