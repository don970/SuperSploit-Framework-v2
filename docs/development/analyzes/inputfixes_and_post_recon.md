# SuperSploit Project Instructions

## Architecture: Input Fixes and Post-Recon Hooks (Deep Analysis)

This system handles modifications to input and manages actions taken after reconnaissance modules have finished execution. The logic is primarily located in `source/core/inputfixes.py` and `source/core/post_recon_hook.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Input Parsing (`inputfixes.py`)** | A utility module that provides functions to sanitize, normalize, and correct user input before it is processed by the main engines. This handles things like trailing slashes, whitespace, and case sensitivity. |
| **Post-Recon Hook (`post_recon_hook.py`)** | A callback mechanism that is automatically triggered by the `recon_engine.py` immediately after a reconnaissance module completes its execution. |

### Automation Workflow
- **Automated Suggestions**: The primary function of the Post-Recon Hook is to trigger the `auto_suggest` engine. This seamlessly links the data-gathering phase (Recon) with the exploitation phase (Auto Suggest) without requiring user intervention.
- **Data Normalization**: The `inputfixes.py` utilities ensure that commands like `set R_HOST 192.168.1.1/24 ` are cleaned up to `192.168.1.1/24`, preventing unexpected errors down the line.