from typing import List, Dict, Any, Optional
import re
import difflib
from .database import DatabaseManagment

class AutoSuggestCommand:
    def __init__(self, exploit_cache):
        """
        Initializes the auto_suggest command.
        Expects exploit_cache to have an 'all_exploits' attribute and 'metadata_index'.
        """
        self.exploit_cache = exploit_cache

    def execute(self, target_id: str, target_info: Dict[str, Any]):
        """
        Analyzes target metadata and correlates with available exploits AND recon modules.
        """
        print(f"[*] Executing Smarter Analysis for {target_id}...")
        
        # 0. Identify Target Format
        is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_id)
        is_mac = re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", target_id)
        is_domain = "." in target_id and not is_ip
        is_name = " " in target_id or (not is_ip and not is_mac and not is_domain)

        # 0.5 Persona Profile Integration
        profile_data = {}
        profiles = DatabaseManagment.getProfiles()
        # Search by IP
        if is_ip:
            for p_name, p_info in profiles.items():
                if p_info.get("ip") == target_id:
                    profile_data = p_info
                    print(f"[*] Correlated target with Persona Profile: {p_name}")
                    break
        # Search by Name
        if not profile_data and (is_name or target_info.get("hostname")):
            h_name = target_info.get("hostname", target_id)
            if h_name in profiles:
                profile_data = profiles[h_name]
                print(f"[*] Correlated target with Persona Profile: {h_name}")

        # 1. Normalize target data
        services = target_info.get('services', {})
        # ... (rest of normalization)
        if not services:
            legacy_ports = target_info.get('open_ports', target_info.get('ports', []))
            for p in legacy_ports:
                if isinstance(p, dict):
                    p_num = str(p.get('port', ''))
                    services[p_num] = {
                        'protocol': p.get('protocol', 'tcp'),
                        'banner': p.get('banner', 'unknown'),
                        'service': p.get('service', 'unknown')
                    }
                else:
                    services[str(p)] = {'protocol': 'tcp', 'service': 'unknown'}

        target_os = str(target_info.get('os', target_info.get('os_family', profile_data.get('os', '')))).lower()
        target_kernel = str(target_info.get('kernel', target_info.get('kernel_version', profile_data.get('kernel', '')))).lower()
        target_arch = str(target_info.get('arch', target_info.get('architecture', profile_data.get('arch', '')))).lower()
        
        target_cves = target_info.get('cves', [])
        p_cves = profile_data.get("cves", [])
        if isinstance(p_cves, str): p_cves = [p_cves]
        target_cves = list(set(target_cves + p_cves))
        
        target_env = target_info.get('environment', [])
        p_env = profile_data.get("environment", [])
        if isinstance(p_env, str): p_env = [p_env]
        target_env = list(set(target_env + p_env))

        # Extract extra keywords from profile research/notes
        profile_keywords = []
        if profile_data.get("research"):
            for note in profile_data["research"]:
                profile_keywords.extend(re.findall(r'\b\w{3,}\b', note.lower()))
        
        if profile_data.get("internet_footprint"):
            # Extract mentions of platforms or correlations
            footprint = profile_data["internet_footprint"]
            for alias, hits in footprint.get("social", {}).items():
                profile_keywords.append(alias.lower())
                for h in hits:
                    profile_keywords.append(h["platform"].lower())

        recon_suggestions = []
        exploit_suggestions = []

        # 2. RECONNAISSANCE SUGGESTIONS (Format-Based)
        for path, meta in self.exploit_cache.metadata_index.items():
            cat = str(meta.get('cat', '')).lower()
            if "discovery" not in cat and "recon" not in cat and "osint" not in cat:
                continue
                
            r_score = 0
            r_reasons = []
            
            # Bluetooth/BLE logic
            if is_mac:
                if "bluetooth" in meta.get('desc', '').lower() or "ble" in meta.get('desc', '').lower():
                    r_score += 50
                    r_reasons.append("Target format identified as MAC address")
            
            # OSINT logic
            if is_name or is_domain:
                if "osint" in cat:
                    r_score += 40
                    r_reasons.append("Target identified as non-IP entity (Name/Domain)")
                if is_domain and "domain" in meta.get('desc', '').lower():
                    r_score += 15
                    r_reasons.append("Specific domain-level recon module")
            
            # Profile Gap Analysis
            if is_ip:
                if not services and ("port" in meta.get('desc', '').lower() or "scan" in meta.get('desc', '').lower()):
                    r_score += 30
                    r_reasons.append("Target IP has no mapped services; suggesting scanner")
                if not target_os and "fingerprint" in meta.get('desc', '').lower():
                    r_score += 25
                    r_reasons.append("Target OS is unknown; suggesting fingerprinter")
                if "android" in target_os and "exploit" in meta.get('desc', '').lower():
                    r_score += 20
                    r_reasons.append("Android target identified; suggesting mobile exploitation suite")
            
            # Specific Tool: Android Enum
            if "android" in target_os and "enum" in meta.get('name', '').lower() and "android" in meta.get('name', '').lower():
                r_score += 60
                r_reasons.append("Recommended: Comprehensive Android device auditing")

            if r_score > 0:
                recon_suggestions.append({
                    'name': meta.get('name'),
                    'path': path,
                    'score': r_score,
                    'reasons': r_reasons
                })

        # 3. EXPLOIT SUGGESTIONS (State-Based)
        if services or target_os or target_kernel:
            for exploit_path, meta in self.exploit_cache.metadata_index.items():
                cat = str(meta.get('cat', '')).lower()
                if "discovery" in cat or "recon" in cat or "osint" in cat:
                    continue # Ignore recon modules for exploit analysis
                
                score = 0
                reasons = []
                confidence = "Low"
                
                # --- PRE-QUALIFICATION (Hard Filters) ---
                exploit_os = str(meta.get('os', '')).lower()
                if exploit_os and target_os:
                    if not (exploit_os in target_os or target_os in exploit_os):
                        continue 

                exploit_arch = str(meta.get('arch', '')).lower()
                if exploit_arch and target_arch:
                    if not (exploit_arch in target_arch or target_arch in exploit_arch):
                        continue

                # --- HEURISTIC MATCHING ---
                exploit_name = meta.get('name', 'Unknown Exploit')
                exploit_cve = str(meta.get('cve', '')).upper()
                exploit_kernel_vers = meta.get('kernel', [])
                if isinstance(exploit_kernel_vers, str):
                    exploit_kernel_vers = [k.strip() for k in exploit_kernel_vers.split(',')]
                
                keywords = [str(k).lower() for k in meta.get('keywords', [])]
                requirements = meta.get('requirements', [])

                if exploit_cve != "N/A" and exploit_cve in [c.upper() for c in target_cves]:
                    score += 50
                    reasons.append(f"Direct CVE Match: {exploit_cve}")
                    confidence = "Critical"

                if exploit_os and target_os:
                    score += 10
                    reasons.append(f"OS Verified: {exploit_os}")

                if target_kernel and exploit_kernel_vers:
                    matched_kernel = False
                    for v in exploit_kernel_vers:
                        if v.strip() and v.lower() in target_kernel:
                            score += 30
                            reasons.append(f"Kernel Version Exact Match ({v})")
                            matched_kernel = True
                            break
                    if not matched_kernel:
                        min_v = meta.get('min_ver')
                        max_v = meta.get('max_ver')
                        if min_v or max_v:
                            if (not min_v or target_kernel >= min_v.lower()) and \
                               (not max_v or target_kernel <= max_v.lower()):
                                score += 25
                                reasons.append(f"Kernel within vulnerable range ({min_v} to {max_v})")

                for kw in keywords:
                    if kw in profile_keywords:
                        score += 15
                        reasons.append(f"Persona Correlation: Exploit keyword '{kw}' found in profile research/footprint")
                        if confidence not in ["Critical", "High"]:
                            confidence = "High"

                if requirements and target_env:
                    matched_reqs = sum(1 for req in requirements if req in target_env)
                    if matched_reqs > 0:
                        score += (matched_reqs * 15)
                        reasons.append(f"Matched {matched_reqs} environmental prerequisites")

                for port_num, service_info in services.items():
                    service_name = str(service_info.get('service', '')).lower()
                    banner = str(service_info.get('banner', '')).lower()
                    if port_num in keywords:
                        score += 5
                        reasons.append(f"Port {port_num} explicitly targeted")
                    if service_name != 'unknown':
                        matches = difflib.get_close_matches(service_name, keywords, n=1, cutoff=0.8)
                        if matches:
                            score += 10
                            reasons.append(f"Service match: {service_name} (Fuzzy match: {matches[0]})")
                        elif any(service_name in kw for kw in keywords):
                            score += 8
                            reasons.append(f"Service name substring match: {service_name}")
                    if banner != 'unknown':
                        version_match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+)', banner)
                        if version_match:
                            ver = version_match.group(1)
                            if any(ver in kw for kw in keywords) or ver in meta.get('desc', ''):
                                score += 20
                                reasons.append(f"Banner version {ver} matches exploit metadata")
                                confidence = "High"
                        for kw in keywords:
                            if len(kw) > 3 and kw in banner:
                                score += 12
                                reasons.append(f"Banner signature match: '{kw}'")

                if confidence != "Critical":
                    if score >= 60: confidence = "High"
                    elif score >= 30: confidence = "Medium"
                
                if score > 0:
                    exploit_suggestions.append({
                        'exploit': exploit_name,
                        'path': exploit_path,
                        'score': score,
                        'confidence': confidence,
                        'reasons': list(set(reasons))
                    })

        # 4. Display Logic
        recon_suggestions.sort(key=lambda x: x['score'], reverse=True)
        exploit_suggestions.sort(key=lambda x: x['score'], reverse=True)
        self._display_results(target_id, recon_suggestions, exploit_suggestions)

    def _display_results(self, target_id: str, recon: List[Dict], exploits: List[Dict]):
        print(f"\n[+] Smarter Suggestion Report for {target_id}")
        
        if recon:
            print("\n--- 🔎 RECOMMENDED RECONNAISSANCE MODULES ---")
            print(f"{'#':<3} {'Score':<7} {'Module Name':<40} {'Path'}")
            print("-" * 90)
            for idx, r in enumerate(recon[:5], 1):
                print(f"{idx:<3} {r['score']:<7} {r['name']:<40} {r['path']}")
                print(f"    -> {', '.join(r['reasons'])}")
            print("-" * 90)

        if exploits:
            print("\n--- 🚀 POTENTIAL EXPLOITS ---")
            print(f"{'#':<3} {'Confidence':<12} {'Score':<7} {'Exploit Name':<40} {'Path'}")
            print("-" * 90)
            for idx, sug in enumerate(exploits[:10], 1):
                print(f"{idx:<3} {sug['confidence']:<12} {sug['score']:<7} {sug['exploit']:<40} {sug['path']}")
                print(f"    -> Reasons: {', '.join(sug['reasons'])}")
            print("-" * 90)

        if not recon and not exploits:
            print(f"[-] No suggestions found for {target_id}. Try more manual discovery.")
