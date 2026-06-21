#!#!#!
# name: Pro Malicious QR Generator
# author: "Donald Ford"
# description: Generates physical SE assets. Creates high-res QR codes pointing to C2 payloads or phishing portals.
# type: se_delivery
# requirements: ["qrcode", "Pillow"]
# options:
#   - PAYLOAD_URL: "The URL the QR code will redirect to (e.g., SuperSploit C2 link)"
#   - OUTPUT_FILE: "Path to save the generated QR image (e.g., /tmp/qr_drop.png)"
# pro_feature: true
#!#!#!

import os
from core.ToStdOut import ToStdout
from core.license_manager import LicenseManager

def run(db):
    if not LicenseManager.gate_access("Malicious QR Generator"):
        return False
        
    try:
        import qrcode
    except ImportError:
        ToStdout.write("[-] ERROR: Required package 'qrcode' is missing. Run: pip install qrcode[pil]\n")
        return False
        
    payload_url = db.get("PAYLOAD_URL")
    output_file = db.get("OUTPUT_FILE", os.path.join(os.getenv("HOME"), "payload_qr.png"))
    
    if not payload_url:
        ToStdout.write("[-] ERROR: PAYLOAD_URL is required.\n")
        return False
        
    ToStdout.write(f"[*] Generating Malicious QR Code for: {payload_url}\n")
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(payload_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_file)
        
        ToStdout.write(f"[+] SUCCESS: QR Code asset saved to {output_file}\n")
        return True
    except Exception as e:
        ToStdout.write(f"[-] ERROR: Failed to generate QR Code: {e}\n")
        return False