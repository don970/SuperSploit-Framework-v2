import sys
import os
import urllib.parse
import datetime

# Dynamically append the framework's source directory to sys.path
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
    from fpdf import FPDF
except ImportError:
    FPDF = None

#!#!#!
name: "Native Background Check OSINT"
description: "Exhaustive public records aggregator. Targets legal data, social footprints, business filings, and leaked documents."
category: "OSINT"
author: "Donald Ford"
keywords: '["background", "osint", "person", "records", "dorking", "dox", "public-records"]'
#!#!#!

class PersonProfile:
    """Structure to hold a comprehensive persona profile."""
    def __init__(self, name, phone="N/A", email="N/A", address="N/A", social_medias=None, geolocation="N/A", aliases=None, employment="N/A", education="N/A"):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.social_medias = social_medias if social_medias else []
        self.geolocation = geolocation
        self.aliases = aliases if aliases else []
        self.employment = employment
        self.education = education

def generate_background_dorks(name, location=None):
    """Generates an exhaustive list of targeted Google Dorks."""
    query_base = f'"{name}"'
    if location:
        query_base = f'"{name}" "{location}"'
    
    dorks = {
        "Primary Aggregators": [
            f'{query_base} site:whitepages.com',
            f'{query_base} site:spokeo.com',
            f'{query_base} site:truepeoplesearch.com',
            f'{query_base} site:peekyou.com',
            f'{query_base} site:voterrecords.com',
            f'{query_base} site:thatsthem.com'
        ],
        "Legal & Criminal": [
            f'{query_base} intitle:court OR intitle:arrest OR intitle:criminal OR intitle:mugshot',
            f'{query_base} filetype:pdf (intext:judgment OR intext:liens OR intext:bankruptcy OR intext:divorce)',
            f'{query_base} site:judyrecords.com',
            f'{query_base} site:jailbase.com'
        ],
        "Social & Professional": [
            f'{query_base} site:linkedin.com',
            f'{query_base} site:facebook.com OR site:instagram.com OR site:x.com OR site:tiktok.com',
            f'{query_base} site:github.com OR site:gitlab.com OR site:stackoverflow.com',
            f'{query_base} site:crunchbase.com OR site:zoominfo.com OR site:rocketreach.co',
            f'{query_base} site:about.me OR site:linktr.ee OR site:behance.net'
        ],
        "Business & Financial": [
            f'{query_base} site:opencorporates.com',
            f'{query_base} site:bizapedia.com',
            f'{query_base} site:sec.gov "intext:{name}"'
        ],
        "Document Leaks & Pastes": [
            f'{query_base} (site:pastebin.com OR site:controlc.com OR site:scribd.com OR site:slideshare.net)',
            f'{query_base} filetype:xls OR filetype:xlsx OR filetype:csv "intext:email" OR "intext:phone"'
        ]
    }
    return dorks

def export_pdf(name, location, dork_map, output_path):
    """Generates a formatted PDF report with clickable search links."""
    if not FPDF:
        return False
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="SuperSploit OSINT Report", ln=True, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Target Information:", ln=True)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Name: {name}", ln=True)
        if location:
            pdf.cell(200, 10, txt=f"Location: {location}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="OSINT Footprints:", ln=True)
        pdf.set_font("Arial", size=8)

        for category, dorks in dork_map.items():
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(200, 8, txt=category, ln=True)
            pdf.set_font("Arial", size=8)
            for d in dorks:
                query = urllib.parse.quote_plus(d)
                url = f"https://www.google.com/search?q={query}"
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 4, txt=f"Dork: {d}")
                pdf.set_text_color(0, 0, 255)
                pdf.cell(0, 4, txt=f"Search URL: {url}", ln=True, link=url)
                pdf.ln(1)
            pdf.ln(3)

        pdf.output(output_path)
        return True
    except Exception as e:
        print(f"[-] PDF Error: {e}")
        return False

def Start(args=None):
    name_input = args[0] if args else ""
    loc_input = args[1] if args and len(args) > 1 else None
    
    if not name_input and DatabaseManagment:
        name_input = DatabaseManagment.get().get("R_HOST", "")

    # Handle cases where R_HOST is stored as a list [Name, Location]
    if isinstance(name_input, list):
        if len(name_input) > 1 and not loc_input:
            loc_input = name_input[1]
        name_input = name_input[0] if len(name_input) > 0 else ""

    name_input = str(name_input).strip()

    if not name_input or name_input.replace('.', '').isdigit():
        print("[-] Error: Provide a name (e.g., run \"John Doe\")")
        return

    print(f"[*] Initiating Profile for: {name_input}")
    
    # Initialize/Update the persistent profile entry
    new_profile = PersonProfile(name=name_input, address=loc_input if loc_input else "N/A")
    if DatabaseManagment:
        DatabaseManagment.addProfile(new_profile.__dict__)
    
    dork_map = generate_background_dorks(name_input, loc_input)
    
    if FPDF:
        install = DatabaseManagment.getInstall() if DatabaseManagment else "."
        loot_dir = os.path.join(install, ".data", ".loot", "reports")
        os.makedirs(loot_dir, exist_ok=True)
        filename = f"Report_{name_input.replace(' ', '_')}_{datetime.date.today()}.pdf"
        path = os.path.join(loot_dir, filename)
        
        if export_pdf(name_input, loc_input, dork_map, path):
            print(f"[+] Report exported: {path}")
    
    print(f"\n[*] Generated Dorks for {name_input}:")
    for category, dorks in dork_map.items():
        print(f"\n--- {category} ---")
        for d in dorks:
            print(f"  - {d}")
    
    if DatabaseManagment:
        all_profiles = DatabaseManagment.getProfiles().values()
        print(f"\n[*] Active Persistent Profiles: {len(all_profiles)}")
        for p_dict in all_profiles:
            print(f"    - {p_dict.get('name', 'N/A')} | Phone: {p_dict.get('phone', 'N/A')} | Email: {p_dict.get('email', 'N/A')} | Geo: {p_dict.get('geolocation', 'N/A')}")

if __name__ == "__main__":
    Start(sys.argv[1:])