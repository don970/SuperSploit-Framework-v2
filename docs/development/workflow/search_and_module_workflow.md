# Search and Module Management Workflow

This document describes how the SuperSploit framework handles searching for, loading, and inspecting modules.

## Searching for Modules

[User Input: "search smb"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "search" command)
                |
                +--> Delegates to the Search engine.
                      |
                      +--> source/core/search.py (Search.search)
                            |
                            +--> Identifies the base directories to search (`exploits/`, `recon/`, `payloads/`).
                            |
                            +--> Walks through all files with a `.py` or `.sh` extension.
                            |
                            +--> **Performance Branching**: 
                            |    +--> For Exploits/Recon: Reads the top of the file for the `#!#!#!` block.
                            |    +--> For Pro Tools: Uses `os.SEEK_END` to rapidly read the bottom-anchored `# === TOOL_META ===` block without loading massive GUI scripts into RAM.
                            |
                            +--> Parses fields like `name`, `desc`, `cve`, and `keywords` into the `ExploitCache` dictionary.
                            |
                            +--> Uses `shlex` to parse the user's query, supporting exact phrase matching (`"Dirty Pipe"`) and Key-Value filters (`os=linux`).
                            |
                            +--> Enforces implicit `AND` logic across multiple search terms.
                            |
                            +--> Formats and prints a tabulated list of matching modules.

## Selecting a Module

[User Input: "use exploits/Windows/Eternalblue.py"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "use" command)
                |
                +--> Delegates to the Use engine.
                      |
                      +--> source/core/use.py (Use.execute)
                            |
                            +--> Validates that the provided path exists.
                            |
                            +--> Updates the central database: `DatabaseManagment.get()["EXPLOIT"] = <path>`.
                            |
                            +--> Changes the interactive prompt string to reflect the active module (e.g., `[Eternalblue.py]> `).

## Inspecting a Module

[User Input: "show options"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "show" command)
                |
                +--> Identifies the target as "options".
                |
                +--> Delegates to the Show engine.
                      |
                      +--> source/core/show.py (Show.options)
                            |
                            +--> Retrieves the currently active module from the database (`EXPLOIT`).
                            |
                            +--> Opens the module file and parses its metadata block (`#!#!#!`).
                            |
                            +--> Extracts the `options` field (e.g., `options: "R_HOST, PAYLOAD"`).
                            |
                            +--> Reads the current values for those options from the central database.
                            |
                            +--> Formats and prints a tabulated list showing the required options and their current values.
