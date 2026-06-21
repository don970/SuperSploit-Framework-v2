import os
import json
import urllib.request
import datetime
from .ToStdOut import ToStdout
from .security_engine import SecurityEngine

class LicenseManager:
    LICENSE_FILE = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".config", "license.key")
    
    _is_pro_cache = None # In-memory cache for the current session

    @staticmethod
    def get_hwid():
        """Fetches the hardware ID directly from the compiled Security Engine."""
        # The C binary generates the HWID to prevent spoofing in Python
        return SecurityEngine.get_hwid()

    @classmethod
    def check_pro_status(cls, silent=False):
        """Delegates all status, offline grace, and cache checks to the compiled C binary."""
        if cls._is_pro_cache is not None:
            return cls._is_pro_cache
        
        try:
            # The binary completely takes over reading the file, validating the signature, 
            # fetching the manifest, and enforcing the offline TTL limit.
            status_result = SecurityEngine.run_full_auth_check()
            
            if status_result.get("status") == "success":
                if status_result.get("offline_mode", False) and not silent:
                    days_left = status_result.get("days_remaining", 0)
                    ToStdout.write(f"[*] Using local manifest cache. Expires in {days_left} days.\n")
                cls._is_pro_cache = True
                return True
            
            if status_result.get("message") and not silent:
                ToStdout.write(f"[-] ERROR: {status_result.get('message')}\n")
                
            cls._is_pro_cache = False
            return False
        except Exception as e:
            ToStdout.write(f"[-] ERROR: License validation encountered an error: {e}\n")
            cls._is_pro_cache = False
            return False

    @classmethod
    def activate(cls, key):
        """Passes the key to the C binary for activation and remote syncing."""
        key = key.strip().rstrip(".,!")
        
        ToStdout.write("[*] Delegating multi-factor remote validation to Security Engine...\n")
        cls._is_pro_cache = None

        # The C binary performs the HTTP GET, checks the key, and writes the secure license block to disk
        activation_result = SecurityEngine.run_activation(key)
        
        if activation_result.get("status") == "success":
            cls._is_pro_cache = True
            ToStdout.write("[+] SUCCESS: SuperSploit Pro Activated!\n")
            return True
            
        elif activation_result.get("status") == "needs_vetting":
            # Webhook is the only thing we leave in Python since writing HTTPS POSTs with JSON in C is tedious
            hwid = activation_result.get("hwid")
            ToStdout.write(f"[*] NOTICE: This key is not yet hardware-locked on the remote server.\n")
            ToStdout.write(f"[*] Sending vetting request to administrator via Discord...\n")
            if cls._trigger_registration_webhook(key, hwid):
                ToStdout.write(f"[*] Local anchoring will proceed for HWID: {hwid}\n")
                ToStdout.write(f"[*] To permanently secure this key, wait for the admin to update the manifest.\n")
            else:
                ToStdout.write("[-] ERROR: Failed to send vetting request to Discord. Check your internet connection.\n")
            return False
            
        else:
            cls._is_pro_cache = False
            ToStdout.write(f"[-] ERROR: {activation_result.get('message', 'Multi-factor validation failed.')}\n")
            return False

    @classmethod
    def _trigger_registration_webhook(cls, key, hwid):
        """Sends a Discord webhook to the admin for manual vetting."""
        # Paste your Discord Webhook URL here
        webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
        if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL":
            return False
            
        import socket
        try:
            payload = {
                "embeds": [{
                    "title": "💎 New Pro Activation Request",
                    "color": 0x00ff00,
                    "fields": [
                        {"name": "License Key", "value": f"`{key}`", "inline": True},
                        {"name": "Hardware ID", "value": f"`{hwid}`", "inline": True},
                        {"name": "Machine", "value": f"`{os.getlogin()}@{socket.gethostname()}`", "inline": False},
                        {"name": "Action Required", "value": "Update the mobile app manifest with this HWID to approve."}
                    ],
                    "timestamp": datetime.datetime.now().isoformat()
                }]
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(webhook_url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'SuperSploit-Auth'})
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status in [200, 204]
        except Exception:
            return False

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
