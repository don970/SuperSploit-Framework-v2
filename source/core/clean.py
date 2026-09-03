import os
from .ToStdOut import ToStdout
from .database import DatabaseManagment

print = ToStdout.write

def clean(args=None):
    """Refactored from a class to a function since it just executes a single routine"""
    print("[*] Doing a full clean. Clearing history, logs, targets, and all cached databases.\n")
    
    # Dynamically resolve path to ensure we clean the active environment
    installation = DatabaseManagment.getInstall()

    # Reset in-memory state first to release file handles and clear 'show' output
    try:
        DatabaseManagment.core_db = None
        DatabaseManagment._db_loaded = False
        DatabaseManagment._targets_cache = None
        DatabaseManagment._targets_last_mtime = 0
    except Exception:
        pass

    # Define relative paths from the installation directory for targeted cleaning
    paths = [
        ".data/.history/history", 
        ".data/.logs/activity.log",
        ".data/.logs/recon_activity.log",
        ".data/.errors/error.log",
        ".data/.config/data.db",
        ".data/.config/data.db.bak",
        ".data/.config/data.json",
        ".data/.config/targets.json",
        ".data/.config/nmap-compiled.pkl",
        ".data/.cache/exploit_cache.db",
        ".data/.cache/exploit_details.cache",
        ".data/.included/included.db"
    ]
    
    for rel_path in paths:
        full_path = os.path.join(installation, rel_path)
        if os.path.exists(full_path):
            try:
                # For databases, serialized objects, and binary caches, removal ensures a fresh state
                if full_path.endswith(('.db', '.cache', '.json', '.pkl', '.bak')):
                    os.remove(full_path)
                else:
                    # Truncate text-based logs and history
                    with open(full_path, "w") as file:
                        pass 
            except Exception as e:
                print(f"[-] Failed to clean {rel_path}: {e}\n")

    # Re-initialize a fresh session ID for the new clean state
    try:
        import uuid
        from .set import SetV
        session_id = uuid.uuid4().hex[:8]
        SetV.SetV(f"set SESSION_ID {session_id}")
    except Exception:
        pass

    print("[*] Clean complete.\n")