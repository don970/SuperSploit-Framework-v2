# Pure-Python (Kivy/Buildozer) Android Payload Workflow

## Overview
Unlike the `NativeApkGenerator` (which cross-compiles C code via the NDK and injects it into a Java stub), the `BuildozerPayloadGenerator` is designed to package **pure Python** scripts into standalone Android APKs. It leverages the Kivy framework and Buildozer to create self-contained Python environments that run natively on Android.

## Pipeline Architecture
This pipeline is implemented in `source/core/android_kivy_generator.py`.

### 1. Workspace Preparation (`_prepare_workspace`)
*   The generator provisions a persistent build directory at `~/.SuperSploit/.data/kivy_build/`.
*   Unlike `/tmp/`, keeping this persistent prevents Buildozer from re-downloading the entire Android SDK/NDK and Python compilation toolchain on every build, reducing compile times from 15 minutes down to ~15 seconds on subsequent runs.

### 2. Dynamic Payload Injection (`_write_payload`)
*   The generator reads the selected Python payload template (e.g., `android_beacon_template.py`).
*   It dynamically injects active C2 parameters (`LHOST`, `LPORT`, `XOR_KEY`, `MIN_SLEEP`, `MAX_SLEEP`) directly into the script using variable replacement.
*   The weaponized script is dropped into the workspace as `main.py`, which Kivy requires as its entry point.

### 3. Buildozer Configuration (`_write_buildozer_spec`)
*   The generator dynamically constructs a `buildozer.spec` file.
*   **Permissions:** Automatically maps aggressive Android permissions (e.g., `INTERNET`, `READ_SMS`, `READ_CALL_LOG`, `WAKE_LOCK`, `SYSTEM_ALERT_WINDOW`) so the payload has immediate access to critical subsystems upon installation.
*   **Architectures:** Configures `android.archs = arm64-v8a, armeabi-v7a, x86_64, x86` to ensure the resulting APK works on modern physical devices and emulators alike without throwing `INSTALL_FAILED_NO_MATCHING_ABIS`.
*   **Stealth:** Disables the UI (`fullscreen = 1`) and removes the app from the recents menu (`android.exclude_from_recents = True`).

### 4. Compilation (`_compile_apk`)
*   The engine executes `buildozer android debug` as a subprocess within the workspace.
*   It monitors `stdout` to parse build progress, providing real-time percentage updates to the SuperSploit console so the operator knows it hasn't hung.

### 5. Extraction (`_extract_apk`)
*   Buildozer drops the final compiled APK into `kivy_build/bin/`.
*   The framework grabs the APK, renames it to the specified `APP_NAME`, and moves it to `payloads/android/` for immediate deployment.

## Operational Advantages
*   **Rapid Prototyping:** Operators can write payloads in standard Python without dealing with JNI, C pointers, or memory management.
*   **Cross-Platform Portability:** Kivy payloads can often be recompiled for iOS using the `kivy-ios` toolchain with minimal code changes.
*   **Obfuscation:** Python bytecode packaged inside Kivy is notoriously difficult for standard mobile AV engines to decompile and statically analyze compared to standard Java/Smali wrappers.