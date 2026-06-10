# SuperSploit Search Engine Enhancements (May 2026)

The search functionality was expanded to support deep metadata indexing, multi-argument filtering, and robust argument parsing.

## Key Changes
- **Metadata Indexing**: `ExploitCache.update` now includes recon modules. `_quick_parse` was hardened to handle malformed YAML and skip directories.
- **Expanded Search Pool**: `Search.search` now matches against `name`, `cve`, `cwe`, `desc`, `cat`, `target`, `os`, `arch`, `kernel`, `min_ver`, `max_ver`, `requirements`, and `keywords`.
- **Target Search**: Added keyword filtering to `search targets`, allowing searches by hostname, OS, and services.
- **Robust Parsing**: Updated `Search.search` to use `shlex` for parsing, enabling support for quoted strings (exact phrase matching).
- **AND Logic**: Multiple keywords now use "AND" logic (all terms must match) instead of "OR" logic.
- **Key-Value Filters**: Added support for specific metadata filtering using `key=value` syntax (e.g., `os=linux cve=2024`).

## Implementation Details
- Files modified: `source/core/database.py`, `source/core/search.py`.
- `Search.search` tokenizes input via `shlex.split`, separates filters from keywords, and enforces matches across both sets.
- Target search extracts IP and hostname into a flat dictionary for filter compatibility.
