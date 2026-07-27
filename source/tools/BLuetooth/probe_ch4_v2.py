
import bluetooth
import time
import struct

def probe_channel_4(mac):
    channel = 4
    print(f"[*] Probing {mac} on channel {channel} (IcService_New)...")
    try:
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((mac, channel))
        print("[+] Connected!")
        sock.settimeout(3)

        # Probes:
        # 1. Length-prefixed string "HELLO"
        # 2. Samsung-style packet: [Start (1b)] [Length (2b)] [Opcode (1b)] [Data]
        probes = [
            b"\x05HELLO",
            b"\x00\x00\x00\x01",
            struct.pack(">H", 5) + b"PING",
            b"\xaa\x00\x04\x01\x02\x03\x04", # Generic Samsung pattern
        ]

        for p in probes:
            print(f"[*] Sending probe: {p.hex()}")
            sock.send(p)
            try:
                resp = sock.recv(1024)
                print(f"    -> Received ({len(resp)} bytes): {resp.hex()}")
                if resp:
                    print(f"    -> String: {resp.decode(errors='ignore')}")
            except Exception as e:
                print(f"    -> No response: {e}")
            time.sleep(0.5)

        sock.close()
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    probe_channel_4("48:61:EE:67:C0:0A")
