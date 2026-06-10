# SuperSploit Module Development Guide 🛠️

Native modules in SuperSploit are designed to be lightweight, fileless, and easily integrated. This guide covers the structure required for the framework's `recon_engine` and `exploit_handler`.

## 1. Metadata Block
Every module must begin with a YAML-formatted metadata block delimited by `#!#!#!`. This is parsed by the framework for search and info commands.

```python
#!#!#!
name: "My Custom Module"
description: "Detailed description of what this does."
category: "Exploit" # OSINT, Recon, Exploit, Payload
author: "Your Name"
keywords: '["tag1", "tag2"]'
#!#!#!
```

## 2. Core Structure
The framework looks for a `Start(args=None)` function as the primary entry point.

### Framework Imports
To interact with the core database and session manager, use the following pattern:

```python
import os, sys

# Resolve framework root
_source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "source"))
if _source_dir not in sys.path: sys.path.append(_source_dir)

try:
    from core.database import DatabaseManagment
except ImportError:
    DatabaseManagment = None
```

## 3. Handling Targets
The framework passes variables through the `args` parameter or stores them in `DatabaseManagment`.

```python
def Start(args=None):
    # 1. Check Arguments (Priority)
    target = args[0] if args else None
    
    # 2. Check Database (Fallback)
    if not target and DatabaseManagment:
        target = DatabaseManagment.get().get("R_HOST", "")
        
    # 3. Robust Handling (New in v1.2.18)
    if isinstance(target, list):
        target = target[0] # Handle list targets gracefully
```

## 4. Reporting & Persistance
Use the `PersonProfile` class (if in OSINT) to save data to the persistent store:

```python
if DatabaseManagment:
    profile_data = {"name": "John Doe", "email": "jd@example.com"}
    DatabaseManagment.addProfile(profile_data)
```

## 5. Tips
- **Silent Execution**: Use `subprocess.run(..., capture_output=True)` to prevent leaking noise to the TTY.
- **Clean Up**: If your module creates temp files, use a `try...finally` block to ensure they are deleted.

## 6. HTTP Beacon Architecture
When developing asynchronous HTTP beacon payloads (e.g., `beacon.py`):

- **Task Retrieval**: Perform HTTP GET requests to the C2 server at the `/file` endpoint to fetch tasks.
- **Data Exfiltration**: Perform HTTP POST requests to the `/rfile` endpoint to return command output or exfiltrated files.
- **Listener Compatibility**: Ensure you are using a dedicated SuperSploit HTTP C2 handler. The standard `python3 -m http.server` module does not support POST requests natively and will drop exfiltration attempts with a `501 Unsupported Method` error.