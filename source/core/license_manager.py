import hashlib
import uuid
import os
import json
import sqlite3
from .ToStdOut import ToStdout
from .security_engine import SecurityEngine

class LicenseManager:
    LICENSE_FILE = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "license.key")
    REGISTRY_DB = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "registry.db")
    
    # URL to your hosted manifest.json on GitHub
    REMOTE_MANIFEST_URL = "https://raw.githubusercontent.com/don970/supersploit_key_system/main/manifest.json"
    
    _is_pro_cache = None # In-memory cache for the current session

    @staticmethod
    def get_hwid():
        """Generates a unique Hardware ID for local reference."""
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 8*6, 8)][::-1])
        hwid_raw = f"SuperSploit-{mac}-{os.getlogin()}"
        return hashlib.sha256(hwid_raw.encode()).hexdigest()[:16].upper()

    @classmethod
    def _get_remote_url(cls):
        """Fetches the manifest URL from the database or defaults to GitHub."""
        from .database import DatabaseManagment
        db = DatabaseManagment.get()
        return db.get("REMOTE_MANIFEST_URL", "https://raw.githubusercontent.com/don970/supersploit_key_system/main/manifest.json")

    @classmethod
    def _fetch_remote_manifest(cls):
        """Fetches the central license database from the remote URL."""
        url = cls._get_remote_url()
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            # Fallback/Log error
            ToStdout.write(f"[!] Warning: Could not connect to Remote Security Manifest ({e})\n")
            return None

    @classmethod
    def check_pro_status(cls):
        """Verifies Pro status by invoking the Advanced Security Engine and Remote Manifest."""
        if cls._is_pro_cache is not None:
            return cls._is_pro_cache

        if not os.path.exists(cls.LICENSE_FILE):
            cls._is_pro_cache = False
            return False
        
        try:
            with open(cls.LICENSE_FILE, "r") as f:
                license_data = json.load(f)
            
            key = license_data.get("key")
            stored_hwid = license_data.get("hwid")
            current_hwid = cls.get_hwid()

            # 1. Local HWID Consistency Check
            if stored_hwid != current_hwid:
                ToStdout.write("[-] SECURITY ALERT: HWID Mismatch! License file moved or hardware changed.\n")
                return False

            # 2. Remote Manifest Validation (The Central Check)
            manifest = cls._fetch_remote_manifest()
            if manifest:
                if manifest["policy"].get("global_killswitch"):
                    ToStdout.write("[!] EMERGENCY: Framework has been globally disabled by the developer.\n")
                    return False

                remote_entry = manifest["keys"].get(key)
                if not remote_entry:
                    ToStdout.write(f"[-] ERROR: Key '{key}' is not in the remote manifest.\n")
                    return False
                
                if remote_entry["status"] == "revoked":
                    ToStdout.write(f"[-] ERROR: Key '{key}' has been revoked by the administrator.\n")
                    return False

                if remote_entry["hwid"] and remote_entry["hwid"] != current_hwid:
                    ToStdout.write(f"[-] SECURITY ALERT: This key is anchored to a different HWID ({remote_entry['hwid']}).\n")
                    return False

            # 3. Binary Validation (The Proprietary Engine)
            if SecurityEngine.run_auth_check(key):
                cls._is_pro_cache = True
                return True
            
            cls._is_pro_cache = False
            return False
        except:
            cls._is_pro_cache = False
            return False

    @classmethod
    def activate(cls, key):
        """Attempts to activate the Pro license using the Security Engine and Remote Sync."""
        key = key.strip().rstrip(".,!")
        current_hwid = cls.get_hwid()
        
        ToStdout.write("[*] Initiating multi-factor remote validation...\n")
        cls._is_pro_cache = None

        # 1. Fetch Remote Manifest to check for key existence and anchoring
        manifest = cls._fetch_remote_manifest()
        if manifest:
            remote_entry = manifest["keys"].get(key)
            if not remote_entry:
                ToStdout.write(f"[-] ERROR: Key '{key}' was not found in the remote registry.\n")
                return False
            
            # Automatic Anchoring Logic
            if remote_entry["hwid"] is None:
                ToStdout.write(f"[*] NEW ACTIVATION: Anchoring key '{key}' to this HWID...\n")
                # NOTE: In a 'basic' GitHub-only setup, the admin manually updates the manifest 
                # after being notified. For automation, a Registration Webhook is triggered here.
                cls._trigger_registration_webhook(key, current_hwid)
                ToStdout.write("[*] Registration request sent. Please wait for the admin to approve the anchor.\n")
            elif remote_entry["hwid"] != current_hwid:
                ToStdout.write(f"[-] SECURITY ALERT: Key is already anchored to HWID: {remote_entry['hwid']}\n")
                return False

        # 2. Run Binary Check
        if SecurityEngine.run_auth_check(key):
            data = {
                "key": key, 
                "hwid": current_hwid, 
                "swid": str(uuid.uuid4()),
                "timestamp": str(datetime.datetime.now())
            }
            
            config_dir = os.path.dirname(cls.LICENSE_FILE)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
                
            with open(cls.LICENSE_FILE, "w") as f:
                json.dump(data, f)
            
            cls._is_pro_cache = True
            ToStdout.write("[+] SUCCESS: SuperSploit Pro Activated!\n")
            return True
        else:
            cls._is_pro_cache = False
            ToStdout.write("[-] ERROR: Multi-factor validation failed.\n")
            return False

    @classmethod
    def _trigger_registration_webhook(cls, key, hwid):
        """Notifies the administrator of a new activation request for anchoring."""
        from .database import DatabaseManagment
        import socket
        db = DatabaseManagment.get()
        webhook_url = db.get("LICENSE_WEBHOOK")
        
        if not webhook_url:
            return

        try:
            payload = {
                "embeds": [{
                    "title": "💎 New Pro Activation Request",
                    "color": 0x00ff00,
                    "fields": [
                        {"name": "License Key", "value": f"`{key}`", "inline": True},
                        {"name": "Hardware ID", "value": f"`{hwid}`", "inline": True},
                        {"name": "Machine", "value": f"`{os.getlogin()}@{socket.gethostname()}`", "inline": False},
                        {"name": "Action Required", "value": f"Run: `python3 source/tools/licensing/manager.py --anchor {key} {hwid}`"}
                    ],
                    "timestamp": datetime.datetime.now().isoformat()
                }]
            }
            
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'SuperSploit-Auth'})
            with urllib.request.urlopen(req, timeout=5) as response:
                pass
        except:
            pass

    @staticmethod
    def gate_access(feature_name):
        """Simple wrapper to check license and print warning if unauthorized."""
        if not LicenseManager.check_pro_status():
            ToStdout.write(f"\n[!] ACCESS DENIED: '{feature_name}' is a SuperSploit Pro feature.\n")
            ToStdout.write(f"[*] Your HWID: {LicenseManager.get_hwid()}\n")
            ToStdout.write("[*] Please visit the Pro-Portal to purchase a license.\n")
            ToStdout.write("[*] See 'docs/Legal/PRO_PRICING.md' for more details.\n")
            return False
        return True
