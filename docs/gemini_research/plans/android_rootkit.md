# Android Rootkit Research & Implementation (May 2026)

This research focused on developing a specialized Android payload template for rooted devices that bypasses standard security prompts and provides persistent, system-level access.

## Architecture
The rootkit is implemented as a headless Kivy application (`android_rootkit_template.py`). Unlike standard payloads, it contains no UI and masquerades as a system service.

## Key Features
- **Silent Root Elevation**: Integrates the **Dirty Pipe (CVE-2022-0847)** LPE exploit. This allows the payload to gain root privileges on vulnerable kernels (5.8 - 5.16) without triggering the Magisk/Superuser authorization prompt.
- **Magisk Persistence**: Implements an automated `persist` command that installs a startup script into `/data/adb/service.d/`. This ensures the payload restarts automatically on every boot.
- **Deep Data Extraction**: Includes the `dump_data` command, which leverages root access to archive and exfiltrate protected app data from `/data/data/` (e.g., WhatsApp databases, Browser history).
- **Silent App Management**: Provides commands to silently install or uninstall APKs in the background using the `pm` (Package Manager) utility via the root shell.
- **Stealth**:
    - Headless operation (no visible UI).
    - Thread renaming to `com.android.system.service` to evade manual process inspection.
    - Automatic launcher icon hiding via the Android PackageManager.

## Communication Protocol & SSL Security (Updated May 2026)
- **SSL/TLS Encryption**: The rootkit uses `ssl.PROTOCOL_TLS_CLIENT` to wrap its raw socket connection. It is configured to ignore hostname and certificate verification (`CERT_NONE`) to maintain compatibility with the framework's ephemeral, self-signed C2 certificates. This resolved the previous "SSL Handshake Error" during agent check-in.
- **Messaging Protocol**: Implements a structured XOR + Base64 protocol.
    - **Outbound**: Data is XOR-encrypted with a shared `XOR_KEY`, Base64 encoded, and prefixed with a 4-byte big-endian length header.
    - **Inbound**: Expects a 4-byte length header, followed by Base64 encoded XOR-encrypted data.
- **Command Dispatcher**: Includes a built-in dispatcher for core C2 commands (`ls`, `cat`, `upload`, `download`, `exec`, `load`, `ps`, `whoami`) and hooks for root-level execution via the `auto_root` and `_run_root` methods.
- **Reconnection Logic**: Implements jittered reconnection attempts (10-30 seconds) to ensure persistence despite network instability.
- **Stability & Persistence (Fix May 2026)**: 
    - Removed a 15-second socket timeout that caused frequent reconnections during idle periods. The agent now uses blocking sockets to align with the framework's heartbeat intervals (45-75s).
    - Implemented a root-level wakelock (`/sys/power/wake_lock`) that is automatically acquired once root privileges are established. This prevents Android's power management from terminating the background process.
- **Exploit Loading (Fix May 2026)**: Resolved "invalid syntax" errors in LPE exploits (`dirtycow`, `dirtypipe`) by wrapping framework metadata in multi-line strings. Updated payload delivery to explicitly register functions in `globals()` to fix "name not defined" errors during automated C2 triggering.
- **Exploit Triggering (Fix May 2026)**: Fixed `TypeError: exec() arg 1 must be a string` by removing redundant `exec()` wrapping in the listener and updating agent dispatchers to recognize raw function calls (e.g., `check_dirtycow()`) as Python code.
- **DirtyCOW Logic Fix (May 2026)**: Resolved a false negative in `cve_2016_5195_dirtycow.py` where vulnerability detection was incorrectly calculated on the attacker's machine. The check logic now executes dynamically on the target agent.
- **Help Documentation (Updated May 2026)**: Updated the framework's help engine (`generate-apk`, `android`, `listener`) to include documentation for the rootkit payload type and the `auto_root` command.
- **Linker Error Fix (May 2026)**: Resolved `CANNOT LINK EXECUTABLE` errors by sanitizing the environment in all Android payload templates. Child processes now clear `LD_LIBRARY_PATH` before execution to prevent linking against incompatible bundled Kivy/Python libraries.
- **Automated Cross-Compilation (May 2026)**: Upgraded `SessionLoader._load_c()` to automatically detect Android targets and utilize the Android NDK Clang compiler (`aarch64-linux-android*-clang`) for ARM64 compilation. This ensures that C-based exploits are binary-compatible with the target device before being staged in memory.

## Integration
- **Payload Type**: Added as the `rootkit` type in the `generate-apk` command.
- **Framework Support**: Updated `android_kivy_generator.py` and `input_handling_engine.py` to support automated generation of this variant.
