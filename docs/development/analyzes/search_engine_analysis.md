# SuperSploit Project Instructions

## Architecture: Search Engine (Deep Analysis)

The Search Engine provides an advanced, fast, and heavily filtered query interface for locating modules within the SuperSploit Framework. This logic is primarily implemented in `source/core/search.py` and relies heavily on the in-memory cache built by `source/core/database.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **In-Memory Caching (`ExploitCache`)** | Upon startup, the framework parses the YAML metadata (`#!#!#!` blocks) of all exploits, payloads, and recon scripts, indexing them in RAM. This prevents the search engine from performing slow disk I/O on every query. |
| **Advanced Parsing (`shlex`)** | Utilizes `shlex.split()` to intelligently parse search strings, supporting quoted phrases for exact matches (e.g., `"Dirty Pipe"`). |
| **Key-Value Filtering** | Allows operators to filter by specific metadata fields using an `=` syntax (e.g., `os=linux`, `cve=2024`, `author=donald`). |
| **Implicit AND Logic** | When multiple keywords are provided, the engine enforces an `AND` logic requirement, meaning a module must match *all* provided terms across its indexed fields (Name, Description, CVEs, etc.) to be returned. |

### Automation & Indexing Workflow
- **Startup Indexing**: The framework crawls the relevant module directories at launch.
- **Metadata Extraction**: It looks for the framework-standard YAML headers and extracts fields like `description`, `cve`, `os`, and `requirements`.
- **Query Execution**: When `search <term>` is executed, it iterates over the cache and applies the filtering logic before formatting the results into a tabulated console output.

---

## Upcoming Expansion: Built-in Tool Integration
*Objective: Expand the search engine's scope to include framework utilities and Pro-Tier tools located in `source/tools/`.*

Currently, the search engine strictly indexes exploits, payloads, and recon modules. To significantly improve the operator workflow, the search feature will be updated to index standalone utilities and GUI tools (e.g., DNS Patcher, Web Stager, APK Generator).

### Implementation Strategy
1. **Bottom-Anchored Metadata Standardization**: 
   - Unlike exploits, Pro-Tier tools will store their YAML metadata block at the **bottom** of the file (e.g., delineated by `# === TOOL_META ===`).
   - This keeps the top of complex GUI scripts clean for Python imports and core logic.
   - Ensure all tools are tagged with highly relevant operator keywords (e.g., tagging the Web Stager with `phishing`, `mitm`, `aitm`, `credentials`, `web`).

2. **Cache Expansion**: 
   - Update the caching engine in `database.py` to index the `tools` directory during the startup sequence.
   - **Performance Win:** Implement `os.SEEK_END` to read the files backwards. This prevents the framework from loading massive GUI scripts into memory during startup just to parse the metadata.

3. **Query Routing & UI**: 
   - Update `search.py` to include a dedicated `Tools` category in its output tables. 
   - When an operator types `search phishing`, the engine should return the `web_stager_gui.py` tool alongside any relevant exploits.

4. **In-Memory Execution Pipeline (`ToolEngine`)**:
   - Add support for loading tools via the `use` command (e.g., `use tools/web_stager`).
   - When `run` is executed, the newly planned `ToolEngine` will load the script as a raw string, strip out the bottom metadata block, compile it, and execute it entirely in RAM via `exec(compiled_code, module_namespace)`.
   - To prevent GUI tools (like `tkinter`) from blocking the main CLI loop, the `ToolEngine` will spawn the execution within an isolated `multiprocessing.Process`.

5. **Suggestion Engine Integration**:
   - Update `auto_suggest.py` to cross-reference the new Tools cache.
   - Example: If the Asynchronous Port Scanner detects `UDP/53`, the engine will intelligently suggest `use tools/web/dns_patcher`.

6. **Clean Up & Artifact Management (Post-Execution)**:
   - **Process Reaping**: Ensure the `ToolEngine` safely joins and terminates the isolated `multiprocessing` children when a GUI tool is closed, preventing zombie processes.
   - **Alias Scrubbing**: Any dynamic command aliases temporarily injected into `.data/.config/Aliases.json` to support the tool's execution must be purged upon exit.
   - **Memory/Variable Reset**: Scrub any temporary framework variables (e.g., `LHOST`, `LPORT`) instantiated solely for the tool to prevent cross-session workspace pollution.