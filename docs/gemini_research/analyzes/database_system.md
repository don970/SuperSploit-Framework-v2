# SuperSploit Project Instructions

## Architecture: Database System (Deep Analysis)

The Database System manages the persistence, retrieval, and synchronization of the framework's configuration, target data, and user profiles. This logic is primarily implemented in `source/core/database.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **SQLite Dict Wrapper** | Implements the `MutableMapping` interface (`SQLiteDict`) to act like a standard Python dictionary, but automatically persists key-value pairs to an underlying SQLite database (`data.db`, `profiles.db`). |
| **In-Memory Caching** | The `ExploitCache` class statically loads and indexes YAML metadata (`#!#!#!` blocks) for all exploits and payloads upon startup, significantly speeding up the `search` engine. |
| **Target Synchronization** | Target state (IPs, open ports, MACs) is tracked in an in-memory dictionary (`_targets_cache`). The framework utilizes an asynchronous background thread (`start_background_sync()`) to dump this cache to `targets.json` every 60 seconds, or on demand. |
| **Cross-Process Syncing** | Handles mtime (modified time) checks before retrieving target data to ensure the main application loop always has the most recent recon data, even if it was written by an isolated `sudo` subprocess. |

### Automation Workflow
- **Auto-Migration**: Automatically detects legacy `data.json` files on startup and migrates them to the new `.db` format.
- **Dynamic Aliasing**: Pulls from `Aliases.json` dynamically to augment the interactive CLI loop.
- **Context Handling**: Automatically maps human-readable keys (e.g., `target`) to internal framework identifiers (e.g., `R_HOST`) when directly modifying the database via CLI `set` commands.