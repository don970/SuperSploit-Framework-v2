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

[User Input: "load payloads/Stage2/beacon.py"]
    |
    +--> source/core/exploit_engine.py (ExploitHandler._cmd_load)
          |
          +--> Calls `SessionLoader.load()` with the file path.
                |
                +--> source/core/session_loader.py (SessionLoader.load)
                      |
                      +--> Detects the file extension is `.py`.
                      |
                      +--> Calls `_load_python()` with the file path.
                            |
                            +--> Reads the content of `beacon.py`.
                            |
                            +--> Parses the Python code into an Abstract Syntax Tree (AST).
                            |
                            +--> Walks the AST to identify:
                            |    |
                            |    +--> Functions: `beacon_loop`, `add`
                            |    |
                            |    +--> Imports: `base64`, `os`, `subprocess`, etc.
                            |    |
                            |    +--> Entry Point: Identifies `add` as the main entry point.
                            |    |
                            |    +--> Auto-Execution: Detects the `if __name__ == "__main__"` block, confirming it's self-detonating.
                            |
                            +--> Determines it's a "Raw Fileless Stage 2 Script".
                            |
                            +--> Returns the full Python code content and the entry point function name ("add").
                |
                +--> The `(loader_payload, func_name)` tuple is returned to the Exploit Engine.
          |
          +--> The Exploit Engine sends a "load" command to the active C2 session.
          |
          +--> The remote agent responds with "READY".
          |
          +--> The Exploit Engine sends the full content of `beacon.py` over the encrypted socket.
                |
                +--> [Remote Agent]
                      |
                      +--> Receives the Python code.
                      |
                      +--> Executes the code using `exec()`.
                            |
                            +--> The `if __name__ == "__main__"` block is triggered.
                                  |
                                  +--> The `add()` function is called.
                                        |
                                        +--> A new background thread is created, targeting `beacon_loop()`.
                                              |
                                              +--> The `beacon_loop()` function begins its main C2 check-in and command execution cycle.
