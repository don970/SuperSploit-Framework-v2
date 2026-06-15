# SuperSploit Project Instructions

## Architecture: Suggestion Engine (Deep Analysis)

The Suggestion Engine utilizes a multi-factor scoring system to correlate target data with exploit metadata. This logic is primarily implemented in `source/core/auto_suggest.py`.

### Scoring Factors & Weights

| Factor | Weight (Score) | Description |
| :--- | :--- | :--- |
| **Direct CVE Match** | +50 | Exact match between target `cves` list and exploit `cve` metadata. |
| **Exact Kernel Match** | +30 | Target `kernel_version` matches one of the exploit's `kernel_versions`. |
| **Kernel Range Match** | +25 | Target `kernel_version` falls between `min_ver` and `max_ver`. |
| **Banner Version Match** | +20 | Regex-extracted version from service banner matches exploit keywords/description. |
| **Requirement Match** | +15 (ea) | Target `environment` satisfies an exploit's `requirements` (e.g., `/dev/binder`). |
| **Banner Signature** | +12 | Generic keyword match within a raw service banner. |
| **OS Verified** | +10 | Target OS family matches the exploit's `os` metadata. |
| **Fuzzy Service Match** | +10 | `difflib` match between scanned service name and exploit keywords. |
| **Port Match** | +5 | Scanned port matches an exploit keyword. |

### Mandatory Filters (Pre-Qualification)
- **OS Mismatch**: If an exploit defines an `os` (e.g., `android`) and the target `os_family` differs (e.g., `linux`), the exploit is excluded.
- **Architecture Mismatch**: If an exploit defines an `arch` (e.g., `aarch64`) and the target `architecture` differs, the exploit is excluded.

### Automation Workflow
- **Post-Recon Hook**: Automatically triggered after any recon module execution if `auto_suggest` is enabled.
- **State Management**: Uses the target data stored in the framework's JSON/SQLite database (synchronized from `targets.json`).
