# SuperSploit Private Project Memory Index

## Core Components
- **Reconnaissance Modules**:
    - `recon/native-discovery/lateral_discovery.py`: Stealthy host discovery (NBNS, mDNS, LLMNR, SSDP). Requires root.
    - `recon/native-discovery/host_discovery.py`: Standard ARP/ICMP sweep.
- **Core Engines**:
    - `source/core/recon_engine.py`: Module loader and root elevation handler.
    - `source/core/database.py`: Centralized state and target management.

## Research & Documentation
- [Development Backlog](../../../.SuperSploit/docs/research/TODO.md): Roadmap for stealth, exploitation, and C2 features.
- [Android Payload Enhancements](./android-payload-enhancements.md): SMS/Call dumping and icon hiding.
- [Android Stealth Strategies](./android_stealth.md): Technical details on icon hiding and UI toggles.
- [LPE Enumeration Roadmap](./lpe_roadmap.md): Plans for Linux and Android local privilege escalation.
- [Native C Payloads](./native-c-payloads.md): Investigation into C-based stagers.
- [Unisoc BROM Exploit](./unisoc_brom_exploit.md): Analysis of bootrom vulnerabilities.

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
- [SSL Workflow](./analyzes/ssl_workflow.md)
