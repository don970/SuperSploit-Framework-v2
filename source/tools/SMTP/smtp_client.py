import smtplib
import base64
from email.parser import BytesParser
from email.policy import default

# Configuration
SMTP_SERVER = '127.0.0.1'
SMTP_PORT = 2525
USERNAME = 'admin'
PASSWORD = 'password'

# The file we want to send
EML_FILE = '/home/donald/Downloads/gemini-code-1781022897289.eml'

# Envelope Addresses (These are used in the MAIL FROM and RCPT TO protocol commands)
ENVELOPE_SENDER = 'rewards@cslplasma.com'
# We'll use a dummy recipient for the demo
ENVELOPE_RECIPIENT = 'donald.ford@example.local'

def send_spoofed_email():
    print(f"[*] Reading EML file: {EML_FILE}")
    with open(EML_FILE, 'rb') as fp:
        msg = BytesParser(policy=default).parse(fp)
    
    print(f"[*] Connecting to Fake SMTP Server at {SMTP_SERVER}:{SMTP_PORT}...")
    try:
        # We use smtplib.SMTP and turn on debugging so we can see the exact conversation
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1) # This prints the client/server conversation to the console
        
        # 1. EHLO
        print("\n[*] Sending EHLO...")
        server.ehlo()
        
        # 2. Authentication
        print(f"\n[*] Authenticating as '{USERNAME}'...")
        # Since our fake server uses a basic AUTH LOGIN implementation, we do it manually or let smtplib handle it
        server.login(USERNAME, PASSWORD)
        
        # 3. Send the email (MAIL FROM, RCPT TO, DATA)
        print("\n[*] Sending Email Data...")
        server.send_message(msg, from_addr=ENVELOPE_SENDER, to_addrs=[ENVELOPE_RECIPIENT])
        
        # 4. Disconnect
        server.quit()
        print("\n[+] Email successfully queued on the fake server!")
        
    except Exception as e:
        print(f"\n[-] SMTP Error: {e}")

if __name__ == "__main__":
    send_spoofed_email()
