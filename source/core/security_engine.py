import os
import subprocess
import urllib.request
import hashlib
import json
from .ToStdOut import ToStdout

class SecurityEngine:
    """
    The Advanced Multi-Factor Security Engine.
    Handles the downloading, verification, and execution of the proprietary 
    authentication binary from GitHub.
    """
    AUTH_BIN_PATH = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "supersploit_auth")
    # REPLACE THIS WITH THE ACTUAL RAW URL OF YOUR COMPILED BINARY ON GITHUB
    REMOTE_BIN_URL = "https://raw.githubusercontent.com/don970/supersploit_key_system/main/supersploit_auth"
    
    # SUCCESS_CODE: The specific exit code returned by the binary on success.
    # Should be non-standard to avoid lucky guesses (e.g. 127, 200, etc.)
    SUCCESS_CODE = 127 
    
    @classmethod
    def _download_binary(cls):
        """Downloads the pre-compiled authentication binary from GitHub."""
        try:
            ToStdout.write("[*] Synchronizing Security Engine with remote policy...\n")
            with urllib.request.urlopen(cls.REMOTE_BIN_URL, timeout=10) as response:
                with open(cls.AUTH_BIN_PATH, "wb") as f:
                    f.write(response.read())
            
            # Set execution permissions
            os.chmod(cls.AUTH_BIN_PATH, 0o755)
            return True
        except Exception as e:
            ToStdout.write(f"[-] Critical Error: Failed to synchronize Security Engine ({e})\n")
            return False

    @classmethod
    def run_auth_check(cls, license_key):
        """
        Executes the proprietary binary to perform multi-factor validation.
        Returns True if the binary returns the SUCCESS_CODE.
        """
        if not os.path.exists(cls.AUTH_BIN_PATH):
            if not cls._download_binary():
                return False

        try:
            # The binary is expected to autonomously gather telemetry 
            # and verify against the GitHub manifest.
            result = subprocess.run(
                [cls.AUTH_BIN_PATH, license_key],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            # Check for success exit code
            if result.returncode == cls.SUCCESS_CODE:
                return True
            
            # Failure: Print the message returned by the binary (if any)
            if result.stdout:
                ToStdout.write(f"\n[!] SECURITY ALERT: {result.stdout.strip()}\n")
            return False
            
        except subprocess.TimeoutExpired:
            ToStdout.write("[-] Security Engine Timeout: Remote validation took too long.\n")
            return False
        except Exception as e:
            ToStdout.write(f"[-] Security Engine Internal Error: {e}\n")
            return False

    @classmethod
    def sync_manifest(cls):
        """Triggers a force sync of the remote security manifest (via the binary)."""
        if os.path.exists(cls.AUTH_BIN_PATH):
            try:
                # Binary might have a --sync flag to refresh local manifest.cache
                subprocess.run([cls.AUTH_BIN_PATH, "--sync"], capture_output=True, timeout=5)
            except:
                pass
