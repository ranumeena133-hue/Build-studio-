package com.buildstudio.sync;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Environment;

import java.io.File;

/**
 * सेटिंग्स सेव/लोड करने वाली छोटी क्लास।
 * यहाँ GitHub का token, owner, repo वगैरह SharedPreferences में रखे जाते हैं।
 */
public class Settings {

    private static final String FILE_NAME = "build_studio_settings";

    public String token = "";       // GitHub का personal access token
    public String owner = "";       // GitHub username (जैसे ranumeena133-hue)
    public String repo = "";        // repository का नाम (जैसे Build-studio-)
    public String branch = "main";  // ब्रांच
    public String remotePath = "responsey.txt";  // repo के अंदर फाइल का रास्ता
    public String localPath = "";   // फोन के अंदर फाइल का पूरा रास्ता

    /** डिफ़ॉल्ट लोकल जगह: Download/BuildStudio/<फाइल का नाम> */
    public static String defaultLocalPath(String remotePath) {
        String name = remotePath;
        int i = name.lastIndexOf('/');
        if (i >= 0) name = name.substring(i + 1);
        if (name.length() == 0) name = "responsey.txt";
        File dir = new File(
                Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),
                "BuildStudio");
        return new File(dir, name).getAbsolutePath();
    }

    public static Settings load(Context c) {
        SharedPreferences p = c.getSharedPreferences(FILE_NAME, Context.MODE_PRIVATE);
        Settings s = new Settings();
        s.token = p.getString("token", "");
        s.owner = p.getString("owner", "");
        s.repo = p.getString("repo", "");
        s.branch = p.getString("branch", "main");
        s.remotePath = p.getString("remotePath", "responsey.txt");
        s.localPath = p.getString("localPath", defaultLocalPath(s.remotePath));
        return s;
    }

    public void save(Context c) {
        SharedPreferences p = c.getSharedPreferences(FILE_NAME, Context.MODE_PRIVATE);
        p.edit()
                .putString("token", token)
                .putString("owner", owner)
                .putString("repo", repo)
                .putString("branch", branch)
                .putString("remotePath", remotePath)
                .putString("localPath", localPath)
                .apply();
    }

    /** चेक करता है कि ज़रूरी चीज़ें भरी हुई हैं या नहीं */
    public String validate() {
        if (token.trim().length() == 0) return "GitHub token खाली है";
        if (owner.trim().length() == 0) return "GitHub username खाली है";
        if (repo.trim().length() == 0) return "Repository का नाम खाली है";
        if (remotePath.trim().length() == 0) return "Repo के अंदर फाइल का रास्ता खाली है";
        if (localPath.trim().length() == 0) return "फोन में फाइल का रास्ता खाली है";
        return null; // सब ठीक है
    }
}
