import json
import os
import sys
import re
from .database import DatabaseManagment, ExploitCache, exploitDetails, installation as framework_installation
from .auto_suggest import AutoSuggestCommand
from .ToStdOut import ToStdout


installation = framework_installation

# ASCII Art Banners for visual appeal
BANNER_DYNAMIC_VARS = r"""
 ____                                  _       _ _   
/ ___| _   _ _ __   ___ _ __ ___ _ __ | | ___ (_) |_ 
\___ \| | | | '_ \ / _ \ '__/ __| '_ \| |/ _ \| | __|
 ___) | |_| | |_) |  __/ |  \__ \ |_) | | (_) | | |_ 
|____/ \__,_| .__/ \___|_|  |___/ .__/|_|\___/|_|\__|
            |_|                 |_|                  

"""

BANNER_ALIASES = r"""
  _   _   _   _   _   _   _
 / \ / \ / \ / \ / \ / \ / \
( V | I | R | U | S | . | E )
 \_/ \_/ \_/ \_/ \_/ \_/ \_/

      _.-^^---....,,--
  _--                  --_
 <                        >)
 |                         |
  \._                   _./
"""

BANNER_SHELLS = r"""
           .-------------------------------.
         |  /-------------------------\  |
         | |                           | |
         | |                           | |
         | |       SuperSploit         | |
         | |                           | |
         | |                           | |
         | |                           | |
         | |                           | |
         |  \_________________________/  |
         |_______________________________|
       ,---\_____     []     _______/---,
      /         /______________\         \
     /_____________________________________\
     |                                     |
     |  _________________________________  |
     | | ||_|| ||_|| ||_|| ||_|| ||_|| ||_|| |
     | |_________________________________| |
     |_____________________________________|
"""

BANNER_TARGETS = r"""
 _____         _      _   _            
|_   _|_ _ _ _( )_ __| |_| |_ ___ _ _  
  | |/ _` | '_|/| / _|  _|  _/ -_) '_| 
  |_|\__,_|_|   |_\__|\__|\__\___|_|   
"""


class Show:
    @staticmethod
    def shells(args):
        ToStdout.write(BANNER_SHELLS + "\n")
        try:
            with open('/etc/shells') as file:
                ToStdout.write(file.read() + "\n")
        except FileNotFoundError:
            ToStdout.write("[-] Error: /etc/shells not found.\n")
        ToStdout.write("-" * 40 + "\n")  # Footer for consistency

    @staticmethod
    def show(data):
        import shlex # Import shlex here to avoid circular dependency with input_handling_engine
        args = shlex.split(data)

        if len(args) < 2:
            Show._show_dynamic_variables()
            return

        target = args[1].lower()

        if target in ["exploit", "details", "info"]:
            # Display metadata for the currently selected exploit
            ToStdout.write("\n" + "=" * 10 + " Selected Exploit Info " + "=" * 10 + "\n")
            # Pass the original data to exploitDetails for potential index/path parsing
            exploitDetails(data)
            ToStdout.write("=" * 43 + "\n") 
            return

        elif target == "aliases":
            Show._show_aliases()
            return

        elif target == "recon":
            Show._show_recon_details()
            return

        elif target in ["profile", "profiles", "personas"]:
            Show._show_profiles(args)
            return

        elif target in ["target", "targets"]:
            Show._show_targets(args)
            return

        # If the user provides specific variables like "show R_HOST L_PORT"
        else:
            Show._show_specific_variables(args[1:])

    @staticmethod
    def _show_dynamic_variables():
        """Displays all currently set dynamic variables with an ASCII art banner and categorized layout."""
        ToStdout.write(BANNER_DYNAMIC_VARS + "\n")
        db = DatabaseManagment.get()
        if not db:
            ToStdout.write("  No dynamic variables currently set.\n")
            ToStdout.write("-" * 40 + "\n")  # Footer
            return

        # Define categories and their associated keys
        categories = {
            "Target Information": ["R_HOST", "R_PORT", "R_MAC", "TARGET_OS", "TARGET_ARCH", "ACTIVE_PROFILE"],
            "Local Host Configuration": ["LHOST", "LPORT", "L_HOST", "L_PORT"],
            "Module Selection": ["EXPLOIT", "PAYLOAD", "RECON_NAME", "RECON_PATH"],
            "Payload Settings": [
                "XOR_KEY", "C2_URL", "STAGE2URL", "STAGE2_URL", "STAGE_TWO",
                "STAGE_KEY_FLAG", "MASTER_C2_KEY", "GENERATED_PAYLOAD"
            ],
            "Session Management": ["SESSION_ID", "VERBOSE_LOGGING", "DEV_MODE", "ACTIVE_WORKSPACE"],
            "Other Variables": [] # For any keys not explicitly categorized
        }

        # Populate categorized_data and find max_key_len for alignment
        categorized_data = {name: {} for name in categories}
        all_keys = list(db.keys())
        max_key_len = 0

        for key in all_keys:
            found = False
            for cat_name, cat_keys in categories.items():
                if key in cat_keys:
                    categorized_data[cat_name][key] = db[key]
                    max_key_len = max(max_key_len, len(key))
                    found = True
                    break
            if not found:
                categorized_data["Other Variables"][key] = db[key]
                max_key_len = max(max_key_len, len(key))
        
        # Print categorized output
        for cat_name, vars_dict in categorized_data.items():
            if vars_dict: # Only print category if it has variables
                ToStdout.write(f"\n  --- {cat_name} ---\n")
                for k, v in vars_dict.items():
                    display_value = str(v)
                    if len(display_value) > 70: # Truncate long values for readability
                        display_value = display_value[:67] + "..."
                    ToStdout.write(f"  {k:<{max_key_len}}: {display_value}\n")
        
        ToStdout.write("\n" + "-" * 40 + "\n")  # Footer

    @staticmethod
    def _show_aliases():
        """Displays all configured aliases with an ASCII art banner."""
        ToStdout.write(BANNER_ALIASES + "\n")
        aliases = DatabaseManagment.getAliases()
        if not aliases:
            ToStdout.write("  No aliases currently defined.\n")
        else:
            # Determine max key length for aligned output
            max_key_len = max(len(k) for k in aliases.items()) if aliases else 0
            for k, v in aliases.items():
                ToStdout.write(f"  {k:<{max_key_len}}: {v}\n")
        ToStdout.write("-" * 40 + "\n")  # Footer

    @staticmethod
    def _show_specific_variables(requested_vars):
        """Displays specific dynamic variables requested by the user."""
        ToStdout.write(BANNER_DYNAMIC_VARS + "\n")  # Re-use banner for specific variables
        db = DatabaseManagment.get()
        max_key_len = max(len(req) for req in requested_vars) if requested_vars else 0

        for req in requested_vars:
            if req in db:
                ToStdout.write(f"  {req:<{max_key_len}}: {db[req]}\n")
            else:
                ToStdout.write(f"  {req:<{max_key_len}}: [-] Variable '{req}' not set.\n")
        ToStdout.write("-" * 40 + "\n")  # Footer

    @staticmethod
    def _show_recon_details():
        """Displays metadata for the currently selected reconnaissance module."""
        db = DatabaseManagment.get()
        recon_path = db.get("RECON_PATH")
        if not recon_path:
            ToStdout.write("  [!] No recon module selected. Use 'use recon <index>'.\n")
            return

        # Reuse the core parser to load the recon module's YAML block
        ExploitCache._parse_details(recon_path)
        cache = ExploitCache.details

        if not cache or cache.get("status") != "ok":
            ToStdout.write("  [!] Error loading recon metadata.\n")
            return

        ToStdout.write("\n" + "=" * 10 + " Recon Module Details " + "=" * 10 + "\n")
        ToStdout.write(f"  Name:        {cache.get('name', 'Unknown')}\n")
        ToStdout.write(f"  Description: {cache.get('info', 'No description provided.')}\n")
        ToStdout.write("-" * 42 + "\n")

        # Filter out keys already shown in the header or internal status keys
        hidden_keys = ["name", "info", "status", "path", "dev_status"]
        for opt, value in cache.items():
            if opt not in hidden_keys and value not in ["N/A", "None", "", [], "known"]:
                ToStdout.write(f"  {opt.capitalize():<12}: {value}\n")
        ToStdout.write("-" * 42 + "\n")

    @staticmethod
    def _show_targets(args):
        """Displays discovered targets. 'show targets' lists all, 'show target [<ip>]' shows details."""
        targets_cache = DatabaseManagment.getTargets()
        
        if not targets_cache:
            ToStdout.write("\n  [!] No targets found in the cache. Run a recon module first.\n\n")
            return

        # Command is `show targets`
        if len(args) > 1 and args[1].lower() == "targets":
            ToStdout.write(BANNER_TARGETS + "\n")
            ToStdout.write(f"  {'IP Address':<18} {'Hostname':<25} {'OS Family':<20} {'Open Ports'}\n")
            ToStdout.write(f"  {'-'*18} {'-'*25} {'-'*20} {'-'*15}\n")

            for ip, data in sorted(targets_cache.items()):
                hostname = data.get('hostname', 'N/A')
                os_family = data.get('os_family', 'N/A')
                port_count = len(data.get('services', data.get('ports', data.get('open_ports', []))))
                
                ToStdout.write(f"  {ip:<18} {hostname:<25} {os_family:<20} {port_count}\n")
            ToStdout.write("-" * 80 + "\n")
            return

        # Command is `show target [<ip>]`
        if len(args) > 1 and args[1].lower() == "target":
            target_ip = None
            if len(args) > 2:
                target_ip = args[2]  # User provided an IP
            else:
                # No IP provided, use R_HOST from the database
                db = DatabaseManagment.get()
                target_ip = db.get("R_HOST")
                if not target_ip:
                    ToStdout.write("\n  [!] No target specified. Set R_HOST or use 'show target <ip>'.\n\n")
                    return

            if target_ip in targets_cache:
                # Call the new smart render function
                Show._render_smart_target_view(target_ip, targets_cache)
            else:
                ToStdout.write(f"\n  [!] Target '{target_ip}' not found in cache.\n\n")
            return

    @staticmethod
    def _get_successful_exploits_for_ip(ip):
        """Parses the activity log to find successful exploits against a given IP."""
        log_path = os.path.join(DatabaseManagment.getInstall(), ".data", ".logs", "activity.log")
        successful_exploits = []
        if not os.path.exists(log_path):
            return successful_exploits

        try:
            with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    # Example log: [2026-07-04 12:30:00] - Session: abcdef12 - Module: exploits/linux/cve_xxxx.py - Status: Success - Target: 192.168.1.101 - Args: {}
                    if f"Target: {ip}" in line and "Status: Success" in line and "Module: exploits/" in line:
                        parts = line.split(" - ")
                        for part in parts:
                            if part.startswith("Module:"):
                                module_path = part.replace("Module: ", "").strip()
                                exploit_name = os.path.basename(module_path)
                                if exploit_name not in successful_exploits:
                                    successful_exploits.append(exploit_name)
        except Exception:
            # Silently fail if log parsing has issues
            pass
        return successful_exploits

    @staticmethod
    def _render_smart_target_view(ip, targets_cache):
        """Renders a comprehensive, stylish view of a single target's data, including suggestions."""
        data = targets_cache[ip]
        display_data = data.copy() # Start with discovered data

        # --- Fetch and merge profile data ---
        profile_data = None
        profiles_db = DatabaseManagment.getProfiles()
        for p_name, p_info in profiles_db.items():
            # Match by IP or by hostname (if hostname is available and matches profile name)
            if p_info.get("ip") == ip or (display_data.get("hostname") and p_info.get("name") == display_data["hostname"]):
                profile_data = p_info
                break
        
        if profile_data:
            ToStdout.write(f"\n  [+] Correlated with Persona Profile: {profile_data.get('name', 'N/A')}\n")
            # Overlay/augment display_data with profile info, prioritizing profile data if more specific
            display_data['hostname'] = profile_data.get('name', display_data.get('hostname', 'N/A'))
            display_data['mac_address'] = profile_data.get('mac', profile_data.get('mac_address', display_data.get('mac_address', 'N/A')))
            display_data['vendor'] = profile_data.get('vendor', 'N/A') # Keep N/A if not in profile
            
            # Use the new 'os', 'arch', 'kernel' keys from database.py
            display_data['os'] = profile_data.get('os', display_data.get('os', 'N/A'))
            display_data['arch'] = profile_data.get('arch', display_data.get('arch', 'N/A'))
            display_data['kernel'] = profile_data.get('kernel', display_data.get('kernel', 'N/A'))

            # Explicitly set brand, device, security_patch from profile
            display_data['name'] = profile_data.get('name', display_data.get('name', 'N/A')) # Ensure name is merged
            display_data['security_patch'] = profile_data.get('security_patch', display_data.get('security_patch', 'N/A'))
            display_data['brand'] = profile_data.get('brand', display_data.get('brand', 'N/A'))
            display_data['device'] = profile_data.get('device', display_data.get('device', 'N/A'))
            display_data['services'] = profile_data.get('services', display_data.get('services', {})) # Prioritize profile services
            
            # Merge CVEs (ensure unique)
            profile_cves = profile_data.get('cves', [])
            if isinstance(profile_cves, str): # Handle cases where CVEs might be a single string
                profile_cves = [c.strip() for c in profile_cves.split(',') if c.strip()]
            current_cves = display_data.get('cves', [])
            display_data['cves'] = sorted(list(set(current_cves + profile_cves)))

            # Add profile-specific info
            if profile_data.get('research'):
                display_data['research'] = profile_data['research']
            if profile_data.get('environment'):
                display_data['environment'] = profile_data['environment']
            if profile_data.get('raw_content'):
                display_data['raw_content'] = profile_data['raw_content']
            if profile_data.get('attack_plan'):
                display_data['attack_plan'] = profile_data['attack_plan']
            if profile_data.get('framework_notes'):
                display_data['framework_notes'] = profile_data['framework_notes']

        # Use the profile's name for the dossier title if available
        dossier_name = display_data.get('name', ip)
        ToStdout.write("\n" + "=" * 15 + f" Target Dossier: {dossier_name} ({ip}) " + "=" * 15 + "\n")
        
        # --- Basic Info ---
        ToStdout.write(f"  {'Hostname:':<15} {display_data.get('hostname', 'N/A')}\n")
        ToStdout.write(f"  {'MAC Address:':<15} {display_data.get('mac_address', display_data.get('mac', 'N/A'))}\n")
        ToStdout.write(f"  {'Vendor:':<15} {display_data.get('vendor', 'N/A')}\n")
        ToStdout.write(f"  {'Brand:':<15} {display_data.get('brand', 'N/A')}\n")
        ToStdout.write(f"  {'Device:':<15} {display_data.get('device', 'N/A')}\n")
        ToStdout.write("-" * 50 + "\n")
        
        # --- System Info ---
        os_info = display_data.get('os', 'N/A') # Use 'os' key
        kernel_version = display_data.get('kernel', 'N/A') # Use 'kernel' key
        architecture = display_data.get('arch', 'N/A') # Use 'arch' key

        # Adjust OS Family display
        if 'android' in os_info.lower():
            os_info = 'Android/Linux'
        
        # Adjust Architecture display
        if architecture.lower() == 'aarch64':
            architecture = 'Arm64'

        ToStdout.write(f"  {'OS Family:':<15} {os_info}\n")
        ToStdout.write(f"  {'Architecture:':<15} {architecture}\n")
        ToStdout.write(f"  {'Kernel:':<15} {kernel_version}\n")
        ToStdout.write(f"  {'Uptime:':<15} {display_data.get('uptime', 'N/A')}\n")
        if display_data.get('security_patch'):
            ToStdout.write(f"  {'Security Patch:':<15} {display_data.get('security_patch')}\n")
        ToStdout.write("-" * 50 + "\n")

        # --- Services & Banners ---
        services = display_data.get('services', {})
        if services:
            ToStdout.write("  Services & Banners:\n")
            ToStdout.write(f"    {'PORT':<8} {'SERVICE':<20} {'BANNER'}\n")
            ToStdout.write(f"    {'----':<8} {'-------':<20} {'------'}\n")
            for port, s_info in sorted(services.items(), key=lambda item: int(item[0])):
                service_name = s_info.get('service', 'unknown')
                banner = s_info.get('banner', '')
                if len(banner) > 45:
                    banner = banner[:42] + "..."
                ToStdout.write(f"    {port:<8} {service_name:<20} {banner}\n")
        else:
            # If no structured services, try to get a simple list of ports
            # Prioritize ports from the profile if available, otherwise from recon
            profile_ports = display_data.get('ports', [])
            recon_ports = display_data.get('open_ports', [])
            
            if profile_ports:
                sorted_ports = sorted([int(p) for p in profile_ports if str(p).isdigit()])
            elif recon_ports:
                port_list = [p.get('port') if isinstance(p, dict) else p for p in recon_ports]
                sorted_ports = sorted([int(p) for p in port_list if str(p).isdigit()])
            else:
                sorted_ports = []

            if sorted_ports:
                ToStdout.write(f"  {'Open Ports:':<15} {', '.join(map(str, sorted_ports))}\n")
        ToStdout.write("-" * 50 + "\n")

        # --- Suggested Exploits ---
        suggestions = AutoSuggestCommand.suggest_for_ip(ip, {ip: display_data}, silent=True)

        if suggestions:
            ToStdout.write("  Suggested Exploits (Top 5):\n")
            ToStdout.write(f"    {'CONFIDENCE':<12} {'EXPLOIT':<35} {'REASON'}\n")
            ToStdout.write(f"    {'----------':<12} {'-------':<35} {'------'}\n")
            for suggestion in suggestions[:5]:
                confidence_str = suggestion['confidence']
                exploit_name = suggestion['exploit']
                reason = suggestion.get('reason', ', '.join(suggestion.get('reasons', [])))
                
                # Colorize confidence
                if confidence_str == "Critical":
                    color_code = "\033[91m"  # Red
                elif confidence_str == "High":
                    color_code = "\033[93m"  # Yellow
                else:
                    color_code = "\033[94m"  # Blue
                
                ToStdout.write(f"    {color_code}{confidence_str:<12}\033[0m {exploit_name:<35} {reason}\n")

        ToStdout.write("-" * 50 + "\n")

        # --- CVE Handling ---
        all_cves = display_data.get('cves', [])
        kev_matches = [cve for cve in all_cves if cve.startswith('[KEV MATCH]')]
        
        if kev_matches:
            ToStdout.write("  Kev Matches:\n")
            for cve in kev_matches:
                ToStdout.write(f"    {cve}\n")
            ToStdout.write("-" * 50 + "\n")
        
        # --- Research Notes & Critical Findings ---
        research_notes = display_data.get('research', [])
        
        # Filter out the critical findings header and process them separately
        general_research_items = []
        critical_findings_items = []
        in_critical_findings_block = False

        for note in research_notes:
            # Filter out "Attack Plan" and "Framework Notes"
            if re.match(r'^\s*#+\s*Attack Plan', note, re.IGNORECASE) or \
               re.match(r'^\s*#+\s*Framework Notes', note, re.IGNORECASE):
                in_critical_findings_block = False # Reset in case it was true
                continue

            if re.match(r'^\s*#+\s*Critical Findings & LPE Paths', note, re.IGNORECASE):
                in_critical_findings_block = True
                continue # Skip the header itself
            
            if in_critical_findings_block:
                critical_findings_items.append(note)
            else:
                # Only add non-KEV CVEs to general research if they are not part of critical findings
                if not note.startswith('[KEV MATCH]'): # Ensure we don't duplicate KEV matches here
                    general_research_items.append(note)

        # Add non-KEV CVEs to general research items (if they weren't already added from profile's research list)
        other_cves_from_profile = [cve for cve in all_cves if not cve.startswith('[KEV MATCH]')]
        # Ensure no duplicates if CVEs are already in general_research_items from profile's research list
        for cve in other_cves_from_profile:
            if cve not in general_research_items:
                general_research_items.append(cve)
        
        if general_research_items or critical_findings_items:
            ToStdout.write("  Research:\n")
            
            # Print general research items first
            for item in general_research_items:
                # Only print if not empty or just whitespace
                if item.strip():
                    ToStdout.write(f"    {item.strip()}\n")

            if critical_findings_items:
                ToStdout.write("     Critical Findings & LPE Paths:\n")
                for note in critical_findings_items:
                    cleaned_note = note
                    
                    # Apply specific stripping rules
                    cleaned_note = re.sub(r'is world-readable.*', '', cleaned_note)
                    cleaned_note = re.sub(r'This can be used to defeat KASLR and find kernel symbols for exploit development\.', '', cleaned_note)
                    cleaned_note = re.sub(r'a use-after-free in the Binder driver.*', '', cleaned_note)
                    cleaned_note = re.sub(r'This is a high-priority target for local privilege escalation\.', '', cleaned_note)
                    cleaned_note = re.sub(r'a use-after-free in the vold \(volume manager daemon\).*', '', cleaned_note)
                    cleaned_note = re.sub(r'This can be used to gain system-level privileges\.', '', cleaned_note)
                    cleaned_note = re.sub(r'are all World-Writable.*', '', cleaned_note)
                    cleaned_note = re.sub(r'This provides a direct path for Binder-based UAF and memory injection attacks\.', '', cleaned_note)
                    cleaned_note = re.sub(r'are mounted as read-write.*', '', cleaned_note)
                    cleaned_note = re.sub(r'which could allow for tampering with device-specific data or configuration\.', '', cleaned_note)
                    
                    # Handle numbered/bolded lines and bullet points with precise indentation
                    match_numbered_bold = re.match(r'^(\s*\d+\.\s*\*\*[^:]+?\*\*):\s*(.+)', cleaned_note)
                    match_bullet_point = re.match(r'^(\s*\*\s*.+)', cleaned_note)

                    if match_numbered_bold:
                        bullet_part = match_numbered_bold.group(1).strip()
                        desc_part = match_numbered_bold.group(2).strip()
                        ToStdout.write(f"   {bullet_part}:\n")
                        # Check if the description part starts with a bullet point and indent accordingly
                        if desc_part.startswith('*'):
                            ToStdout.write(f"       {desc_part}\n") # Indent by 7 spaces
                        else:
                            ToStdout.write(f"     {desc_part}\n") # Indent by 5 spaces for general description
                    elif match_bullet_point:
                        ToStdout.write(f"       {cleaned_note.strip()}\n")
                    else:
                        # Fallback for any other lines within critical findings
                        if cleaned_note.strip(): # Only print if not empty
                            ToStdout.write(f"     {cleaned_note.strip()}\n")
            ToStdout.write("-" * 50 + "\n")

        ToStdout.write("=" * 50 + "\n")

    @staticmethod
    def _show_profiles(args):
        """Displays identified persona profiles. 'show profile' shows active, 'show profiles' shows all."""
        target = args[1].lower()
        profiles_db = DatabaseManagment.getProfiles()
        db = DatabaseManagment.get()
        active_profile_name = db.get("ACTIVE_PROFILE")

        if target == "profile":
            ToStdout.write("\n" + "=" * 10 + " Active Persona Profile " + "=" * 10 + "\n")
            if not active_profile_name:
                ToStdout.write("  [!] No active profile set. Use 'use profile <index>'.\n")
            elif active_profile_name not in profiles_db:
                ToStdout.write(f"  [!] Active profile '{active_profile_name}' no longer exists.\n")
            else:
                p = profiles_db[active_profile_name]
                Show._render_single_profile(p, is_active=True)
            ToStdout.write("=" * 44 + "\n")
        else: # profiles or personas
            ToStdout.write("\n" + "=" * 15 + " Persona Profiles " + "=" * 15 + "\n")
            profiles = list(profiles_db.values())
            if not profiles:
                ToStdout.write("  No profiles currently in the session database.\n")
            else:
                for p in profiles:
                    name = p.get('name', 'N/A')
                    is_active = (name == active_profile_name)
                    Show._render_single_profile(p, is_active=is_active)
            ToStdout.write("=" * 48 + "\n")

    @staticmethod
    def _render_markdown(text):
        """Simple regex-based terminal markdown renderer for clean CLI display."""
        import re
        # 1. Bold: **text** -> \033[1mtext\033[0m
        text = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', text)
        
        # 2. List items: - text or * text -> • text
        text = re.sub(r'^(\s*)[\-\*]\s+', r'\1• ', text, flags=re.MULTILINE)
        
        # 3. Headers: # Header -> Bold + Underlined
        text = re.sub(r'^#+\s+(.*)', r'\033[1;4m\1\033[0m', text, flags=re.MULTILINE)
        
        return text

    @staticmethod
    def _render_single_profile(p, is_active=False):
        """Helper to render a single profile's data, prioritizing raw content layout."""
        prefix = "[ACTIVE] " if is_active else ""
        ToStdout.write(f"  {prefix}Name:        {p.get('name', 'N/A')}\n")
        
        # If the profile has raw content (e.g. from a Markdown import), render it nicely
        if p.get('raw_content'):
            rendered = Show._render_markdown(p.get('raw_content'))
            ToStdout.write(rendered + "\n")
            ToStdout.write("-" * 48 + "\n")
            return

        if p.get('ip'):
            ToStdout.write(f"  IP:          {p.get('ip')}\n")
        
        # Compact view for the list if needed, but keeping original structure for now
        ToStdout.write(f"  Phone:       {p.get('phone', 'N/A')}\n")
        ToStdout.write(f"  Email:       {p.get('email', 'N/A')}\n")
        ToStdout.write(f"  Address:     {p.get('address', 'N/A')}\n")
        ToStdout.write(f"  Geo:         {p.get('geolocation', 'N/A')}\n")
        
        if p.get('os') or p.get('arch'):
            ToStdout.write(f"  System:      {p.get('os', 'N/A')} ({p.get('arch', 'N/A')})\n")
        
        social_medias = p.get('social_medias', [])
        if social_medias:
            ToStdout.write(f"  Socials:     {', '.join(social_medias)}\n")
        
        research = p.get('research', [])
        if research:
            ToStdout.write(f"  Research:\n")
            for note in research:
                ToStdout.write(f"    - {note}\n")
        
        ToStdout.write("-" * 48 + "\n")