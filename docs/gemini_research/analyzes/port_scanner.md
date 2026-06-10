# SuperSploit Project Instructions

## Architecture: Asynchronous Port Scanner (Deep Analysis)

The Asynchronous Port Scanner is a high-speed, concurrent port scanner with active and passive service detection capabilities. This logic is primarily implemented in `recon/native-portscan/port_scanner.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Asynchronous I/O (`asyncio`)** | Utilizes Python's `asyncio` library to perform thousands of non-blocking socket operations concurrently, dramatically increasing scan speed over traditional threaded models. |
| **Concurrency Limiting (`asyncio.Semaphore`)** | Employs a semaphore to limit the number of concurrent open file descriptors, preventing the scanner from crashing the host OS by exceeding `ulimit` restrictions. |
| **Dual-Probe Service Detection** | First, it passively listens for a service banner (e.g., from SSH or FTP). If no banner is received, it actively sends an HTTP GET request to elicit a response from web servers and proxies. |
| **Heuristic and Signature Matching** | Matches received banners against a list of hardcoded regex signatures and a dynamically loaded database of Nmap service probes for accurate service identification. Falls back to a dictionary of common ports if active probing fails. |

### Automation Workflow
- **Dynamic Database Fallback**: If the scanner is run in an isolated `sudo` environment where it cannot import the core framework modules, it automatically falls back to reading the configuration directly from the `data.db` SQLite file.
- **Intelligent Merging**: When saving results, the scanner intelligently merges new findings with existing data in `targets.json`, ensuring that data from previous scans is not overwritten.
- **CIDR and Range Support**: Natively parses and scans full CIDR network ranges (e.g., `192.168.1.0/24`) and complex port ranges (e.g., `80,443,1000-2000`).