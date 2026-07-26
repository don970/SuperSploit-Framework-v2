# Architectural Analysis: Apple Zero-Day Hybrid Weaponization

## 1. Native macOS Bridging (`osascript`)
**Component:** `imessage_gui.py` & `se_imessage_injector.py`

**Mechanism:**
To dispatch malicious "blue-bubble" payloads seamlessly, the framework bridges directly into the macOS operating system's native IPC (Inter-Process Communication) via AppleScript. 
By wrapping `osascript -e` in a Python subprocess, the framework silently commandeers the background `Messages` daemon. It authenticates through the operator's active Apple ID, allowing for massive, rate-limit-evading bulk dispatches to target phone numbers or iCloud emails.

## 2. Dynamic C-Template Injection (CVE-2026-20700)
**Component:** `cve_2026_20700_dyld_cache.py`

**Mechanism:**
Standalone C exploits typically suffer from hardcoded IP addresses, requiring the operator to manually modify source code before compilation. 
SuperSploit solves this using "Hybrid Weaponization":
1. **Generation:** The `ShellcodeGenerator` crafts PIE-compliant, perfectly aligned ARM64 reverse TCP shellcode using the active `LHOST`/`LPORT` variables.
2. **Injection:** The Python weaponizer reads the raw C exploit template, locates the `unsigned char payload[]` buffer using regular expressions, and injects the raw hex bytes directly into the C source code in memory.
3. **Compilation:** The framework immediately triggers the `aarch64-linux-gnu-gcc` cross-compiler.

**Impact:** The operator can launch complex, memory-corrupting iOS/macOS 0-days directly from the SuperSploit prompt just as easily as launching a Python script, with the framework handling all architecture alignment and linkage in the background.