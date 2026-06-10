import sys
import time
sys.path.append('/home/donald/.SuperSploit/source')

from core.database import DatabaseManagment
from core.listener import Listener

DatabaseManagment.install_dir = '/home/donald/.SuperSploit/'
db = DatabaseManagment.get()
db["LHOST"] = "0.0.0.0"
db["LPORT"] = "5000"
DatabaseManagment._update(db)

print("[*] Starting C2 Listener on port 5000...")
Listener.start(db)

# Keep script running to maintain the listener thread if needed, 
# though Listener.start spawns its own thread.
# We will use this to monitor sessions.
try:
    while True:
        if Listener.active_sessions:
            for sid in list(Listener.active_sessions.keys()):
                print(f"[+] Active Session Found: {sid}")
        time.sleep(5)
except KeyboardInterrupt:
    pass
