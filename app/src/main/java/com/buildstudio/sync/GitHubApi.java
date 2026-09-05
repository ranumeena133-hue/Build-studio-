package com.buildstudio.sync;

import android.util.Base64;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;

/**
 * GitHub से बात करने वाली क्लास।
 * यहाँ कोई बाहरी library नहीं है — सिर्फ Android के अपने HttpURLConnection,
 * Base64 और org.json (ये तीनों Android में पहले से मौजूद हैं)।
 */
public class GitHubApi {

    private final Settings s;

    public GitHubApi(Settings s) {
        this.s = s;
    }

    /** एक फाइल की जानकारी: उसका content और sha */
    public static class FileInfo {
        public byte[] content;  // फाइल का असली डेटा
        public String sha;      // GitHub वाला sha (update करते वक्त ज़रूरी)
        public boolean exists;  // repo में फाइल है या नहीं
    }

    private String contentsUrl() throws Exception {
        StringBuilder sb = new StringBuilder("https://api.github.com/repos/");
        sb.append(enc(s.owner)).append('/').append(enc(s.repo)).append("/contents/");
        // रास्ते के हर हिस्से को अलग-अलग encode करते हैं ताकि '/' बचा रहे
        String[] parts = s.remotePath.trim().split("/");
        for (int i = 0; i < parts.length; i++) {
            if (parts[i].length() == 0) continue;
            if (i > 0) sb.append('/');
            sb.append(enc(parts[i]));
        }
        return sb.toString();
    }

    private static String enc(String v) throws Exception {
        return URLEncoder.encode(v.trim(), "UTF-8").replace("+", "%20");
    }

    private HttpURLConnection open(String url, String method) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setRequestMethod(method);
        c.setRequestProperty("Authorization", "token " + s.token.trim());
        c.setRequestProperty("Accept", "application/vnd.github+json");
        c.setRequestProperty("User-Agent", "BuildStudioApp");
        c.setConnectTimeout(20000);
        c.setReadTimeout(40000);
        return c;
    }

    /** GitHub से फाइल पढ़ना (download) */
    public FileInfo getFile() throws Exception {
        String url = contentsUrl() + "?ref=" + enc(s.branch);
        HttpURLConnection c = open(url, "GET");
        int code = c.getResponseCode();
        FileInfo info = new FileInfo();

        if (code == 404) {
            info.exists = false;
            c.disconnect();
            return info;
        }
        if (code < 200 || code >= 300) {
            String err = readAll(c.getErrorStream());
            c.disconnect();
            throw new Exception("GitHub ने मना किया (कोड " + code + "): " + shorten(err));
        }

        String body = readAll(c.getInputStream());
        c.disconnect();

        JSONObject o = new JSONObject(body);
        info.exists = true;
        info.sha = o.optString("sha", "");
        String b64 = o.optString("content", "");
        if (b64.length() > 0) {
            info.content = Base64.decode(b64, Base64.DEFAULT);
        } else {
            // बड़ी फाइल हो तो GitHub content खाली भेजता है — तब download_url से लेते हैं
            String dl = o.optString("download_url", "");
            if (dl.length() > 0) info.content = downloadRaw(dl);
            else info.content = new byte[0];
        }
        return info;
    }

    private byte[] downloadRaw(String url) throws Exception {
        HttpURLConnection c = open(url, "GET");
        int code = c.getResponseCode();
        if (code < 200 || code >= 300) {
            c.disconnect();
            throw new Exception("फाइल download नहीं हो पाई (कोड " + code + ")");
        }
        byte[] data = readBytes(c.getInputStream());
        c.disconnect();
        return data;
    }

    /** फोन वाली फाइल को GitHub पर चढ़ाना (create या update) */
    public String putFile(byte[] data, String sha, String message) throws Exception {
        JSONObject body = new JSONObject();
        body.put("message", message);
        body.put("content", Base64.encodeToString(data, Base64.NO_WRAP));
        body.put("branch", s.branch.trim());
        if (sha != null && sha.length() > 0) body.put("sha", sha);

        HttpURLConnection c = open(contentsUrl(), "PUT");
        c.setDoOutput(true);
        c.setRequestProperty("Content-Type", "application/json");
        OutputStream os = c.getOutputStream();
        os.write(body.toString().getBytes("UTF-8"));
        os.flush();
        os.close();

        int code = c.getResponseCode();
        if (code < 200 || code >= 300) {
            String err = readAll(c.getErrorStream());
            c.disconnect();
            throw new Exception("अपलोड फेल (कोड " + code + "): " + shorten(err));
        }
        String resp = readAll(c.getInputStream());
        c.disconnect();

        JSONObject o = new JSONObject(resp);
        JSONObject content = o.optJSONObject("content");
        return content != null ? content.optString("sha", "") : "";
    }

    private static String shorten(String s) {
        if (s == null) return "";
        s = s.replace('\n', ' ');
        return s.length() > 200 ? s.substring(0, 200) + "..." : s;
    }

    private static String readAll(InputStream in) throws Exception {
        if (in == null) return "";
        BufferedReader r = new BufferedReader(new InputStreamReader(in, "UTF-8"));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = r.readLine()) != null) sb.append(line).append('\n');
        r.close();
        return sb.toString();
    }

    private static byte[] readBytes(InputStream in) throws Exception {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) > 0) bos.write(buf, 0, n);
        in.close();
        return bos.toByteArray();
    }
}
