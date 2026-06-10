# Native APK Generator Workflow Analysis

This document outlines the step-by-step automated pipeline executed by the `NativeApkGenerator` class (`native_apk_generator.py`) when generating a native Android payload.

### 1. Workspace Preparation (`_prepare_workspace`)
* The generator clears out any old artifacts in `~/.SuperSploit/.data/native_build/`.
* It determines whether you are trojanizing an existing app (`target_apk`) or building a fresh one (`stub.apk`).
* It executes **Apktool** to decompile the chosen APK, extracting its `AndroidManifest.xml`, `smali` code, and resources directly into the `native_build` workspace.

### 2. Dynamic Variable Injection (`_inject_c_variables`)
* The framework reads your raw C template (`native_drs.c`).
* It pulls your active variables from the SuperSploit database (`LHOST`, `LPORT`, `XOR_KEY`).
* Using Regex and string replacement, it swaps out the placeholder macros and writes a temporary, ready-to-compile file named `patched_payload.c` into the build directory.

### 3. NDK Cross-Compilation (`_compile_c_payload` & `_compile_for_abi`)
* The engine searches your `~/.buildozer/android/platform/` directory for the official Android NDK LLVM/Clang toolchains.
* It fires off the Clang compiler against `patched_payload.c` with the `-shared` and `-fPIC` flags.
* Instead of building a standalone executable, it compiles the payload into an Android Shared Object library (`libmain.so`).
* It automatically creates the correct architecture directories (e.g., `lib/armeabi-v7a/` or `lib/arm64-v8a/`) inside the Apktool workspace and drops the `.so` files inside.

### 4. Resource & Manifest Patching (`_patch_stub`)
* The generator checks the decompiled workspace for `AndroidManifest.xml`. (If it's missing, it dynamically copies the fallback from the `stub_template` folder).
* It modifies the manifest to ensure the `APP_NAME` and necessary permissions (Internet, Wakelock) match your framework configurations.

### 5. Repacking and Signing (`_build_apk`)
* **Apktool Build:** It runs `apktool b` to repack the entire `native_build` directory (which now contains your compiled `libmain.so` inside the `lib/` folder) into a raw, unsigned APK.
* **Alignment:** It uses Android's `zipalign` utility to optimize the APK's memory layout.
* **Signing:** Finally, it signs the APK using SuperSploit's embedded debug keystore (`apksigner`).

---
*This pipeline guarantees ANR-free execution by loading the payload via JNI and detaching it into a POSIX thread, allowing the Java UI wrapper to remain fully responsive.*