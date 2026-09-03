# SuperSploit Project Instructions

## Architecture: Error Handling & Logging System (Deep Analysis)

This system manages how the framework logs events, reports errors, and handles unexpected exceptions. This logic is primarily implemented in `source/core/errors.py` and `source/core/logger.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Error Handling (`errors.py`)** | Provides a centralized `Error` class that takes a traceback and writes it to the `.data/.errors/error.log` file, preventing crashes and providing a persistent record of failures. |
| **Execution Logging (`logger.py`)** | The `Logger` class provides a structured way to log module execution events. It records the module name, success status, and arguments to `.data/.logs/activity.log`. |
| **Standard Output (`ToStdOut.py`)** | A simple wrapper class that provides a consistent `write()` function for printing to the console, ensuring uniform output formatting. |

### Automation Workflow
- **Centralized Error Reporting**: Instead of printing stack traces to the console, modules and engines call the `Error` class to ensure all exceptions are handled gracefully and logged.
- **Persistent Activity Log**: The `Logger` provides an audit trail of all actions taken within the framework, which is critical for debugging and operational analysis.
