"""
Domain/Subdomain Enumerator
Performs passive subdomain discovery via crt.sh (Certificate Transparency Logs).
Synchronizes discovered subdomains to the SuperSploit targets database.
"""

import sys
import os
import json
import requests
import urllib.parse

# Dynamically resolve paths for framework integration
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
source_dir = os.path.join(framework_root, "source")

if source_dir not in sys.path:
    sys.path.append(source_dir)

try:
    from core.database import DatabaseManagment
    has_db = True
except ImportError:
    has_db = False

#!#!#!
name: "Domain Enumerator"
description: "Passive subdomain discovery via crt.sh Certificate Transparency logs."
category: "OSINT"
author: "Donald Ford"
#!#!#!

def fetch_subdomains(domain):
    """
    Queries crt.sh for all certificates associated with a domain.
    """
    print(f"[*] Querying crt.sh for subdomains of: {domain}")
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"[-] Error: crt.sh returned status code {response.status_code}")
            return []
        
        data = response.json()
        subdomains = set()
        
        for entry in data:
            name_value = entry.get('name_value', '')
            # Split names if multiple are in one certificate (e.g., via wildcards or SANs)
            names = name_value.split('\n')
            for name in names:
                name = name.strip().lower()
                if name.endswith(domain) and '*' not in name:
                    subdomains.add(name)
        
        return sorted(list(subdomains))
        
    except Exception as e:
        print(f"[-] Request failed: {e}")
        return []

def Start(args=None):
    target_domain = ""
    if args:
        target_domain = args[0]
    elif has_db:
        target_domain = DatabaseManagment.get().get("R_HOST", "")

    if not target_domain or "." not in target_domain:
        print("[-] Error: A valid target domain (e.g., example.com) is required.")
        return

    subdomains = fetch_subdomains(target_domain)
    
    if not subdomains:
        print(f"[-] No subdomains found for {target_domain}.")
        return

    print(f"\n[+] Discovered {len(subdomains)} subdomains:")
    for sub in subdomains:
        print(f"    - {sub}")

    if has_db:
        print(f"\n[*] Synchronizing discovered subdomains to targets database...")
        targets = DatabaseManagment.getTargets()
        new_count = 0
        
        for sub in subdomains:
            if sub not in targets:
                targets[sub] = {
                    "hostname": sub,
                    "status": "unknown",
                    "discovery_method": "crt.sh OSINT",
                    "os_family": "Unknown",
                    "architecture": "Unknown"
                }
                new_count += 1
        
        DatabaseManagment.updateTargets(targets)
        DatabaseManagment.sync_targets_to_disk()
        print(f"[+] Database updated. {new_count} new targets added.")

if __name__ == "__main__":
    Start(sys.argv[1:])
