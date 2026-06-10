# Unisoc sp9832e LPE Research & Weaponization Report (June 2026)

## 1. Target Overview
*   **Device:** SkyDevices Elite P55 (ELITE_P55US)
*   **Platform:** Unisoc sp9832e (ARMv7 32-bit)
*   **OS:** Android 11 (SDK 30)
*   **Kernel:** Linux 4.14.193
*   **Security Patch:** 2021-06-05
*   **Status:** Encrypted, Treble Enabled, SELINUX Enforcing (`u:r:shell:s0`)

---

## 2. Tooling Enhancements

### A. Standalone HTTPS Fetcher (`minish`)
*   **Problem:** Target lacked `curl`, `wget`, and `openssl` binaries, preventing security tools from querying online LPE databases.
*   **Solution:** Developed `minish.c`, a lightweight C-based HTTPS client.
*   **Technical Achievement:** 
    *   Uses `dlopen()` to dynamically resolve symbols from the system's `libssl.so` and `libcrypto.so` at runtime.
    *   Implemented manual **SNI (Server Name Indication)** support via `SSL_set_tlsext_host_name` to satisfy modern API requirements.
    *   Integrated `SSL_VERIFY_NONE` to bypass certificate trust issues in minimal environments.

### B. Intelligent LPE Enumeration Tool
*   **Expansion:** Database increased to **120+ targets**, including 2024-2026 vulnerabilities (e.g., CVE-2024-1086, CVE-2026-0073).
*   **Intelligence:** Implemented patch-level correlation that compares `ro.build.version.security_patch` against disclosure dates to distinguish between `[POSSIBLE]` and `[PATCHED]` vulnerabilities.

---

## 3. Exploit Research & Optimization

### Vector 1: Binder UAF (CVE-2020-0423 / CVE-2019-2215)
*   **Finding:** Initial attempts failed due to non-standard `thread_info` layouts in the Unisoc kernel.
*   **Optimization:** Overhauled the Binder exploit with an **Automated Brute-Force** mode. 
    *   Automatically tests multiple stack alignments (8KB/16KB) and structure offsets (8/12) based on the leaked kernel pointer.
    *   Implemented 32-bit specific address handling to prevent pointer truncation.

### Vector 2: Mali GPU UAF (CVE-2023-4211)
*   **Finding:** Standard Mali exploits failed with `Invalid Argument` due to the target using the modern **`kbase`** driver architecture instead of the legacy driver.
*   **Weaponization:** 
    *   Synchronized `struct mali_mem_alloc_args` to use explicit `uint64_t` types to match the 4.14 kernel's expectation on a 32-bit userland.
    *   Implemented the mandatory `KBASE_IOCTL_VERSION_CHECK` and `KBASE_IOCTL_SET_FLAGS` handshake sequence.
    *   Successfully established communication with `/dev/mali0` for heap reclamation.

---

## 4. Framework Integration
*   **Suggestion Engine:** Upgraded the SuperSploit `suggest` command to accept raw **Device Fingerprints**. 
*   **Workflow:** Tools now output a copy-pasteable fingerprint (e.g., `os=android kernel=4.14.193 arch=armv7l board=sp9832e`) allowing for local correlation on the host machine when the target is completely isolated.

---

## 5. Artifacts Produced (`android_v7`)
*   `payloads/android_lpe_cve_lookup_android_v7`: Enhanced LPE Enumerator.
*   `payloads/android_lpe_enum_android_v7`: Advanced Security Audit Suite.
*   `payloads/minish_android_v7`: Standalone Dynamic SSL Fetcher.
*   `payloads/android11_kaslr_leak_android_v7`: Specialized Binder/signalfd leak.
*   `payloads/badbinder_full_android_v7`: Automated Binder LPE.
*   `payloads/cve_2023_4211_mali_leak_android_v7`: Specialized kbase leak.
*   `payloads/cve_2023_4211_mali_gpu_android_v7`: Specialized kbase LPE.

**Report Status:** Completed. All binaries synchronized and deployment scripts updated.
