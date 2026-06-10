# SuperSploit Project Instructions

## Architecture: Session Loader & Payload Detonation (Deep Analysis)

This document outlines the workflow of loading a Python-based payload (like `beacon.py`) through the `SessionLoader` and executing it on a remote target. The logic is primarily located in `source/core/session_loader.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Index Resolution** | Translates numeric input from search results (e.g., `load 1`) into absolute file paths by intercepting the `Search` engine's standard output. |
| **AST Parsing (`ast`)** | Parses Python payload files statically to extract function definitions, imports, and detect self-detonating entry points (e.g., `if __name__ == '__main__':`) without executing the code locally. |
| **Dynamic Execution (`importlib`)** | If the payload is a classic exploit module, it is dynamically imported into the attacker's memory to extract the raw string payload it returns. |
| **Remote Detonation** | Sends the raw Python payload as text to the remote agent, where it is compiled and evaluated in memory using `exec()`. |

### Automation Workflow

1.  **User Command**: The user initiates the process by typing `load payloads/Stage2/beacon.py`.
2.  **Initial Handling**: The command is parsed by the `InputHandlingEngine` and delegated to the `ExploitEngine`.
3.  **Session Loader Invocation**: The `ExploitEngine` calls `SessionLoader.load()` with the provided file path.
4.  **Payload Analysis**:
    *   The `SessionLoader` detects that it's a Python file.
    *   It reads `beacon.py` and uses Abstract Syntax Trees (AST) to analyze its structure without executing it. It identifies key components like functions (`beacon_loop`, `add`), imports, and the entry point (`add`).
    *   It determines the payload is a "Raw Fileless Stage 2 Script" and returns the full source code.
5.  **Remote Injection**:
    *   The `ExploitEngine` sends a `load` command to the active C2 session.
    *   After receiving a `READY` confirmation from the agent, it streams the entire `beacon.py` source code over the encrypted socket.
6.  **Detonation on Target**:
    *   The remote agent receives the source code.
    *   It uses `exec()` to compile and run the code in memory.
    *   The `if __name__ == '__main__':` block in `beacon.py` is triggered, calling the `add()` function.
    *   The `add()` function spawns a new background thread, starting the main `beacon_loop()` C2 communication cycle.