"""
GitHub Public Repo Scanner
Searches for leaked credentials and sensitive files in public repositories.
Supports GITHUB_TOKEN for higher rate limits.
"""

import sys
import os
import requests
import json
import time

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
name: "Public Repo Scanner"
description: "Searches GitHub for leaked API keys, secrets, and configuration files associated with a domain or organization."
category: "OSINT"
author: "Donald Ford"
#!#!#!

DORKS = [
    "filename:.env",
    "filename:config.php",
    "filename:wp-config.php",
    "filename:settings.py",
    "filename:.git-credentials",
    "filename:.bash_history",
    "extension:pem",
    "extension:ppk",
    "extension:sql",
    "AWS_ACCESS_KEY_ID",
    "DATABASE_URL",
    "HEROKU_API_KEY",
    "JDBC_CONNECTION_STRING",
    "slack_api_token"
]

def search_github(query, token=None):
    """
    Executes a code search on GitHub.
    """
    url = "https://api.github.com/search/code"
    params = {"q": query, "per_page": 10}
    headers = {"Accept": "application.vnd.github.v3+json"}
    
    if token:
        headers["Authorization"] = f"token {token}"
        
    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        
        if response.status_code == 403:
            print("[-] Error: GitHub API rate limit exceeded.")
            return []
        elif response.status_code != 200:
            print(f"[-] Error: GitHub API returned status code {response.status_code}")
            return []
            
        data = response.json()
        return data.get('items', [])
        
    except Exception as e:
        print(f"[-] GitHub Request failed: {e}")
        return []

def Start(args=None):
    target = ""
    token = None
    
    if args:
        target = args[0]
    elif has_db:
        db = DatabaseManagment.get()
        target = db.get("R_HOST", "")
        token = db.get("GITHUB_TOKEN", None)

    if not target:
        print("[-] Error: A target organization or domain is required.")
        return

    print(f"[*] Starting Public Repo Scan for: {target}")
    if token:
        print("[*] Utilizing GITHUB_TOKEN for authenticated search.")
    
    all_findings = []
    
    for dork in DORKS:
        query = f"{dork} {target}"
        print(f"[*] Searching: {query}...")
        results = search_github(query, token)
        
        if results:
            print(f"[!] Found {len(results)} potential leaks with dork: {dork}")
            for item in results:
                finding = {
                    "dork": dork,
                    "repo": item['repository']['full_name'],
                    "path": item['path'],
                    "url": item['html_url']
                }
                all_findings.append(finding)
                print(f"    - URL: {finding['url']}")
        
        # Sleep to avoid hitting rate limits (GitHub search has strict limits)
        time.sleep(2 if token else 10)

    print(f"\n[+] Scan Complete. Found {len(all_findings)} potential leaks across GitHub.")

if __name__ == "__main__":
    Start(sys.argv[1:])
