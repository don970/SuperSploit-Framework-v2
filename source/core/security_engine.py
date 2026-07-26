import os
import json
import subprocess

class SecurityEngine:
    """Python bridge to the compiled native C authentication engine."""
    
    # Pointing to the binary we just compiled via gcc
    AUTH_BINARY = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "supersploit_auth")
    LICENSE_FILE = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "license.key")

    @classmethod
    def get_hwid(cls):
        """Executes the auth binary to retrieve the hardware fingerprint."""
        if not os.path.exists(cls.AUTH_BINARY):
            return "AUTH_BIN_NOT_FOUND"
        try:
            result = subprocess.run([cls.AUTH_BINARY, "--hwid"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "HWID_GENERATION_FAILED"
    
    @classmethod
    def _get_saved_key(cls):
        """Reads the active key from the local config."""
        if not os.path.exists(cls.LICENSE_FILE):
            return None
        try:
            with open(cls.LICENSE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("key")
        except Exception:
            return None

    @classmethod
    def run_full_auth_check(cls):
        """Runs the background validation using the saved key."""
        key = cls._get_saved_key()
        if not key:
            return {"status": "error", "message": "No license key found locally."}
        
        return cls._execute_binary("--check", key)

    @classmethod
    def run_activation(cls, key):
        """Runs the manual online activation workflow."""
        result = cls._execute_binary("--activate", key)
            
        # Only save the key locally if the activation was successful or requires vetting
        if result.get("status") in ["success", "needs_vetting"]:
            os.makedirs(os.path.dirname(cls.LICENSE_FILE), exist_ok=True)
            try:
                with open(cls.LICENSE_FILE, 'w') as f:
                    json.dump({"key": key}, f)
            except Exception:
                pass
                
        return result

    @classmethod
    def _execute_binary(cls, mode, key):
        """Helper to execute the compiled C engine and parse the JSON response."""
        if not os.path.exists(cls.AUTH_BINARY):
            return {"status": "error", "message": "Security engine binary missing. Please recompile."}
            
        try:
            # We don't use check=True because the C binary returns non-zero codes on failures (e.g. revoked),
            # but still prints structured JSON to stdout that we want to parse.
            result = subprocess.run([cls.AUTH_BINARY, mode, key], capture_output=True, text=True)
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {"status": "error", "message": "Engine returned malformed response or crashed."}
        except Exception as e:
            return {"status": "error", "message": f"Engine execution failed: {str(e)}"}
