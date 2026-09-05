package com.example.newproject3;

import android.app.Activity;
import android.os.Bundle;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Toast;

// Chaquopy imports
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

public class MainActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);

        setContentView(R.layout.main);

        // 1. Python ko initialize karna (Agar pehle se start nahi hai toh)
        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        // 2. Button click par Python script run karna
        findViewById(R.id.fullscreen_content).setOnClickListener(v -> {
            try {
                // Python ka instance lena
                Python py = Python.getInstance();
                
                // "test_script" naam ki python file ko load karna
                PyObject pyObject = py.getModule("test_script"); 
                
                // us file ke andar "get_message" function ko call karna
                PyObject result = pyObject.callAttr("get_message"); 

                // Python se aaye result ko Toast me dikhana
                Toast.makeText(MainActivity.this, "Python says: " + result.toString(), Toast.LENGTH_LONG).show();
                
            } catch (Exception e) {
                // Agar koi error aaye toh wo bhi dikh jaye
                Toast.makeText(MainActivity.this, "Error: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }
}
