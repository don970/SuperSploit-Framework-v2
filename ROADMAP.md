# SuperSploit Framework Development Roadmap

This document outlines the strategic engineering priorities for evolving SuperSploit into a production-grade security tool. The focus is on building a resilient, scalable, and stable core infrastructure before expanding feature density.

---

### **Architectural Prioritization Matrix**

| Backlog Phase | Current Priority | Recommended Priority | Engineering Justification |
| --- | --- | --- | --- |
| **5. Command & Control (C2 Server)** | Low / Unmarked | **Critical / Immediate** | A robust, concurrent network I/O loop is the essential foundation for all downstream network data and prevents protocol limitations. |
| **6. Quality of Life (UX & Profiles)** | Low | **High** | Features like Workspace Management and Job Control directly impact memory safety and prevent cross-session pollution during automation. |
| **7. Pro-Tier Delivery & Web** | Active | **High** | Extending the framework with AitM capabilities, rogue DNS, and out-of-band delivery (SMS/SMTP) adds critical attack vectors. |
| **4. OSINT & Reconnaissance** | Low | **Medium** | Implementing structured document scrapers and API integrations expands coverage safely within user-space before touching unstable low-level environments. |
| **2 & 3. Advanced Payloads & Persistence** | High | **Deferred Phase** | Introducing complex platform-specific modules before standardizing the core APIs and error recovery frameworks risks creating a fragile environment. |

---

## 1. 🕹️ Command & Control (C2) Infrastructure (Critical Priority)
*Objective: Eliminate protocol bottlenecks and build a resilient, asynchronous network engine.*
- [X] **Asynchronous HTTP/HTTPS Server**: Replace the standard Python web server with a dedicated, non-blocking asynchronous engine (e.g., using `asyncio`) to handle high-concurrency C2 check-ins from beacon payloads.
- [X] **State Management**: Implement thread-safe asynchronous queues (`asyncio.Queue`) to manage data flow between concurrent C2 connections and the main framework, preventing state corruption.

## 2. ✨ Quality of Life & Infrastructure (High Priority)
*Objective: Ensure memory safety, state isolation, and a predictable user experience.*
- [X] **Workspace Management**:
    - [X] Refactor the database engine to instantiate fully isolated SQLite database files per workspace directory.
    - [X] Add commands to create, switch, and delete workspaces.
- [X] **Job Control & Process Management**:
    - [X] Implement a centralized job registry to track background tasks (listeners, scans, etc.).
    - [X] Create a `jobs` command to view, manage, and terminate background processes gracefully.
- [X] **Modernize the Console Interface**:
    - [X] Implement dynamic tab completion for commands, file paths, and module names.
    - [X] Add `Ctrl+R` for reverse-searching command history.
    - [X] Use a library like `rich` to create interactive, sortable tables for `search` and `sessions`.

## 3. 🔎 OSINT & Reconnaissance (Medium Priority)
*Objective: Expand footprint analysis capabilities with stable, user-space tools.*
- [X] **Public Repo Scanner**: Search GitHub/GitLab for leaked API keys and internal docs.
- [X] **Shodan/Censys Integration**: Leverage search engine APIs for banner grabbing and vulnerability correlation.
- [X] **Domain/Subdomain Enumeration**: Identify subdomains, associated IPs, and DNS records.
- [X] **Metadata Scraper**: Extract metadata from publicly available documents (PDFs, DOCX, XLSX).

## 4. 🚀 Exploitation & Payloads (Deferred Phase)
*Objective: Broaden the attack surface after the core infrastructure is stable.*
- [ ] **CVE Integration**:
    - [X] **PwnKit / Polkit pkexec (CVE-2021-4034)** - *Integrate into interactive sessions for auto-escalation.*
    - [ ] F5 BIG-IP TMUI RCE (CVE-2020-5902).
- [ ] **Advanced Payloads**:
    - [ ] **Process Hollowing/Injection**: Injecting into trusted processes (Win/Linux).
    - [ ] **Windows Reflective DLL Injection**: Fileless DLL loading.
    - [X] **Platform Support**: Add native payload generation support for iOS (dyld Cache / Hybrid Weaponization).
    - [X] **Platform Support**: Native APK Generation (Android C-based DRS, Beacon, Rootkit).

## 5. ⚓ Persistence Mechanisms (Deferred Phase)
*Objective: Establish long-term access after the core C2 and payload systems are mature.*
- [ ] **WMI Event Subscription (Windows)**: Fileless event-based execution.
- [ ] **LD_PRELOAD Hijacking (Linux)**: Hooking functions via shared libraries.
- [ ] **DLL Sideloading**: Exploiting DLL search order in legitimate apps.

## 6. 🎣 Pro-Tier Tooling & Delivery Systems (Active)
*Objective: Expand the framework's social engineering and network manipulation capabilities.*
- [X] **AitM Proxy & Web Stager**: Interactive GUI for real-time session hijacking, credential harvesting, and JS injection.
- [X] **Active DNS Patcher**: UDP Port 53 interception with dynamic interface routing and IPv4 spoofing for local MITM.
- [X] **SMTP Spoofing Suite**: Integrated email spoofing and templating for payload delivery.
- [X] **SMS Sender**: Pro-tier module for direct-to-device mobile weaponization.

## 7. ⚙️ ToolEngine Pipeline (Active Priority)
*Objective: Establish an in-memory execution pipeline to seamlessly integrate standalone Pro-Tier tools into the main SuperSploit CLI, Search, and Suggestion ecosystems.*
- [ ] Architect the `ToolEngine` bridge to ingest standalone GUI and CLI modules natively.
- [ ] Map all Pro OSINT, Scanners, and SE tools to the central Search Engine.
- [ ] Unify Sentry Dark Theme styling across all dynamically loaded Tkinter interfaces.
