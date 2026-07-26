# SuperSploit Framework - Templates Library (High-Level Overview)

*This document provides a strategic overview of the structural templates, UI stubs, and social engineering lures integrated into the SuperSploit Framework. These files act as the foundational blueprints for the framework's dynamic payload generators and Adversary-in-the-Middle (AitM) web stagers.*

---

## 1. Social Engineering & Web Lures (`templates/web/`)
*Objective: Provide high-fidelity, pixel-perfect HTML/CSS clones of major authentication portals. Designed for seamless integration with the `web_stager_gui.py` AitM proxy and credential harvester.*

### Standard Credential Harvesters
- **`01_CashApp_Auth.html`**: Mobile-optimized Cash App login mimic.
- **`02_PayPal_Security.html`**: Clean, modern PayPal login clone.
- **`03_Google_SSO.html`**: Single Sign-On (SSO) template mimicking Google's OAuth flow.
- **`04_Netflix_Billing.html`**: Dark-themed Netflix login portal.
- **`05_Facebook_Mobile.html`**: Mobile-responsive Facebook login trap.
- **`06_Instagram_Verify.html`**: Instagram verification/login portal.
- **`07_Amazon_Prime.html`**: Amazon retail authentication mimic.
- **`08_Apple_ID.html`**: Apple ID management portal clone.
- **`09_Microsoft_365.html`**: Enterprise Microsoft 365 / Azure AD login mimic.
- **`10_X_Twitter.html`**: Modern X (formerly Twitter) dark-mode login.

### Advanced MFA Interception (Multi-Stage)
- **`11_Microsoft_365_MFA_Advanced.html`**: A two-stage JavaScript payload. Stage 1 captures the username/password and displays a loading spinner. Stage 2 dynamically prompts the user for their 6-digit Authenticator code, transmitting it to the C2 for live session hijacking.
- **`12_GitHub_2FA_Advanced.html`**: Similar to the M365 template, designed to bypass GitHub's mandatory 2FA requirements via dynamic DOM manipulation.

### Utility Web Stagers
- **`payload_download.html`**: A generic "Secure Document Share" portal. Coerces the victim into downloading an embedded payload (e.g., a trojanized APK or PDF) disguised as a secure viewer plugin.
- **`exploit_stage.html`**: An automated redirector. Displays a "Loading..." animation while silently redirecting the victim's browser to an exploit trigger URL (e.g., a WebKit JIT vulnerability endpoint).
- **`google_reset.html` / `cashapp_reset.html`**: Spear-phishing specific templates designed to capture existing passwords under the guise of an emergency password reset.

---

## 2. Payload & Weaponization Templates (`templates/payload/`)
*Objective: Provide the raw source code skeletons and Android application structures used by the framework to dynamically compile custom C2 agents.*

### Kivy / Python Android Agents (`templates/payload/kivy/`)
*These templates are injected with variables (LHOST, LPORT, XOR_KEY) and compiled via `buildozer` to create standalone Android APKs.*
- **`android_drs_template.py`**: The standard Dynamic Reverse Shell (DRS) agent. Wraps the malicious background thread in a fully functional, playable "Flappy Bird" clone (`GameActivity`) to avoid user suspicion.
- **`android_beacon_template.py`**: A low-noise, asynchronous HTTP beacon wrapped in the same Flappy Bird UI. Designed for long-term, stealthy persistence.
- **`android_rootkit_template.py`**: A specialized agent that mimics a "SuperUser Management" application (similar to Magisk/SuperSU). Requests root access upon execution and hides its own launcher icon.
- **`android_messages_template.py`**: An incredibly stealthy UI wrapper that mimics the default Android SMS/Messages application. Generates fake SMS threads locally while the C2 agent runs silently in the background.

### Native C/JNI Android Stubs (`templates/payload/native_gen/`)
*These directories contain complete Apktool project structures (`AndroidManifest.xml`, `smali`, `res`). The `NativeApkGenerator` compiles a C payload into an NDK `.so` library, injects it into these stubs, and repacks them.*
- **`stub_template/`**: A headless, invisible Android service named "Google Play Services Core". Automatically launches the native payload on boot (`RECEIVE_BOOT_COMPLETED`).
- **`game_stub_template/`**: A native Java implementation of the "Sky Jump" (Flappy Bird) game. The native C payload is loaded stealthily via a static JNI `System.loadLibrary("payload")` block during the game's `onCreate()` lifecycle.
- **`messages_stub_template/`**: A native Java implementation of a fake, empty SMS messaging app. Provides a clean, innocuous UI while executing the native payload.
- **`rootkit_stub_template/`**: Requests every dangerous Android permission available (SMS, Contacts, Camera, Location, Root) upon installation. Mimics a root management app.

### Native Exploit Components (`templates/payload/native_gen/`)
- **`native_drs.c`**: The core C-based reverse shell. Features heavy environment pinning (anti-debug, anti-sandbox), XOR cryptography, Base64 encoding, and dynamic module loading via `memfd_create`.
- **`exploit_wrapper.c`**: A bridging template. Allows the framework to take a standalone Linux/Android C exploit (e.g., Dirty Pipe), wrap it in JNI headers, and execute it reliably inside a background thread within a trojanized APK.
- **`phantom_lib.c`**: A constructor-based shared library (`__attribute__((constructor))`). Used to generate Magisk modules that hijack system libraries (like `libvold.so`) for indestructible boot-persistence.

### Cross-Platform Utilities (`templates/payload/misc/`)
- **`c_stager.c`**: An ultra-minimalist Linux C stager. Connects to the C2, downloads a massive Stage 2 binary directly into RAM, and executes it filelessly using `memfd_create`.
- **`cert_installer.py`**: A cross-platform (Windows, macOS, Linux) utility script designed to silently install rogue root CA certificates into the OS trust store, facilitating HTTPS decryption.
- **`frida_universal_ssl_bypass.js`**: A powerful dynamic instrumentation script. When injected via Frida, it shatters TLS certificate pinning boundaries by hooking `X509TrustManager`, `OkHttp3`, and `TrustKit` in memory.

---

## 3. Module Development Skeletons (`templates/recon/`, `templates/exploit/`)
*Objective: Enforce coding standards and metadata formatting for researchers contributing new exploits or scanners to the framework.*

### Reconnaissance Skeleton (`templates/recon/recon.py`)
- Provides the standard `#!#!#!` metadata block required by the Suggestion Engine.
- Implements stealthy, obfuscated dynamic imports (`_so = __import__('soc' + 'ket')`) to evade static Python analysis if dropped on a target disk.
- Defines the standard `Start(args=None)` entry point utilized by the framework's internal `input_handling_engine`.

### Exploit Skeleton (`templates/exploit/exploit.py`)
- Mirrors the Recon skeleton but is pre-configured with tags (`cve`, `target`) specifically tracked by the Exploit Engine.
- Demonstrates how to map the `Start()` execution alias to ensure seamless compatibility with the framework's interactive CLI loop.