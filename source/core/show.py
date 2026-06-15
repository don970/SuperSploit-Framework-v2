import json
import os
import sys
from .database import DatabaseManagment, ExploitCache, exploitDetails, installation as framework_installation
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

        # If the user provides specific variables like "show R_HOST L_PORT"
        else:
            Show._show_specific_variables(args[1:])

    @staticmethod
    def _show_dynamic_variables():
        """Displays all currently set dynamic variables with an ASCII art banner."""
        ToStdout.write(BANNER_DYNAMIC_VARS + "\n")
        db = DatabaseManagment.get()
        if not db:
            ToStdout.write("  No dynamic variables currently set.\n")
        else:
            # Determine max key length for aligned output
            max_key_len = max(len(k) for k in db.keys()) if db else 0
            for k, v in db.items():
                if len(str(v)) > 100:
                    ToStdout.write(f"  {k:<{max_key_len}}: {str(v)[:47]}...\n")
                else:
                    ToStdout.write(f"  {k:<{max_key_len}}: {v}\n")
        ToStdout.write("-" * 40 + "\n")  # Footer

    @staticmethod
    def _show_aliases():
        """Displays all configured aliases with an ASCII art banner."""
        ToStdout.write(BANNER_ALIASES + "\n")
        aliases = DatabaseManagment.getAliases()
        if not aliases:
            ToStdout.write("  No aliases currently defined.\n")
        else:
            # Determine max key length for aligned output
            max_key_len = max(len(k) for k in aliases.keys()) if aliases else 0
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