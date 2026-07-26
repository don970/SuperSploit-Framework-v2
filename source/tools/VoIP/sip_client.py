import socket
import random
import string
import time
import threading

class SIPClient:
    def __init__(self, server, port, user, password=None):
        self.server = server
        self.port = int(port)
        self.user = user
        self.password = password
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        self.local_ip = self._get_local_ip()

    def _get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except:
            return "127.0.0.1"
        finally:
            s.close()

    def _generate_id(self, length=10):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def make_call(self, target_number, audio_file=None, log_callback=None):
        def log(msg):
            if log_callback: log_callback(msg)
            else: print(msg)

        call_id = self._generate_id(15)
        from_tag = self._generate_id(8)
        cseq = 1
        
        # SIP INVITE with SDP
        sdp = (
            f"v=0\r\n"
            f"o={self.user} 123456 654321 IN IP4 {self.local_ip}\r\n"
            f"s=-\r\n"
            f"c=IN IP4 {self.local_ip}\r\n"
            f"t=0 0\r\n"
            f"m=audio 4000 RTP/AVP 0\r\n" # Port 4000, PCMU
            f"a=rtpmap:0 PCMU/8000\r\n"
        )
        
        invite = (
            f"INVITE sip:{target_number}@{self.server} SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP {self.local_ip};branch=z9hG4bK{self._generate_id(10)}\r\n"
            f"Max-Forwards: 70\r\n"
            f"From: <sip:{self.user}@{self.server}>;tag={from_tag}\r\n"
            f"To: <sip:{target_number}@{self.server}>\r\n"
            f"Call-ID: {call_id}\r\n"
            f"CSeq: {cseq} INVITE\r\n"
            f"Contact: <sip:{self.user}@{self.local_ip}>\r\n"
            f"Content-Type: application/sdp\r\n"
            f"Content-Length: {len(sdp)}\r\n\r\n{sdp}"
        )
        
        try:
            log(f"[*] Sending INVITE to {target_number}...")
            self.sock.sendto(invite.encode(), (self.server, self.port))
            
            # Simple State Machine
            while True:
                data, addr = self.sock.recvfrom(4096)
                resp = data.decode('utf-8', errors='ignore')
                
                if "100 Trying" in resp: log("[*] Server received request...")
                elif "180 Ringing" in resp: log("[*] Target is ringing...")
                elif "200 OK" in resp:
                    log("[+] CALL ANSWERED! Starting audio stream...")
                    # Send ACK
                    ack = (
                        f"ACK sip:{target_number}@{self.server} SIP/2.0\r\n"
                        f"Via: SIP/2.0/UDP {self.local_ip};branch=z9hG4bK{self._generate_id(10)}\r\n"
                        f"Max-Forwards: 70\r\n"
                        f"From: <sip:{self.user}@{self.server}>;tag={from_tag}\r\n"
                        f"To: <sip:{target_number}@{self.server}>\r\n"
                        f"Call-ID: {call_id}\r\n"
                        f"CSeq: {cseq} ACK\r\n\r\n"
                    )
                    self.sock.sendto(ack.encode(), (self.server, self.port))
                    
                    if audio_file:
                        self._stream_audio(audio_file, addr[0], 4000, log)
                    break
                elif "401 Unauthorized" in resp or "407 Proxy Authentication Required" in resp:
                    log("[-] Authentication required but not implemented in this stub.")
                    break
                elif resp.startswith("SIP/2.0 4") or resp.startswith("SIP/2.0 5"):
                    log(f"[-] Call failed: {resp.splitlines()[0]}")
                    break
                    
        except Exception as e:
            log(f"[-] SIP Client Error: {e}")

    def _stream_audio(self, file_path, target_ip, target_port, log_func):
        """Simulated RTP Streaming for demonstration."""
        log_func(f"[*] Streaming {file_path} to {target_ip}:{target_port} (Mock RTP)")
        # In a real tool, we would read the WAV, convert to G.711 PCMU, and send UDP packets every 20ms
        # This implementation is a high-level stub for the SE suite logic.
        time.sleep(5)
        log_func("[+] Audio transmission complete.")

if __name__ == "__main__":
    client = SIPClient("127.0.0.1", 5060, "supersploit")
    client.make_call("15551234567")
