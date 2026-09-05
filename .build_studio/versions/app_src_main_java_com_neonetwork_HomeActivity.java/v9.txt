
package com.neonetwork;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.EditText;

public class HomeActivity extends Activity implements TextWatcher {

    private EditText etHomeSearch;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.home);

        initViews();
        setupSearchListener();
    }

    private void initViews() {
        etHomeSearch = findViewById(R.id.et_home_search);
    }

    private void setupSearchListener() {
        etHomeSearch.addTextChangedListener(this);
    }

    @Override
    public void beforeTextChanged(CharSequence s, int start, int count, int after) {
        // Not needed for this example
    }

    @Override
    public void onTextChanged(CharSequence s, int start, int before, int count) {
        // Handle search text changes here
    }

    @Override
    public void afterTextChanged(Editable s) {
        // Not needed for this example
    }
}
