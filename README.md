<p align="center">
  <img src="./.data/.assets/Logo-v2.png" alt="SuperSploit Framework Logo" width="500"/>
</p>

<h1 align="center">SuperSploit Framework v2</h1>

<p align="center">
  <strong>A Modern, Stealth-Focused C2 & Exploitation Framework for Elite Red Teams.</strong>
</p>
<p align="center">
  <em>From Recon to Root, Undetected.</em>
</p>

---

> SuperSploit is an advanced, stealth-focused exploitation and Command & Control (C2) framework built for elite red teamers and penetration testers. It specializes in **fileless payload execution**, **in-memory C2**, **hybrid weaponization**, and **comprehensive Android targeting**, providing a seamless, automated pipeline from high-speed reconnaissance to deep post-exploitation.

> By fusing an asynchronous, highly concurrent Recon Engine with an intelligent, multi-dimensional Suggestion Engine and a resilient Cryptography System, SuperSploit significantly reduces operator workload while evading modern signature-based detection mechanisms.

---

## 💎 SuperSploit Pro

SuperSploit Pro is a premium extension of the framework designed for professional security firms and high-tempo red team engagements. It features a hardened, remote-controlled security architecture to protect elite intellectual property.

### 🛡️ Advanced Security Engine
*   **Proprietary Binary Validation:** Core licensing logic is anchored in a compiled C-based **Security Engine** (`supersploit_auth`), moving validation outside of easily patched Python source code to defeat local cracking attempts.
*   **Multi-Factor Environmental Anchoring:** Licenses are cryptographically locked to a unique fingerprint including **Hardware ID (HWID)**, **Software ID (SWID)**, **External IP**, **Geographic Region**, and **Timezone**.
*   **Remote Policy Enforcement:** Real-time synchronization with a GitHub-hosted security manifest allows for instant global revocation of leaked keys and dynamic remote hardware locking.
*   **Activation Telemetry:** Built-in support for Discord/Slack Webhooks provides developers with real-time alerts for every license activation, complete with machine fingerprints and network metadata.

### 🪙 License Tiers
- **Individual Pro:** Unlock the full suite of 0-day modules and advanced stealth features.
- **Red Team:** Collaborate with up to 5 operators, featuring polymorphic signature rotation and priority research access.
- **Enterprise:** Full custom integration, dedicated support, and private C2 infrastructure.

For more information, see the [Pro License Agreement](./docs/Legal/PRO_LICENSE_AGREEMENT.md) and [Pro Pricing](./docs/Legal/PRO_PRICING.md).

---

## 🚀 Core Pillars & Architecture

### 👻 **Stealth & Evasion**
SuperSploit is engineered from the ground up for high-tier operational security and detection bypass.
*   **Polymorphic Signature Rotation:** The `native_apk_generator` automatically randomizes native library names (e.g., `libcore_x72b9a.so`) and JNI method names for every build, defeating static Play Protect signatures.
*   **In-Memory Execution Pipeline:** Python modules are executed directly in RAM, while Linux C binaries use anonymous memory file descriptors (`memfd_create`), leaving no trace on the target filesystem.
*   **Advanced Anti-Analysis:** Native payloads implement **Environment Pinning**, utilizing `ptrace` and uptime checks to detect and gracefully exit in the presence of debuggers, emulators, or sandboxes.
*   **Opportunistic OLLVM Integration:** Support for **Obfuscator-LLVM** allows for Control Flow Flattening and Instruction Substitution on all C-based payloads, rendering them nearly impossible to decompile.
*   **Network Domain Fronting:** The native HTTPS fetcher supports SNI-masking via a `FRONT_DOMAIN` (e.g., Cloudflare), hiding C2 entropy within legitimate, high-reputation CDN traffic.
*   **Resilient C2 Cryptography:** All communications are wrapped in a custom TLS tunnel with layered XOR + Base64 obfuscation keyed to the active session.

### 📱 **Advanced Android Arsenal**
SuperSploit provides an unparalleled suite of tools for compromising and persisting on modern Android environments.
*   **Native APK Generation:** A sophisticated automated pipeline (`native_apk_generator`) injects custom C payloads into an Android Shared Object library (`libmain.so`) using NDK cross-compilation. It repacks, aligns, and signs the final APK, with the payload executing via a JNI-detached POSIX thread for a guaranteed ANR-free user experience.
*   **Versatile Payload Architectures:**
    *   **DRS:** A reverse shell disguised as a Flappy Bird game, complete with extensive data exfiltration commands (`dump_sms`, `dump_calls`, `dump_chrome`, `dump_wifi`, and more).
    *   **Beacon:** A deep-stealth agent that periodically polls C2 for tasks using XOR-encrypted HTTP beacons via specific URI routing (`GET /file`, `POST /rfile`).
    *   **Rootkit:** A fully functional mock SuperUser root manager application supporting silent privilege escalation (e.g., Dirty Pipe LPE) and background persistence via **Magisk `service.d` (Golden Path)**.
*   **Encrypted Native Agents:** The **SuperSploit Phantom Agent** provides an ultra-lightweight, 100% native C alternative to APKs, featuring process masking, anti-debug, and XOR+Base64 encrypted C2.
*   **Deep Post-Exploitation Enumeration:** Native C enumeration suites (`android_lpe_enum.c` and `android-enum3.c`) perform offline CVE mapping, network stack auditing, virtualization detection, and extract crucial target information directly into a persistent central persona database.

### 🎭 **Advanced Delivery & OSINT Suite (2026 Upgrade)**
SuperSploit now features a collection of stylish GUI-based standalone tools for payload delivery and intelligence gathering.
*   **SuperSploit Mailer (GUI):** An advanced SMTP delivery system with live composition, .EML template loading, and built-in spoofing logic.
*   **SMS Spoofing Suite (GUI):** A multi-protocol delivery engine supporting commercial APIs (Twilio/Sinch), Direct SIP (VoIP), and Free Email-to-SMS fallback gateways.
*   **Web Stager & AitM (GUI):** Advanced harvester supporting static templates and live **Adversary-in-the-Middle (AitM)** proxying for real-time MFA and session cookie interception.
*   **Mimic Vishing Suite (GUI):** Deepfake voice-spoofing module with integrated TTS and SIP audio streaming for automated, voice-spoofed social engineering calls.
*   **Deep Metadata Scraper (GUI):** Extract hidden intelligence from documents (PDF/Office) and images (EXIF/GPS). Automatically uncovers embedded URLs and email addresses for target footprinting.

### 🎯 **Automated Recon & Targeting**
The framework accelerates the discovery phase using highly concurrent tools paired with a robust, synchronized database.
*   **Asynchronous Port Scanner:** A high-speed, `asyncio`-driven scanner capable of sweeping thousands of ports concurrently. It implements Dual-Probe Service Detection (passive banner grabbing followed by active HTTP GET probes) and seamlessly parses full CIDR ranges.
*   **Protocol Auto-Detection:** The C2 listener now automatically distinguishes between TLS and lightweight XOR-only connections, ensuring stable callbacks for both APK and Native C agents.
*   **Smart Compiler Logic:** The `compile` command now automatically detects SuperSploit placeholders (`LHOST`, `XOR_KEY`) and injects active C2 configuration on-the-fly, while applying legacy Android linker compatibility.
*   **Deep Analysis Suggestion Engine:** A `post_recon_hook` automatically correlates newly discovered target data with the exploit database. It utilizes a multi-factor scoring system to identify high-confidence vulnerabilities (CVE matching, Kernel matching, and Regex banner extraction).
*   **Exhaustive OSINT Suite:** Perform automated social media and web reconnaissance via background dorking, phone lookups, and email searches, pushing discovered intelligence directly to persistent Profile/Target records and generating comprehensive PDF reports.
*   **Intelligent State & Workspace Management:** An asynchronous sync mechanism seamlessly merges the in-memory target cache with the persistent `targets.json` and internal SQLite databases (`signatures.db`, `services.db`). Fully isolated workspaces ensure memory safety across separate engagements.

### 🧩 **Hybrid Weaponization & Modularity**
SuperSploit features a unique metadata parser (`#!#!#!`) that allows operators to rapidly develop custom exploits and payloads in **Python**, **C**, and **Bash**.
*   **Dynamic C-Code Weaponization:** Python "Weaponizer" wrappers dynamically inject framework variables (LHOST, LPORT) into C source code templates before cross-compiling them on the fly (e.g., producing PIE-compliant ARM64 shellcode for iOS exploits or the CVE-2026-20700 Apple zero-day suite).
*   **Universal Payload Generation:** A powerful engine ingests raw scripts, auto-injects networking values, obfuscates classes and functions, and generates web-safe Base64 Python one-liners directly mapped to the active C2 listener.
*   **Interactive Modern CLI:** Features dynamic tab completion, workspace management, background job control (`jobs kill <id>`), and integrated `rich` tables for fluid, stylized terminal interaction.

---

## 🛠️ Quick Start Guide

Launch the framework and display the main help menu:
```sh
./SuperSploit.py
[SuperSploit]: help all
```

### Standard Attack Workflow
```sh
# 1. Search for a module using the fast, cached YAML search engine
[SuperSploit]: search recon smb

# 2. Load the module into the interactive prompt
[SuperSploit]: use recon 1

# 3. View and set parameters, updating the internal SQLite database
[SuperSploit]: show options
[SuperSploit]: set R_HOST 192.168.1.50

# 4. Execute the recon module (runs in an isolated subprocess if root is required)
[SuperSploit]: run

# 5. Let the Deep Analysis Engine correlate findings and suggest exploits
[SuperSploit]: suggest
[SuperSploit]: use exploit 1
[SuperSploit]: exploit

# 6. Interact with the encrypted C2 session
[SuperSploit]: sessions -i 1
Session 1> load /path/to/post_exploit/keylogger.py
```

---

## 📚 Documentation & Configuration

- **Global Variables**: Review `.data/.help/vars` for all configurable framework variables.
- **Project AI Memory**: See `gemini.md` for historical and architectural context.
- **Changelog**: Reference `CHANGELOG.md` under the `[Unreleased]` section for recent updates.
- **Help Documentation**: All help files are stored in `.data/.help`.

---

### ⚠️ **Disclaimer**
SuperSploit is a professional security tool designed strictly for authorized penetration testing, red teaming, and educational purposes. Unauthorized use of this software on any system, network, or device is illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program.