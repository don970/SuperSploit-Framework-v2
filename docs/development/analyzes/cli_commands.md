# SuperSploit Project Instructions

## Architecture: CLI Command System (Deep Analysis)

The CLI Command System handles the primary user-facing commands that are not part of a larger engine. This logic is distributed across several files in `source/core/`.

### Core Commands & Mechanisms

| Command | File | Description |
| :--- | :--- | :--- |
| **set** | `set.py` | Modifies the in-memory database by mapping user-friendly variable names (e.g., `target`) to internal database keys (e.g., `R_HOST`). |
| **use** | `use.py` | Sets the active exploit or recon module in the database and updates the interactive prompt to reflect the current context. |
| **show** | `show.py` | Reads and displays metadata from the currently loaded module, such as required options, author, and description. |
| **help** | `help.py` | Displays help information for commands and modules by reading `.help` files from the `.data` directory. |
| **search** | `search.py` | Queries the `ExploitCache` to find modules matching a keyword, searching against names, descriptions, and CVEs. |
| **clean** | `clean.py` | Wipes temporary files, logs, and cached data from the `.data` directory to ensure a clean state. |
| **banners** | `banners.py` | Manages the display of ASCII art banners and informational headers. |
