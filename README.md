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

> SuperSploit is an APT-tier, multi-platform exploitation framework designed for elite Red Teams and Security Researchers. It bridges the gap between high-level social engineering, Adversary-in-the-Middle (AitM) staging, and highly evasive hardware/kernel-level exploitation.

> Featuring an intelligent, state-driven database, SuperSploit automatically correlates discovered target vulnerabilities with over 260+ offline CVEs, seamlessly injecting dynamic, polymorphic payloads into targeted applications and memory spaces.

---

## 💎 SuperSploit Pro
SuperSploit Pro is a premium extension of the framework designed for professional security firms and high-tempo red team engagements. It features a hardened, remote-controlled security architecture to protect elite intellectual property.

### 👑 Exclusive Pro Features & Tools
The following advanced modules, graphical interfaces, and weaponization pipelines are strictly gated behind the SuperSploit Pro license:
* **Social Engineering GUI Suite:** Advanced SMTP Spoofing Suite, SMS Smishing Engine, Deepfake Vishing Suite, iMessage/RCS Injector, Evil Twin/Rogue AP, and Malicious QR Generator.
* **Advanced Weaponization & Evasion:** Polymorphic Shellcode Packer, APK Polymorphic Crypter, APK Trust Store Patcher, and the Professional Cross-Arch Compilation Suite.
* **Apple Zero-Day Attack Chain:** Safari WebKit Stager (CVE-2026-10002), iMessage Zero-Click (CVE-2026-10001), AWDL Proximity RCE (CVE-2026-10003), and dyld_shared_cache LPE (CVE-2026-20700).
* **Command & Control (C2) & AitM:** Asynchronous AES-256-GCM HTTP C2 Server, Automated Native Exploitation (`auto_root`), and the AitM Proxy & Web Stager.
* **Post-Exploitation Suite:** Auto-Exfil Engine (SQLite/Cookie harvesting), Persistence Manager (Magisk/systemd/cron), and Proxy Pivot & Routing (SOCKS5 via Chisel).

### 🛡️ Advanced Security Engine
*   **Proprietary Binary Validation:** Core licensing logic is anchored in a compiled C-based **Security Engine** (`supersploit_auth`), moving validation outside of easily patched Python source code to defeat local cracking attempts.
*   **Multi-Factor Environmental Anchoring:** Licenses are cryptographically locked to a unique fingerprint including **Hardware ID (HWID)**, **Software ID (SWID)**, **External IP**, **Geographic Region**, and **Timezone**.
*   **Remote Policy Enforcement:** Real-time synchronization with a GitHub-hosted security manifest allows for instant global revocation of leaked keys and dynamic remote hardware locking.
*   **Activation Telemetry:** Built-in support for Discord/Slack Webhooks provides developers with real-time alerts for every license activation, complete with machine fingerprints and network metadata.

### 🪙 License Tiers
SuperSploit operates under an **Open Core** model.
- **Core Framework:** Licensed under the [MIT License](./LICENSE-CORE).
- **Pro Tier:** Licensed under the [Pro License Agreement](./docs/Legal/PRO_LICENSE_AGREEMENT.md). See [Pro Pricing](./docs/Legal/PRO_PRICING.md) for subscription details.

For a full breakdown of the licensing structure, see the root [LICENSE](./LICENSE) file.

---

## 🚀 Ecosystem Capabilities

### 🍏 Apple iOS & macOS Ecosystem
A complete, native attack chain for the Apple ecosystem:
* **Safari WebKit Stager (CVE-2026-10002):** 1-Click remote code execution via DFG JIT Type Confusion, featuring automatic RWX memory allocation and shellcode execution.
* **iMessage Zero-Click (CVE-2026-10001):** Sandbox escape via malformed HEIF metadata, dispatched flawlessly over native macOS `osascript` bridging.
* **AWDL/AirDrop RCE (CVE-2026-10003):** Proximity-based RCE targeting `sharingd` buffer overflows via raw 802.11 Action Frames.
* **dyld_shared_cache LPE (CVE-2026-20700):** Hybrid weaponized Local Privilege Escalation cross-compiled on the fly for A-Series ARM64 chips.

### 🤖 Android & Linux Exploitation
An end-to-end weaponization pipeline bypassing modern EDR and AV engines:
* **Polymorphic APK Crypter:** Deep Smali string encryption and dynamic JNI method rotation to defeat static YARA signatures.
* **Native C Payload Generation:** Cross-compiles C payloads via the Android NDK, linking them into trojanized, legitimate APKs via JNI.
* **Mass CVE Correlation Engine:** Offline database of 260+ vulnerabilities (e.g., Dirty Pipe, Dirty Cred) that fingerprints SoC, kernel, and SDK to pinpoint specific LPE vectors.
* **"Ultra-Enum" System Auditor:** High-performance C auditor mapping container escapes, kernel leaks (`/proc/kallsyms`), and vulnerable device nodes (`/dev/binder`, `/dev/mali0`).

### 📡 Advanced Command & Control (C2)
* **Asynchronous HTTP Beacons:** Powered by Python's `asyncio` for zero-bottleneck concurrency.
* **Military-Grade Cryptography:** 100% of C2 traffic is encapsulated in **AES-256-GCM** authenticated encryption wrapped inside Base64 and TLS, completely blinding packet inspectors to the payloads.
* **Environment Pinning:** Native agents utilize `ptrace(PTRACE_TRACEME)` to detect debuggers/sandboxes, silently terminating before exposing cryptographic keys.

### 🎣 Social Engineering & Phishing
* **Advanced SMTP Suite:** Mass-phishing engine with HTML template injection, attachment bundling, and real-time CSV spear-phishing variable replacement.
* **SMS & Vishing Deepfakes:** Delivers SMS payloads via SIP injection, Twilio, or Free Relays. Incorporates an automated gTTS voice-phishing engine over VoIP.
* **Evil Twin / Rogue AP:** Automates `hostapd`/`dnsmasq` for credential harvesting with built-in `aireplay-ng` Deauthentication.
* **Web Stager & AitM:** Transparent proxy harvester that sniffs credentials and dynamically injects JavaScript into the victim's DOM.

### 🥷 Post-Exploitation & Exfiltration
* **Auto-Exfil Engine:** Instantly generates compressed payloads to harvest Chrome/Firefox cookies, WhatsApp message stores (`msgstore.db.crypt14`), Signal databases, and SSH keys.
* **Persistence Manager:** Automated installation of systemless root backdoors via Magisk modules, Linux `systemd`, or `cron`.
* **Proxy Pivot Routing:** Automated SOCKS5 tunneling (via Chisel) directly through active C2 connections to pivot into internal corporate networks.

---

## ⚙️ Core Framework Architecture

* **Suggestion Engine (Auto-Suggest):** Uses a multi-factor heuristic algorithm to analyze targets (OS, Kernel, Services, Banners) and immediately suggest high-probability exploits.
* **Hybrid Weaponizer:** Reads raw C exploit templates, calculates dynamic register alignments, and injects custom-generated Polymorphic XOR-packed shellcode directly into source files prior to cross-compilation.
* **Intelligent State & Workspace Management:** An asynchronous sync mechanism seamlessly merges the in-memory target cache with the persistent `targets.json` and internal SQLite databases.

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
- **Changelog**: Reference `CHANGELOG.md` under the `[Unreleased]` section for recent updates.
- **Help Documentation**: All help files are stored in `.data/.help`.

---

### ⚠️ **Disclaimer**
SuperSploit is a professional security tool designed strictly for authorized penetration testing, red teaming, and educational purposes. Unauthorized use of this software on any system, network, or device is illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program.