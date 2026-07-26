FRIDA_PAYLOADS = {
    "None": "",
    "Bypass SSL Pinning": """
        try {
            var array_list = Java.use("java.util.ArrayList");
            var ApiClient = Java.use('com.android.org.conscrypt.TrustManagerImpl');
            ApiClient.checkTrustedRecursive.implementation = function(a1, a2, a3, a4, a5, a6) {
                send("[+] Bypassing SSL Pinning (TrustManagerImpl)");
                return array_list.$new();
            }
        } catch (e) { send("[-] SSL Pinning Bypass failed: " + e); }
    """,
    "Root Detection Spoof": """
        try {
            var RootPackages = ["com.noshufou.android.su", "com.thirdparty.superuser", "eu.chainfire.supersu", "com.topjohnwu.magisk"];
            var ApplicationPackageManager = Java.use("android.app.ApplicationPackageManager");
            ApplicationPackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function(pname, flags) {
                if (RootPackages.indexOf(pname) > -1) {
                    send("[+] Spoofing Root Package check for: " + pname);
                    pname = "com.nonexistent.package";
                }
                return this.getPackageInfo(pname, flags);
            };
        } catch (e) { send("[-] Root Detection Spoof failed: " + e); }
    """,
    "Dump SharedPreferences": """
        try {
            var ContextWrapper = Java.use("android.content.ContextWrapper");
            ContextWrapper.getSharedPreferences.overload('java.lang.String', 'int').implementation = function(name, mode) {
                send("[+] Accessing SharedPreferences: " + name);
                return this.getSharedPreferences(name, mode);
            };
        } catch (e) { send("[-] SharedPreferences hook failed: " + e); }
    """
}