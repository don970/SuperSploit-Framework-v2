#Target: Samsung Android 11 Galaxy Tab A8
**Date:** June 7, 2026# FRP Research: Samsung Android 11 Bypass
**Date:** June 7, 2026
**Target:** Samsung Galaxy Tab A8 (Android 11, Kernel 4.4.199)
**MAC:** 48:61:EE:67:C0:0A
**Status:** In Progress (Payload Delivered / Host Blocked

## 1. Exploit Analysis
###CVE-2021-39685 ("Inspector Gadget")
- **Type:** USB Heap Overflow (Kernel RCE).
- **Status:** **Blocked (Host-Side)**. The host machine enforces a 4096-byte limit on USB control transfers, preventing the delivery of the 65,535-byte overflow payload.
###CVE-2025-21042 ("LANDFALL")
- **Type:** OOB Write in `libimagecodec.quram.so` (Media Scanner RCE).
- **Delivery:** Successfully delivered `exploit.dng` to the device via Bluetooth OBEX Object Push (Channel 12).
- **Trigger:** Gallery/Media Scanner thumbnail generation.
- **Status:** **Active**. The payload is on the device; trigger success depends on the scanner processing the file.
###CVE-2026-20981/83 (Bluetooth AT RCE)
- **Type:** Unauthenticated AT Command Injection via Bluetooth HFP.
- **Handshake:** Successfully established HFP connection on RFCOMM Channel 3.
- **Status:** **Restricted**. Standard AT commands are accepted, but factory/mode-switch commands (`AT+KNOXSTEP`) are currently rejected by the device's secure state.

## 2. Current Blockers & Next Steps
- **USB Host Limit:** The 4KB limit on the current machine's USB stack prevents direct kernel overflow exploitation.
- **MTP Lock:** The filesystem remains restricted despite Browser Trigger (0x9401) acknowledgment, suggesting a more recent patch level.
- **ADB Activation:** THIS CANT BE DONE DUBUGGING IS LOCKED OUT BUILD NUMBER DONT TAP. IF YOU TRY TO OPEN APPS IN THE SETTING IT CRASHES THE SETTINGS APP THIS SIS PART OF NEW FRP PROTECTIONS

# 5 Next Steps
### Smart Switch Vector:
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

