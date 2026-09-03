import os
import datetime
import pathlib
import uuid
from .database import DatabaseManagment


install_location = f'{os.getenv("HOME")}/.SuperSploit'
log_dir = f"{install_location}/.data/.logs"
log_path = f"{log_dir}/activity.log"
recon_path = f"{log_dir}/recon_activity.log"
softerror_log_path = f"{log_dir}/softerror.log"


# Set max file size to 5MB to keep the system footprint small
MAX_LOG_SIZE = 5 * 1024 * 1024



class Logger:
    @classmethod
    def initializeReconMoodle(cls, moduleName, path, error):
        db = {
            "SessionID": str(uuid.uuid4()),
            "moduleName": str(moduleName),
            "modulePath": pathlib.Path(path)}

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [SessionID: {db['SessionID']}] Name: {db['moduleName']} | Path: {db['modulePath']} | {error}"
        cls._write_recon_log(entry)
        return db

    @staticmethod
    def _rotate_logs():
        """Checks log size and archives it if it exceeds the maximum allowed size."""
        try:
            if os.path.exists(log_path) and os.path.getsize(log_path) > MAX_LOG_SIZE:
                # Append a timestamp to the archived log
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_path = f"{log_dir}/activity_archive_{timestamp}.log"
                
                # Rename rotates the file instantly without keeping file handlers locked
                os.rename(log_path, archive_path)
        except Exception:
            # Fail silently on rotation errors so the framework execution isn't interrupted
            pass

    @staticmethod
    def _write_log(entry):
        """Internal method to handle file I/O safely."""
        try:
            os.makedirs(log_dir, exist_ok=True)
            
            # Check if rotation is needed before writing
            Logger._rotate_logs()
            
            with open(log_path, "a") as f:
                f.write(entry + "\n")
        except Exception as e:
            from .errors import Error
            Error.silent(f"Logging Failed: {e}")
        
    @staticmethod
    def start_session():
        """Marks the beginning of a new framework session."""
        db = DatabaseManagment.get()
        session_id = db.get("SESSION_ID", "UNKNOWN")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        divider = "-" * 50
        entry = f"{divider}\n[{timestamp}] [SESSION: {session_id}] --- SUPERSPLOIT FRAMEWORK LAUNCHED ---"
        Logger._write_log(entry)

    @staticmethod
    def _write_recon_log(entry):
        """Internal method to handle file I/O safely."""
        try:
            os.makedirs(log_dir, exist_ok=True)

            # Check if rotation is needed before writing
            Logger._rotate_logs()

            with open(recon_path, "a") as f:
                f.write(entry + "\n")
        except Exception as e:
            from .errors import Error
            Error.silent(f"Logging Failed: {e}")

    @staticmethod
    def log_soft_error(entry):
        """Logs the execution details, with optional verbose argument tracking."""
        db = DatabaseManagment.get()
        session_id = db.get("SESSION_ID", "UNKNOWN")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [SESSION: {session_id}| {entry}]"
        Logger._write_log(entry)


    @staticmethod
    def log_execution(exploit_type, success=True, args=None):
        """Logs the execution details, with optional verbose argument tracking."""
        db = DatabaseManagment.get()
        session_id = db.get("SESSION_ID", "UNKNOWN")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        exploit = db.get("EXPLOIT", "Unknown")
        target = db.get("R_HOST", "N/A")
        
        # Check if verbose logging is enabled (handle various truthy strings)
        verbose_flag = str(db.get("VERBOSE_LOGGING", "false")).strip().lower()
        is_verbose = verbose_flag in ["true", "1", "yes", "y", "on"]
        
        entry = f"[{timestamp}] [SESSION: {session_id}] TYPE: {exploit_type} | EXPLOIT: {exploit} | TARGET: {target} | SUCCESS: {success}"
        
        # Append arguments if verbose mode is on and arguments exist
        if is_verbose and args:
            arg_str = " ".join(args) if isinstance(args, list) else str(args)
            entry += f" | ARGS: {arg_str}"
            
        Logger._write_log(entry)