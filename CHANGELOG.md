# Changelog

### [Unreleased]
- **Bug Fixes**:
    - Fixed: Added missing directory structure for `.data/.logs`, `.data/.history`, and `.data/.errors` to prevent framework crashes. Included `.gitkeep` files to ensure these directories are tracked in the repository.
    - Fixed: Added missing `urllib.request` and `datetime` imports in `license_manager.py` that were causing silent Discord notification failures.
- **Target Profile System Enhancements**:
    - Added: `sync profile` command to refresh persona dossiers with latest reconnaissance data.
    - Improved: `import from targets` now pulls deep metadata including MAC, vendor, services, and uptime.
    - Improved: `suggest` command now natively supports named profiles, pulling data directly from the persistent profile database.
- **Licensing & Legal**:
    - Added: **Dual-License Open Core Model** - Transitioned the project to a dual-licensing structure to support both open-source and commercial tiers.
    - Added: **Root `LICENSE`** - Comprehensive licensing overview for the framework.
    - Added: **`LICENSE-CORE` (MIT)** - Explicit MIT license for the open-source core components.
    - Updated: **README.md** - Refactored License Tiers documentation with direct links to core and pro licensing.
- **Core Executable Update**:
    - Updated: **SuperSploit Auth Engine** (`/usr/local/bin/supersploit`) - Replaced the global executable with the latest `supersploit_auth` binary from the `supersploit_key_system` repository (Commit `26d9216`).
- **SuperSploit Pro Ecosystem**:
    - Added: **Pro License Agreement** (`docs/Legal/PRO_LICENSE_AGREEMENT.md`) - Official terms and conditions for professional users.
    - Added: **Pro Pricing Model** (`docs/Legal/PRO_PRICING.md`) - Tiered subscription structure for Individual, Red Team, and Enterprise levels.
    - Added: **Pro Key Generation Engine** (`source/tools/cryptography/pro_keygen.py`) - Standalone utility for generating cryptographically signed license keys for specific Hardware IDs (HWIDs).
- **Advanced Stealth & Evasion Suite**:
    - Added: **Environment Pinning (Anti-Analysis)** - Native `ptrace` and uptime checks in C payloads to detect and evade debuggers, emulators, and sandboxes.
    - Added: **Polymorphic Signature Rotation** - Automated randomization of native library names and JNI method names for every build, preventing static signature detection.
    - Added: **Opportunistic OLLVM Integration** - Support for the `OLLVM_ENABLED` variable to apply advanced control flow flattening and instruction substitution to native C binaries.
    - Added: **Network Domain Fronting** - Upgraded `minish.c` to support SNI-masking via a front domain, hiding C2 traffic within high-reputation CDN flows (Cloudflare/Akamai).
    - Added: **Phantom Library Persistence** - New `phantom_persistence.py` weaponizer for systemless boot persistence via Magisk library hijacking (`libvold.so`).
- Added: `exploits/linux/cve_2021_4034_pwnkit_fileless.py` - Python memory loader for the PwnKit LPE.
- Improved: C2 Listener now intercepts `auto_root` for Linux sessions to deploy PwnKit automatically.
- Added: Automated Vulnerability Tagging engine in the C2 Listener. Automatically parses CVEs from command output (e.g., `lpe_enum`) and enriches the target's persona in `profiles.db`.
- Added: `recon/osint-tools/domain_enum.py` - Passive subdomain discovery via crt.sh (Certificate Transparency Logs).
- Added: `recon/osint-tools/repo_scanner.py` - GitHub code search for leaked API keys and sensitive configuration files.
- Added: `recon/osint-tools/shodan_recon.py` - Shodan API integration for automated port, banner, and CVE mapping.
- Added: `recon/osint-tools/footprint_analyzer.py` - Professional digital footprint correlation engine. Links IPs, social media, and database records.
- Improved: `recon/osint-tools/background_check.py` - Refactored into a professional-grade Investigative Dossier Engine with PI-style PDF reporting.
- Added: `recon/native-discovery/ble_layered_profiler.py` - A comprehensive multi-layer BLE reconnaissance module covering Layers 2 through 5.
- Improved: Unified Bluetooth discovery and deep GATT profiling capabilities.
- Added: `payloads/Stage2/ghost_beacon.py` - Specialized "Smash-and-Grab" ephemeral payload for Linux/Tizen Wi-Fi credential exfiltration.
- Added: `recon/native-discovery/bt_auditor.py` - New active Bluetooth auditing module for RFCOMM (Samsung Ch 4) and BLE GATT enumeration.
- Improved: `recon/native-discovery/bluetooth_discovery.py` - Upgraded to v2.0 using `bluetoothctl` for Classic/BLE support, OUI/vendor lookups, and enhanced OS fingerprinting.
- Improved: Added `R_MAC` to `.data/.help/vars` for Bluetooth/Ethernet target management.
- Added: `profiles/elite_p55_profile.md` - Comprehensive target profile for SkyDevices Elite P55 (Unisoc sp9832e). Details ARMv7 weaponization, Binder/Mali LPE paths, and network isolation bypass strategies.
- Added: `profiles/galaxy_s21_profile.md` - Comprehensive target profile for Samsung Galaxy S21 (SM-G991U) running Android 15. Includes networking audit (ADB port 5555), LPE surface mapping, and CVE-2026-0073 correlation.
- Improved: Enhanced `android-enum3.c` to **Version 5.0 (The Singularity)**. 
    - Added: Deep Network Stack Auditing (Listening ports, ADB-over-IP detection).
    - Added: Mount Point Security Analysis (RW system detection, executable tmp detection).
    - Added: Virtualization & Container Detection (Docker, WSL2, Microdroid, ARC++).
    - Added: Sensitive File Discovery (.ssh, .bash_history, shadow).
    - Improved: Expanded Native LPE Surface mapping (Qualcomm/MediaTek/Exynos specific nodes).
    - Improved: Advanced Exploit Correlation (CVE-2024-1086, CVE-2023-4211, CVE-2026-0073).
- Improved: Updated `AUTO_ENUM` to use the high-performance `android-enum3.c` suite for automated post-exploitation auditing.
- Added: `exploits/android/cve_2026_0073_chromebook_proxy.py` - Weaponized ADB Master Key exploit with native SOCKS5/HTTP proxy support for Chromebook targets.
- Improved: Added Chromebook-specific enumeration defaults to the ADB Master Key research.

### Added
- **Enhanced Compilation Engine**:
    - Added native support for **Android x86_64** cross-compilation using the internal NDK toolchain (`x86_64-linux-android*-clang`).
    - Introduced the `COMP_STATIC` global variable to toggle **static linking** (`-static`) during the `compile` command, improving binary portability across different libc versions (e.g., glibc to Bionic).
    - Updated the `compile` command to display static linking status during the build process.
    - Expanded `.data/.help/vars` to include documentation for `android_x86_64` and `COMP_STATIC`.
- **Target & Profile Import Improvements**:
    - Added support for plural command forms (`import targets`, `import profiles`).
    - Enhanced JSON target parsing to handle both dictionary and list formats.
    - Implemented automatic path resolution for core configuration files (e.g., `targets.json`) if not found in the local directory.
- **Markdown Import Support**:
    - Updated the `import target` and `import profile` commands to support Markdown (.md) files.
    - Implemented a robust regex-based parser in `DatabaseManagment` that extracts metadata (IP, OS, Kernel, Arch, Ports, CVEs, etc.) from Markdown profiles.
    - Supports multi-target/persona parsing within a single Markdown file using `# Target:` headers.
- **Asynchronous C2 Infrastructure (Roadmap Priority)**:
    - Completely overhauled the `c2_server.py` HTTP beacon listener from a synchronous `socketserver` to a native `asyncio` architecture.
    - Replaced the global string buffer with thread-safe `asyncio.Queue` structures to safely transfer commands from the interactive console to the background I/O event loop.
    - This eliminates threading bottlenecks and state corruption during high-concurrency beacon check-ins.
- **Workspace Management (Roadmap Priority)**:
    - Refactored `DatabaseManagment` to support fully isolated SQLite databases and configurations per workspace directory.
    - Added the `workspace` command to list, create, switch, and delete workspaces natively from the CLI.
    - Ensures memory safety and prevents cross-session pollution when managing multiple targets or engagements.
- **Job Control & Process Management (Roadmap Priority)**:
    - Implemented a centralized `JobManager` registry to track background tasks within the framework.
    - Added the `jobs` command to list active background threads (like C2 listeners) and their current uptimes.
    - Added `jobs kill <id>` to gracefully invoke termination callbacks (e.g., closing sockets) without crashing the framework.
- **Console Interface Modernization (Roadmap Priority)**:
    - Implemented dynamic tab completion using `prompt_toolkit`. The console intelligently auto-completes main commands, workspace names, and deep module paths (e.g., `use payloads/...`).
    - Integrated the `rich` Python library to replace raw console output with stylish, readable tables for the `search` and `sessions` commands.
    - Verified native support for `Ctrl+R` reverse history search.
- **Samsung FRP Bypass Research (Smart Switch Vector)**:
    - Documented a new strategic plan for bypassing Samsung Android 11 FRP using modified Smart Switch backups (`docs/research/smart_switch_bypass_strategy.md`).
    - Identified key SettingsProvider XML targets (`settings_secure.xml`, `settings_global.xml`) and Samsung-specific FRP flags for emulator-based research.
### Improved
- **Target Profile System**:
    - Added ability to import profiles from the targets database using `add profile --import <IP>`.
    - Profiles now persist IP, OS, Architecture, and Kernel information.
    - Added support for persistent research logging with `edit profile "<name>" research add "<info>"`.
    - Updated `show profiles` to display comprehensive persona data and research notes.
- **Automated C2 Enumeration**:
    - Implemented `AUTO_ENUM` feature in the listener.
    - New sessions now automatically trigger a background enumeration suite using `android_lpe_enum.c`.
    - The framework automatically identifies target architecture and cross-compiles the enumeration tool on-the-fly using the NDK or system compilers.
    - Key vulnerabilities and "micro-cracks" are automatically extracted from the enumeration report and added to the target's persona profile for persistent tracking.
- Native Android LPE enumeration program in C (`payloads/android_lpe_enum.c`).
- Comprehensive security checks including system properties, SELinux status, writable directories, and accessible device nodes.
- Improved `compile` command with support for 32-bit Android architectures (`android_arm`, `android_x86`) using the internal NDK toolchain.
- **Enhanced Android LPE Enumeration (`android_lpe_cve_lookup.c`)**:
    - Expanded offline CVE database to 120+ targets, including 2024-2026 critical vulnerabilities (e.g., CVE-2024-1086, CVE-2025-0012, CVE-2026-0073).
    - Implemented intelligent **Security Patch Correlation**: The tool now pulls `ro.build.version.security_patch` and compares it against vulnerability disclosure dates to differentiate between "POSSIBLE" and "PATCHED" states.
    - Expanded **LPE Surface Probing**: Added 15+ new device nodes to the audit, specifically targeting Unisoc/Spreadtrum multimedia and IPC drivers (`/dev/sprd_*`, `/dev/trusty-ipc-dev0`).
    - Improved **Filesystem Audit**: Added deep-scanning for writable vendor partitions and sensitive system binaries (`iptables`, `ip6tables`).
    - Added comprehensive **Kernel Hardening Audit**: Integrated checks for `userfaultfd`, `perf_event_paranoid`, and KASLR leak detection in `/proc/kallsyms`.
- **Advanced Security Audit Suite (`android_lpe_enum.c`)**:
    - Integrated deep third-party app auditing with debuggable flag detection and version fingerprinting.
    - Added service fingerprinting for critical system daemons (`surfaceflinger`, `vold`, `zygote`).
    - Implemented "Micro-Crack" detection for sensitive information leaks in `dmesg` and `proc` files.
- **Native C Exploit Embedding**:
    - Implemented `exploit=<path>` flag for `generate_apk`, allowing direct integration of standalone C exploits into Android apps.
    - Created `exploit_wrapper.c` JNI template for automatic detached thread execution.
    - Automated `main()` renaming and metadata stripping in the NDK compilation pipeline.
    - Supported automated "Omni-Permission" injection for maximum sandbox attack surface.
### Added
- **CVE-2026-0073 "Master Key" Weaponization**: Overhauled the stub exploit for the ADB Master Key vulnerability.
    - Implemented the full `A_STLS` upgrade sequence for modern Wireless ADB.
    - Integrated dynamic EC P-256 certificate generation to trigger the `adbd_tls_verify_cert` return value bypass (-1 interpreted as true).
    - Added a direct ADB protocol state machine for encrypted TLS tunnels, supporting automated command execution and persistent DRS payload deployment.
- **Basic C Reverse Shell**: Added a lightweight, standalone C reverse shell implementation (`payloads/basic_rev_shell.c`) designed for Linux payload delivery testing. Supports dynamic LHOST/LPORT configuration via CLI arguments or compiler macros.
- **Android Stealth Mechanisms**:
    - Implemented `jnius`-based- app icon hiding (`HIDE_ICON`) using `PackageManager`.
    - Added a silent UI toggle (`SHOW_UI`) for headless operation.
    - Integrated dynamic import obfuscation in all Android templates.
- **Android Exfiltration Commands**: Added `dump_sms` and `dump_calls` commands to the DRS template.
- **Android Enumeration**: Added `lpe_enum` for specialized local vulnerability analysis on Android targets.
- **Dynamic Architecture Selection**: Implemented the `APK_ARCH` global variable, allowing users to specify the target CPU architecture (`arm64`, `armv7`, `x86_64`, `x86`, or `all`) for native Android payloads. The `native_apk_generator.py` now dynamically cross-compiles C code for the selected architecture(s).
- **Cross-Compilation Command**: Introduced the `compile` command to easily cross-compile C files into binaries directly from the CLI. This command is highly configurable via the `COMP_ARCH` variable (supporting native, x86_64, i686, aarch64, and Android NDK) and the `COMP_OUT` variable for custom output paths.
- **Android Rootkit SSL Security**: Implemented full SSL/TLS encryption for the rootkit payload, utilizing `ssl.PROTOCOL_TLS_CLIENT` and framework-ephemeral certificates for secure C2 check-ins.
- **Configurable App Name**: Introduced the `APP_NAME` variable to `generate-apk`, allowing users to fully spoof the installed application's title. If omitted, the framework now automatically defaults to highly stealthy names (e.g., "Google Play Services").
- **Root-Level Wakelock**: Integrated automatic acquisition of `/sys/power/wake_lock` for the Android rootkit once root privileges are established, significantly improving background persistence against Android's Doze mode.
- **C2 Command Dispatcher for Rootkit**: Overhauled the rootkit's communication loop to support the full SuperSploit C2 protocol, including encrypted file transfers (`upload`/`download`), memory execution (`exec`/`load`), and silent privilege escalation (`auto_root`).
- **Detailed Help Topics**: Added comprehensive help documentation for `auto_root` and updated the `android` and `generate-apk` guides to cover new rootkit features.
- **DirtyCOW ARM64 Binary**: Created the C source implementation (`exploits/android/cve_2016_5195_dirtycow.c`) and compiled it into a PIE-compliant ARM64 binary (`payloads/android/dirtycow_arm64`) using the Android NDK toolchain.
- **Automated Android Cross-Compilation**: Enhanced `SessionLoader._load_c()` to intelligently detect Android targets and utilize the Android NDK Clang compiler (`aarch64-linux-android*-clang`) for ARM64 cross-compilation of C exploits.
- **Native Android Architecture**: Completely replaced the Kivy/Buildozer payload generation pipeline with a high-performance Native C/Java hybrid architecture.
- **Legacy Buildozer Command**: Re-added the original Kivy/Buildozer APK generation pipeline under the new command `generate-apk-buildozer` to allow users to continue using Python-based payloads when needed.
- **APK Trojanization Support**: Integrated advanced trojanization capabilities into the `generate-apk` command. Users can now use the `inject=<path_to_apk>` flag to decompile a legitimate Android application, inject the Native C payload service and libraries, and recompile it. This inherits the original application's identity and permissions for maximum stealth.
    - **Ultra-Fast Generation**: Payload compilation and signing dropped from ~3 minutes to ~2 seconds.
    - **Significant Footprint Reduction**: Payload size reduced from ~40MB to <1MB.
    - **Stealth Enhancements**: Headless execution via Native Java Services and spoofed system application names (e.g., "Google Play Services").
    - **Dependency Removal**: Eliminated framework reliance on Buildozer, Python-for-Android, and Gradle for payload generation.
    - **Native Command Execution**: Implemented a JNI-based C execution engine (`native_drs.c`) for low-level shell operations.
- **KASLR Slide Calculator**: Introduced the `kaslr` command and standalone tool for calculating KASLR slides, leaked addresses, and static kernel bases. Features an interactive mode with built-in reference addresses for common Linux and Android architectures.
- **Mali GPU KASLR Leak (CVE-2023-4211)**: Implemented a new exploit module (`exploits/android/cve_2023_4211_mali_leak.c`) that weaponizes the Mali GPU UAF primitive to scan kernel memory for pointers and automatically calculate the KASLR slide.
- **Legacy Android KASLR Leak (CVE-2017-0630)**: Added a module (`exploits/android/legacy_kaslr_leak.c`) targeting Android 4.x/5.x that leaks pointers from the kernel trace subsystem.
- **Android 11 KASLR Leak (CVE-2020-0423)**: Implemented a Binder-based information leak module (`exploits/android/android11_kaslr_leak.c`) targeting Android 11 kernel UAF vulnerabilities.

### Improved
- **Rootkit Stability**: Removed a 15-second socket timeout that caused frequent reconnections during idle periods. The agent now utilizes blocking sockets synchronized with framework heartbeat intervals.
- **Exploit Triggering Engine**: Enhanced the listener and agent templates to support raw Python function calls (e.g., `check_dirtycow()`) as C2 commands, resolving previous `TypeError` exceptions during automated exploit triggering.

### Fixed
- **Exploit Metadata Syntax**: Resolved "invalid syntax" errors in LPE exploits (`dirtycow`, `dirtypipe`) by wrapping framework metadata in Python-compliant multi-line strings.
- **Global Function Registration**: Fixed "name not defined" errors during automated exploitation by ensuring payload stagers explicitly register exploit functions in the agent's `globals()` scope.
- **DirtyPipe Function Alignment**: Renamed the `dirtypipe` payload function and updated the listener's automated trigger to ensure perfect synchronization during the `auto_root` workflow.

### Fixed
- **Native JNI Linkage**: Resolved `java.lang.UnsatisfiedLinkError` in DRS and Messages payloads by implementing missing `executeNative` and `start` JNI exports in `native_drs.c`.
- **Messages Payload Activation**: Fixed a naming mismatch in the Messages stub Smali where it incorrectly sought `libmain.so` instead of `libpayload.so`.
- **Background Persistence**: Corrected `targetSdkVersion` to 25 and `minSdkVersion` to 21 across all native stubs to bypass background service execution restrictions on modern Android devices.
- **Generator Logic**: Fixed a Python syntax error in `native_apk_generator.py` and ensured the Messages `AndroidManifest.xml` correctly declares the `PayloadService`.

### Added
- **Native `auto_root` Detection**: Ported kernel-level vulnerability detection (Dirty COW, Dirty Pipe) into the C execution engine, allowing native payloads to identify escalation paths via the `auto_root` command.
- **C2 Jitter & Retries**: Implemented a connection retry loop in the native C template to improve session stability during network fluctuations.

### Added
- **CVE-2026-20700 Hybrid Weaponization**: Implemented a sophisticated weaponization pipeline for the Apple dyld Shared Cache zero-day. 
    - Created a dynamic Python weaponizer (`cve_2026_20700_dyld_cache.py`) that injects framework-generated ARM64 shellcode into a C exploit template.
    - Integrated automatic ARM64 cross-compilation for weaponized payloads.
    - Added a realistic C-based exploit implementation (`cve_2026_20700_dyld_cache.c`) for dyld shared cache memory corruption.
- **Apple Zero-Day Suite (2026)**: Implemented three advanced, fully weaponized exploit simulation modules targeting the most critical iOS/macOS attack vectors:
    - **iMessage Zero-Click (CVE-2026-10001)**: Hybrid C/Python module simulating BlastDoor sandbox escape via malformed HEIF attachments.
    - **Safari WebKit RCE (CVE-2026-10002)**: 1-Click exploit targeting DFG JIT type confusion, including a built-in malicious HTML hoster.
    - **AWDL/AirDrop RCE (CVE-2026-10003)**: Proximity-based exploit targeting `sharingd` buffer overflows via malformed AWDL discovery broadcasts.
- **CVE-2026-0047 Exploit**: Implemented UI bitmap exfiltration exploit for Android 16 (QPR2) targeting the `ActivityManagerService` missing permission check.
- **CVE-2026-0047 Research**: Added a technical breakdown of the `dumpBitmapsProto` vulnerability in `docs/research/`.
- **Native Flappy Bird Lure**: Implemented a fully working **Flappy Bird** style game as a stealthy lure for standalone native Android payloads (`drs` and `beacon` types). This replaces the generic "Google Play Services" placeholder when trojanization is not used, providing a functional UI to evade user suspicion.
- **Native Rootkit Overhaul**: Upgraded the `rootkit` native payload template from a headless service into a fully functional mock **SuperUser** root manager application.
    - Added a programmatic UI (`RootManagerActivity.java`) that convincingly mimics a root access manager and triggers the **Magisk/SU prompt** upon launch.
    - Implemented a `BootReceiver` for reliable startup persistence on device boot.
    - Extensively expanded the `AndroidManifest.xml` to include **real-world root permissions** (Storage, SMS, Contacts, Location, Boot Completed, Foreground Service, Kill Background Processes, etc.).
    - Updated the native DRS stager (`native_drs.c`) to automatically detect existing `su` binaries and utilize them for elevated command execution if granted.
    - **Advanced Stealth**: The app now automatically hides its launcher icon 15 seconds after execution and is permanently excluded from the Android "Recents/Overview" menu via `excludeFromRecents=true`.
    - **Anti-Forensics**: The background native C2 threads dynamically rename themselves to `sys_watchdog` using `prctl(PR_SET_NAME)` to blend into `ps` outputs.
    - **Data Exfiltration**: Fully implemented a comprehensive suite of extraction commands:
        *   `dump_sms`: Extract the entire device SMS inbox.
        *   `dump_calls`: Extract full call history.
        *   `dump_contacts`: Extract all stored contacts and phone numbers.
        *   `dump_calendar`: Extract all calendar events.
        *   `dump_wifi`: Extract stored WiFi SSIDs and PSK passwords (Requires Root).
        *   `dump_chrome`: Harvest Chrome browser cookies and saved logins (Requires Root).
        *   `dump_google_passwords`: Targeted extraction of Google Play Services (GMS) autofill and credential manager databases (Requires Root).
        *   `find_cookies`: Recursively locate SQLite cookie databases for all apps (Requires Root).
        *   `find_passwords`: Recursively locate "Login Data" and password stores for all apps (Requires Root).
        *   `get_accounts`: List all configured accounts (Google, Samsung, etc.).
        *   `get_location`: Extract the last known GPS coordinates.
        *   `list_apps`: List all installed applications and their APK paths.
    - **Kivy Rootkit Overhaul**: Applied the "SuperUser" mock UI and advanced exfiltration suite to the Python/Kivy-based rootkit template (`android_rootkit_template.py`).
    - **Global Kivy Template Upgrade**: Upgraded **all** Kivy-based Android templates (`beacon`, `drs`, `messages`) to support the full data exfiltration suite and advanced stealth features.
        - Integrated automatic root detection and elevated command execution across all Python payloads.
        - Enabled high-privilege exfiltration commands (`dump_google_passwords`, `dump_wifi`, `dump_chrome`, etc.) for all Kivy-generated APKs.
        - Applied anti-forensic thread renaming and "Recents" menu exclusion to the entire Kivy pipeline.
    - **Listener QOL Enhancements**: Ported the advanced input handling features from the main CLI to the C2 interaction sessions.
        - Implemented persistent command history for all C2 sessions (`c2_history`).
        - Added auto-suggestions and reverse-history search via `PromptSession`.
        - Integrated support for command chaining (`&&`) and local output redirection (`>`).
        - Added support for framework aliases within active sessions.
        - Added a native `clear` command to the interactive C2 menu.
    - **Messages Template Fix**: Overhauled the `messages` native payload template.
    - Updated `StubActivity.java` to correctly start the background `PayloadService` upon application launch.
    - Recompiled Java source to fresh Smali files to ensure reliable C2 initialization.
    - Added missing Android resources (`res/`) to prevent build failures.
    - Fixed a bug where the UI would appear empty without initializing the native DRS service.

## [2.0.0] - 2026-06-01
### Added
-**android support in payload generation**


## [1.2.20] - 2026-05-25

### Added
- **HTTP Beacon Endpoint Routing**: Implemented strict URI routing for the HTTP beacon payload (`beacon.py`). The payload now actively polls `GET /file` for task retrieval and utilizes `POST /rfile` for asynchronous data and file exfiltration.
- **Dynamic Stage 2 TLS Packaging**: Upgraded the background TLS listener to dynamically package, encrypt, and deliver Stage 2 in-memory C2 payloads upon catching Stage 1 connections, providing real-time console feedback.
- **Standalone XOR Encrypter Tool**: Added `xor_encrypter.py` for standalone XOR payload encryption and decryption workflows.
- **Cross-Platform Compilation Validation**: Upgraded `SessionLoader` to natively detect and use Linux cross-compilers (`x86_64-linux-gnu-gcc` and `aarch64-linux-gnu-gcc`) when running on macOS.

## [1.2.19] - 2026-05-24

### Added
- **100% Encrypted C2 Stream**: Completely replaced plaintext shell sockets with length-prefixed, Base64-encoded, XOR-encrypted frames over TLS. All commands, responses, and file transfers are now completely hidden from packet inspection.
- **HTTP Beacon Architecture**: Introduced `beacon.py`, an asynchronous post-exploitation payload that utilizes jitter (randomized sleep cycles) and HTTP GET/POST requests to fetch tasks and return results, evading continuous-connection monitoring.
- **Universal Payload Generator**: Refactored `stager_generator.py` to ingest *any* raw Python script, auto-inject active networking configurations (`LHOST`, `LPORT`, `STAGE2URL`), dynamically obfuscate classes/functions/variables, and output a web-safe Base64 Python one-liner.
- **Intelligent Session Loader**: Upgraded `SessionLoader` with Python's Abstract Syntax Tree (`ast`) module to statically analyze Python payloads before injection. Provides detailed terminal intelligence (Entry Points, Imported Modules, Auto-Execution status, and Payload Size).
- **Encrypted File Transfers**: Added seamless, any-size `upload` and `download` commands to the active C2 session, utilizing the new length-prefixed encrypted frame protocol.
- **C2 Command Registry**: Overhauled the `listener.py` interaction loop into a modular command registry, drastically improving code readability and framework extensibility.
- **Command Shadowing**: Implemented dynamic command routing in active sessions. Unrecognized C2 commands seamlessly fall through to the target's native OS shell.

### Improved
- **Anti-Analysis OPSEC**: Added anti-sandbox timing checks and Framework Magic Byte validation (`\x53\x53`) to `stager.py` to prevent automated analysis or accidental execution of corrupted streams.
- **Bulletproof Dynamic Imports**: Upgraded Stage 2 payloads (`DRS.py`, `keylogger.py`, `beacon.py`) to use inline Base64 decode helpers for resolving high-signal modules (`os`, `subprocess`) to prevent import tracking and string-based memory detection.
- **Web-Safe Base64**: The Exploit Engine now automatically appends a `.replace(b' ', b'+')` failsafe to generated one-liners to prevent payload corruption from web servers decoding HTTP parameters.

---

## [1.2.18] - 2026-05-23

### Added
- **Exhaustive OSINT Suite**: 
    - **`background_check.py`**: Overhauled with a categorized dorking engine (Aggregators, Legal, Social, Financial, Leaks) and structured PDF reporting via FPDF.
    - **`email_recon.py`**: Expanded dork library to include professional registries and paste site lookups.
    - **`phone_recon.py`**: Integrated `phonenumbers` library for local metadata discovery and massive social media dorking.
- **Persona Profile Persistence**: OSINT modules now automatically initialize and update persistent entries in the `DatabaseManagment` profile database.

### Fixed
- **Input Handling**: Resolved `AttributeError: 'list' object has no attribute 'replace'` in `recon_engine.py` by implementing robust type-checking for `R_HOST`. Modules now gracefully handle targets set as lists (e.g., `["Name", "Location"]`).
- **PDF Export**: Fixed directory resolution issues for loot reports when running in memory.

---

## [1.2.17] - 2026-05-13

### Added
- **New `edit` command**: Allows modification of profile data including phone, email, and social media links.
- **New `suggest` command**: Analyzes target metadata and open ports to suggest relevant exploits.
- **Fileless Execution Engine**: 
    - C-based exploits now utilize `memfd_create` on Linux for in-memory execution.
    - Python modules are executed directly in a virtual namespace to avoid disk I/O.
- **Command Chaining**: Added support for `&&` to run multiple commands sequentially.
- **Output Redirection**: Added support for `>` to append command output to files.
- **One-Liner Payload Generation**: Automatically generate base64-encoded Python one-liners for fileless staging.
- **Interactive Help**: Comprehensive help files added for all core commands.

### Changed
- **Refactored `clean` command**: Now performs a deep purge of logs, session history, and cached databases.
- **Enhanced `inputfixes`**: Centralized core command registry for `cd`, `cat`, `clear`, and `exit`.
- **Improved `cd`**: Added support for default HOME directory when no path is provided.
- **Exploit Handler**: Improved metadata parsing and automatic payload linking.
- **CLI UX**: Switched to `shlex` for safer command parsing and alias handling.

### Fixed
- **Path Handling**: Fixed `__file__` resolution issues during in-memory module execution.
- **Subprocess Security**: Implemented secure temporary file handling for unstable exploits.
- **Terminal State**: Fixed issues where the terminal would occasionally hang after fileless binary execution.

---

## [1.2.16] - 2026-05-13

### Security
- **TOCTOU Race Condition Patch:** Fixed a critical Time-Of-Check to Time-Of-Use vulnerability in `recon_engine.py`. By moving the user prompt to *before* the temporary Python script is written to disk, the race window for a local attacker to overwrite the file prior to `sudo` execution was eliminated.

### Changed
- **SQLite Database Migration:** Overhauled the core `DatabaseManagment` engine to use a real-time SQLite database (`data.db`) via a custom `MutableMapping` wrapper (`SQLiteDict`). This seamlessly replaces the legacy JSON memory cache, providing robust transactional writes while preserving dictionary-style syntax (`db["KEY"]`) across the entire framework.
- **Programmatic Output Capturing:** Upgraded the Python, Bash, and C execution handlers in `exploithandler.py` to leverage `subprocess.run(capture_output=True)`. Exploits no longer dump blindly to the TTY; instead, the framework programmatically captures `stdout`/`stderr` strings for advanced processing and logging.
- **Advanced Port Scope Parsing:** Refactored the port scope parser in `port_scanner.py` to intelligently handle comma-separated lists, ranges, and single ports simultaneously (e.g., `22,80,443,1000-2000`).
- **Stage 2 EDR Evasion (OPSEC):** Hardened the Stage 2 C2 listener (`listener.py`) and dynamic reverse shell payload (`dynamic_reverse_shell.py`) by compiling incoming code strings into bytecode objects (`compile(..., 'exec')`) prior to execution. This effectively bypasses basic AST and string-based hooking from security products.

### Fixed
- **Nmap DB Sequence Metrics:** Fixed a logic flaw in the OS fingerprinting engine (`Custom_nmap_db_Lookup.py`) where raw TCP sequence numbers were being recorded. The engine now correctly calculates and evaluates the mathematical derivatives (GCD, SP, and ISR) required by Nmap's `nmap-os-db.txt`.
- **Aliases Abstraction Break:** Fixed a hardcoded JSON file read in `show.py` by routing alias fetching through the new `DatabaseManagment.getAliases()` abstraction.
- **Standalone Module Bootstrapping:** Updated numerous framework modules (including `host_discovery.py`, `Eternalblue.py`, and `CWE78_RCE.py`) to dynamically locate the framework root and pull configuration directly from the new SQLite core when executed as standalone scripts outside the main CLI.

---

## [1.2.15] - 2026-05-13

### Added
- **Fileless ELF Memory Loader (`session_loader.py`):** Added intelligent payload routing that detects compiled binaries (`.elf`, `.bin`) and automatically wraps them in a `memfd_create` Python loader. Allows execution of C-based kernel exploits directly from RAM without touching the disk.
- **Native Python Execution Engine:** Upgraded the Stage 2 reverse shell (`dynamic_reverse_shell.py`) to actively intercept Python execution strings (`exec()` or function calls). Evaluates them directly in RAM and captures `sys.stdout` over the TLS socket, completely bypassing the noisy `shell=True` subprocess fallback.

### Changed
- **Universal C2 Load Command:** Updated the session manager's `load` command to route through the new `SessionLoader` class, providing seamless loading of both Python exploits and native C binaries.
- **Stage 2 Fallback Synchronization:** Synced the hardcoded Stage 2 shell in `listener.py` with the new native Python execution engine to ensure the C2 remains fully functional even if external payload files are deleted.

---

## [1.2.14] - 2026-05-12

### Added
- **Advanced Nmap Signature Parsing:** Enhanced the OS fingerprinting engine (`Custom_nmap_db_Lookup.py`) to natively parse complex Nmap ranges (e.g., hex ranges like `400-FFFF`) and alternatives (`Y|N`), dramatically improving accuracy on noisy networks.
- **Non-Interactive TTY Fallback:** Added a safety net in the core input handler. If the framework is executed in a background process, IDE, or detached sudo environment where `prompt_toolkit` fails to attach to a TTY (`termios.error`), it gracefully falls back to the standard Python `input()` function.

### Changed
- **Safe Target Merging:** Upgraded `host_discovery.py` and `Custom_nmap_db_Lookup.py` to safely merge discovered data (like MAC addresses and OS fingerprints) into existing target dictionaries without destroying previously collected open ports.
- **OS Fingerprinting Engine Parity:** Brought `Custom_nmap_db_Lookup.py` up to architectural parity with the port scanner by adding dynamic `sys.path` injection for sudo subprocesses and native JSON file I/O fallbacks.

### Fixed
- **Target Database Wipes:** Fixed a critical bug in `host_discovery.py` that aggressively overwrote existing target dictionaries with a string (`"N/A"`), wiping out previously discovered port data.
- **Subprocess Memory Loss:** Added explicit `DatabaseManagment.sync_targets_to_disk()` calls inside `host_discovery.py` and `Custom_nmap_db_Lookup.py` so isolated sudo subprocesses properly flush their memory to disk before exiting, ensuring the main framework recognizes the updates.

---

## [1.2.13] - 2026-05-10
### Added
- **CIDR Subnet Support:** Upgraded the async port scanner to natively support CIDR notation (`192.168.0.1/24`) by utilizing the built-in `ipaddress` module to automatically expand and iterate through target ranges.
- **Global Exception Handler:** Implemented a global exception catching block in `main.py` to prevent silent crashes and gracefully dump tracebacks during fatal framework failures.

### Changed
- **In-Memory Config Caching:** Completely overhauled `DatabaseManagment` and the `set` command to treat `cls.core_db` as the single source of truth in memory, drastically reducing disk I/O and resolving cache desynchronization.
- **Pretty-Print JSON:** Standardized `data.json` and `targets.json` output formatting to use `indent=4` to automatically generate clean, human-readable configuration files right from startup.
- **Sudo Subprocess Resilience:** Enhanced `recon_engien.py` to dynamically inject true script paths into the execution buffer, fixing `__file__` resolution issues when executing from `/tmp`.
- **Target Cache Syncing:** Configured `recon_engien.py` and `port_scanner.py` to explicitly flush memory to disk before and after execution, ensuring `sudo` subprocesses always access and update the absolute latest target data.

### Fixed
- **Info Command UI Bug:** Removed a rogue `os.system("clear")` call in `exploitDetails` that was wiping the terminal screen and deleting previous command outputs.
- **Sudo Module Imports:** Fixed an `ImportError` bug during isolated `sudo` module execution by dynamically appending the framework's `source` directory to `sys.path`.
- **POSIX Locale Encoding Crash:** Added `encoding="utf-8"` to all file read/write operations across the framework to prevent `UnicodeDecodeError` silent crashes when running in restricted `C` or `POSIX` `sudo` environments.
- **Legacy Target Database Crash:** Fixed a `TypeError` in the target database manager that caused the framework to crash when encountering legacy or corrupt string entries instead of mapping them as dictionaries.
- **Multi-Word Variable Truncation:** Fixed the `set` command parsing logic so that multi-word values (e.g., payloads or descriptions) are joined properly and no longer truncated to the first word.
- **Startup Crash:** Removed an orphaned, parameter-less `_quick_parse()` call in `inputHandler.py` that was triggering a fatal `TypeError` on framework boot.

---

### [1.2.12] - 2026-05-10
### Added
- **ServiceDetector:** Introduced an asynchronous heuristic service and protocol detector to the native port scanner (`port_scanner.py`).
- **Dual-Probe Architecture:** The port scanner now utilizes both passive listening and active generic HTTP probing to coerce service banners.
- **Nmap Signature Parsing:** Added the ability to dynamically parse and compile regex signatures from `nmap-service-probes.txt` natively over Python raw sockets.
- **Interpreter-Level Caching:** Implemented a global cache via the `sys` module (`sys._supersploit_nmap_cache`) to prevent re-parsing of the massive Nmap database during dynamic module reloads, resulting in near-instantaneous subsequent scans.
- **Target Database Integration:** Discovered open ports, services, and banners are now seamlessly logged to the framework's core target database (`DatabaseManagment`).
- **Heuristic Fallbacks:** Added a `COMMON_PORTS` dictionary to accurately guess services when banners cannot be extracted or active probes are dropped.

### Fixed
- **Auto-Suggest Target Querying:** Fixed a bug in `inputHandler.py` where the `auto_suggest` engine queried the main configuration database instead of the dedicated targets database, resulting in missed port data.
- **Metadata Parsing Crash:** Fixed an `auto_suggest.py` error where the correlation engine tried to read keywords as object attributes from file path strings. It now accurately queries the `ExploitCache` metadata index.
- **Keyword Type Handling:** Added robust parsing in `auto_suggest.py` to gracefully handle legacy comma-separated string formats for `keywords` if a module developer forgets to use a YAML array.
- **Exploit Cache Status Conflict:** Resolved an issue in `database.py` where a module's YAML `status` (e.g., "testing") collided with the framework's internal read `status` ("ok"). Separated these into `dev_status` and `status` to prevent the "Select a valid exploit first" lock-out error.
- **Info Display Clutter:** Cleaned up the `info` command CLI output to actively filter out redundant internal framework keys (`name`, `cve`, `info`, `status`) from the secondary print loop.
- **Target Serialization:** Ensured target dictionaries are properly queried and formatted when the auto-suggest engine executes post-reconnaissance.

## [1.2.11] - 2026-05-10
### Added
- **Intelligent Auto-Suggest:** Introduced the `auto_suggest` command which automatically analyzes a target's open ports from RAM and correlates them with framework exploits based on metadata keywords.
- **C2 Connection Heartbeat:** Implemented an aggressive heartbeat monitor in the background TLS listener. It utilizes both OS-level TCP Keepalives and a 60-second 1-byte ping loop to automatically detect drops and purge dead sessions.
- **macOS/BSD Socket Reclamation:** Added `socket.SO_REUSEPORT` support to the background listener to forcefully bypass strict kernel-level socket TIME_WAIT locks that previously caused "Address still in use" errors on macOS.
- **Help Documentation Redesign:** Overhauled the entire `.data/.help/` directory. Help menus now feature a stylized markdown aesthetic with emojis, clearer syntax examples, and updated C2 documentation.

### Changed
- **Unified C2 Listener Routing:** Removed duplicate and conflicting socket listening code from `exploithandler.py`. All reverse shell catching is now routed cleanly through the centralized `Listener` class, ensuring `sessions` always displays active connections.
- **Robust Argument Parsing:** Updated `sessions.py` to use `shlex.split()` instead of standard string splitting, preventing index out-of-bounds crashes when users enter multiple spaces.

### Fixed
- **Path Parsing Resilience:** Replaced hardcoded colon (`:`) path separators in `inputHandler.py` with cross-platform `os.pathsep`, preventing crashes on Windows or misconfigured PATH environments.
- **Boolean Parsing Bug:** Fixed an initialization crash in `inputHandler.py` where a raw boolean `True` from the configuration database would crash the `.lower()` string cast check.
- **Use Command Bounds Check:** Added bounds checking and `ValueError` handling in `use.py` to gracefully reject invalid or non-integer indices instead of crashing the framework.

## [1.2.10] - 2026-05-10
### Added
- **Extended Port Scope Configuration:** Added support for the `PORT_RANGE` flag in the async port scanner. The scanner now intelligently merges the `PORTS` and `PORT_RANGE` database variables to allow for simultaneous custom lists and specific ranges.
- **Fileless Payload Delivery:** Transformed the payload generator in `exploithandler.py` into a purely in-memory architecture. SuperSploit now automatically formats generated stagers into Base64-encoded Python one-liners, allowing for instant, diskless execution on target machines.
- **Advanced Diagnostic Commentary:** Injected extensive inline debugging notes (`# DEBUG TIP:`) throughout the async port scanner detailing `asyncio` file descriptor constraints, TCP handshake bottlenecks, and socket exception triage.
- **Automated Exploit-to-Payload Linking:** Upgraded the `ExploitHandler` execution logic to automatically detect if `PAYLOAD` is set in the database during exploit execution. If present, the framework seamlessly compiles the payload, caches the encryption key, and starts the C2 listener dynamically before the exploit fires.
- **Modular Stage 2 Payloads:** Added the ability to dynamically load custom post-exploitation C2 payloads by setting the `STAGE_TWO` database variable. If not set, the framework safely falls back to a default interactive reverse shell.
- **SSL/TLS Command and Control (C2):** Upgraded the C2 communication architecture from basic XOR encryption to fully authenticated SSL/TLS stream encryption. The framework now automatically leverages `openssl` to generate ephemeral self-signed certificates and wrap the raw TCP sockets. The stager payload has been updated to initiate a client-side TLS handshake while ignoring strict certificate validation.
- **Detailed Reconnaissance Logging:** Implemented a unified dual-handler logging architecture across all recon modules (`host_discovery.py`, `port_scanner.py`, `Custom_nmap_db_Lookup.py`). The modules now write clean output to the console (`INFO`) while simultaneously writing highly detailed socket forensics, dropped packets, and exception states to a centralized background file (`.data/.logs/recon_activity.log`) at the `DEBUG` level.
- **Write-Back Memory Cache:** Implemented a centralized in-memory state manager for the targets database within `DatabaseManagment` to drastically reduce disk I/O and prevent race conditions.
- **Background Synchronization & Graceful Shutdown:** Added a daemon thread that silently flushes dirty memory cache to disk every 60 seconds, along with a `finally` block in `main.py` to guarantee pending targets are safely serialized upon application exit.

### Changed
- **Port Boundary Expansion:** Updated the async port scanner's boundary calculation to support scanning port `0`, officially spanning the entire `0-65535` range.
- **Stale Cache Elimination:** Refactored `host_discovery.py` and `os-fingerprint.py` to load the `data.json` database dynamically at execution time (within `Start.__init__`) rather than at global module import time.
- **Dynamic Port Targeting:** Updated the native `os-fingerprint.py` module to fetch the target port from the database (`R_PORT`) dynamically instead of enforcing a hardcoded port 80 check.
- **JSON Dictionary Optimization:** Simplified target appending logic in both the port scanner and Custom Nmap OS Lookup modules using Python's native `dict.setdefault()`, significantly reducing verbosity and eliminating the risk of `KeyError` crashes.
- **Dual Variable Syntax:** Updated the payload generator and listener to intelligently support both standard (`LHOST`/`LPORT`) and legacy (`L_HOST`/`L_PORT`) variable syntaxes simultaneously to prevent failed reverse shell callbacks.
- **Silent Auto-Generation:** Refined the automated payload compilation workflow to run completely silently in the background, removing unnecessary UI view prompts and keeping the exploit execution sequence completely seamless.
- **Show Command Formatting:** Refined the `show` command output to elegantly truncate extremely long values (like the Base64 generated payload) to keep the CLI visually aligned and prevent terminal clutter.
- **Recon Disk I/O Reduction:** Upgraded all native recon modules (`port_scanner.py`, `host_discovery.py`, and `Custom_nmap_db_Lookup.py`) to map discovered targets directly to the framework's lightning-fast in-memory cache. Included a seamless `ImportError` fallback so the modules remain fully functional as standalone CLI scripts using standard file I/O.

### Fixed
- **Input Fallback Safety:** Hardened the async port scanner's scope generation block. If an invalid or malformed port range is provided, it now gracefully defaults to well-known privileged ports (`1-1024`) instead of crashing or executing an empty scan.
- **OS Fingerprint Accuracy:** Fixed a critical assumption in `Custom_nmap_db_Lookup.py` where closed ports were blindly guessed. The engine now actively scans for verifiable closed TCP (via `RST`) and UDP (via `ICMP Port Unreachable`) ports using random high-port probes, drastically improving the accuracy of T5-T7 and U1 Nmap signature metrics.
- **Session ID Persistence:** Fixed a string-parsing logic bug in `source/main.py` where the framework's unique UUID session ID was failing to save to the database on boot. The `SetV` handler now correctly receives argument lists rather than raw strings, ensuring activity logs accurately track the active session.
- **Listener Port Alignment:** Fixed a configuration key typo in `exploithandler.py` where the background C2 listener was querying `L_PORT` instead of `LPORT`, causing it to listen on port `4444` while payloads were generated for `5000`. The payload generator and listener are now perfectly synchronized.
- **Dangling Listener Cleanup:** Fixed a bug where running an exploit multiple times in a single session resulted in an `[Errno 48] Address already in use` crash. The `ExploitHandler` now tracks active daemon sockets and cleanly terminates them before binding new listeners, preventing port contention and mismatched XOR keys.
- **Stager Execution Bug:** Added the missing `Start()` initialization call to the bottom of the `stager.py` payload. The fileless Stage 1 stager now automatically executes upon being decoded in memory on the target.
- **Loopback IP Trap:** Implemented a pre-generation sanity check that warns users if they accidentally attempt to map a reverse shell back to a local loopback or wildcard address (`127.0.0.1` or `0.0.0.0`).
- **Stage 2 Cryptography Crash:** Fixed a `TypeError` in the C2 handler where dynamically loaded Stage 2 payload files were read as standard strings instead of raw bytes, which crashed the XOR encryption loop.
- **Display Control Flow:** Fixed a missing `else` block in `show.py` that caused truncated strings to instantly print their full-length counterparts on the very next line.

## [1.2.9] - 2026-05-10
### Added
- **Advanced Nmap OS Fingerprinting:** Implemented a highly accurate, pure-Python OS fingerprinting engine (`Custom_nmap_db_Lookup.py`) using Scapy. Replicates Nmap's 13 specific probes (SEQ, OPS, WIN, ECN, T1-T7, U1, IE) and correlates raw responses against `nmap-os-db.txt` using official generation match points and weight formulas.
- **Concurrent Network Probing:** Upgraded the OS fingerprinting engine to utilize `asyncio` combined with a `ThreadPoolExecutor` to execute blocking Scapy network probes concurrently, drastically accelerating OS detection.
- **Heuristic Service Detection:** Introduced a `ServiceDetector` class to the native async port scanner, providing active protocol signature matching (e.g., `SSH-2.0`, `HTTP/1.1`) and intelligent standard-port fallbacks.
- **Custom Port Scopes:** Added support for specifying custom port sweeps in the async port scanner utilizing the `PORTS` global variable (supports comma-separated lists and ranges like `80,443,8000-8080`).

### Changed
- **Dynamic Variable Loading:** Refactored the async port scanner to load `data.json` dynamically at execution time rather than at module import time, eliminating stale memory cache bugs when users update global variables.
- **Centralized Target Persistence:** Upgraded both the port scanner and OS fingerprinting modules to natively append their findings (open ports, detected services, and matched OS fingerprints) directly to the nested `TARGETS` dictionary in `targets.json` without destroying or overwriting existing host entries.
- **Educational Code Documentation:** Added deep, technically rigorous inline docstrings across `host_discovery.py`, `port_scanner.py`, and `Custom_nmap_db_Lookup.py` explaining raw socket behavior, OSI network layers, `asyncio` limitations, and packet formulation logic.

### Fixed
- **Module Metadata Integration:** Fixed a critical `IndexError` crash in the `recon_engien.py` loader by injecting the missing `#!#!#!` framework metadata block into the new OS fingerprint module.
- **Scapy Parsing Exception:** Resolved a `Layer [IP] not found` exception in the OS fingerprint module's ICMP Echo (IE) probe by validating packet request IDs directly instead of improperly digging into Echo Reply payloads.
- **Connection Reset Handling:** Added `ConnectionResetError` catching in the port scanner to prevent mid-handshake firewall `RST` packets from crashing the asynchronous event loop.

## [1.2.8] - 2026-05-08
### Added
- **Recon Documentation:** Created a dedicated and highly detailed help page for reconnaissance modules (`.data/.help/recon`).
- **Feature Documentation:** Documented new core framework features in the help files, including automated post-recon exploit suggestions (`auto_suggest`), native background raw TCP listeners (`listener`), and comprehensive target database management.

### Changed
- **Help System Overhaul:** Completely rewrote and stylized the core help files (`all`, `show`, `search`, `use`, `set`, and `modules`). Introduced cleaner visual formatting, emoji headers, better sectioning, and more detailed command usage examples.

### Fixed
- **Search Output Clutter:** Updated `source/core/search.py` to correctly filter out and hide `__pycache__` directories when searching for exploits, payloads, and recon modules.
- **Code Cleanup:** Fixed a malformed and duplicate class definition/import statement at the top of `source/core/search.py`.

## [1.2.7] - 2026-05-08
### Added
- **Native Host Discovery:** Implemented `recon/native-discovery/host_discovery.py` using raw sockets and Scapy to perform hyper-fast asynchronous Layer 2 (ARP) and Layer 3 (ICMP) ping sweeps, completely replacing Nmap's `-sn` capabilities.
- **Async Port Scanner:** Upgraded the native port scanner in `recon/native-portscan/port_scanner.py` to utilize Python's `asyncio` and `Semaphore` for non-blocking, concurrent network mapping and dynamic active banner grabbing.

### Changed
- **Dedicated Targets Database:** Separated discovered network targets from the main framework configuration (`data.json`) into a dedicated `targets.json` database. Updated `DatabaseManagment` in `source/core/database.py` and the host discovery module to seamlessly read from and write to this new structure.

### Fixed
- **Recon Module Caching Bug:** Fixed an issue in `source/core/recon_engien.py` where switching recon modules would execute the previously loaded module. The database configuration fetch (`DatabaseManagment.get()`) was moved inside the `Recon.__init__` method to guarantee the latest module path is pulled on every execution.

## [1.2.6] - 2026-05-08
### Added
- **Recon Commands in Help:** Added the `recon` command to `.data/.help/all` and created `.data/.help/recon` help documentation.
- **Recon Support in Search:** Added the `recon` category to the `search` command to search for recon modules in `source/core/search.py`.
- **Recon Selection in Use:** Updated the `use` command in `source/core/use.py` to allow selecting and setting `RECON_NAME` and `RECON_PATH` when using recon modules.
- **Port Scanner Recon Module:** Added a new native port scanner module in `recon/native-portscan/port_scanner.py`.
- **Recon Logging:** Created a new `recon_activity.log` file with rotation logic for reconnaissance sessions in `source/core/logger.py`.
- **Recon Engine Execution:** Implemented the actual execution capability using a dynamically loaded Python module for recon scripts in `source/core/recon_engien.py` and linked it via the `Input` handler.

### Changed
- **Database Recon Management:** Extended `DatabaseManagment` in `source/core/database.py` with `UpdateReconDB` and `_reconDB` to map and parse recon directories.
- **Configuration Schema:** Added `dev_mode`, `sessionId`, `recon_name`, and `recon_path` variables to the main DB configuration loader.
- **OS Fingerprint Script:** Migrated `os-fingerprint.py` from `source/core/recon/` to `recon/os-fingerprinting/` and enhanced the start script implementation.

### Fixed
- **Python Module Loader Issue:** Corrected typos (`biypass` -> `bypass`, `spec_from_fle_location` -> `spec_from_file_location`) when executing Python payloads dynamically via `importlib` in `source/core/exploithandler.py`.
- **Installer Script Fix:** Corrected an issue where `supersploit` would fail directly without `sudo` in `install.sh` and `start.sh` due to permission checks.

## [1.2.5] - 2026-05-02
### Added
- **Advanced OS Fingerprinting:** Expanded the network fingerprint dictionary in `os-fingerprint.py` to capture deep IP and TCP layer metrics (TOS, IHL, fragmentation, seq/ack numbers) and explicit TCP option ordering (`options_order`) for improved identification accuracy.

### Changed
- **Documentation:** Added comprehensive docstrings and inline comments to the `Recon` class in `source/core/recon_engien.py` to improve maintainability and clarify dynamic execution logic.

### Fixed
- **Target Parsing:** Integrated `urllib.parse.urlparse` in the OS fingerprint module to safely sanitize URLs and strip ports from `R_HOST` before executing Scapy network probes.
- **Graceful Error Handling:** Added explicit exception catching for `PermissionError` and `Scapy_Exception` in `os-fingerprint.py` to warn users about missing root privileges instead of crashing the engine with stack traces.

## [1.2.4] - 2026-04-29
### Added
- **OS Fingerprinting Engine:** Introduced modular `OSFingerprintEngine` class for active OS detection via TCP fingerprinting with Scapy integration. Supports remote signature database queries and session-based logging.
- **Development**: Introduced a `DEVMODE` toggle in `start.sh` to allow running the application directly from the source directory.
- **Development**: Added basic support for mac-os development.
- **Documentation**: Added comprehensive module, class, and method docstrings to `source/core/database.py`.
- **Documentation**: Added inline comments to clarify YAML metadata extraction, file traversals, and JSON database modifications.
- **Documentation**: Updated exploit integration documentation with complete working examples demonstrating variable retrieval, socket usage, and error handling patterns.

### Changed
- **Help System Redesign:** Completely restructured help documentation with ASCII art branding, organized command categories, and improved clarity for end-users.
- **Command Simplification:** Eliminated command categories (`recon_cmds`, `wifi_cmds`, `bt_cmds`) from the input handler to streamline core functionality and reduce complexity.
- **Architecture:** Refactored the input handler to remove verbose command routing, enabling a future plugin-based reconnaissance system.
- **Code Style**: Refactored boolean conditional prompts in `source/core/exploithandler.py` to be more Pythonic.
- **Session Logging:** Continued session-based activity tracking with framework launch events logged to `activity.log`.

### Deprecated
- **Reconnaissance Module:** The legacy `reconCore` module is deprecated in favor of future modular recon plugins. This includes Bluetooth utilities, external tool wrappers, and network reconnaissance functions.

### Removed
- **BREAKING**: The following commands are no longer available: `ducky`, `ranger`, `recon`, `scan`, `full-scan`, `custom-scan`, `get-targets`, `import-targets`, `view-targets`, `port-scan`.
- **Bluetooth Module:** Removed `BlueDucky.py` and all HID keyboard emulation utilities.
- **External Tool Wrappers:** Removed `phoneinfoga`, `namesearch`, and `bettercap` wrapper classes.
- **Network Reconnaissance:** Removed `NmapWrapper` class and associated nmap scanning functionality.
- **Legacy Data Files:** Removed nmap targets (`target.json`), security checksums (`checksums.json`), and deprecated help files.
- Purged `__pycache__` directories for removed modules to maintain a clean repository state.

### Fixed
- **Critical Bug:** Fixed a Python module caching bug in `source/core/exploithandler.py` by implementing dynamic module loading (`importlib.util`) to bypass `sys.modules` cache retention.
- Corrected the `except` block syntax in `exploithandler.py` from `except Exception or KeyboardInterrupt:` to `except (Exception, KeyboardInterrupt):`.
- Fixed invalid exception handling syntax and exception-swallowing `return` statements in the Python exploit module runner's `finally` block.
- Implemented cleanup for the temporary `exec_temp.py` file in `exploithandler.py` to prevent leftover files.
- Removed redundant `file.close()` calls within `with` statement context managers.
- Removed an unnecessary `chmod +x` subprocess call after `gcc` compilation for C exploits.
- Cleaned up logic for executing dynamically loaded Python exploit modules with and without arguments.
- **Input Handling**: Fixed an issue where trailing spaces were not properly removed from user input by changing `lstrip` to `rstrip` in `inputHandler.py`.

### Security
- Added system package integrity verification for `recon-ng` using the `validator` module (`inputHandler.py`).

---

## [version 1.2.3] - 2026-04-21
### Enhancements
* **Command Handler Refactoring:** Streamlined WiFi scanning commands by removing deprecated target management workflow. Unified scanning interface with simplified `scan` and `full-scan` commands.
* **External Tools Modernization:** Updated external tool classes (`bettercap`, `namesearch`, `phoneinfoga`) with improved error handling, better prompt integration, and consistent code patterns.
* **Debug and Info Commands:** Added new diagnostic commands `debugdb` (displays full database memory cache) and `update-info` (updates exploit cache) for enhanced troubleshooting.
* **Input Handler Improvements:** Refactored input handler to use `NmapWrapper` directly instead of legacy nmap module imports with proper error handling.

### New Features
* **Diagnostic Commands:** Implemented `debugdb` command to print full database memory cache for debugging purposes.
* **Cache Update Command:** Added `update-info` command to manually trigger exploit cache updates.
* **Info Display Command:** Added `info` command for displaying current exploit details in the CLI.
* **Enhanced NmapWrapper:** Improved network scanning with better target range formatting and verification.

### Bug Fixes
* **Database Method Signatures:** Fixed `DatabaseManagment.Debug()` method to properly accept optional data parameter.
* **ExploitCache Update Method:** Fixed `ExploitCache.update()` to accept optional parameter for consistent API usage.
* **External Tool Module Imports:** Cleaned up external tools module initialization by removing stale imports.
* **Network Recon Import Issues:** Fixed NetworkRecon module initialization to use direct `NmapWrapper` import.
* **Command Registration:** Fixed various command registrations in input handler that were failing due to incorrect method signatures.

### Code Quality
* **Removed Deprecated Features:** Eliminated old target management commands (`get-targets`, `import-targets`, `view-targets`, `view-targets-v`, `port-scan`, `scan-target`) that are now consolidated into simplified scanning interface.
* **Module Cleanup:** Removed unused `wireshark.py` and cleaned up external tools `__init__.py` for better maintainability.
* **Improved Error Handling:** Enhanced subprocess error handling and verification checks in network reconnaissance tools.
* **Test Exploit Updates:** Updated test exploit metadata with proper CVE format and enhanced description.
* **Payload Refinements:** Updated `exec_temp.py` with improved SQL injection test exploit demonstrating command injection payloads.

### Maintenance
* **Help Documentation:** Updated help files to reflect new command structure with `scan` and `full-scan` replacements.
* **Code Refactoring:** Reorganized external tool implementations for consistency and maintainability.
* **Activity Logging:** Continued operational logging and tracking of framework execution sessions.

---

## [version 1.2.2] - 2026-04-21
### Enhancements
* **Python Exploit Handler Refactoring:** Restructured `exploithandler.py` with improved metadata handling using delimiter-based parsing (`#!#!#!`).
* **Temporary File Execution:** Implemented cleaner temporary file handling for exploit execution with consistent path management via `exec_temp.py`.
* **Module Execution Improvements:** Enhanced dynamic module loading with better file cleanup and metadata separation.
* **Network Information Gathering:** Replaced subprocess-based network detection in `inputHandler.py` with efficient `psutil` library integration for improved reliability and cross-platform compatibility.

### New Features
* **Test Exploit Framework:** Added new test exploit (`exploits/test/test.py`) demonstrating the new metadata delimiter system for exploit documentation.
* **Enhanced Network Detection:** Implemented smarter IPv4 address detection that filters out loopback addresses and properly retrieves network interface information.

### Bug Fixes
* **Handler Initialization:** Fixed database initialization in exploit handler with proper `DatabaseManagment.get()` calls.
* **Argument Parsing:** Improved argument parsing and shell command construction in Python exploit execution.
* **Network Information Retrieval:** Fixed `get_network_info()` in `inputHandler.py` to reliably detect non-loopback IPv4 addresses across different system configurations.

---

## [version 1.2.1] - 2026-04-21
### Bug Fixes
* **Missing Functions Resolution:** Fixed critical issues with missing functions that were causing execution failures.
* **Code Refactoring:** Optimized `search.py` and `exploithandler.py` with streamlined logic and reduced redundancy.
* **Input Handler Improvements:** Enhanced `inputHandler.py` with better error handling and validation.

### Code Quality
* **Database Optimization:** Further refined `database.py` with improved caching mechanisms and reduced complexity (225 lines refactored).
* **Exploit Cleanup:** Removed obsolete exploit files for Windows, routers, and deprecated Android tools that were no longer maintained.
* **Chrome Exploit Updates:** Updated Chrome OS privilege escalation exploit with refined execution logic.

### Maintenance
* **Asset Cleanup:** Removed outdated PDF and image assets from the assets folder for better repository hygiene.
* **Activity Logging:** Enhanced operational logging in `activity.log` to track framework execution more reliably.
* **Configuration Updates:** Updated `.data/.config/data.json` with improved settings management.

---

version 1.2.0

## [Core Updates & Refactoring]
### I/O & Performance Optimizations (Bottleneck Fixes)
* **Database I/O Reduction:** Updated `getCVE` in `database.py` to cache results locally. It now returns the CVE immediately if present, preventing redundant disk reads on the exploit file during subsequent calls.
* **Streamlined Standard Output:** Refactored `ToStdOut.py` to write directly to `/dev/stdout` instead of using the standard `print()` function, handling formatting and decoding on the fly to prevent output-heavy payloads from lagging the terminal.
* **Silent Error Handling:** Reworked `errors.py` to dump stack traces silently to `.data/.errors/error.log` without interfering with active program execution or disrupting the CLI flow.

### Centralized Caching & Data Management (`database.py`)
* **In-Memory Exploit Location Cache:** Implemented centralized in-memory caching system for exploit locations and payloads to eliminate redundant file system traversals and significantly improve lookup performance across framework operations.
* **Central Database Architecture:** Transitioned to a unified central database for managing all exploit metadata, locations, and associated payloads. This centralized approach ensures consistency across the framework and reduces data fragmentation.
* **Optimized Cache Invalidation:** Integrated smart cache invalidation mechanisms that maintain data freshness while minimizing disk I/O operations.

### Execution Engine Enhancements (`exploithandler.py`)
* **Dynamic Python Modules:** Added the ability to load and run Python exploits directly into memory as dynamic modules (`importlib.util`). This prevents polluting source folders or causing cache bugs, executing the `exploit()` function directly.
* **Bash Return State Auditing:** Updated the `sh` execution handler to strictly evaluate shell return codes, properly distinguishing between successful runs and failures.
* **C-Compilation Safety:** Added real-time GCC compilation for C exploits with an automatic, fail-safe cleanup mechanism. The compiled `./exploit_bin` is reliably removed after execution, even if a crash or interrupt occurs.
* **Terminal Parsing:** Added `findTerm()` in the database manager to dynamically verify available terminal programs against `/bin` for the threaded exploit handlers.

## [New Features]
### Activity Logging System (`logger.py`)
* **Operational Auditing:** Separated debugging errors from operational logs. Created a dedicated `activity.log` to track exactly which exploits were run, when, and against which targets.
* **Session ID Tracking:** Integrated an 8-character hex Session ID (via `uuid`) generated upon framework launch. All exploit executions are tied to this ID, making it easy to track the flow of a single session.
* **Staged Initialization:** Added a `start_session()` hook that prints a clear demarcation line in the log file every time the framework is booted up.
* **Verbose Arguments Toggle:** Added a `VERBOSE_LOGGING` flag to the database key map. When toggled on, the framework securely dumps the exact command-line arguments and options passed to scripts and binaries into the log.
* **Zero-Lock Log Rotation:** Implemented a native, footprint-conscious log rotation script. If `activity.log` exceeds 5MB, it is instantly archived with a timestamp using `os.rename`, preventing locking issues and keeping the tool lightweight.

### Modular Help Architecture (`help.py`)
* **File-Based Documentation:** Removed hardcoded help strings from the core logic. Help documentation is now pulled dynamically from modular text files stored in `.data/.help/` (e.g., `main`, `set`, `search`).
* **Path Sanitization:** Integrated strict input sanitization (`os.path.basename`) on user topic requests to prevent directory traversal exploits when querying help files.
* **Improved Topic Handling:** Added error handling for missing help topics, defaulting to "all" help file when no topic is specified. Updated help directory path for consistency.

## [Bug Fixes]
### Execution Engine Enhancements (`exploithandler.py`)
* **Method Reordering:** Corrected the order of `sh` and `c` handler methods to match their intended functionality.
* **Enhanced Return Code Auditing:** Updated bash and Python script execution to properly evaluate return codes, distinguishing between successful runs and failures.
* **Improved C Compilation Logging:** Separated logging for C compilation and execution phases, with better error reporting using the Error class.
* **Dynamic Module Execution:** Enhanced Python module loading with proper success/failure logging based on return codes.

### Security and Stability Updates
* **Comprehensive Security Review:** Conducted full framework security audit and implemented stability improvements across all core modules.
* **Input Validation:** Strengthened input sanitization and validation throughout the codebase.
* **Error Handling:** Improved error logging and handling mechanisms to prevent crashes and improve user experience.

### General Improvements
* **Typo Corrections:** Fixed typos in `main.py`, `set.py`, `exploitHandler.py`, and other files.
* **Author Attribution:** Added proper citations for external tool authors (phoneinfoga, recon-ng, Bettercap) in documentation and code comments.

## Unreleased
### Added
* Chrome OS support started.
* Added `bettercap` to the tool list.
* Added `clean` method to clear the target list and scan history.
* Added a name search ability to recon.
* Added the eternal blue exploits and a leaked emails and password file.
* Added new exploit android root and linux setup file.
* Added blueDucky hid attack script and payloads, organized `.data` folder better.
* Added sha256-checksum verification for all external tools including blue-ducky, recon-ng, blue-ranger, nmap, phoneinfoga.
* Added the ability to run the python exploit as a module.
* Created SuperSploit Module Development Guide.

### Changed
* Updated `exploithandler.exploitDetails` class to show required arguments.
* Fixed `ToStdOut` to use `sys.stdout` then fallback on manually opening `stdout` if an error happens.
* Updated ADB interface: added the push method and ability to use the back camera.
* Updated the exploit handler to show required options.
* Updated input handlers for main, recon and Wi-Fi menus.
* Updated exploit handler to now be compatible with C exploits.
* Updated the recon to be able to run from anywhere on the disk.
* Integrated recon mode into main menu.
* UI and display text updates.
* Beautified the output of json dumps and more.
* Updated logo.
* Encryption update.
* Security and stability update.
* Enhance README with disclaimer and framework details.
* Update README with core strengths and features.
* Revise README with framework capabilities and roadmap.
* Enhance README with images for architecture and roadmap.

### Fixed
* Fixed the issue of aliases not working.
* Fixed formatting issues with exploits details, updated exploit handler.
* Fixed formatting issues with router exploits and added the ability to show aliases.
* Setup fixes.
* Fixed file path error in code.
* Fixed the setup script.
* Fixed typo in exploit handler.
* Fixed typo in `main.py` and `set.py`.
* Fixed typos.
* `exploithandler` fix.
* Fixed issues with missing functions.
* Fixed syntax error in `logger.py`.

### Removed
* Deleted a bunch of old test payloads and exploits from original dev back in 2020.