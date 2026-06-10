import sys
import os
import unittest
import json
from unittest.mock import patch

# Mock input() to avoid hanging
def mock_input(prompt):
    if "Run as a module" in prompt:
        return "y"
    if "Enter arguments" in prompt:
        return ""
    return ""

sys.path.append('/home/donald/.SuperSploit/source')
from core.database import DatabaseManagment, ExploitCache
from core.recon_engine import Recon

# Populate Exploit Cache
ExploitCache.update()

# Set the recon path in DB
db = DatabaseManagment.get()
db['RECON_PATH'] = '/home/donald/.SuperSploit/recon/test_suggest_hook.py'
db['RECON_NAME'] = 'test_suggest_hook'

# Clear targets first
targets_path = "/home/donald/.SuperSploit/.data/.config/targets.json"
with open(targets_path, "w") as f:
    json.dump({"TARGETS": {}}, f)

# Re-inject the 192.158.151.158 target (so we have it for analysis)
with open(targets_path, "r") as f:
    targets = json.load(f)
targets["TARGETS"]["192.158.151.158"] = {
    "status": "up",
    "os": "Linux",
    "kernel": "5.10.0",
    "arch": "x86_64",
    "services": {
        "8080": {
            "protocol": "tcp",
            "service": "http",
            "banner": "VulnServer v1.0 (CWE-78 Diagnostic)"
        }
    }
}
with open(targets_path, "w") as f:
    json.dump(targets, f, indent=4)

with patch('builtins.input', side_effect=mock_input):
    print("[*] Starting Recon Engine Test...")
    Recon()
