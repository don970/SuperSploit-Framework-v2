# SuperSploit Project Instructions

## Architecture: Recon Engine (Deep Analysis)

The Recon Engine manages the execution of reconnaissance modules, privilege escalation, and data synchronization. This logic is primarily implemented in `source/core/recon_engine.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Privilege Escalation** | Parses module metadata for the `root: "true"` flag and automatically re-launches the script via `sudo` in an isolated subprocess. |
| **Data Synchronization** | Interacts with `database.py` to read configuration settings (e.g., `R_HOST`) and write structured results (e.g., open ports, banners) back to the `targets.json` database. |

### Automation Workflow
- **Post-Recon Hook**: Automatically triggers the `auto_suggest` engine after a module completes, correlating newly discovered target data with available exploits.
- **Isolated Execution**: Runs modules in separate processes to prevent unstable scripts from crashing the main SuperSploit framework.
