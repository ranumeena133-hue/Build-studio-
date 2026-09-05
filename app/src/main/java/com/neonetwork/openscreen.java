package com.neonetwork;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.view.Window;
import android.view.WindowManager;
import android.view.animation.AlphaAnimation;
import android.widget.Toast;

public class openscreen extends Activity {

    private Handler handler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Fullscreen mode
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);

        // Set Layout
        setContentView(R.layout.openscreen);

        // Start Logo Fade-In Animation
        startLogoAnimation();

        // Click Listener
        findViewById(R.id.fullscreen_content).setOnClickListener(v ->
                Toast.makeText(openscreen.this, "Welcome to Neo Network!", Toast.LENGTH_SHORT).show());

        // 5 Seconds ke baad login screen open karo
        handler = new Handler();
        handler.postDelayed(() -> {
            try {
                Intent intent = new Intent(openscreen.this, login.class);
                startActivity(intent);
                overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
                finish();
            } catch (Exception e) {
                Intent intent = new Intent(openscreen.this, login.class);
                startActivity(intent);
                finish();
            }
        }, 5000);
    }

    // Logo Fade-In Animation
    private void startLogoAnimation() {
        try {
            if(findViewById(R.id.logo_image) != null) {
                AlphaAnimation fade = new AlphaAnimation(0f, 1f);
                fade.setDuration(1500);
                fade.setFillAfter(true);
                findViewById(R.id.logo_image).startAnimation(fade);
            }

            if(findViewById(R.id.app_name_text) != null) {
                AlphaAnimation textFade = new AlphaAnimation(0f, 1f);
                textFade.setDuration(1500);
                textFade.setStartOffset(500);
                textFade.setFillAfter(true);
                findViewById(R.id.app_name_text).startAnimation(textFade);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if(handler != null) {
            handler.removeCallbacksAndMessages(null);
        }
    }

    @Override
    public void onBackPressed() {
        Toast.makeText(this, "Please wait... Loading...", Toast.LENGTH_SHORT).show();
    }
}