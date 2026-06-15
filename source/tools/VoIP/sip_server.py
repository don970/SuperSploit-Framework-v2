import socket
import re
import time

# Configuration
BIND_IP = "0.0.0.0"
BIND_PORT = 5060  # SIP standard port (may require sudo)
# BIND_PORT = 8060 # Alternative high port if non-root

def start_sip_server():
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((BIND_IP, BIND_PORT))
        print(f"[*] SuperSploit SIP Gateway active on {BIND_IP}:{BIND_PORT} (UDP)")
        print(f"[*] Awaiting SIP MESSAGE packets...")
    except PermissionError:
        print(f"[-] ERROR: Permission denied on port {BIND_PORT}. Try running with 'sudo' or change to port 8060.")
        return
    except Exception as e:
        print(f"[-] ERROR: Could not bind to {BIND_IP}:{BIND_PORT}: {e}")
        return

    while True:
        try:
            data, addr = sock.recvfrom(4096)
            msg = data.decode('utf-8', errors='ignore')
            
            # Simple SIP Request detection
            if msg.startswith("MESSAGE"):
                print(f"\n[+] Received SIP MESSAGE from {addr[0]}:{addr[1]}")
                
                # Extract headers via regex
                from_header = re.search(r'From: <sip:(.*?)@', msg)
                to_header = re.search(r'To: <sip:(.*?)@', msg)
                call_id = re.search(r'Call-ID: (.*?)\r\n', msg)
                
                # Body is separated by double CRLF
                body = ""
                if "\r\n\r\n" in msg:
                    body = msg.split("\r\n\r\n", 1)[1].strip()

                print("================== SIP SMS TRANSACTION ==================")
                print(f"SENDER (From)    : {from_header.group(1) if from_header else 'UNKNOWN'}")
                print(f"RECIPIENT (To)  : {to_header.group(1) if to_header else 'UNKNOWN'}")
                print(f"CALL-ID         : {call_id.group(1) if call_id else 'N/A'}")
                print(f"MESSAGE CONTENT : {body}")
                print("==========================================================")

                # Send 200 OK Response (SIP Success)
                if call_id:
                    # We mirror back some headers to satisfy the client
                    via = re.search(r'(Via: .*?)\r\n', msg).group(1)
                    fr = re.search(r'(From: .*?)\r\n', msg).group(1)
                    to = re.search(r'(To: .*?)\r\n', msg).group(1)
                    cseq = re.search(r'(CSeq: .*?)\r\n', msg).group(1)
                    cid = call_id.group(0)

                    response = (
                        f"SIP/2.0 200 OK\r\n"
                        f"{via}\r\n"
                        f"{fr}\r\n"
                        f"{to}\r\n"
                        f"{cid}"
                        f"{cseq}\r\n"
                        f"Content-Length: 0\r\n"
                        f"\r\n"
                    )
                    sock.sendto(response.encode(), addr)
                    print(f"[*] Dispatched '200 OK' to {addr[0]}")

        except KeyboardInterrupt:
            print("\n[*] Shutting down SIP Gateway...")
            break
        except Exception as e:
            print(f"[-] Gateway Error: {e}")

if __name__ == "__main__":
    start_sip_server()
