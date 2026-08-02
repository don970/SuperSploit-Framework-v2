
import usb.core
import usb.util
import struct
import time

def create_mtp_packet(opcode, transaction_id, params=[]):
    length = 12 + (len(params) * 4)
    packet = struct.pack("<IHH I", length, 1, opcode, transaction_id)
    for p in params:
        packet += struct.pack("<I", p)
    return packet

def mtp_discovery(vid=0x04e8, pid=0x6860):
    print(f"[*] Starting Low-Level MTP Discovery (Target: 0x{vid:04x}:0x{pid:04x})")
    dev = usb.core.find(idVendor=vid, idProduct=pid)
    if not dev:
        print("[-] Device not found.")
        return

    try:
        if dev.is_kernel_driver_active(0):
            dev.detach_kernel_driver(0)
        
        cfg = dev.get_active_configuration()
        intf = cfg[(0,0)]
        ep_out = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        ep_in = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)

        print("[*] Opening MTP Session...")
        dev.write(ep_out, create_mtp_packet(0x1002, 0, [0x00000001]))
        resp = dev.read(ep_in, 1024)

        print("[*] Requesting Storage IDs (0x1004)...")
        dev.write(ep_out, create_mtp_packet(0x1004, 1))
        # Data packet
        data = dev.read(ep_in, 1024)
        # Response packet
        resp = dev.read(ep_in, 1024)
        
        if len(data) > 12:
            count = struct.unpack("<I", data[12:16])[0]
            ids = []
            for i in range(count):
                ids.append(struct.unpack("<I", data[16 + (i*4) : 20 + (i*4)])[0])
            print(f"[+] Found {count} storage(s): {[hex(i) for i in ids]}")
            
            for sid in ids:
                print(f"[*] Listing objects in storage {hex(sid)} (0x1007)...")
                dev.write(ep_out, create_mtp_packet(0x1007, sid, [0xFFFFFFFF, 0x00000000]))
                obj_data = dev.read(ep_in, 4096)
                obj_resp = dev.read(ep_in, 1024)
                if len(obj_data) > 12:
                    obj_count = struct.unpack("<I", obj_data[12:16])[0]
                    print(f"    -> Found {obj_count} objects.")
                else:
                    print(f"    -> Storage is empty or locked.")

        dev.write(ep_out, create_mtp_packet(0x1003, 2))
        print("[*] Session closed.")
        
    except Exception as e:
        print(f"[-] MTP Discovery Error: {e}")

if __name__ == "__main__":
    mtp_discovery()
