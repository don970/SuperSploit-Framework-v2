import sys
import os
import urllib.parse

# Dynamically append the framework's source directory to sys.path
# so the module can interact with the core framework when loaded.
_scanner_dir = os.path.dirname(os.path.abspath(__file__))
_framework_root = os.path.abspath(os.path.join(_scanner_dir, "..", ".."))
_source_dir = os.path.join(_framework_root, "source")
if _source_dir not in sys.path:
    sys.path.append(_source_dir)

try:
    from core.database import DatabaseManagment
except ImportError:
    DatabaseManagment = None

#!#!#!
name: "Native Email OSINT"
description: "Identify social media profiles, leaked credentials, and mentions across public data repositories via email."
category: "OSINT"
author: "Donald Ford"
keywords: '["email", "osint", "recon", "leaks", "dorking"]'
#!#!#!

def google_dork(email):
    """
    Generates Google Dork URLs specifically targeted at email address discovery.
    """
    dorks = [
        # Exact matches and general mentions
        f'"{email}"',
        f'intitle:"{email}"',
        
        # Leaked Data & Config Files
        f'"{email}" filetype:pdf OR filetype:xlsx OR filetype:docx',
        f'"{email}" ext:txt OR ext:log OR ext:sql OR ext:env',
        f'"{email}" intext:"password" OR intext:"pwd" OR intext:"login"',
        
        # Paste Sites
        f'"{email}" (site:pastebin.com OR site:ghostbin.com OR site:controlc.com OR site:pastie.io OR site:hastebin.com OR site:rentry.co OR site:0bin.net OR site:privatebin.net OR site:justpaste.it OR site:paste.ee)',
        
        # Professional & Social Media
        f'"{email}" site:linkedin.com',
        f'"{email}" site:github.com OR site:gitlab.com OR site:bitbucket.org',
        f'"{email}" site:facebook.com OR site:instagram.com OR site:twitter.com OR site:x.com',
        f'"{email}" site:reddit.com OR site:quora.com OR site:medium.com',
        
        # Breach hints
        f'"{email}" site:leak-lookup.com OR site:breachdirectory.org OR site:intelx.io',
        
        # Public Directories
        f'inurl:contact "{email}"',
        f'inurl:staff OR inurl:employees "{email}"'
    ]
    return dorks

def Start(args=None):
    """
    Main entry point for the Email OSINT module.
    """
    email_input = ""
    if args:
        email_input = args[0]
    elif DatabaseManagment:
        db = DatabaseManagment.get()
        email_input = db.get("R_HOST", "")

    # Handle cases where R_HOST is a list
    if isinstance(email_input, list) and email_input:
        email_input = email_input[0]

    # Sanitize input
    email_input = str(email_input).strip()

    if not email_input or "@" not in email_input:
        print("[-] Error: A valid email address is required.")
        print("[*] Usage: set target <user@example.com>  OR  run <email>")
        return

    print(f"[*] Initiating OSINT analysis for email: {email_input}\n")

    try:
        # 1. Verification Logic
        # This module uses the dorking method; external API verification could be added here.
        user_part, domain_part = email_input.split('@')
        
        print(f"[+] Initial Analysis")
        print(f"    - Target User:   {user_part}")
        print(f"    - Domain:        {domain_part}")
        
        # 2. Generate Dorks
        print(f"\n[*] Generating Email Footprints (Copy into browser):")
        dorks = google_dork(email_input)
        for d in dorks:
            # Standard plus-encoding for search queries
            query = urllib.parse.quote_plus(d)
            print(f"    - {d}")
            print(f"      URL: https://www.google.com/search?q={query}")

    except Exception as e:
        print(f"[-] Analysis Error: {e}")

if __name__ == "__main__":
    Start(sys.argv[1:])