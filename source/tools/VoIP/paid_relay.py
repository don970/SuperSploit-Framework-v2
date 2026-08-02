import socket
import re
import threading

# Configuration
LOCAL_BIND = "0.0.0.0"
LOCAL_PORT = 5060

# Upstream SIP Trunk (Configure your commercial provider here)
REMOTE_SIP_SERVER = "sip.provider.com"
REMOTE_SIP_PORT = 5060

class PaidSipRelay:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((LOCAL_BIND, LOCAL_PORT))
        print(f"[*] Paid SIP Relay active on {LOCAL_BIND}:{LOCAL_PORT}")
        print(f"[*] Upstream Trunk: {REMOTE_SIP_SERVER}:{REMOTE_SIP_PORT}")

    def handle_client(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(4096)
                msg = data.decode('utf-8', errors='ignore')
                
                if msg.startswith("MESSAGE"):
                    print(f"\n[+] Relaying MESSAGE from {addr[0]}")
                    
                    # 1. Modify headers to match Upstream requirements if needed
                    # (Standard SIP forwarding logic)
                    modified_msg = msg.replace("127.0.0.1", REMOTE_SIP_SERVER)
                    
                    # 2. Forward to real SIP Trunk
                    self.sock.sendto(modified_msg.encode(), (REMOTE_SIP_SERVER, REMOTE_SIP_PORT))
                    print(f"[*] Forwarded to Trunk: {REMOTE_SIP_SERVER}")

                    # 3. Handle immediate local success response to GUI
                    # (Optional: Wait for trunk response and relay it back)
                    response = "SIP/2.0 200 OK\r\n" # Mock success to GUI
                    self.sock.sendto(response.encode(), addr)

            except Exception as e:
                print(f"[-] Relay Error: {e}")

if __name__ == "__main__":
    relay = PaidSipRelay()
    relay.handle_client()
