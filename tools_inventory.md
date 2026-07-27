# SuperSploit Framework - Comprehensive Tools Inventory

*This document serves as the master index for all standalone utilities, Pro-Tier GUI applications, and weaponization scripts residing in the `source/tools/` directory. It is actively maintained to track development progress and assist with the integration of the upcoming `ToolEngine`.*

---

## 🎣 Social Engineering & Delivery (`/SE`, `/Web`, `/SMTP`)
*Tools handling adversarial payload delivery, phishing, and adversary-in-the-middle attacks.*

- **Web Stager & AitM Proxy** (`Web/web_stager_gui.py`): Interactive GUI for live session hijacking, credential harvesting, and rogue DNS patching.
- **Evil Twin AP Deployer** (`SE/evil_twin_gui.py` & `SE/se_captive_portal.py`): Automates `hostapd` and `dnsmasq` to deploy Rogue APs and captive portals.
- **Malicious QR Generator** (`SE/qr_gui.py` & `SE/se_qr_generator.py`): Generates physical asset drops (QR codes) pointing to C2 payloads.
- **Advanced SMTP Spoofing Suite** (`SMTP/smtp_gui.py` & `SE/se_smtp_spoofer.py`): High-end email spoofing engine with HTML templating, attachment binding, and direct SMTP relay configurations.
- **iMessage / RCS Injector** (`SE/imessage_gui.py` & `SE/se_imessage_injector.py`): Bridges via macOS `osascript` to natively dispatch Apple iMessages to target IDs.
- **Fake SMTP Server** (`SMTP/fake_smtp.py` & `SMTP/smtp_client.py`): A local mock SMTP server used for testing phishing delivery pipelines offline.
- **DNS Patcher GUI** (`SE/dns_patcher_gui.py`): Active UDP port 53 interception and local DNS spoofing interface.

## 📞 VoIP, SMS & Deepfake Vishing (`/VoIP`)
*Tools dedicated to telecommunications abuse and voice-based social engineering.*

- **SMS Spoofing Suite v2.0** (`VoIP/sms_gui.py` & `SE/se_sms_sender.py`): Deep interaction SMS sender using Twilio (HTTP), Direct SIP, or Free Carrier Relays.
- **Deepfake Vishing Suite** (`VoIP/vishing_gui.py`): Uses text-to-speech (gTTS) or custom WAV files coupled with a direct SIP client to launch automated, spoofed voice calls.
- **SIP Infrastructure** (`VoIP/sip_client.py`, `VoIP/sip_server.py`, `VoIP/fake_voip.py`): Core routing components and mock gateways for managing VoIP and SMS traffic.
- **Relay Gateways** (`VoIP/free_relay.py`, `VoIP/paid_relay.py`): Scripts managing carrier-to-carrier email-to-sms relaying and direct SIP trunk proxies.
- **VoIP Server Setup** (`VoIP/setup_voip_server.sh`): Automates the deployment of an Asterisk PBX for private standalone SIP MESSAGE delivery.

## 🔎 Advanced OSINT & Reconnaissance (`/OSINT`)
*Graphical intelligence gathering and correlation engines.*

- **Credential Breach Monitor** (`OSINT/breach_gui.py`): Queries HIBP and generates intelligent Pastebin dorks for target identities.
- **Phone Intelligence Suite** (`OSINT/phone_osint_gui.py`): Validates numbers, maps carriers, detects burner/VoIP usage, and generates OSINT pivots for WhatsApp/Telegram.
- **Crypto Ledger Tracer** (`OSINT/crypto_gui.py`): Interrogates BTC/ETH blockchains to track balances and map counterparty transaction histories.
- **Domain & Infrastructure Scanner** (`OSINT/domain_gui.py`): Enumerates DNS records, WHOIS data, and uses Certificate Transparency (crt.sh) / SecurityTrails to map subdomains.
- **Deep Metadata & IOC Scraper** (`OSINT/metadata_gui.py`): Recursively hunts through images (EXIF/GPS), PDFs, and Office docs, while performing deep regex scraping for AWS/Google API keys.
- **Deepfake & Synthetic Media Verifier** (`OSINT/deepfake_gui.py`): Performs Error Level Analysis (ELA) and proprietary EXIF checks to mathematically score the likelihood of an image being AI-generated.
- **Advanced Reverse Image OSINT** (`OSINT/reverse_image_gui.py`): Stages images to ephemeral servers and concurrently launches Google Lens, Yandex, Bing, TinEye, and SauceNAO correlations.

## 📱 Android/Linux Enumeration & Analysis (`/android_enum`, `/linux_enum`)
*Static/Dynamic analysis and native C-based device auditors.*

- **APK SAST Scanner** (`android_enum/sast_gui.py`): Decompiles APKs (via apktool) and greps Smali/Manifests for exported components, weak crypto, and hardcoded secrets.
- **APK DAST Scanner** (`android_enum/dast_gui.py`): Hooks into running apps using Frida to dynamically intercept crypto keys, network requests (OkHttp3), and Intents.
- **Ultra-Enum Android Security Audit Suite** (`android_enum/android-enum3.c` & `android_enum/android-enum2.c`): Extremely deep native C auditors that map the Android LPE surface (Binder, KGSL, mount points, containers, SUIDs).
- **MASS-CVE Correlation Engine** (`android_enum/android-cve-lookup.c`): A standalone C binary packing a database of over 260+ Android CVEs to perform rapid offline exploit matching against the target's kernel and SDK.
- **Exhaustive Linux Security Audit Suite** (`linux_enum/linux_enum.c` & `linux_enum/linux-enum1.c`): Native C auditor for standard Linux distributions checking MAC (SELinux/AppArmor), Kernel Hardening (KASLR), and correlating 1-days like Dirty Pipe or PwnKit.

## 💻 Command & Control & Post-Exploitation (`/c2`, `/PostExploitation`)
*Session handling, persistence, and lateral movement.*

- **Advanced C2 Session Manager** (`PostExploitation/c2_gui.py`): The master GUI for interacting with compromised sessions. Handles module deployment, shell access, and file I/O.
- **Network Pivot & Routing** (`PostExploitation/pivot_manager.py`): Deploys and manages Chisel to create reverse SOCKS5 proxies through compromised hosts.
- **Persistence Manager** (`PostExploitation/persistence_gui.py`): Generates persistent artifacts (Magisk Modules for Android, Systemd/Cron for Linux) to survive reboots.
- **Auto-Exfil Engine** (`PostExploitation/exfil_gui.py`): Generates chained bash commands to quietly harvest Chrome cookies, WhatsApp DBs, Signal keys, and SSH keys.
- **SUDO Prompt Hijacker** (`PostExploitation/sudo_password_harvester.sh`): Injects an alias into bashrc/zshrc to present a fake sudo prompt, log the password, and pass execution to the real sudo binary.
- **Async HTTP C2 Server** (`c2/c2_server.py`) & **Phantom Agent** (`c2/phantom_agent.c`): A fully asynchronous C2 architecture using AES-256-GCM encryption with a native C-based implant.
- **C2 Listener Test Wrapper** (`c2/run_listener.py`): Testing wrapper to initiate the primary Python listener.

## ⚙️ Payload Generation & Cryptography (`/android_payload_generators`, `/cryptography`)
*Weaponization and obfuscation pipelines.*

- **Native APK Generator** (`android_payload_generators/build_lpe_apk.py`): Wrapper for generating native NDK-compiled shared object payloads.
- **Buildozer Payload Generator** (`android_payload_generators/android_payload_generator.py`): Generates Python/Kivy-based Android payloads with dynamic `buildozer.spec` creation.
- **APK Polymorphic Crypter** (`android_payload_generators/apk_crypter.py`): Injects a custom Smali decryption class and dynamically encodes all strings inside an existing APK to bypass static AV signatures.
- **APK Trust Store Patcher** (`android_payload_generators/apk_trust_patcher.py`): Modifies the `network_security_config.xml` of an APK to force it to trust user-installed CA certificates (crucial for MitM).
- **XOR Encrypter** (`cryptography/xor_encrypter.py` & `_xor_encrypter.py`): Standalone utility to encrypt/decrypt payloads and C2 traffic using the framework's symmetric XOR keys.

## 🔌 Hardware, Wireless & Bluetooth (`/Hardware`, `/HID_USB`, `/BLuetooth`)
*Close-proximity and physical hardware attack vectors.*

- **NFC Attack Suite** (`Hardware/nfc_gui.py`): Uses `nfcpy` to read and maliciously write NDEF records (URI web drops or Text SE payloads) to NFC tags.
- **Wi-Fi Pineapple & Karma Integration** (`Hardware/pineapple_gui.py`): Connects to Hak5 Pineapples via REST API to automate PineAP, Karma, and rogue beacon deployments.
- **HID USB Unlockers** (`HID_USB/aoa_hid_direct.py` & `HID_USB/aoa_hid_unlocker.py`): Leverages Android Open Accessory (AOA) mode to register a virtual keyboard and blindly inject keystrokes (ChoiceJacking).
- **MTP Discovery** (`HID_USB/mtp_discovery.py`): Low-level USB fuzzer to discover locked storage objects over MTP.
- **Bluetooth OBEX Push** (`BLuetooth/send_obex.py`): Pushes payloads to target devices over Bluetooth channel 12 without pairing.
- **Bluetooth Channel Probers** (`BLuetooth/probe_ch4_v2.py`): Probes hidden Bluetooth RFCOMM channels for vendor-specific vulnerabilities.

## 🛠️ Kernel & Exploit Development Utilities (`/AndroidKernel`, `/miniFetchers`, `/adb_deployment_scripts`, `/Exploit-testets`)
*Tools to assist in active exploit research and testing.*

- **KASLR Calculator** (`AndroidKernel/kaslr_calculator.py`): Computes Kernel Address Space Layout Randomization slides from leaked pointers.
- **ADB Proc Dumper** (`AndroidKernel/adb_proc_dump.py`): Automates dumping world-readable `/proc` files via ADB to hunt for info leaks.
- **Minimal Fetchers** (`miniFetchers/minifetch.c` & `miniFetchers/minish.c`): Ultra-tiny C-based HTTP/HTTPS downloaders (compiled into payloads) that use direct sockets and OpenSSL, bypassing the need for `curl`/`wget`. `minish.c` supports Domain Fronting.
- **ADB LPE Deployer** (`adb_deployment_scripts/deploy_lpe.sh`): Bash script to automate the pushing and sequential execution of exploit chains over ADB.
- **Exploit Test Suites** (`Exploit-testets/`): Includes Python wrappers and C source testers for verifying `AF_PACKET` behavior, `openssl` imports, AT modem injection, and Bluetooth interactions.