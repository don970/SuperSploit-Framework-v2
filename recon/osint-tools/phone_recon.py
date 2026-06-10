import sys
import os
import urllib.parse
import threading

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

try:
    from .background_check import ProfileDB, PersonProfile
except ImportError:
    ProfileDB = None

#!#!#!
name: "Native Phone OSINT"
description: "Advanced phone number information gathering. Replicates phoneinfoga capabilities natively using Python."
category: "OSINT"
author: "Donald Ford"
keywords: '["phone", "osint", "recon", "dorking"]'
#!#!#!

def google_dork(phone_number):
    """
    Generates Google Dork URLs to find the phone number in various formats 
    across leaked documents, logs, and directory listings.
    """
    dorks = [
        f'"{phone_number}"',
        f'"{phone_number}" filetype:pdf OR filetype:xlsx OR filetype:docx',
        f'"{phone_number}" ext:txt OR ext:log OR ext:sql OR ext:env',
        f'intitle:"index of" "{phone_number}"',
        f'inurl:contact "{phone_number}"',
        # Background Check & Public Records
        f'"{phone_number}" site:whitepages.com',
        f'"{phone_number}" site:spokeo.com',
        f'"{phone_number}" site:truepeoplesearch.com',
        f'"{phone_number}" site:peekyou.com',
        f'"{phone_number}" intitle:court OR intitle:arrest OR intitle:criminal',
        f'"{phone_number}" filetype:pdf (intext:judgment OR intext:liens OR intext:bankruptcy)',
        f'inurl:staff OR inurl:employees "{phone_number}"',
        f'intext:"{phone_number}" (inurl:admin OR inurl:setup)', # General admin/setup pages
        # Top 10 Pastebin-style sites for leaked data
        f'"{phone_number}" (site:pastebin.com OR site:ghostbin.com OR site:controlc.com OR site:pastie.io OR site:hastebin.com OR site:rentry.co OR site:0bin.net OR site:privatebin.net OR site:justpaste.it OR site:paste.ee)',
        # Social Media Top 50
        f'"{phone_number}" site:facebook.com',
        f'"{phone_number}" site:instagram.com',
        f'"{phone_number}" site:twitter.com',
        f'"{phone_number}" site:x.com',
        f'"{phone_number}" site:linkedin.com',
        f'"{phone_number}" site:youtube.com',
        f'"{phone_number}" site:reddit.com',
        f'"{phone_number}" site:tiktok.com',
        f'"{phone_number}" site:pinterest.com',
        f'"{phone_number}" site:snapchat.com',
        f'"{phone_number}" site:whatsapp.com',
        f'"{phone_number}" site:telegram.org',
        f'"{phone_number}" site:discord.com',
        f'"{phone_number}" site:tumblr.com',
        f'"{phone_number}" site:flickr.com',
        f'"{phone_number}" site:quora.com',
        f'"{phone_number}" site:medium.com',
        f'"{phone_number}" site:vk.com',
        f'"{phone_number}" site:ok.ru',
        f'"{phone_number}" site:weibo.com',
        f'"{phone_number}" site:twitch.tv',
        f'"{phone_number}" site:github.com',
        f'"{phone_number}" site:gitlab.com',
        f'"{phone_number}" site:stackoverflow.com',
        f'"{phone_number}" site:vimeo.com',
        f'"{phone_number}" site:behance.net',
        f'"{phone_number}" site:dribbble.com',
        f'"{phone_number}" site:about.me',
        f'"{phone_number}" site:linktr.ee',
        f'"{phone_number}" site:t.me',
        f'"{phone_number}" site:nextdoor.com',
        f'"{phone_number}" site:meetup.com',
        f'"{phone_number}" site:xing.com',
        f'"{phone_number}" site:weheartit.com',
        f'"{phone_number}" site:foursquare.com',
        f'"{phone_number}" site:yelp.com',
        f'"{phone_number}" site:tripadvisor.com',
        f'"{phone_number}" site:trustpilot.com',
        f'"{phone_number}" site:crunchbase.com',
        f'"{phone_number}" site:angel.co',
        f'"{phone_number}" site:myspace.com',
        f'"{phone_number}" site:soundcloud.com',
        f'"{phone_number}" site:bandcamp.com',
        f'"{phone_number}" site:mixcloud.com',
        f'"{phone_number}" site:patreon.com',
        f'"{phone_number}" site:deviantart.com',
        f'"{phone_number}" site:goodreads.com',
        f'"{phone_number}" site:wattpad.com',
        f'"{phone_number}" site:strava.com'
    ]
    return dorks

def _run_internal(args=None):
    """Internal execution logic."""
    try:
        import phonenumbers
        from phonenumbers import carrier, geocoder, timezone
    except ImportError:
        print("[-] Error: 'phonenumbers' library is required for native replication.")
        print("[*] Install it via: pip install phonenumbers")
        return

    # Resolve Target Phone Number (Argument > Database)
    phone_input = ""
    if args:
        phone_input = args[0]
    elif DatabaseManagment:
        db = DatabaseManagment.get()
        phone_input = db.get("R_HOST", "")

    # Handle cases where R_HOST is a list
    if isinstance(phone_input, list) and phone_input:
        # Take the first element as the primary phone number
        phone_input = phone_input[0]

    # Ensure phone_input is a string and stripped of whitespace
    phone_input = str(phone_input).strip()

    if not phone_input:
        print("[-] No phone number target found.")
        print("[*] Usage: set target <+14155552671>  OR  run <number>")
        return

    print(f"[*] Initiating OSINT analysis for: {phone_input}\n")

    try:
        # 1. Parsing & Validation with Region Fallback
        if not phone_input.startswith('+'):
            # If no '+' is found, attempt to parse as a US number by default
            parsed_number = phonenumbers.parse(phone_input, "US")
        else:
            parsed_number = phonenumbers.parse(phone_input, None)

        if not phonenumbers.is_valid_number(parsed_number):
            print("[!] Warning: This number does not appear to be valid according to international standards.")

        # 2. Local Metadata Discovery (No API required)
        fmt_international = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        country = geocoder.description_for_number(parsed_number, "en")
        carrier_name = carrier.name_for_number(parsed_number, "en")
        time_zones = timezone.time_zones_for_number(parsed_number)

        print(f"[+] Local Metadata Discovery")
        print(f"    - International: {fmt_international}")
        print(f"    - E164 Format:   {fmt_e164}")
        print(f"    - Region:        {country}")
        print(f"    - Carrier:       {carrier_name if carrier_name else 'Unknown/Virtual'}")
        print(f"    - Timezone(s):   {', '.join(time_zones)}")

        # Update In-Memory Profile Database
        if ProfileDB:
            # Attempt to find by name if we have one, otherwise use the number as the primary identifier
            new_profile = PersonProfile(name=fmt_international, phone=fmt_e164, geolocation=country)
            ProfileDB.add_profile(new_profile)
            print(f"[*] Persona profile updated in memory database.")

        # 3. Search Engine Footprint (Dorking)
        print(f"\n[*] Generating Google Dorking Footprints (Copy into browser):")
        dorks = google_dork(fmt_e164)
        for d in dorks:
            # Cleanly format the search query URL
            query = urllib.parse.quote_plus(d)
            print(f"    - {d}")
            print(f"      URL: https://www.google.com/search?q={query}")

    except Exception as e:
        print(f"[-] Analysis Error: {e}")

def Start(args=None):
    """
    Main entry point. Replicates the PhoneInfoGa 'scan' routine.
    Wraps execution in a thread with timeout to prevent hanging.
    """
    t = threading.Thread(target=_run_internal, args=(args,))
    t.start()
    t.join(timeout=10) # 10 second timeout for OSINT module
    if t.is_alive():
        print("[-] Error: Module execution timed out.")

if __name__ == "__main__":
    Start(sys.argv[1:])