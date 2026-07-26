# Pro-Tier Tool Engine Workflow

This document outlines the workflow of loading, executing, and tearing down standalone Pro-Tier GUI tools (like the Web Stager or Evil Twin Deployer) via the `ToolEngine`.

## 1. Tool Initialization & Memory Loading

[User Input: "run"] (When a tool from `source/tools/` is active)
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py
                |
                +--> Routes execution to `ToolEngine.execute()`.
                      |
                      +--> **Source Ingestion**: Reads the target tool's `.py` file into a raw string buffer.
                      |
                      +--> **Metadata Stripping**: Utilizes regex to dynamically strip the bottom-anchored `# === TOOL_META ===` block to prevent Python compilation errors.
                      |
                      +--> **Code Compilation**: Compiles the raw string into a Python bytecode object (`compile(source, '<string>', 'exec')`).

## 2. Multiprocessing & Execution

To prevent GUI main loops (like `tkinter.mainloop()`) from blocking the SuperSploit CLI, the tool is detonated inside an isolated process.

    |
    +--> `ToolEngine` initializes a `multiprocessing.Process`.
          |
          +--> Passes the compiled bytecode object and a sterile `types.ModuleType` namespace to the child process.
          |
          +--> [Child Process]
                |
                +--> Executes the bytecode via `exec(compiled_code, namespace)`.
                |
                +--> The Tool's GUI initializes and handles its own logic, sockets, and interactions.
          |
          +--> [Parent Process (SuperSploit CLI)]
                |
                +--> Returns control to the operator instantly.
                |
                +--> Operator can continue searching, scanning, or managing C2 sessions while the Pro Tool runs independently.

## 3. Teardown & Artifact Cleanup

[User closes the Tool's GUI window]
    |
    +--> Child Process terminates.
    |
    +--> `ToolEngine` detects the `Process.join()` exit code.
    |
    +--> **Artifact Scrubbing**: Automatically removes any temporary execution aliases injected into `.data/.config/Aliases.json` that were used specifically by the tool.
    |
    +--> Drops any temporary framework variables (`LHOST`, `LPORT`) instantiated solely for the tool's run context to prevent workspace pollution.