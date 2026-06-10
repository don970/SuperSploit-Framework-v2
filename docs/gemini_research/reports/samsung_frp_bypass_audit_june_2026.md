# Audit Report: Samsung Galaxy Tab A8 FRP Bypass & RCE
**Date:** June 7, 2026
**Target:** Samsung Galaxy Tab A8 (Android 11, Kernel 4.4.199)
**MAC:** 48:61:EE:67:C0:0A
**Status:** In Progress (Payload Delivered / Host Blocked)

---

## 1. Executive Summary
This audit focused on identifying and weaponizing attack vectors to bypass Factory Reset Protection (FRP) and achieve Remote Code Execution (RCE) on a locked Samsung tablet. We successfully overhauled the framework's USB exploit suite, upgraded the shellcode generator for Android compatibility, and delivered a malicious media payload via Bluetooth OBEX. While the primary kernel overflow is currently blocked by a host-side USB transfer limit, the secondary LANDFALL vector is active on the device.

## 2. Exploit Analysis & Weaponization

### 2.1 CVE-2021-39685 ("Inspector Gadget")
- **Type:** USB Heap Overflow (Kernel RCE).
- **Weaponization:**
    - Updated `exploits/android/cve_2021_39685_inspector_gadget.py` with automated Samsung VID/PID detection.
    - Integrated `root: "true"` metadata to trigger automated `sudo` elevation.
    - Implemented a post-exploitation `WIPE_FRP` flag that executes `dd` commands against `/dev/block/persistent`.
- **Status:** **Blocked (Host-Side)**. The host machine enforces a 4096-byte limit on USB control transfers, preventing the delivery of the 65,535-byte overflow payload.

### 2.2 CVE-2025-21042 ("LANDFALL")
- **Type:** OOB Write in `libimagecodec.quram.so` (Media Scanner RCE).
- **Delivery:** Successfully delivered `exploit.dng` to the device via Bluetooth OBEX Object Push (Channel 12).
- **Trigger:** Gallery/Media Scanner thumbnail generation.
- **Status:** **Active**. The payload is on the device; trigger success depends on the scanner processing the file.

### 2.3 CVE-2026-20981/83 (Bluetooth AT RCE)
- **Type:** Unauthenticated AT Command Injection via Bluetooth HFP.
- **Handshake:** Successfully established HFP connection on RFCOMM Channel 3.
- **Status:** **Restricted**. Standard AT commands are accepted, but factory/mode-switch commands (`AT+KNOXSTEP`) are currently rejected by the device's secure state.

## 3. Framework Enhancements

### 3.1 Shellcode Generator (`source/core/shellcode_generator.py`)
- **Android Compatibility:** Replaced hardcoded `/bin/sh` with `/system/bin/sh`.
- **Command Execution:** Added `arm64_command_exec(command)` method to dynamically construct ARM64 opcodes for executing arbitrary shell commands via `sh -c`.

### 3.2 Exploit Engine (`source/core/exploit_engine.py`)
- **Privilege Escalation:** Added logic to recognize the `root: "true"` metadata flag. The engine now automatically requests `sudo` elevation for hardware-level exploits (USB/Bluetooth).

## 4. Current Blockers & Next Steps

### 4.1 Blockers

- **USB Host Limit:** The 4KB limit on the current machine's USB stack prevents direct kernel overflow exploitation.

- **MTP Lock:** The filesystem remains restricted despite Browser Trigger (0x9401) acknowledgment, suggesting a more recent patch level.

3. **ADB Activation:** Continue guiding the user to enable USB Debugging via Settings > Software Information > Build Number.
        THIS CANT BE DONE DUBUGGING IS LOCKED OUT BUILD NUMBER DONT TAP. IF YOU TRY TO OPEN APPS IN THE SETTING IT CRASHES THE SETTINGS APP THIS SSSIS PART OF NEW FRP PROTECTIONS


### 4.2 Next Steps
2. **Smart Switch Vector:** Investigate if Smart Switch backup/restore can be used to inject a modified `settings.db` to disable FRP.

---
*End of Report*
