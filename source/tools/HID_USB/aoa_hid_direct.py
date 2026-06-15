
import usb.core
import usb.util
import time
import struct

REPORT_DESCRIPTOR = b"".join([
    b"\x05\x01\x09\x06\xa1\x01\x05\x07\x19\xe0\x29\xe7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x95\x05\x75\x01\x05\x08\x19\x01\x29\x05\x91\x02\x95\x01\x75\x03\x91\x01\x95\x06\x75\x08\x15\x00\x25\x65\x05\x07\x19\x00\x29\x65\x81\x00\xc0"
])

def send_key(dev, keycode):
    report = struct.pack("BBBBBBBB", 0, 0, keycode, 0, 0, 0, 0, 0)
    dev.ctrl_transfer(0x40, 56, 1, 0, report)
    time.sleep(0.05)
    report = struct.pack("BBBBBBBB", 0, 0, 0, 0, 0, 0, 0, 0)
    dev.ctrl_transfer(0x40, 56, 1, 0, report)
    time.sleep(0.05)

def unlock_direct(vid=0x04e8, pid=0x6860):
    print(f"[*] Starting Direct HID Unlocker (Target: 0x{vid:04x}:0x{pid:04x})")
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if not dev:
        print("[-] Device not found.")
        return

    try:
        print("[*] Registering HID Keyboard directly in MTP mode...")
        dev.ctrl_transfer(0x40, 54, 1, len(REPORT_DESCRIPTOR))
        dev.ctrl_transfer(0x40, 55, 1, 0, REPORT_DESCRIPTOR)
        
        print("[*] Injecting 'Tab' -> 'Enter'...")
        send_key(dev, 0x2b) # Tab
        time.sleep(0.2)
        send_key(dev, 0x28) # Enter
        print("[+] Done.")
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    unlock_direct()
