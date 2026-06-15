"""
SuperSploit Internet Footprint Analyzer
A professional-grade OSINT tool for deep digital footprinting and correlation.
Links Public IPs, Social Media, and Persona data into a unified profile.
"""

import sys
import os
import requests
import json
import argparse
import time
import re

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
name: "Internet Footprint Analyzer"
description: "Professional digital footprint correlation engine. Links IPs, social media, and database records."
category: "OSINT"
author: "Donald Ford"
#!#!#!

PLATFORMS = {
    "GitHub": "https://github.com/{}",
    "Twitter": "https://twitter.com/{}",
    "Instagram": "https://www.instagram.com/{}",
    "Reddit": "https://www.reddit.com/user/{}",
    "Medium": "https://medium.com/@{}",
    "TikTok": "https://www.tiktok.com/@{}",
    "YouTube": "https://www.youtube.com/@{}",
    "Pinterest": "https://www.pinterest.com/{}",
    "Facebook": "https://www.facebook.com/{}",
    "LinkedIn": "https://www.linkedin.com/in/{}",
    "StackOverflow": "https://stackoverflow.com/users/{}",
    "Behance": "https://www.behance.net/{}",
    "Dribbble": "https://dribbble.com/{}",
    "About.me": "https://about.me/{}",
    "Linktree": "https://linktr.ee/{}"
}

class FootprintAnalyzer:
    def __init__(self, debug=False):
        self.debug = debug
        self.findings = {
            "ips": {},
            "social": {},
            "correlations": []
        }

    def correlate_ip(self, ip):
        """Geolocates and analyzes a public IP address."""
        print(f"[*] Correlating IP Address: {ip}...")
        try:
            # Using ip-api.com (free for non-commercial use, 45 requests/min)
            response = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,mobile,proxy,hosting", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.findings["ips"][ip] = data
                    print(f"    - Location: {data.get('city')}, {data.get('country')}")
                    print(f"    - ISP:      {data.get('isp')} ({data.get('as')})")
                    if data.get("proxy") or data.get("hosting"):
                        print(f"    [!] OPSEC Alert: IP identified as Hosting/Proxy/VPN.")
                else:
                    print(f"    [-] Shodan/IP-API Error: {data.get('message')}")
        except Exception as e:
            print(f"    [-] IP Correlation failed: {e}")

    def probe_social(self, alias):
        """Checks for an alias across multiple platforms."""
        print(f"[*] Probing Social Footprint for alias: {alias}...")
        results = []
        for platform, url_template in PLATFORMS.items():
            url = url_template.format(alias)
            try:
                # Use a standard User-Agent to avoid simple blocking
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                # Using a 5s timeout and verifying existence via status codes
                resp = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                if resp.status_code == 200:
                    print(f"    [+] Found presence on {platform}: {url}")
                    results.append({"platform": platform, "url": url})
            except:
                pass
            time.sleep(0.5) # Gentle rate limiting
        self.findings["social"][alias] = results

    def cross_reference_db(self, name=None, email=None, phone=None):
        """Pulls existing context from SuperSploit databases."""
        if not has_db: return
        print("[*] Cross-referencing findings with SuperSploit Persona Database...")
        
        profiles = DatabaseManagment.getProfiles()
        targets = DatabaseManagment.getTargets()
        
        matched_profiles = []
        for p_id, p_data in profiles.items():
            if (name and name.lower() in p_data.get("name", "").lower()) or \
               (email and email.lower() in p_data.get("email", "").lower()) or \
               (phone and phone in p_data.get("phone", "")):
                matched_profiles.append(p_data)
                self.findings["correlations"].append(f"Matched Profile: {p_data.get('name')} (ID: {p_id})")

        if matched_profiles:
            print(f"    [!] Identified {len(matched_profiles)} existing persona matches.")
            for p in matched_profiles:
                print(f"    -> Profile: {p.get('name')} | Last Audit: {p.get('last_audit', 'N/A')}")
        else:
            print("    [-] No existing persona matches found.")

def Start(args=None):
    parser = argparse.ArgumentParser(description="Internet Footprint Analyzer")
    parser.add_argument("--ip", help="Public IP address to correlate")
    parser.add_argument("--name", help="Target full name")
    parser.add_argument("--email", help="Target email address")
    parser.add_argument("--phone", help="Target phone number")
    parser.add_argument("--alias", help="Target username/alias", action="append")
    
    # Support for SuperSploit positional args
    if args and not args[0].startswith("--"):
        # Very basic positional parsing if someone just does 'run <target>'
        target = args[0]
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
            parsed_args = parser.parse_args(["--ip", target])
        elif "@" in target:
            parsed_args = parser.parse_args(["--email", target])
        else:
            parsed_args = parser.parse_args(["--name", target])
    else:
        parsed_args = parser.parse_args(args if args else [])

    analyzer = FootprintAnalyzer()
    print(f"[*] --- INTERNET FOOTPRINT ANALYSIS START ---")
    
    # 1. Database Enrichment
    analyzer.cross_reference_db(name=parsed_args.name, email=parsed_args.email, phone=parsed_args.phone)

    # 2. IP Correlation
    if parsed_args.ip:
        analyzer.correlate_ip(parsed_args.ip)

    # 3. Social Footprinting
    aliases = parsed_args.alias or []
    # Auto-generate aliases from email if provided
    if parsed_args.email and "@" in parsed_args.email:
        email_alias = parsed_args.email.split("@")[0]
        if email_alias not in aliases:
            print(f"[*] Auto-derived alias from email: {email_alias}")
            aliases.append(email_alias)
    
    # Auto-generate aliases from name if provided
    if parsed_args.name:
        name_parts = parsed_args.name.lower().split()
        if len(name_parts) >= 2:
            n_alias = "".join(name_parts)
            if n_alias not in aliases:
                print(f"[*] Auto-derived alias from name: {n_alias}")
                aliases.append(n_alias)

    for a in aliases:
        analyzer.probe_social(a)

    # 4. Final Synthesis
    print(f"\n[*] --- ANALYSIS SUMMARY ---")
    if analyzer.findings["ips"]:
        for ip, data in analyzer.findings["ips"].items():
            print(f"[IP: {ip}] Location: {data.get('city')}, {data.get('country')} | ISP: {data.get('isp')}")
    
    total_social = sum(len(hits) for hits in analyzer.findings["social"].values())
    print(f"[Social] Total Profiles Identified: {total_social}")
    
    for alias, hits in analyzer.findings["social"].items():
        if hits:
            print(f"  -> Alias: {alias} ({len(hits)} hits)")
            for h in hits:
                print(f"     - {h['platform']}: {h['url']}")

    # Update database
    if has_db and (parsed_args.name or parsed_args.email or aliases):
        profile_update = {
            "name": parsed_args.name or (aliases[0] if aliases else "Unknown"),
            "email": parsed_args.email or "Unknown",
            "phone": parsed_args.phone or "Unknown",
            "internet_footprint": analyzer.findings,
            "last_audit": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        # Attempt to link to existing or create new
        DatabaseManagment.addProfile(profile_update)
        print("\n[*] Digital footprint synchronized to Persona Database.")

if __name__ == "__main__":
    # If run standalone, sys.argv[1:] will be passed to Start
    Start(sys.argv[1:])
