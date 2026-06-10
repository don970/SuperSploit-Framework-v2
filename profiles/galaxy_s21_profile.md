# Target: Samsung Galaxy S21 (SM-G991U)
- **Name**: Galaxy S21 (Lahaina)
- **OS**: Android 15 (SDK 35)
- **Brand**: Samsung
- **Device**: SM-G991U (o1qsqw)
- **Arch**: aarch64
- **Kernel**: 5.4.274-qgki-30957850-abG991USQSJHZAA
- **Security Patch**: 2026-01-01
- **SELinux**: Enforcing (u:r:shell:s0)
- **User Context**: shell (UID 2000)
- **Open Ports**: 5555 (ADB over Network)
- **Vulnerabilities**: 
    - [MATCH] CVE-2026-0073: ADB Master Key Bypass (Return value bypass in adbd TLS verification)
- **Environment**: 
    - /dev/binder: READ/WRITE
    - /dev/hwbinder: READ/WRITE
    - /dev/ashmem: READ/WRITE
    - /dev/kgsl-3d0: READ/WRITE
    - /data/local/tmp: WRITABLE
- **Notes**: 
    - Critical exposure due to ADB over Network being enabled on port 5555.
    - Multiple LPE surfaces detected via writable device nodes.
    - Kernel info leaks provide high-fidelity mapping for exploit development.

# Critical Findings & LPE Paths:
   1. **Exploitable ADB (Critical)**: 
       * ADB over Network is ENABLED. Combined with the CVE-2026-0073 match, this allows for unauthenticated remote access and bypass of TLS verification.
   2. **Kernel Info Leaks (High Risk)**:
       * `/proc/modules`, `/proc/slabinfo`, and `/proc/config.gz` are all READABLE. 
       * This allows for precise kernel memory layout mapping and ROP chain construction.
   3. **Exposed Device Nodes**:
       * `/dev/binder`, `/dev/hwbinder`, and `/dev/ashmem` are World-Writable (rw-rw-rw-).
       * `/dev/kgsl-3d0` (Adreno GPU) is writable, providing a significant surface for GPU-based LPE.
   4. **Targeted Research**:
       * The device SDK (35) and TLS ADB support confirm the vulnerability to the "ADB Master Key" bypass.
