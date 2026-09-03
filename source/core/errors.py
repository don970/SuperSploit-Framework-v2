import os
import sys
from .ToStdOut import ToStdout

write = ToStdout.write
installation = f'{os.getenv("HOME")}/.SuperSploit'

class Error:
    def __init__(self, data):
        self._handle_error(data, silent=False)

    @staticmethod
    def silent(data):
        Error._handle_error(data, silent=True)
        
    @staticmethod
    def _handle_error(data, silent: bool):
        # Pythonic type checking
        if isinstance(data, bytes):
            data = data.decode(errors="ignore")
        elif not isinstance(data, str):
            data = str(data)
            
        if not data.endswith("\n"):
            data += "\n"
            
        error_dir = f"{installation}/.data/.errors"
        error_file = f"{error_dir}/error.log"
        
        # Ensure directory exists before writing to prevent crash-loops
        os.makedirs(error_dir, exist_ok=True)
        
        try:
            with open(error_file, "a") as stdout:
                stdout.write(data)
                
            if not silent:
                write(data)
        except Exception as e:
            # Absolute fallback if disk is full or permissions are broken
            sys.stderr.write(f"CRITICAL ERROR: Could not write to log. Original Error: {data}\n")
            sys.stderr.write(f"Log Error: {e}\n")