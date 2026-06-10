# Native Payload Stabilization & Rootkit Implementation (June 2026)

## Overview
This technical note details the resolution of JNI linkage failures and the implementation of rootkit-specific logic within the SuperSploit native Android payload architecture.

## Technical Fixes

### 1. JNI Linkage & Stability
The primary cause of payload instability was a `java.lang.UnsatisfiedLinkError`. The Java-side `PayloadService` was calling native methods that were not exported by the C template (`native_drs.c`).
- **Implemented `executeNative(String)`**: Added a C implementation using `popen` to execute shell commands and capture output.
- **Implemented `start(Context)`**: Added a C implementation to handle the initial connection logic for the Messages variant, allowing for a pure-C connection loop.
- **Library Naming**: Standardized the native library name to `libpayload.so` across all Smali and Java components, resolving "library not found" errors.

### 2. Bypass of Background Restrictions
Modern Android versions (10+) aggressively kill background services.
- **SDK Level Adjustment**: Forced `targetSdkVersion` to 25 and `minSdkVersion` to 21 in `apktool.yml` and `AndroidManifest.xml`. This triggers "Legacy Mode" in the ActivityManager, allowing services to run with fewer restrictions.
- **Foreground Service Requirement**: Ensured `PayloadService` is declared and started as a foreground service to improve lifetime on target.

### 3. Native Rootkit Implementation
The "rootkit" variant was previously a clone of DRS. It now has unique C-level logic.
- **`auto_root` Command**: Ported kernel version detection logic from the Python template into native C.
    - Uses `uname()` to detect `3.x`, `4.x`, and `5.x` kernel series.
    - Identifies vulnerability windows for **Dirty COW (CVE-2016-5195)** and **Dirty Pipe (CVE-2022-0847)**.
    - Requests corresponding exploits from the C2 server upon detection.

## Operational Guide

### Deployment Workflow
To ensure successful execution on a target device via ADB:
1. **Generate**: `generate-apk [drs|messages|rootkit]`
2. **Whitelist**: 
   ```bash
   adb shell cmd deviceidle whitelist +org.supersploit.stub
   ```
3. **Start**:
   ```bash
   adb shell am start-foreground-service -n org.supersploit.stub/.PayloadService
   ```

### Debugging
If a session drops or fails to connect:
- Check JNI exports: `strings libpayload.so | grep Java_`
- Monitor logs for linkage errors: `adb logcat | grep UnsatisfiedLinkError`
- Verify process status: `adb shell ps -A | grep supersploit`
