# FRP Research: Samsung Android 11 Bypass
**Date:** June 7, 2026
**Target:** Samsung Galaxy Tab A8 (Android 11, Kernel 4.4.199)
**MAC:** 48:61:EE:67:C0:0A
**Status:** In Progress (Payload Delivered / Host Blocked)

- **Target Profile:** Samsung Galaxy devices running Android 11, Kernel 4.4.199, Security Patch level May 2022.
- **Key Vulnerabilities:**
    - **CVE-2021-39685 ("Inspector Gadget"):** USB heap overflow in `composite.c` for Kernel RCE. Weaponized in `exploits/android/cve_2021_39685_inspector_gadget.py`.
    - **CVE-2022-20113:** Logic error to force MTP mode without user authentication, enabling stage-2 delivery.
    - **CVE-2025-21042 ("LANDFALL"):** OOB write in `libimagecodec.quram.so` via DNG thumbnail parsing over MTP.
- **Bypass Mechanism:** Use kernel-level shell to zero out the FRP storage partition (`/dev/block/persistent` or `/dev/block/frp`) using `dd if=/dev/zero ...`. This wipes the security token, allowing the Setup Wizard to skip account verification.
- **Status:** **FAILED**. Inspector Gadget and MTP bypass methods did not work on the target tablet.
- **New Direction:** Pivoting to **Unisoc (Spreadtrum) bootloader exploits**, specifically targeting the BROM handshake and potential CVE-2022-38694 vulnerabilities.
- **Detailed Report:** `/home/donald/.SuperSploit/docs/research/android_11_usb_vectors.md`

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

3. **ADB Activation:** THIS CANT BE DONE DUBUGGING IS LOCKED OUT BUILD NUMBER DONT TAP. IF YOU TRY TO OPEN APPS IN THE SETTING IT CRASHES THE SETTINGS APP THIS SIS PART OF NEW FRP PROTECTIONS


### 4.2 Next Steps
2. **Smart Switch Vector:** Investigate if Smart Switch backup/restore can be used to inject a modified `settings.db` to disable FRP.

---
# Project LANDFALL-SWITCH: Samsung Android 11 FRP Bypass Strategy

## 1. Objective
To bypass Factory Reset Protection (FRP) on Samsung Android 11 devices (Target: Galaxy Tab A8) by injecting a modified SettingsProvider configuration through a crafted Smart Switch (EasyMover) backup.

## 2. Research & Environment Setup
- **Emulator:** Android 11 (API 30) x86_64 Google APIs image (Downloading...).
- **Analysis Tools:**
    - `apktool` / `jadx-gui`: For decompiling `EasyMover.apk`.
    - `openssl` / `pycryptodome`: For AES-256-CBC decryption/encryption.
- **App:** `com.sec.android.easyMover` (Smart Switch).
- **Encryption Algorithm:** AES-256-CBC (standard for EasyMover `.exml` and `.senc` files).
- **Potential Keys:**
    - Legacy Key: `backup data!!!!` (Hex: `6261636b757020646174612121212121`)
    - Modern Key: Likely derived from a static string in `libccrypto.so` or `EasyMover` Java classes.

## 3. Detailed Execution Plan

### Phase 1: Baseline Extraction (Emulator)
... [rest of Phase 1] ...

### Phase 2: Decryption & Manipulation
1.  Identify the `.exml` file containing `SettingsProvider` data (e.g., `SystemSettings.exml`).
2.  Decrypt the file using identified fixed keys.
3.  Modify the following XML keys in the decrypted `settings_secure.xml` and `settings_global.xml`:
    - `user_setup_complete` -> `1`
    - `device_provisioned` -> `1`
    - `setup_wizard_has_run` -> `1`
    - `frp_address` -> (Delete or set to empty)
4.  Re-encrypt the XML file, ensuring the file structure and metadata (hash/checksum) are preserved.

### Phase 3: Delivery Vector (Target Device)
1.  Connect the locked Samsung Tab A8 via USB.
2.  Execute the **MTP Browser Trigger** (OpCode `0x9401`):
    - OpCode: `0x9401`
    - Param1: `0x00000000`
    - Param2: `0x00000000`
    - Data: `https://youtube.com/redirect?q=supersploit.local/staging`
3.  Navigate to a local staging server (hosted by SuperSploit) to:
    - Download and install the Smart Switch APK (if the device doesn't have it).
    - Download the **Modified Backup Folder** to the device's internal storage or an SD card.
4.  Launch Smart Switch on the target.
5.  Select **Restore** -> **SD Card** -> **Modified Backup**.

### Phase 4: Finalization
1.  Once the restore process completes, reboot the device.
2.  Verify the "Setup Wizard" is bypassed and the device is fully functional.

## 4. Immediate Next Steps
- [ ] Monitor Android 11 System Image download (16% as of last check).
- [ ] Install `apktool` and `jadx` for local analysis.
- [ ] Extract `com.sec.android.easyMover` from a Samsung device or download a clean APK for analysis.
- [ ] Research specific AES keys for Smart Switch version 3.7+ (Android 11 era).
# Strategic Plan: Samsung FRP Bypass via Smart Switch & Settings Injection

## 1. Objective
To bypass the Factory Reset Protection (FRP) on Samsung Android 11 devices by injecting a modified `settings.db` or SettingsProvider XML files through a crafted Smart Switch backup.

## 2. Research Phase (Active)
### 2.1 Environment Setup
- **Tool:** Android Studio (AVD).
- **Image:** Rooted Android 11 (matches target OS version).
- **Goal:** Map the SettingsProvider structure and identify FRP-bypassable flags.

### 2.2 Data Extraction Targets
Once the emulator is rooted, the following files must be pulled for analysis:
1.  **XML Settings:**
    - `/data/system/users/0/settings_secure.xml`
    - `/data/system/users/0/settings_global.xml`
    - `/data/system/users/0/settings_system.xml`
2.  **Binary Provider:**
    - `/system/priv-app/SecSettingsProvider2/SecSettingsProvider2.apk` (Samsung's specific provider).

### 2.3 Flag Identification
Analyze the extracted XMLs for the following keys:
- `user_setup_complete`
- `device_provisioned`
- `frp_address`
- `secure_frp_mode`
- `setup_wizard_has_run`

## 3. Analysis Phase
- **Decompilation:** Use `jadx-gui` or `apktool` on `SecSettingsProvider2.apk` to understand the logic behind the `persistent` partition check.
- **Smart Switch Format:** Research the encryption and packaging of `com.sec.android.easyMover` backups. 
    - *Note:* Backups are typically AES-256 encrypted. Keys may be found within the EasyMover binary itself.

## 4. Execution Strategy (Conceptual)
1.  Generate a legitimate "Settings Only" backup on a clean device (emulator).
2.  Modify the backup contents to set `user_setup_complete = 1`.
3.  Re-pack and sign/encrypt the backup.
4.  Trigger Smart Switch on the locked target device via the Browser/YouTube MTP trigger.
5.  Restore the modified backup to skip the Setup Wizard.

---
*Created June 7, 2026 - SuperSploit Research Engine*
*End of Report*
