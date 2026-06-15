"""
Shodan Infrastructure Recon
Queries Shodan for open ports, banners, and known CVEs for a target IP or Domain.
Integrates directly with the auto_suggest engine.
"""

import sys
import os
import requests
import json

# Framework integration
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
name: "Shodan Recon"
description: "Passive infrastructure mapping via Shodan API. Extracts open ports, hostnames, and known vulnerabilities (CVEs)."
category: "OSINT"
author: "Donald Ford"
#!#!#!

def query_shodan(query, api_key):
    """
    Queries Shodan API for host information.
    """
    # Shodan can query by IP or Domain
    url = f"https://api.shodan.io/shodan/host/{query}?key={api_key}"
    
    try:
        response = requests.get(url, timeout=20)
        if response.status_code == 404:
            print(f"[-] Shodan: No information found for {query}")
            return None
        elif response.status_code != 200:
            print(f"[-] Shodan API Error: {response.status_code}")
            return None
            
        return response.json()
        
    except Exception as e:
        print(f"[-] Shodan Request failed: {e}")
        return None

def Start(args=None):
    target = ""
    api_key = None
    
    if args:
        target = args[0]
    elif has_db:
        db = DatabaseManagment.get()
        target = db.get("R_HOST", "")
        api_key = db.get("SHODAN_API_KEY", None)

    if not target:
        print("[-] Error: A target IP or domain is required.")
        return

    if not api_key:
        print("[-] Error: SHODAN_API_KEY is not set in the database.")
        print("[*] Fix: set SHODAN_API_KEY <your_key>")
        return

    print(f"[*] Querying Shodan for: {target}")
    data = query_shodan(target, api_key)
    
    if not data:
        return

    print(f"\n[+] Shodan Host Report: {data.get('ip_str', target)}")
    print(f"    - Organization: {data.get('org', 'Unknown')}")
    print(f"    - OS:           {data.get('os', 'Unknown')}")
    print(f"    - Ports:        {data.get('ports', [])}")
    
    vulns = data.get('vulns', [])
    if vulns:
        print(f"    - Vulnerabilities: {len(vulns)} detected.")
        for v in vulns[:5]:
            print(f"      -> {v}")
        if len(vulns) > 5:
            print("      -> ...")

    if has_db:
        print(f"\n[*] Enriching target database with Shodan data...")
        targets = DatabaseManagment.getTargets()
        ip = data.get('ip_str', target)
        
        if ip not in targets:
            targets[ip] = {"mac": "Unknown", "status": "up", "discovery_method": "Shodan"}

        targets[ip].update({
            "hostname": data.get('hostnames', [ip])[0],
            "os_family": data.get('os', 'Unknown'),
            "ports": data.get('ports', []),
            "cves": vulns,
            "shodan_data": {
                "org": data.get('org'),
                "isp": data.get('isp'),
                "last_update": data.get('last_update')
            }
        })
        
        DatabaseManagment.updateTargets(targets)
        DatabaseManagment.sync_targets_to_disk()
        print("[+] Database updated. Auto-suggest engine now has fresh CVE data.")

if __name__ == "__main__":
    Start(sys.argv[1:])
