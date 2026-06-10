import json
import os

targets_path = "/home/donald/.SuperSploit/.data/.config/targets.json"
os.makedirs(os.path.dirname(targets_path), exist_ok=True)

targets = {
    "TARGETS": {
        "192.158.151.158": {
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
    }
}

with open(targets_path, "w") as f:
    json.dump(targets, f, indent=4)

print("[+] Test target injected into targets.json")
