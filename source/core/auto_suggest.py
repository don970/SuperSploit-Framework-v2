from typing import List, Dict, Any, Optional
import re
import difflib
from datetime import datetime
from .database import DatabaseManagment, ExploitCache

class AutoSuggestCommand:
    def __init__(self, exploit_cache):
        """
        Initializes the auto_suggest command.
        Expects exploit_cache to have an 'all_exploits' attribute and 'metadata_index'.
        """
        self.exploit_cache = exploit_cache

    def execute(self, target_id: str, target_info: Dict[str, Any], silent: bool = False):
        """
        Analyzes target metadata and correlates with available exploits AND recon modules.
        """
        if not silent:
            print(f"[*] Executing Smarter Analysis for {target_id}...")
        
        # 0. Identify Target Format
        is_ip = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_id)
        is_mac = re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", target_id)
        is_domain = "." in target_id and not is_ip
        is_name = " " in target_id or (not is_ip and not is_mac and not is_domain)

        # target_info already contains merged profile data from show.py
        profile_data = target_info 

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

        target_os = str(target_info.get('os', target_info.get('os_family', ''))).lower()
        target_kernel = str(target_info.get('kernel', target_info.get('kernel_version', ''))).lower()
        target_arch = str(target_info.get('arch', target_info.get('architecture', ''))).lower()
        
        target_cves = target_info.get('cves', [])
        # Ensure CVEs are unique and uppercase for consistent matching, handling potential nested lists
        # target_cves is already merged from profile in show.py
        target_cves = list(set([c.upper() for c in target_cves if isinstance(c, str)]))
        
        target_device = str(target_info.get('device', '')).lower()
        target_brand = str(target_info.get('brand', '')).lower()
        target_security_patch_str = str(target_info.get('security_patch', ''))
        target_security_patch = None
        if target_security_patch_str and target_security_patch_str != 'n/a':
            try:
                target_security_patch = datetime.strptime(target_security_patch_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        target_env = target_info.get('environment', [])
        # target_env is already merged from profile in show.py
        target_env = list(set([e for e in target_env if isinstance(e, str)]))

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
                
                exploit_device_models = [str(d).lower() for d in meta.get('device_models', [])]
                exploit_brands = [str(b).lower() for b in meta.get('brands', [])]
                exploit_max_security_patch_str = str(meta.get('max_security_patch', ''))
                exploit_max_security_patch = None
                if exploit_max_security_patch_str:
                    try:
                        exploit_max_security_patch = datetime.strptime(exploit_max_security_patch_str, '%Y-%m-%d').date()
                    except ValueError:
                        pass

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

                # --- New: Device/Brand Specificity ---
                if target_device and exploit_device_models:
                    if target_device in exploit_device_models:
                        score += 15
                        reasons.append(f"Device Model Match: {target_device}")
                        if confidence not in ["Critical", "High"]:
                            confidence = "High"
                if target_brand and exploit_brands:
                    if target_brand in exploit_brands:
                        score += 10
                        reasons.append(f"Brand Match: {target_brand}")
                        if confidence not in ["Critical", "High"]:
                            confidence = "High"

                # --- New: Security Patch Level Correlation ---
                if target_security_patch and exploit_max_security_patch:
                    if target_security_patch <= exploit_max_security_patch:
                        score += 20
                        reasons.append(f"Security Patch Level: Target ({target_security_patch_str}) <= Exploit Max ({exploit_max_security_patch_str})")
                        if confidence not in ["Critical", "High"]:
                            confidence = "High"
                    else:
                        # If target's patch is newer than exploit's max, it's likely patched.
                        # Do not add score, but don't filter out entirely unless explicitly required.
                        pass

                # --- Existing: Keywords from Profile Research/Footprint ---
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

                # --- Existing: Service Banners & Version Strings ---
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
                    
                    # --- New: Explicit Vulnerable Service Tag ---
                    # Assuming "Vulnerable Service" from markdown profile is parsed into service_name or banner
                    if "vulnerable service" in service_name or "vulnerable service" in banner:
                        if port_num in keywords or any(kw in service_name for kw in keywords) or any(kw in banner for kw in keywords):
                            score += 25
                            reasons.append(f"Explicitly Vulnerable Service on Port {port_num}")
                            if confidence not in ["Critical", "High"]:
                                confidence = "High"

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

        if silent:
            # The show command needs a simplified reason. Let's join them.
            for sug in exploit_suggestions:
                sug['reason'] = ', '.join(sug.get('reasons', []))
            return exploit_suggestions

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

    @staticmethod
    def suggest_for_ip(ip: str, targets_cache: Dict[str, Any], silent: bool = False) -> Optional[List[Dict]]:
        """
        Static method to get exploit suggestions for a specific IP.
        If silent is False, it prints the results.
        If silent is True, it returns the exploit suggestions list.
        """
        if ip not in targets_cache:
            return None

        target_info = targets_cache[ip]
        
        exploit_cache = ExploitCache
        if not exploit_cache.metadata_index:
            exploit_cache.update()

        suggester = AutoSuggestCommand(exploit_cache)
        return suggester.execute(ip, target_info, silent=silent)
