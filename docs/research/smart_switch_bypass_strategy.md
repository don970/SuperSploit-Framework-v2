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
