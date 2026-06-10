# SuperSploit Framework Development Roadmap

This document outlines the strategic engineering priorities for evolving SuperSploit into a production-grade security tool. The focus is on building a resilient, scalable, and stable core infrastructure before expanding feature density.

---

### **Architectural Prioritization Matrix**

| Backlog Phase | Current Priority | Recommended Priority | Engineering Justification |
| --- | --- | --- | --- |
| **1. OSINT & Reconnaissance** | Low | **Medium** | Implementing structured document scrapers and API integrations expands coverage safely within user-space before touching unstable low-level environments. |
| **2. Advanced Payloads & Persistence** | High | **Deferred Phase** | Introducing complex platform-specific modules before standardizing the core APIs and error recovery frameworks risks creating a fragile environment. |
| **3. Advanced Profile Research (Phase 1)** | Medium | **High** | Maximizes the utility of the newly integrated profile database for automated LPE tracking and fleet correlation. |
| **4. OSINT Persona Enrichment (Phase 2)** | Low | **Medium** | Bridges the gap between passive reconnaissance and active target persona management. |
| **5. Quality of Life (QOL)** | High | **High** | Enhancements to user experience and operational flow significantly improve framework usability and efficiency. |

---

## 1. 🔎 OSINT & Reconnaissance (Medium Priority)
*Objective: Expand footprint analysis capabilities with stable, user-space tools.*
- [ ] **Public Repo Scanner**: Search GitHub/GitLab for leaked API keys and internal docs.
- [ ] **Shodan/Censys Integration**: Leverage search engine APIs for banner grabbing and vulnerability correlation.
- [ ] **Domain/Subdomain Enumeration**: Identify subdomains, associated IPs, and DNS records.
- [ ] **Metadata Scraper**: Extract metadata from publicly available documents (PDFs, DOCX, XLSX).

## 2. 🚀 Exploitation & Payloads (Deferred Phase)
*Objective: Broaden the attack surface after the core infrastructure is stable.*
- [ ] **CVE Integration**:
    - [ ] **PwnKit / Polkit pkexec (CVE-2021-4034)** - *Integrate into interactive sessions for auto-escalation.*
    - [ ] F5 BIG-IP TMUI RCE (CVE-2020-5902).
- [ ] **Advanced Payloads**:
    - [ ] **Process Hollowing/Injection**: Injecting into trusted processes (Win/Linux).
    - [ ] **Windows Reflective DLL Injection**: Fileless DLL loading.
- [ ] **Platform Support**: Add native payload generation support for iOS.

## 3. ⚓ Persistence Mechanisms (Deferred Phase)
*Objective: Establish long-term access after the core C2 and payload systems are mature.*
- [ ] **WMI Event Subscription (Windows)**: Fileless event-based execution.
- [ ] **LD_PRELOAD Hijacking (Linux)**: Hooking functions via shared libraries.
- [ ] **DLL Sideloading**: Exploiting DLL search order in legitimate apps.

## 4. 🧠 Advanced Profile System (Phase 1)
*Objective: Transform the profile system into an automated, long-term threat intelligence database.*
- [ ] **Automated Vulnerability Tagging**: Parse outputs from on-device enumeration tools (e.g., `android-enum3.c`) and automatically map discovered micro-cracks or CVEs directly to the profile's research log.
- [ ] **Historical Timeline & State Diffing**: Track chronological changes in a target's state (e.g., new ports, updated OS patches, reboot events) to identify temporal weaknesses over multiple C2 sessions.
- [ ] **Cross-Profile Correlation Mapping**: Query the `profiles.db` to identify fleet-wide vulnerabilities (e.g., "Show all stored profiles vulnerable to CVE-2024-1086") for coordinated campaign planning.
- [ ] **Profile-Based Dynamic Execution**: Allow payloads to alter their execution strategy dynamically based on attributes stored in their respective target profile (e.g., selecting an exploit chain based on known kernel versions).
- [ ] **Profile Export/Sharing**: Implement secure serialization and export of individual or bulk profiles for sharing intelligence across operator teams or storing in centralized knowledge bases.
- [ ] **Automated Artifact Association**: Automatically link downloaded files (loot, backups, dumps) directly to the specific target profile that generated them for organized forensic review.
- [ ] **Custom Profile Tagging & Labeling**: Allow operators to manually or programmatically assign color-coded tags or risk scores (e.g., "High Value", "Pivot Node") to profiles for rapid visual sorting in the CLI.
- [ ] **Smart Re-Engagement Triggers**: Create alerts within profiles that notify the operator when a target comes back online or when new vulnerabilities match previously stored profile attributes.

## 5. 🕵️ OSINT Persona Enrichment (Phase 2)
*Objective: Seamlessly integrate external reconnaissance data into structured target personas.*
- [ ] **Automated OSINT Data Ingestion**: Pipe outputs from the Email, Phone, and Background Check recon modules directly into the target persona, automatically populating leaked credentials, aliases, and metadata.
- [ ] **Persona Social Graphing**: Link multiple profiles together based on shared OSINT data (e.g., overlapping domains, shared infrastructure, or known associations) to map out organizational hierarchies.
- [ ] **Breached Credential Correlation**: Integrate with services like Have I Been Pwned (HIBP) to automatically check discovered email addresses against known data breaches and flag compromised accounts.
- [ ] **Social Media Footprinting**: Develop modules to scrape and analyze public profiles (LinkedIn, Twitter, Facebook) associated with a persona's email or name, extracting connections, posts, and interests.
- [ ] **Visual Relationship Mapping**: Generate graphical charts that visually represent the connections between different personas, domains, and discovered assets for intuitive analysis.

## 6. ✨ Quality of Life (QOL) & UX
*Objective: Streamline operational workflows and improve operator efficiency.*
- [ ] **Interactive Payload Builder UI**: Develop a menu-driven, interactive builder within the CLI (using `prompt_toolkit`) that guides users through configuring advanced payloads without manually setting database variables.
- [ ] **Session Screen Multiplexing**: Implement a `tmux`-like interface within the interactive C2 console, allowing operators to manage and view output from multiple active sessions simultaneously.
- [ ] **Automated Cleanup Routines**: Add an `autoclean` toggle that automatically wipes compiled binaries, temporary scripts, and staging files from the target device upon session termination.
- [ ] **Context-Aware Help System**: Enhance the `help` command to automatically display documentation relevant to the currently loaded module or active workspace state without requiring specific arguments.
- [ ] **Customized Command Aliases**: Allow users to define their own persistent shortcut aliases for complex commands or frequently used module configurations.

---

## Random Thoughts 
- [ ] Expand the Auto-Enum engine to automatically query `profiles.db` upon session catch and cross-reference previous enumeration runs to avoid redundant data generation.