package com.buildstudio.sync;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * यही असली काम करने वाला background service है।
 * दो काम करता है:
 *   1) DOWNLOAD  -> GitHub की फाइल उठाकर फोन में सही जगह रख देना
 *   2) UPLOAD    -> फोन की फाइल उठाकर GitHub repo में update कर देना
 * UI बंद हो जाए तब भी काम चलता रहता है।
 */
public class SyncService extends Service {

    public static final String ACTION_DOWNLOAD = "com.buildstudio.sync.DOWNLOAD";
    public static final String ACTION_UPLOAD = "com.buildstudio.sync.UPLOAD";

    /** MainActivity इसी broadcast को सुनकर स्क्रीन पर लॉग दिखाती है */
    public static final String BROADCAST_LOG = "com.buildstudio.sync.LOG";
    public static final String EXTRA_MSG = "msg";
    public static final String EXTRA_DONE = "done";

    private static final String CHANNEL_ID = "build_studio_sync";
    private static final int NOTI_ID = 101;

    @Override
    public IBinder onBind(Intent intent) {
        return null; // बाइंडिंग की ज़रूरत नहीं
    }

    @Override
    public int onStartCommand(final Intent intent, int flags, int startId) {
        final String action = intent != null ? intent.getAction() : null;

        startForeground(NOTI_ID, buildNotification("काम चालू है..."));

        // अलग thread ताकि मुख्य thread अटके नहीं
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    if (ACTION_DOWNLOAD.equals(action)) {
                        doDownload();
                    } else if (ACTION_UPLOAD.equals(action)) {
                        doUpload();
                    } else {
                        log("कुछ समझ नहीं आया — कोई काम नहीं दिया गया");
                    }
                } catch (Exception e) {
                    log("गड़बड़: " + (e.getMessage() == null ? e.toString() : e.getMessage()));
                } finally {
                    done();
                    stopSelf();
                }
            }
        }).start();

        return START_NOT_STICKY;
    }

    // ---------------- काम 1: GitHub -> फोन ----------------
    private void doDownload() throws Exception {
        Settings s = Settings.load(this);
        String bad = s.validate();
        if (bad != null) { log("रुको: " + bad); return; }

        log("GitHub से फाइल माँगी जा रही है: " + s.remotePath);
        GitHubApi api = new GitHubApi(s);
        GitHubApi.FileInfo info = api.getFile();

        if (!info.exists) {
            log("repo में ये फाइल मिली ही नहीं: " + s.remotePath);
            return;
        }

        File out = new File(s.localPath);
        File dir = out.getParentFile();
        if (dir != null && !dir.exists()) {
            if (!dir.mkdirs()) log("फोल्डर बनाने में दिक्कत: " + dir.getAbsolutePath());
        }

        FileOutputStream fos = new FileOutputStream(out);
        fos.write(info.content);
        fos.flush();
        fos.close();

        log("हो गया — फाइल यहाँ रख दी: " + out.getAbsolutePath()
                + " (" + info.content.length + " bytes)");
        notify("Download पूरा हुआ");
    }

    // ---------------- काम 2: फोन -> GitHub ----------------
    private void doUpload() throws Exception {
        Settings s = Settings.load(this);
        String bad = s.validate();
        if (bad != null) { log("रुको: " + bad); return; }

        File in = new File(s.localPath);
        if (!in.exists()) {
            log("फोन में ये फाइल नहीं मिली: " + in.getAbsolutePath());
            return;
        }

        byte[] data = new byte[(int) in.length()];
        FileInputStream fis = new FileInputStream(in);
        int read = 0;
        while (read < data.length) {
            int n = fis.read(data, read, data.length - read);
            if (n < 0) break;
            read += n;
        }
        fis.close();

        log("फाइल पढ़ ली (" + data.length + " bytes), अब GitHub पर चढ़ा रहे हैं...");

        GitHubApi api = new GitHubApi(s);
        GitHubApi.FileInfo old = api.getFile();  // पुराना sha चाहिए update के लिए
        String sha = old.exists ? old.sha : null;

        String time = new SimpleDateFormat("dd-MM-yyyy HH:mm:ss", Locale.getDefault())
                .format(new Date());
        String msg = (old.exists ? "Update " : "Add ") + s.remotePath + " from Build Studio app (" + time + ")";

        String newSha = api.putFile(data, sha, msg);
        log("हो गया — GitHub पर " + (old.exists ? "update" : "नई फाइल add") + " कर दी गई। sha: "
                + (newSha.length() > 7 ? newSha.substring(0, 7) : newSha));
        notify("Upload पूरा हुआ");
    }

    // ---------------- छोटे-मोटे हेल्पर ----------------
    private void log(String msg) {
        Intent i = new Intent(BROADCAST_LOG);
        i.putExtra(EXTRA_MSG, msg);
        i.setPackage(getPackageName());
        sendBroadcast(i);
    }

    private void done() {
        Intent i = new Intent(BROADCAST_LOG);
        i.putExtra(EXTRA_DONE, true);
        i.setPackage(getPackageName());
        sendBroadcast(i);
    }

    private void notify(String text) {
        NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.notify(NOTI_ID, buildNotification(text));
    }

    private Notification buildNotification(String text) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            NotificationChannel ch = new NotificationChannel(CHANNEL_ID, "Build Studio Sync",
                    NotificationManager.IMPORTANCE_LOW);
            if (nm != null) nm.createNotificationChannel(ch);
            return new Notification.Builder(this, CHANNEL_ID)
                    .setContentTitle("Build Studio")
                    .setContentText(text)
                    .setSmallIcon(android.R.drawable.stat_sys_upload)
                    .build();
        }
        return new Notification.Builder(this)
                .setContentTitle("Build Studio")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_upload)
                .build();
    }
}
