# 1. Social Engineering & Phishing Suite
    Advanced SMTP Spoofing Suite (smtp_gui.py): Mass-phishing tool with custom SMTP relay routing, STARTTLS/SSL, dynamic HTML templates, attachment bundling, and dynamic CSV-based spear-phishing variable injection.
    SMS Spoofing Suite (sms_gui.py): SMS dispatcher utilizing Twilio HTTP APIs, direct SIP trunks, and email-to-SMS gateways, complete with dynamic variable injection for spear-phishing.
    Deepfake Vishing Suite (vishing_gui.py): An automated voice phishing tool using gTTS and SIP protocols (sip_client.py) to stream generated audio payloads directly to target phone numbers.
    iMessage Injector (imessage_gui.py): Uses native macOS AppleScript (osascript) bridging to mass-dispatch "blue-bubble" iMessages to Apple IDs or phone numbers. 
    Evil Twin / Rogue AP (evil_twin_gui.py): Automates hostapd and dnsmasq for rogue Wi-Fi deployment, features an integrated captive portal web server, and includes a built-in Deauth Engine using aireplay-ng.
    Malicious QR Generator (qr_gui.py): Rapid physical asset generation tool for crafting QR codes pointing to payload drops.

# 2. Adversary-in-the-Middle (AitM) & Web Staging
    AitM Proxy & Harvester (web_stager_gui.py): A transparent HTTP/HTTPS proxy that intercepts authentication flows. It features real-time credential/cookie parsing, dynamic HTML/JavaScript payload injection (e.g., BeEF hooks), and custom SSL/TLS certificate handling.
    Root Certificate Installer (cert_installer.py): A post-exploitation script that automates the addition of custom CA certificates to Windows, macOS, and Linux system trust stores to bypass browser SSL warnings.

# 3. Command & Control (C2) & Agents
    Async HTTP C2 Server (c2_server.py): An asynchronous Command & Control server handling task queuing and AES-256-GCM + Base64 encrypted callbacks.
    Native Phantom Agent (phantom_agent.c): A highly stealthy C-based payload featuring process masking (prctl), AES-256-GCM + Base64 encrypted communications, arbitrary shell execution, and built-in commands for Android content provider exfiltration (SMS and call logs).

# 4. Android Enumeration, LPE & Exploitation
    Deep System Auditors (linux-enum1.c, android-enum2.c, android-enum3.c): High-performance C binaries that map the Android attack surface, auditing kernel hardening mitigations, SELinux domains, mount points, SUID binaries, and vulnerable device nodes (e.g., /dev/binder, /dev/mali0).
    Mass CVE Correlation Engine (android-cve-lookup.c): An offline database of 260+ Android CVEs that fingerprints the target device and cross-references it against known vulnerabilities (e.g., Dirty Pipe, Dirty Cred, Binder UAFs).
    APK Trust Store Patcher (apk_trust_patcher.py): Automates the decompilation of target APKs to inject a rogue Network Security Configuration (<certificates src="user" />), forcing the app to trust user-installed CA certificates.
    Universal SSL Shatter Hook (frida_universal_ssl_bypass.js): A Frida dynamic instrumentation script that hooks X509TrustManager, OkHttp3, and TrustKit in memory to bypass SSL pinning.
    Native APK Generator Pipeline (build_lpe_apk.py, android_payload_generator.py): Tools to cross-compile C payloads into shared objects (.so) via the Android NDK and embed them into APKs (or build fresh Python/Kivy APKs via Buildozer).

# 5. Hardware & Protocol Exploitation
    Bluetooth OBEX Delivery (send_obex.py): Automates payload delivery over Bluetooth using the Object Push Profile (OPP).
    Bluetooth Protocol Probing & AT Injection (probe_ch4_v2.py, test_bluetooth_hfp.py, test_bluetooth_samsung_at.py): Scripts designed to probe RFCOMM channels, execute initialization handshakes, and inject malicious AT commands (e.g., Samsung PACM knock sequences).
    Android Open Accessory (AOA) HID Injection (aoa_hid_direct.py, aoa_hid_unlocker.py): Forces an Android device into Accessory Mode to emulate a physical USB keyboard and inject keystrokes (e.g., PIN unlocking or prompt acceptance).
    Low-Level MTP Discovery (mtp_discovery.py): Interacts directly with USB endpoints to query Media Transfer Protocol (MTP) storage objects.

# 6. Post-Exploitation & Automated Exfiltration
    Auto-Exfil Engine (exfil_gui.py): Automated harvesting of high-value databases (Chrome cookies, WhatsApp, Signal, SSH keys) from compromised devices.
    Persistence Manager (persistence_gui.py): Automated installation of root/system-level persistence mechanisms (Magisk modules, systemd, cron).
    Network Pivot & Routing (pivot_manager.py): Deployment of SOCKS5 proxies (e.g., Chisel) over C2 channels for internal network pivoting.

# 7. Advanced Evasion & Packing
    Polymorphic Shellcode Packer (shellcode_generator.py): In-memory XOR decoder stub generation for ARM64 and x86_64 payloads.
    APK Polymorphic Crypter (apk_crypter.py): Deep Smali string encryption engine to defeat static YARA rules and hide C2 configurations.

# 8. Future Roadmap (Planned Capabilities)
    iOS & macOS Ecosystem: Expansion of Apple-specific vectors including Safari WebKit stagers and local privilege escalation chains.
    Hardware & Close Access Expansion: NFC cloning/injection and automated Wi-Fi Pineapple/Karma integrations.
    Cloud & Container Escapes: Automated credential harvesting from AWS/GCP/Azure instance metadata and Kubernetes lateral movement.
