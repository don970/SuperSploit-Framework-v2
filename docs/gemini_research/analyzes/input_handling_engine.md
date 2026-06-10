# SuperSploit Project Instructions

## Architecture: Input Handling Engine (Deep Analysis)

The Input Handling Engine manages the parsing, routing, and execution of user commands within the framework. This logic is primarily implemented in `source/core/input_handling_engine.py` and the main REPL loop.

### Command Routing & Resolution

| Mechanism | Description |
| :--- | :--- |
| **Direct Command Matching** | Checks the base command against a dictionary of natively supported commands (`help`, `show`, `set`, `use`, `run`, `search`). |
| **Alias Resolution** | If a command is not natively recognized, the engine queries the secondary dictionary (`.data/.config/Aliases.json`) to resolve custom user aliases. |
| **Module Delegation** | Routes execution contexts dynamically based on the active module (e.g., passing `run` to the Exploit Engine or Recon Engine). |

### Automation Workflow
- **State Management**: Updates interactive prompt strings to reflect the currently loaded module.
- **Error Handling**: Provides standardized error messages for unknown commands or invalid syntax before they hit the underlying execution engines.