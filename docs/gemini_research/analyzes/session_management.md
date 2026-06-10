# SuperSploit Project Instructions

## Architecture: Session Management (Deep Analysis)

The Session Management system provides the user interface for listing and interacting with active C2 sessions. This logic is primarily implemented in `source/core/sessions.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Session Listing** | The `sessions` command, when run without arguments, retrieves the `active_sessions` dictionary from the `Listener` class and displays a tabulated list of all active connections (ID, Target IP, Port). |
| **Session Interaction** | When run with the `-i` flag (e.g., `sessions -i 1`), it delegates to the `Listener.interact()` method, passing the specified session ID to drop into an interactive C2 shell. |
| **Session Termination** | When run with the `-k` flag (e.g., `sessions -k 1`), it retrieves the specified session from the `active_sessions` dictionary, sends an "exit" command to the remote agent, and closes the socket. |

### Automation Workflow
- **Dynamic Session State**: The `sessions` command directly reflects the real-time state of the `Listener`'s session dictionary, providing an always-up-to-date view of active connections.
- **Centralized Interaction Logic**: Instead of duplicating code, the session management system acts as a front-end that delegates all interaction and termination logic to the `Listener` class, ensuring a single source of truth for session state.