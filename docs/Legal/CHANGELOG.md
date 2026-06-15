# SuperSploit Framework - Changelog
# Changelog
All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **HTTP Beacon Endpoint Routing**: Implemented strict URI routing for the HTTP beacon payload (`beacon.py`). The payload now actively polls `GET /file` for task retrieval and utilizes `POST /rfile` for asynchronous data and file exfiltration.
- **Dynamic Stage 2 TLS Packaging**: Upgraded the background TLS listener to dynamically package, encrypt, and deliver Stage 2 in-memory C2 payloads upon catching Stage 1 connections, providing real-time console feedback.
- **Android Capabilities Documentation**: Added a comprehensive Android capabilities guide (`help android`) covering ADB reconnaissance, fileless AArch64 C2 execution, native post-exploitation commands (`pm`, `am`, `dumpsys`), and stealth execution.
- **APK Generator (`generate-apk`)**: Implemented a new command to generate standalone or trojanized Android APK payloads embedded with TLS/HTTP beacons.
- **Android Stealth & Beaconing Options**: Added support for advanced Android module options, including dynamic wakelocks (Doze mode bypass), automatic app icon hiding (`HIDE_ICON`), custom session tags (`TAG`), and fileless Termux deployment.

### Changed
- **Documentation Refinements**: Updated the `modules` development guide to explicitly outline how to declare required/optional options in the `#!#!#!` metadata block. Corrected the module integration guide reference in the main help menu and fixed markdown syntax in the `recon` guide.
- **Framework README**: Overhauled the core repository `README.md` to highlight the new Android capabilities, fileless C2 architecture, and automated reconnaissance features.

## [1.2.18] - 2026-05-15

### Added
- **Unified OSINT Persona Database:** Introduced an in-memory `ProfileDB` and `PersonProfile` system. Recon modules (Phone, Email, Background Check) now automatically correlate discovered data into a central persona tracking structure.
- **PDF Report Engine:** Integrated `fpdf` support for the Background Check module to generate professional, clickable OSINT reports in the `.loot/reports` directory.
- **Expanded OSINT Suite:** Added dedicated `email_recon.py` and `background_check.py` modules.

### Changed
- **Recon Automation:** Updated `show recon` to display deep metadata and requirement flags (like root or external libraries).

## [1.2.17] - 2026-05-14

### Added
- **Comprehensive Framework Reset:** Overhauled the `clean` command to perform a multi-layered wipe of the framework's state. It now purges session variables (`data.db`), target databases (`targets.json`), module metadata (`included.db`), and various exploit/recon caches.
- **Native Phone OSINT Module:** Added a pure-Python OSINT tool (`phone_recon.py`) that replicates PhoneInfoGa capabilities. Performs metadata extraction and footprint generation without external binaries.
- **In-Memory State Flushing:** The `clean` utility now resets the `DatabaseManagment` singleton state, releasing file locks and ensuring that commands like `show` immediately reflect the sanitized environment.

### Changed
- **Smart Cleanup Routine:** Refactored the cleanup logic to distinguish between text-based logs (truncation) and binary/serialized databases (removal). This ensures SQLite and Pickle files are correctly re-initialized by the framework.

### Fixed
- **In-Memory Exploit `__file__` Resolution:** Resolved a `NameError` where exploits relying on `__file__` for relative pathing would fail when executed as in-memory modules. The `ExploitHandler` now performs dynamic path injection into the code buffer.
- **Dynamic Installation Pathing:** Fixed the `clean` utility to resolve the framework's installation path using `DatabaseManagment.getInstall()`, ensuring it targets the correct files regardless of whether it's running in a production or development environment.

## [1.2.16] - 2026-05-13

### Security
- **TOCTOU Race Condition Patch:** Fixed a critical Time-Of-Check to Time-Of-Use vulnerability in `recon_engine.py`. By moving the user prompt to *before* the temporary Python script is written to disk, the race window for a local attacker to overwrite the file prior to `sudo` execution was eliminated.

### Changed
- **Fileless C Execution (OPSEC):** Refactored the C execution handler in `exploit_engine.py` to utilize `memfd_create` for fileless execution on Linux. Compiled binaries are now read into memory and executed via anonymous file descriptors, with the original binary wiped from disk immediately post-compilation to bypass disk-based EDR signatures.
- **SQLite Database Migration:** Overhauled the core `DatabaseManagment` engine to use a real-time SQLite database (`data.db`) via a custom `MutableMapping` wrapper (`SQLiteDict`). This seamlessly replaces the legacy JSON memory cache, providing robust transactional writes while preserving dictionary-style syntax (`db["KEY"]`) across the entire framework.
- **Programmatic Output Capturing:** Upgraded the C execution handler in `exploit_engine.py` to leverage `subprocess.run(capture_output=True)`. This allows the framework to programmatically capture `stdout` and `stderr` strings for logging and advanced processing, rather than dumping output blindly to the terminal.
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

### Changed
- Updated the bundled `nmap-os-db.txt` with a modification notice to comply with the NPSL and appended custom framework signatures.

## [1.2.12] - 2026-05-10
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