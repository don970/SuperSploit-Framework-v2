<p align="center">
  <img width="4400" height="2400" alt="Logo-v2" src="https://github.com/user-attachments/assets/9a9822c9-f0ee-4b7c-8ae8-625bcbf44e0a" />
</p> 

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+"></a>
  <a href="https://github.com/don970/SuperSploit-Framework-v2"><img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg" alt="Maintenance"></a>
</p>
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
## 📑 Table of Contents
- [🚀 Ecosystem Capabilities](#-ecosystem-capabilities)
- [⚙️ Core Framework Architecture](#️-core-framework-architecture)
- [📦 Installation & Setup](#-installation--setup)
- [🛠️ Quick Start Guide](#️-quick-start-guide)
- [📚 Documentation & Configuration](#-documentation--configuration)
- [⚠️ Disclaimer](#️-disclaimer)
## 🚀 Ecosystem Capabilities

### 🍏 Apple iOS & macOS Ecosystem
### 🤖 Android & Linux Exploitation
An end-to-end weaponization pipeline bypassing modern EDR and AV engines:
* **Polymorphic APK Crypter:** Deep Smali string encryption and dynamic JNI method rotation to defeat static YARA signatures.
* **Native C Payload Generation:** Cross-compiles C payloads via the Android NDK, linking them into trojanized, legitimate APKs via JNI.
* **Mass CVE Correlation Engine:** Offline database of 260+ vulnerabilities (e.g., Dirty Pipe, Dirty Cred) that fingerprints SoC, kernel, and SDK to pinpoint specific LPE vectors.
* **"Ultra-Enum" System Auditor:** High-performance C auditor mapping container escapes, kernel leaks (`/proc/kallsyms`), and vulnerable device nodes (`/dev/binder`, `/dev/mali0`).
* **APK SAST & DAST Scanners:** Integrated static analysis for hardcoded secrets and Frida-powered dynamic instrumentation to intercept cryptography, intents, and network traffic in real-time.
* **Self-Contained Crypto:** Native Android payloads are compiled with statically linked OpenSSL, ensuring AES-256-GCM execution works flawlessly regardless of OS restrictions.

### 📻 Hardware & Close Access
Physical airspace and proximity vectors natively integrated into the C2 environment:
* **NFC Attack Suite:** Read, clone, and inject malicious NDEF records (like AitM Web Stager URIs) into physical NFC tags using `nfcpy`.
* **Pineapple Automation Engine:** Remotely orchestrate Hak5 Wi-Fi Pineapples via REST API to trigger PineAP, Karma attacks, and SSID spoofing campaigns.

### 📡 Advanced Command & Control (C2)
* **Asynchronous HTTP Beacons:** Powered by Python's `asyncio` for zero-bottleneck concurrency.
* **Military-Grade Cryptography:** 100% of C2 traffic is encapsulated in **AES-256-GCM** authenticated encryption wrapped inside Base64 and TLS, completely blinding packet inspectors to the payloads.
* **Environment Pinning:** Native agents utilize `ptrace(PTRACE_TRACEME)` to detect debuggers/sandboxes, silently terminating before exposing cryptographic keys.

### 🎣 Social Engineering & Phishing
* **Advanced SMTP Suite:** Mass-phishing engine with HTML template injection, attachment bundling, and real-time `csv.DictReader` spear-phishing variable replacement.
* **Multi-Stage MFA Web Stager:** Adversary-in-the-Middle (AitM) proxy that silently harvests credentials via background `fetch()` requests, simulates TOTP/SMS 2FA prompts, and intercepts session tokens before seamlessly redirecting victims to legitimate portals.
* **iMessage Zero-Click Delivery:** Bridges native macOS `osascript` to commandeer the `Messages` daemon, dispatching payloads directly into the iOS BlastDoor sandbox to bypass carrier filtering.
* **SMS & Vishing Deepfakes:** Delivers SMS payloads via SIP injection, Twilio, or Free Relays. Incorporates an automated gTTS voice-phishing engine over VoIP.
* **Physical Vectors & Close-Access Lures:** Automates `hostapd`/`dnsmasq` for Evil Twin credential harvesting with built-in `aireplay-ng` deauthentication, and generates malicious QR codes for physical payload drops.

### 🥷 Post-Exploitation & Exfiltration
* **Auto-Exfil Engine:** Instantly generates compressed payloads to harvest Chrome/Firefox cookies, WhatsApp message stores (`msgstore.db.crypt14`), Signal databases, and SSH keys.
* **Persistence Manager:** Automated installation of systemless root backdoors via Magisk modules, Linux `systemd`, or `cron`.
* **Proxy Pivot Routing:** Automated SOCKS5 tunneling (via Chisel) directly through active C2 connections to pivot into internal corporate networks.

---

## ⚙️ Core Framework Architecture

* **ToolEngine (Pro):** A planned unified execution pipeline natively bridging standalone GUI and CLI modules (OSINT, Scanners, Post-Ex) directly into the main SuperSploit ecosystem, standardized with the new "Sentry Dark Theme".
* **Suggestion Engine (Auto-Suggest):** Uses a multi-factor heuristic algorithm to analyze targets (OS, Kernel, Services, Banners) and immediately suggest high-probability exploits.
* **Hybrid Weaponizer:** Reads raw C exploit templates, calculates dynamic register alignments, and injects custom-generated Polymorphic XOR-packed shellcode directly into source files prior to cross-compilation.
* **Intelligent State & Workspace Management:** An asynchronous sync mechanism seamlessly merges the in-memory target cache with the persistent `targets.json` and internal SQLite databases.

---

## 📦 Installation & Setup

SuperSploit is optimized for Unix-based systems (Linux, Kali, ParrotOS, macOS) and requires **Python 3.8+**.

```sh
# 1. Clone the repository
git clone https://github.com/don970/SuperSploit-Framework-v2.git
cd SuperSploit-Framework-v2

# 2. Install Python dependencies
pip3 install -r setup/requirements.txt

# 3. Run the automated installer (sets up directories, DBs, and permissions)
chmod +x setup/install.sh
sudo ./setup/install.sh
```

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
- **Architecture Analyses**: Deep-dive developer documentation, including exhaustive tool inventories, exploit breakdowns, and payload delivery mechanics, are located in `docs/development/analyzes/`.

---

### ⚠️ **Disclaimer**
SuperSploit is a professional security tool designed strictly for authorized penetration testing, red teaming, and educational purposes. Unauthorized use of this software on any system, network, or device is illegal. The developers assume no liability and are not responsible for any misuse or damage caused by this program.
