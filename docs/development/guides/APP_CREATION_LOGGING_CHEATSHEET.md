# 🛠️ SuperSploit: App Creation & Error Logging Cheat Sheet (2026)

This guide details the internal automated build pipeline for Android payloads and the framework's multi-tiered logging and diagnostic system.

---

## 🏗️ 1. Native APK Build Pipeline (`NativeApkGenerator`)

SuperSploit automates the transformation of raw C source code into fully signed Android APKs using an integrated NDK and Smali-patching engine.

### **The 5-Stage Workflow**
1.  **Workspace Preparation:**
    - **Standalone:** Uses a pre-defined stub template (e.g., Game, Rootkit, Messages).
    - **Trojanize:** Executes `apktool d` on a target APK to extract Manifest and Smali.
2.  **Variable Injection:**
    - Swaps placeholders (`LHOST`, `LPORT`, `XOR_KEY`) in the C template.
    - **Exploit Embedding:** Automatically renames `main()` to `exploit_main()` and merges your exploit C source into the payload wrapper.
3.  **Polymorphic Cross-Compilation:**
    - Uses **NDK Clang** (from `~/.buildozer`) to build `.so` libraries.
    - **Randomization:** Library names (e.g., `libcore_x12.so`) and JNI method names are randomized per-build.
    - **OLLVM:** If `OLLVM_ENABLED` is true, applies control flow flattening and instruction substitution for advanced evasion.
4.  **Smali Hooking & Resource Patching:**
    - **Manifest:** Injects up to 80+ permissions and the `PayloadService` declaration.
    - **Hooking:** Locates the `onCreate` method of the Main Activity and injects Smali code to start the malicious service automatically.
    - **Multidex Support:** "SMART_inject" detects large apps and isolates the payload in a new `smali_classesN.dex` to avoid the 64K method limit.
5.  **Repacking & Signing:**
    - `apktool b` -> `zipalign` -> `apksigner` (using a debug keystore).

---

## 📋 2. Framework Activity & Recon Logging

SuperSploit maintains a detailed audit trail of all operations to assist in debugging and session management.

### **Core Log Files**
| Log Type | File Path | Description |
| :--- | :--- | :--- |
| **Activity Log** | `.data/.logs/activity.log` | Records framework launches, module executions, and success/failure status. |
| **Recon Log** | `.data/.logs/recon_activity.log` | Tracks target discovery, port scans, and service fingerprinting results. |
| **Error Log** | `.data/.errors/error.log` | Centralized repository for all Python tracebacks and framework exceptions. |

### **Operational Tips**
- **Log Rotation:** The framework automatically rotates (archives) logs once they exceed **5MB** to maintain a small disk footprint.
- **Verbose Debugging:** Use `set VERBOSE_LOGGING true` to include full command arguments in the activity log.
- **Quick View:** Use the `logs` command (if alias set) or `tail -f ~/.SuperSploit/.data/.logs/activity.log` for real-time monitoring.

---

## 🐞 3. Error Diagnosis & Troubleshooting

### **Common Build Failures**
| Symptom | Probable Cause | Resolution |
| :--- | :--- | :--- |
| `Compilation failed` | Missing NDK Toolchain | Ensure `~/.buildozer` contains the NDK for your `APK_ARCH`. Run `compile` once to verify. |
| `Apktool build failed` | Resource/Manifest Collision | Check `error.log`. Common fixes include removing duplicate `pointerIconHelp` or `defaultLocale` attributes. |
| `Signing failed` | Keystore/SDK Issue | Verify `apksigner` path in `~/.buildozer`. Run `setup` to regenerate the debug keystore. |
| `Payload won't start` | Hook Failure | The target app may have a complex boot sequence. Try trojanizing a different "Application" class or use a standalone stub. |

### **Application-Level Debugging (On-Device)**
- **Native Logs:** The C payload uses `__android_log_print`. Monitor with `adb logcat | grep SuperSploit`.
- **Permission Denial:** Check `dumpsys package [PKG]` to see if the device user actually granted the requested permissions at runtime.
- **C2 Connection:** If the agent fails to callback, check the `LHOST` and `LPORT` strings in `res/values/strings.xml` inside the generated APK.

---

## ⚙️ 4. Quick Config Commands
- `set APK_ARCH arm64` (Targets modern flagships)
- `set OLLVM_ENABLED true` (Adds obfuscation)
- `set VERBOSE_LOGGING true` (Enables detailed debug logs)
- `clean` (Wipes all temporary build files and logs for a fresh start)
