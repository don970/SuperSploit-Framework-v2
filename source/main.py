from core import Input
import uuid
import os
import subprocess
from core.database import DatabaseManagment
from core.set import SetV
import sys
from core.listener import Listener
from core.logger import Logger

install_location = DatabaseManagment.getInstall()


def initialize_session():
    # check sys path and add install if not present
    if f"{install_location}/source" not in sys.path:
        sys.path.append(f"{install_location}/source")

    db = DatabaseManagment.get()
    # Generate an 8-character unique session ID
    session_id = uuid.uuid4().hex[:8]
    SetV.SetV(f"set SESSION_ID {session_id}")
    
    # Flush the updated session ID to disk so data.json formats as a multi-line JSON
    DatabaseManagment._update()

    # Trigger the initial staged log entry for the session
    Logger.start_session()


def check_auto_start():
    db = DatabaseManagment.get()
    auto_start_listener = True if str(db.get("LISTENER", "false")).lower().startswith("t") else False

    if auto_start_listener:
        print("[*] Auto-starting listener as requested by LISTENER variable...")
        # Check if we are already in the new terminal to avoid infinite loops
        if os.environ.get("SUPERSPLOIT_LISTENER_MODE") == "1":
            print("[*] Listener terminal detected. Binding port...")
            Listener.start(db, deploy_stage2=True)
            # Keep the listener thread alive in the new terminal
            import time
            while True:
                time.sleep(1)
        else:
            print("[*] Spawning new terminal for listener...")
            term = DatabaseManagment.findTerm()
            if not term:
                Logger.log_soft_error(f"[*] Failed to find the .terminals file")
                return

            profile = db.get("PROFILE", "")
            profile_cmd = f"set PROFILE {profile}; " if profile else ""
            
            # The python code to execute in the new terminal
            python_cmd = (
                f"import sys, os; "
                f"sys.path.append('{os.path.join(install_location, 'source')}'); "
                f"from core.database import DatabaseManagment; "
                f"from core.listener import Listener; "
                f"db = DatabaseManagment.get(); "
                f"Listener.start(db, deploy_stage2=True); "
                f"import time; "
                f"time.sleep(999999)" # Keep terminal open
            )

            # Command to launch the new terminal
            # This is highly dependent on the terminal emulator. We'll try common ones.
            env_vars = os.environ.copy()
            env_vars["SUPERSPLOIT_LISTENER_MODE"] = "1"

            if term in ["gnome-terminal", "mate-terminal", "xfce4-terminal", "lxterminal"]:
                subprocess.Popen([term, "--", "python3", "-c", python_cmd], env=env_vars)
            elif term == "konsole":
                subprocess.Popen([term, "-e", "python3", "-c", python_cmd], env=env_vars)
            elif term in ["xterm", "uxterm", "rxvt", "urxvt", "st"]:
                subprocess.Popen([term, "-e", "python3", "-c", python_cmd], env=env_vars)
            else:
                print(f"[-] Unsupported terminal for auto-launch: {term}")


class Main:
    def __init__(self):
        initialize_session()
        # Start the background target synchronization thread
        DatabaseManagment.start_background_sync()

        #check_auto_start()
        
        # Don't start the main input loop if we are just the listener instance
        if os.environ.get("SUPERSPLOIT_LISTENER_MODE") != "1":
            try:
                """calls the main input handler"""
                Input.get()
            except KeyboardInterrupt:
                DatabaseManagment.sync_targets_to_disk()
                if input("[*] Are you sure you want to shutdown: ").startswith("y"):
                    print(f"\n[*] Gracefully shutting down...")
                    exit(0)
            except Exception as e:
                print(f"\n[!] Fatal Framework Crash: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Flush any pending target updates to the disk
                DatabaseManagment.sync_targets_to_disk()
                print(f"Good bye. );")
                exit(0)


if __name__ == "__main__":
    Main()
