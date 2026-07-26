# Native APK Payload Generation Workflow

This document maps out the highly automated weaponization pipeline executed by the `NativeApkGenerator` class (`native_apk_generator.py`) when building or trojanizing native Android C2 agents.

## 1. Workspace Preparation

[Triggered by `generate-apk` or ExploitHandler payload hook]
    |
    +--> Purges stale artifacts from `~/.SuperSploit/.data/native_build/`.
    |
    +--> Evaluates if trojanizing an existing app (`target_apk`) or building a fresh lure (`stub.apk`).
    |
    +--> Executes **Apktool** (`apktool d`) to decompile the APK, extracting the `AndroidManifest.xml`, `smali` bytecode, and resources into the workspace.

## 2. Dynamic Variable & Source Injection

    |
    +--> Reads the raw C template (e.g., `native_drs.c` or an embedded exploit like `badbinder_full.c`).
    |
    +--> Injects active framework variables (`LHOST`, `LPORT`, `XOR_KEY`) into the C macros via regex string replacement.
    |
    +--> Writes the prepared, weaponized C source to `patched_payload.c`.

## 3. NDK Cross-Compilation

    |
    +--> Locates the official Android NDK LLVM/Clang toolchain dynamically from the host environment (`~/.buildozer/android/platform/`).
    |
    +--> Executes the Clang compiler against `patched_payload.c` with `-shared -fPIC` flags.
    |
    +--> **JNI Integration**: Instead of a standalone binary, it compiles the payload into an Android Shared Object library (`libpayload.so`).
    |
    +--> Drops the `.so` files into the appropriate architecture directories (e.g., `lib/arm64-v8a/`) inside the Apktool workspace.

## 4. Smali Polymorphism & Trust Patching (Optional)

    |
    +--> **Trust Patching**: Modifies the `network_security_config.xml` and Android Manifest to force the application to trust User-Installed CA certificates (crucial for AitM routing).
    |
    +--> **Polymorphic Crypter**: Iterates through all Smali files, extracts hardcoded strings, Base64+XOR encrypts them, and injects a dynamic `Decryptor.smali` class to decode them at runtime, blinding static AV/EDR analysis.

## 5. Repacking and Signing

    |
    +--> Executes `apktool b` to repack the entire workspace (including the injected `libpayload.so` and modified Smali) into an unsigned APK.
    |
    +--> Utilizes `zipalign` to optimize the memory alignment of the uncompressed data within the APK (mandatory for modern Android OS).
    |
    +--> Executes `apksigner sign` using the framework's embedded `debug.keystore` to generate a valid v2/v3 cryptographic signature.
    |
    +--> Delivers the fully weaponized, undetectable APK payload to the designated `output_apk_path`.