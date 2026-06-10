# Target: SkyDevices Elite P55 (ELITE_P55US)
- **Name**: Elite P55 (Unisoc)
- **OS**: Android 11 (SDK 30)
- **Brand**: SkyDevices
- **Device**: ELITE_P55US
- **Arch**: armv7l (32-bit)
- **Kernel**: Linux 4.14.193
- **SoC/Platform**: Unisoc sp9832e
- **Security Patch**: 2021-06-05
- **Status**: Encrypted, Treble Enabled, SELinux Enforcing (u:r:shell:s0)
- **Open Ports**: 5555 (ADB over Network) via adb tcpip 5555
- **Environment**: 
    - /dev/binder: READ/WRITE
    - /dev/hwbinder: READ/WRITE
    - /dev/mali0: READ/WRITE (kbase driver architecture)
    - /proc/modules: READABLE (Info Leak)
    - /data/local/tmp: WRITABLE
- **Vulnerabilities**: 
    - [FAILED] CVE-2020-0423: Binder UAF (Deep exhaustive brute-force failed; highly non-standard kernel layout)
    - [FAILED] CVE-2023-4211: Mali GPU UAF (Exhaustive layout brute-force failed on kbase v11.13)
- **Custom Toolchain**:
    - `minish`: Standalone HTTPS fetcher (dynamic SSL symbol resolution)
    - `android-enum3`: Version 5.0 (The Singularity) integrated

# Payloads Landed /data/local/tmp
    * native c dynamic reverse shell [working path for remote acssses]
    * adb is authorized [shell user with adb permissions] uid 2000 for loging
    * exploit.dng for CVE-2023-45866 landed but failed to detonante dont need it anyway we have adb authorized

# Critical Findings & Attack Surface:
   1. **Kernel LPE via Binder (Failed)**: 
       * Attempted CVE-2020-0423 using `badbinder_full` (exhaustive ARMv7).
       * **Result**: All wait offsets (24 to 304) failed. The target kernel layout is definitively non-standard and resistant to typical UAF reclamation.
   2. **Mali GPU Exploitation (Failed)**:
       * Attempted CVE-2023-4211 using `cve_2023_4211_mali_leak_android_v7`.
       * **Result**: Exhaustive 32-byte layout brute-force against kbase version 11.13 failed across all common flag combinations. Heap reclamation was unsuccessful.
   3. **Alternative Local Vectors (Failed)**:
       * Attempted `ebpf_lpe_armv7_android_v7` (CVE-2022-23222).
       * **Result**: Failed to create BPF map (Permission denied). Android 11 / Unisoc kernel hardening effectively blocks unprivileged BPF access.
   4. **Network Isolation Bypass**:
       * Lacks `curl`/`wget`. All remote fetching must utilize the custom `minish` binary to bypass the missing system utilities.
   5. **Information Leaks**:
       * Readable `/proc/modules` allows for precise kernel module offset resolution, simplifying ROP chain construction for LPE.
