# SuperSploit Private Project Memory

## Reconnaissance Modules
- `recon/native-discovery/lateral_discovery.py`: New module for stealthy host discovery using broadcast/multicast (NBNS, mDNS, LLMNR, SSDP). Requires root privileges. Discovered hosts are automatically saved to `targets.json`.
- `recon/native-discovery/host_discovery.py`: Standard ARP/ICMP sweep module.

## Core Engines
- `source/core/recon_engine.py`: Handles loading and execution of recon modules, including root privilege elevation via sudo for modules that require it.
- `source/core/database.py`: Centralized state management for variables (like `R_HOST`) and discovered targets.
# SuperSploit Framework Private Memory

## Project Overview
A sophisticated offensive security framework with a focus on stealth and multi-platform exploitation (Linux, Windows, Android).

## Recent Improvements (May 2026)

### Android Payload Refactoring
- **Encrypted C2**: Switched from raw TCP to XOR-encrypted HTTP beacons.
- **Stealth**: 
    - Implemented `jnius`-based app icon hiding (`HIDE_ICON`).
    - Added a silent UI toggle (`SHOW_UI`).
    - Integrated dynamic import obfuscation in templates.
- **Exfiltration**: Added `dump_sms` and `dump_calls` commands to the DRS template.
- **Enumeration**: Added `lpe_enum` for specialized Android vulnerability analysis.

### Local Privilege Escalation (LPE)
- **Linux**: Created `recon/native-discovery/linux_lpe_enum.py` for automated local auditing.
- **Android**: Added specialized exploit modules:
    - `exploits/android/cve_2016_5195_dirtycow.py`
    - `exploits/android/cve_2019_2215_badbinder.py`
    - `exploits/android/cve_2022_0847_dirtypipe.py`

### Core Infrastructure
- **C2 Server**: Upgraded to `ThreadingTCPServer` for concurrent session handling.
- **Path Resolution**: Fixed template pathing issues in `BuildozerPayloadGenerator`.
- **Database**: Reverted CLI logo toggle in `input_handling_engine.py` while keeping backend improvements.

## Active Sub-Notes
- [Android Stealth Strategies](./android_stealth.md)
- [LPE Enumeration Roadmap](./lpe_roadmap.md)

## Architectural Analyses
- [Android Payload Generator](./analyzes/android_payload_generator.md)
- [Auto-Suggest Engine](./analyzes/auto_suggest.md)
- [CLI Command System](./analyzes/cli_commands.md)
- [Cryptography & Obfuscation](./analyzes/cryptography.md)
- [Database System Architecture](./analyzes/database_system.md)
- [DB Migration & Management](./analyzes/db_migration_and_management.md)
- [Error Handling & Logging](./analyzes/error_and_logging.md)
- [Exploit Engine (Dynamic Execution)](./analyzes/exploit_engine.md)
- [Input Handling Engine](./analyzes/input_handling_engine.md)
- [Input Fixes & Hooks](./analyzes/inputfixes_and_post_recon.md)
- [Listener & Session Management](./analyzes/listener_and_session_management.md)
- [Payload Generation (Stagers)](./analyzes/payload_generation.md)
- [Asynchronous Port Scanner](./analyzes/port_scanner.md)
- [Recon Engine Architecture](./analyzes/recon_engine.md)
- [Session Registry Interaction](./analyzes/session_management.md)
- [Suggestion Engine Deep-Dive](./analyzes/suggestion_workflow.md)
