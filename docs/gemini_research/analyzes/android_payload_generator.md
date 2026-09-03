# SuperSploit Project Instructions

## Architecture: Android Payload Generator (Deep Analysis)

The Android Payload Generator manages the dynamic creation and compilation of native C Android APK payloads. This logic is primarily implemented in `source/core/native_apk_generator.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Workspace Preparation** | Creates an isolated build directory (`/.data/native_build`) to prevent collisions between multiple payload generation requests. |
| **Dynamic Cross-Compilation** | Intelligently detects the target architecture based on the `APK_ARCH` flag and uses the appropriate Android NDK compiler (e.g., `aarch64-linux-android-clang`) to compile the C payload into a native shared object (`libpayload.so`). |
| **Resource Patching** | Dynamically modifies the `AndroidManifest.xml` to change the application's name and the `strings.xml` file to inject the LHOST, LPORT, and other configuration variables. |
| **APK Repacking (`apktool`)** | Uses `apktool` to repack the modified resources and the compiled native library into a new, unsigned APK. |
| **Code Signing (`apksigner`)** | Signs the repacked APK with a debug keystore to make it installable on Android devices. |

### Automation Workflow
- **Dynamic Architecture Selection**: The generator reads the `APK_ARCH` variable from the database and compiles the C code for the specified architecture (`arm64`, `armv7`, `x86_64`, `x86`, or `all`).
- **Fail-safe Cleanup**: The build directory is automatically cleaned up after the APK is generated, even if the process fails.
- **Automated Keystore Generation**: If a debug keystore is not found, the generator automatically creates one using `keytool`.
