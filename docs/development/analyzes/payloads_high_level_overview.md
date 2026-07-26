# SuperSploit Framework - Active Payload Library (High-Level Overview)

*This document provides a strategic overview of the payloads and stagers integrated into the SuperSploit Framework. It details the operational capabilities, evasion techniques, and memory management mechanics used to maintain stealthy Command & Control (C2) persistence.*

---

## 1. Initial Access: Stagers (Stage 1)
*Objective: Establish a secure, fileless foothold on the target and load the heavier Stage 2 agent entirely into memory.*

### Standard Python Stager (`stager.py` & `stager_template.py`)
- **Architecture:** Pure Python.
- **Mechanism:** Uses a raw TCP socket wrapped in an unverified TLS/SSL context. It performs a timing-based anti-sandbox check (`time.sleep` delta) before proceeding.
- **Execution:** Receives a length-prefixed payload from the C2. It decodes (Base64), decrypts (XOR), and decompresses (Zlib) the payload. The payload is executed entirely in RAM via `types.ModuleType` and `exec()`, injecting the active socket directly into the new module's namespace.
- **Impact:** Leaves zero artifacts on disk. The Stage 2 payload is never written to a file.

### Windows Native Shellcode Stager (`windows_shellcode_stager.py`)
- **Architecture:** Python (using `ctypes` for native Win32 API calls).
- **Mechanism:** Connects back to the C2 via TLS/SSL to fetch raw, architecture-specific shellcode.
- **Execution:** Uses `VirtualAlloc` to carve out an `RWX` (Read-Write-Execute) memory page within the running Python process. It copies the shellcode using `RtlMoveMemory` and executes it as a background thread via `CreateThread`, blocking the main thread with `WaitForSingleObject`.
- **Impact:** Highly evasive. Bypasses file-based AV/EDR entirely by executing raw shellcode inside the trusted memory space of `python.exe`.

---

## 2. Post-Exploitation: Agents & Beacons (Stage 2)
*Objective: Provide the operator with interactive control, data exfiltration, and stealthy persistence.*

### Dynamic Reverse Shell / DRS (`dynamic-reverse-shell.py`)
- **Architecture:** Pure Python.
- **Mechanism:** An interactive, synchronous C2 agent. 
- **Evasion:** Employs heavy OPSEC measures. It dynamically resolves imports via base64/hex encoding (e.g., `_i(b'b3M=')` for `os`) to hide from static analysis. 
- **Features:** 
  - Implements a custom Base64+XOR send/receive loop.
  - **Process-less Execution:** Uses native Python routines to avoid spawning detectable child processes where possible (e.g., parsing `/proc` manually for `ps`, or using `os.geteuid` for `whoami`).
  - Supports direct fileless loading of additional Python scripts via the `load` command.

### Asynchronous Beacon (`beacon.py`)
- **Architecture:** Pure Python (HTTP/S).
- **Mechanism:** An asynchronous polling agent designed for long-term, stealthy persistence.
- **Features:** Sleeps for heavily randomized jitter intervals (e.g., 24 to 48 hours). It wakes up, checks the C2 server (`/file`) via HTTP GET for tasked commands, executes them in memory, and POSTs the encrypted results back (`/rfile`).
- **Impact:** Highly resilient against network heuristic analysis due to its randomized sleep cycles and standard HTTP traffic profile.

### Ghost Beacon / Smash-and-Grab (`ghost_beacon.py`)
- **Architecture:** Pure Python (HTTP/S).
- **Mechanism:** Ephemeral, highly obfuscated payload tailored for Smart TVs, IoT, and embedded Linux.
- **Features:** Uses character-shifting obfuscation to hide sensitive target paths. Upon execution, it instantly harvests Wi-Fi credentials (`wpa_supplicant.conf`, `connman` profiles), encrypts them, POSTs them to the C2, and immediately calls `sys.exit(0)` to self-destruct and clear its memory footprint.

### Stealth Keylogger (`keylogger.py`)
- **Architecture:** Python (Cross-Platform).
- **Mechanism:** Background thread execution.
- **Features:** 
  - On Linux/macOS, it attempts a silent PIP installation of `pynput` to hook the X11/Wayland input layer.
  - On Windows, it acts as a zero-dependency keylogger, natively querying `ctypes.windll.user32.GetAsyncKeyState` in a tight loop.
  - Buffers keystrokes silently in RAM until the operator issues the `keydump` command.

---

## 3. High-Performance Native Agents (C-Based)
*Objective: Provide maximum stability, speed, and OS-level integration for complex targets (Android/Linux).*

### Native C Stage 2 / DRS (`dynamic-reverse-shell.c`)
- **Architecture:** C (POSIX).
- **Mechanism:** Extremely lightweight, synchronous reverse shell.
- **Features:** 
  - Handles raw socket I/O for direct file uploads and downloads.
  - **Fileless Binary Execution:** Features a `load` command that receives a raw compiled binary over the socket, writes it to an anonymous file descriptor using `memfd_create`, and executes it directly from RAM (`/proc/self/fd/X`), completely bypassing disk-based File Integrity Monitoring (FIM).

### Phantom Agent (`phantom_agent.c`)
- **Architecture:** C (POSIX / Android).
- **Mechanism:** Advanced, persistent Android/Linux implant.
- **Evasion:** 
  - Uses `prctl(PR_SET_NAME)` to mask its process name (e.g., mimicking kernel workers `[kworker/u:1]`).
  - Uses `ptrace(PTRACE_TRACEME)` to detect and halt execution if being analyzed by a debugger.
- **Cryptography:** Implements a robust OpenSSL `AES-256-GCM` encryption loop with dynamic 12-byte Nonce/IV generation for all C2 traffic, wrapped in Base64.
- **Features:** Includes specialized Android command hooks (e.g., `dump_sms` and `dump_calls` via `content query` invocations).