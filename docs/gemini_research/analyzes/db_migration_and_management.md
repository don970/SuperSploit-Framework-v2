# SuperSploit Project Instructions

## Architecture: Database Migration & Management (Deep Analysis)

This system manages the creation, migration, and maintenance of the specialized databases used for OS and service fingerprinting. This logic is distributed across several files in `source/core/`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **OS DB Manager (`os_db_manager.py`)** | Manages the `signatures.db` SQLite database, which stores OS fingerprints and their associated CVEs. |
| **Service DB Manager (`service_db_manager.py`)** | Manages the `services.db` SQLite database, which stores service banners and their associated CVEs. |
| **Nmap DB Migration (`migrate_nmap_db.py`)** | A utility script to parse the `nmap-os-db` file and import its vast collection of OS fingerprints into the `signatures.db`. |
| **Service Probe Migration (`migrate_services.py`)** | A utility script to parse the `nmap-service-probes` file and import its service banner signatures into the `services.db`. |

### Automation Workflow
- **Automated Database Creation**: The DB manager classes automatically create the SQLite databases if they don't exist.
- **One-Time Migration**: The migration scripts are designed to be run once to populate the databases from the Nmap data files, providing a rich dataset for the `auto_suggest` engine.
