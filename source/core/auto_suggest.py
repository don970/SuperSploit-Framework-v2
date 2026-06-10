from typing import List, Dict, Any, Optional
import re
import difflib

class AutoSuggestCommand:
    def __init__(self, exploit_cache):
        """
        Initializes the auto_suggest command.
        Expects exploit_cache to have an 'all_exploits' attribute and 'metadata_index'.
        """
        self.exploit_cache = exploit_cache

    def execute(self, target_ip: str, target_info: Dict[str, Any]):
        """
        Analyzes target metadata and correlates with available exploits using advanced heuristics.
        """
        print(f"[*] Executing Deep Analysis for {target_ip}...")
        print(f"[DEBUG] Considering {len(self.exploit_cache.metadata_index)} exploits.")
        # for p in self.exploit_cache.metadata_index.keys():
        #     print(f"[DEBUG] Exploit Path: {p}")
        
        # 1. Normalize target data
        services = target_info.get('services', {})
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
        target_cves = target_info.get('cves', []) # Support for CVEs discovered by vuln scanners
        target_env = target_info.get('environment', []) # e.g. ["/dev/binder", "selinux_enforcing"]

        if not services and not target_os and not target_kernel:
            print("[-] Insufficient target data for deep analysis. Run more recon modules.")
            return

        suggestions = []
        
        for exploit_path, meta in self.exploit_cache.metadata_index.items():
            score = 0
            reasons = []
            confidence = "Low"
            
            # --- PRE-QUALIFICATION (Hard Filters) ---
            exploit_os = str(meta.get('os', '')).lower()
            if exploit_os and target_os:
                if not (exploit_os in target_os or target_os in exploit_os):
                    print(f"[DEBUG] Skipping {exploit_path} due to OS mismatch (Exploit: {exploit_os}, Target: {target_os})")
                    continue # Hard OS mismatch

            exploit_arch = str(meta.get('arch', '')).lower()
            if exploit_arch and target_arch:
                if not (exploit_arch in target_arch or target_arch in exploit_arch):
                    print(f"[DEBUG] Skipping {exploit_path} due to Arch mismatch (Exploit: {exploit_arch}, Target: {target_arch})")
                    continue # Hard Arch mismatch

            # --- HEURISTIC MATCHING ---
            exploit_name = meta.get('name', 'Unknown Exploit')
            exploit_cve = str(meta.get('cve', '')).upper()
            exploit_kernel_vers = meta.get('kernel', [])
            if isinstance(exploit_kernel_vers, str):
                exploit_kernel_vers = [k.strip() for k in exploit_kernel_vers.split(',')]
            
            keywords = [str(k).lower() for k in meta.get('keywords', [])]
            requirements = meta.get('requirements', [])

            # 1. Direct CVE Correlation (Highest Weight)
            if exploit_cve != "N/A" and exploit_cve in [c.upper() for c in target_cves]:
                score += 50
                reasons.append(f"Direct CVE Match: {exploit_cve}")
                confidence = "Critical"

            # 2. Kernel & OS (Strong Weights)
            if exploit_os and target_os:
                score += 10
                reasons.append(f"OS Verified: {exploit_os}")

            if target_kernel and exploit_kernel_vers:
                matched_kernel = False
                for v in exploit_kernel_vers:
                    if v.lower() in target_kernel:
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

            # 3. Environmental Requirements Matching
            if requirements and target_env:
                matched_reqs = 0
                for req in requirements:
                    if req in target_env:
                        matched_reqs += 1
                if matched_reqs > 0:
                    score += (matched_reqs * 15)
                    reasons.append(f"Matched {matched_reqs} environmental prerequisites")

            # 4. Advanced Port & Banner Matching (Fuzzy)
            for port_num, service_info in services.items():
                service_name = str(service_info.get('service', '')).lower()
                banner = str(service_info.get('banner', '')).lower()
                
                if port_num in keywords:
                    score += 5
                    reasons.append(f"Port {port_num} explicitly targeted")
                
                if service_name != 'unknown':
                    # Fuzzy match service name against keywords
                    matches = difflib.get_close_matches(service_name, keywords, n=1, cutoff=0.8)
                    if matches:
                        score += 10
                        reasons.append(f"Service match: {service_name} (Fuzzy match: {matches[0]})")
                    elif any(service_name in kw for kw in keywords):
                        score += 8
                        reasons.append(f"Service name substring match: {service_name}")
                
                if banner != 'unknown':
                    # Extract version strings from banner for better correlation
                    version_match = re.search(r'(\d+\.\d+\.\d+|\d+\.\d+)', banner)
                    if version_match:
                        ver = version_match.group(1)
                        if any(ver in kw for kw in keywords) or ver in meta.get('desc', ''):
                            score += 20
                            reasons.append(f"Banner version {ver} matches exploit metadata")
                            confidence = "High"

                    # Generic banner keyword search
                    for kw in keywords:
                        if len(kw) > 3 and kw in banner:
                            score += 12
                            reasons.append(f"Banner signature match: '{kw}'")

            # 5. Semantic Correlation (Description & Category)
            cat = str(meta.get('cat', '')).lower()
            if target_os in cat or (target_os == 'android' and 'android' in cat):
                score += 5

            # --- Final Confidence Adjustment ---
            if score >= 60:
                confidence = "High"
            elif score >= 30:
                confidence = "Medium"
            
            if score > 0:
                print(f"[DEBUG] Exploit: {exploit_name}, Score: {score}, Reasons: {reasons}")
                suggestions.append({
                    'exploit': exploit_name,
                    'path': exploit_path,
                    'score': score,
                    'confidence': confidence,
                    'reasons': list(set(reasons))
                })
        
        # Sort and Display
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        self._display_results(target_ip, suggestions)

    def _display_results(self, target_ip: str, suggestions: List[Dict[str, Any]]):
        if not suggestions:
            print(f"[-] No high-confidence matches found for {target_ip}.")
            return
            
        print(f"\n[+] Deep Suggestion Report for {target_ip}")
        print("=" * 90)
        print(f"{'#':<3} {'Confidence':<12} {'Score':<7} {'Exploit Name':<40} {'Path'}")
        print("-" * 90)
        
        for idx, sug in enumerate(suggestions[:15], 1):
            color_code = "[!]" if sug['confidence'] in ["Critical", "High"] else "[*]"
            print(f"{idx:<3} {sug['confidence']:<12} {sug['score']:<7} {sug['exploit']:<40} {sug['path']}")
            print(f"    -> Reasons: {', '.join(sug['reasons'])}")
            if idx < len(suggestions[:15]): print("-" * 90)
        
        print("=" * 90)
        if len(suggestions) > 15:
            print(f"[*] Total suggestions: {len(suggestions)}. Only showing top 15 results.")
