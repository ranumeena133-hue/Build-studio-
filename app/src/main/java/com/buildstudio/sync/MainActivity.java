package com.buildstudio.sync;

import android.Manifest;
import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * एक ही स्क्रीन वाली ऐप।
 * ऊपर सेटिंग्स भरो, नीचे दो बटन:
 *   - "GitHub से लाओ"  (download करके फोन में सही जगह रखेगा)
 *   - "GitHub पर भेजो" (फोन की फाइल repo में update करेगा)
 * असली काम SyncService में background में होता है।
 */
public class MainActivity extends Activity {

    private EditText etToken, etOwner, etRepo, etBranch, etRemote, etLocal;
    private TextView tvLog;
    private ScrollView scroll;

    private BroadcastReceiver receiver;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        etToken = findViewById(R.id.et_token);
        etOwner = findViewById(R.id.et_owner);
        etRepo = findViewById(R.id.et_repo);
        etBranch = findViewById(R.id.et_branch);
        etRemote = findViewById(R.id.et_remote);
        etLocal = findViewById(R.id.et_local);
        tvLog = findViewById(R.id.tv_log);
        scroll = findViewById(R.id.scroll_log);

        Button btnSave = findViewById(R.id.btn_save);
        Button btnDownload = findViewById(R.id.btn_download);
        Button btnUpload = findViewById(R.id.btn_upload);
        Button btnClear = findViewById(R.id.btn_clear);

        loadIntoFields();
        askPermissions();

        btnSave.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (saveFromFields()) {
                    Toast.makeText(MainActivity.this, "सेटिंग्स सेव हो गईं", Toast.LENGTH_SHORT).show();
                    addLog("सेटिंग्स सेव कर दी गईं");
                }
            }
        });

        btnDownload.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (!saveFromFields()) return;
                addLog("---- GitHub से लाने का काम शुरू ----");
                startWork(SyncService.ACTION_DOWNLOAD);
            }
        });

        btnUpload.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (!saveFromFields()) return;
                addLog("---- GitHub पर भेजने का काम शुरू ----");
                startWork(SyncService.ACTION_UPLOAD);
            }
        });

        btnClear.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                tvLog.setText("");
            }
        });

        // service से आने वाले संदेश सुनने के लिए
        receiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                if (intent.getBooleanExtra(SyncService.EXTRA_DONE, false)) {
                    addLog("काम खत्म।");
                    return;
                }
                String msg = intent.getStringExtra(SyncService.EXTRA_MSG);
                if (!TextUtils.isEmpty(msg)) addLog(msg);
            }
        };
    }

    @Override
    protected void onResume() {
        super.onResume();
        IntentFilter f = new IntentFilter(SyncService.BROADCAST_LOG);
        if (Build.VERSION.SDK_INT >= 33) {
            registerReceiver(receiver, f, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(receiver, f);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        try { unregisterReceiver(receiver); } catch (Exception ignored) { }
    }

    /** service चालू करना — यही background में काम करेगा */
    private void startWork(String action) {
        Intent i = new Intent(this, SyncService.class);
        i.setAction(action);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(i);
        } else {
            startService(i);
        }
    }

    private void loadIntoFields() {
        Settings s = Settings.load(this);
        etToken.setText(s.token);
        etOwner.setText(s.owner);
        etRepo.setText(s.repo);
        etBranch.setText(s.branch);
        etRemote.setText(s.remotePath);
        etLocal.setText(TextUtils.isEmpty(s.localPath)
                ? Settings.defaultLocalPath(s.remotePath) : s.localPath);
    }

    private boolean saveFromFields() {
        Settings s = new Settings();
        s.token = etToken.getText().toString().trim();
        s.owner = etOwner.getText().toString().trim();
        s.repo = etRepo.getText().toString().trim();
        s.branch = etBranch.getText().toString().trim();
        if (s.branch.length() == 0) s.branch = "main";
        s.remotePath = etRemote.getText().toString().trim();
        s.localPath = etLocal.getText().toString().trim();
        if (s.localPath.length() == 0) {
            s.localPath = Settings.defaultLocalPath(s.remotePath);
            etLocal.setText(s.localPath);
        }
        String bad = s.validate();
        if (bad != null) {
            Toast.makeText(this, bad, Toast.LENGTH_LONG).show();
            addLog("रुको: " + bad);
            return false;
        }
        s.save(this);
        return true;
    }

    private void addLog(String msg) {
        String time = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
        tvLog.append("[" + time + "] " + msg + "\n");
        scroll.post(new Runnable() {
            public void run() { scroll.fullScroll(View.FOCUS_DOWN); }
        });
    }

    /** ज़रूरी परमिशन माँगना (पुराने Android में storage, नए में notification) */
    private void askPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            java.util.ArrayList<String> need = new java.util.ArrayList<String>();
            if (Build.VERSION.SDK_INT <= 28
                    && checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                    != PackageManager.PERMISSION_GRANTED) {
                need.add(Manifest.permission.WRITE_EXTERNAL_STORAGE);
            }
            if (Build.VERSION.SDK_INT >= 33
                    && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                need.add(Manifest.permission.POST_NOTIFICATIONS);
            }
            if (need.size() > 0) {
                requestPermissions(need.toArray(new String[0]), 1);
            }
        }
    }
}
