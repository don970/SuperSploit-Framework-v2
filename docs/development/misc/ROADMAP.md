# SuperSploit Framework Development Roadmap

This document outlines the strategic engineering priorities for evolving SuperSploit into a production-grade security tool. The focus is on building a resilient, scalable, and stable core infrastructure before expanding feature density.

---

### **Architectural Prioritization Matrix**

| Backlog Phase | Current Priority | Recommended Priority | Engineering Justification |
| --- | --- | --- | --- |
| **5. Command & Control (C2 Server)** | Low / Unmarked | **Critical / Immediate** | A robust, concurrent network I/O loop is the essential foundation for all downstream network data and prevents protocol limitations. |
| **6. Quality of Life (UX & Profiles)** | Low | **High** | Features like Workspace Management and Job Control directly impact memory safety and prevent cross-session pollution during automation. |
| **4. OSINT & Reconnaissance** | Low | **Medium** | Implementing structured document scrapers and API integrations expands coverage safely within user-space before touching unstable low-level environments. |
| **2 & 3. Advanced Payloads & Persistence** | High | **Deferred Phase** | Introducing complex platform-specific modules before standardizing the core APIs and error recovery frameworks risks creating a fragile environment. |

---

## 1. 🕹️ Command & Control (C2) Infrastructure (Critical Priority)
*Objective: Eliminate protocol bottlenecks and build a resilient, asynchronous network engine.*
- [ ] **Asynchronous HTTP/HTTPS Server**: Replace the standard Python web server with a dedicated, non-blocking asynchronous engine (e.g., using `asyncio`) to handle high-concurrency C2 check-ins from beacon payloads.
- [ ] **State Management**: Implement thread-safe asynchronous queues (`asyncio.Queue`) to manage data flow between concurrent C2 connections and the main framework, preventing state corruption.

## 2. ✨ Quality of Life & Infrastructure (High Priority)
*Objective: Ensure memory safety, state isolation, and a predictable user experience.*
- [ ] **Workspace Management**:
    - [ ] Refactor the database engine to instantiate fully isolated SQLite database files per workspace directory.
    - [ ] Add commands to create, switch, and delete workspaces.
- [ ] **Job Control & Process Management**:
    - [ ] Implement a centralized job registry to track background tasks (listeners, scans, etc.).
    - [ ] Create a `jobs` command to view, manage, and terminate background processes gracefully.
- [ ] **Modernize the Console Interface**:
    - [ ] Implement dynamic tab completion for commands, file paths, and module names.
    - [ ] Add `Ctrl+R` for reverse-searching command history.
    - [ ] Use a library like `rich` to create interactive, sortable tables for `search` and `sessions`.

## 3. 🔎 OSINT & Reconnaissance (Medium Priority)
*Objective: Expand footprint analysis capabilities with stable, user-space tools.*
- [ ] **Public Repo Scanner**: Search GitHub/GitLab for leaked API keys and internal docs.
- [ ] **Shodan/Censys Integration**: Leverage search engine APIs for banner grabbing and vulnerability correlation.
- [ ] **Domain/Subdomain Enumeration**: Identify subdomains, associated IPs, and DNS records.
- [ ] **Metadata Scraper**: Extract metadata from publicly available documents (PDFs, DOCX, XLSX).

## 4. 🚀 Exploitation & Payloads (Deferred Phase)
*Objective: Broaden the attack surface after the core infrastructure is stable.*
- [ ] **CVE Integration**:
    - [ ] **PwnKit / Polkit pkexec (CVE-2021-4034)** - *Integrate into interactive sessions for auto-escalation.*
    - [ ] F5 BIG-IP TMUI RCE (CVE-2020-5902).
- [ ] **Advanced Payloads**:
    - [ ] **Process Hollowing/Injection**: Injecting into trusted processes (Win/Linux).
    - [ ] **Windows Reflective DLL Injection**: Fileless DLL loading.
- [ ] **Platform Support**: Add native payload generation support for iOS.

## 5. ⚓ Persistence Mechanisms (Deferred Phase)
*Objective: Establish long-term access after the core C2 and payload systems are mature.*
- [ ] **WMI Event Subscription (Windows)**: Fileless event-based execution.
- [ ] **LD_PRELOAD Hijacking (Linux)**: Hooking functions via shared libraries.
- [ ] **DLL Sideloading**: Exploiting DLL search order in legitimate apps.

## Random Thoughts 
- [X] **let's improve the target profile system in place already.**: i want to have the target profile be able to import from targets database creating a target profile we can attach research to this would be good for local lpe research like iv been doing but also just a good feature and if a active session is caught lets have the agent use the enumeration tools via the upload command. using the enumeration tools in the source/tools folder to create a comprehensive report of the device then adding key points to the profile for persistent testing and research logging


