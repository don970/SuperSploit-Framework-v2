#!#!#!
root: "true"
sudo: "true"
name: "BLE Layer 5 Profiler"
category: "Discovery"
desc: """Comprehensive multi-layer BLE reconnaissance module.
Profiles devices from Link Layer (L2) through Application/GATT Profiles (L5).
Translates standard SIG UUIDs and actively polls characteristics for device intelligence."""
author: "Donald Ford"
#!#!#!
"""
BLE Layer 5 Profiler
Performs a comprehensive multi-layer analysis of BLE devices.
Layers:
  - L2: Link Layer (MAC, RSSI, Vendor)
  - L3: HCI/Advertising (Name, TX Power)
  - L4: ATT/Transport (Handles, UUIDs)
  - L5: GATT/Application (Translated UUIDs, Decoded Values)
"""

import json
import logging
import uuid
import os
import sys
import time
import subprocess
import re

# Dynamically resolve the source directory relative to this script's location
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
source_dir = os.path.join(framework_root, "source")

if source_dir not in sys.path:
    sys.path.append(source_dir)

# Try to import framework modules
try:
    from core.database import DatabaseManagment
    has_db_manager = True
except ImportError:
    has_db_manager = False

OUI_MAP = {
    "48:61:EE": "Samsung Electronics",
    "2C:F0:EE": "Broadcom",
    "80:00:22": "Elite Device",
    "AC:8B:A9": "Apple, Inc.",
    "74:4C:CE": "Apple, Inc.",
    "64:64:53": "Apple, Inc.",
    "B0:F2:F6": "Samsung Electronics",
    "54:3E:F2": "Samsung Electronics",
}

# Standard Bluetooth SIG UUIDs for Layer 5 Translation
SIG_UUIDS = {
    "1800": "Generic Access",
    "1801": "Generic Attribute",
    "180a": "Device Information",
    "180f": "Battery Service",
    "180d": "Heart Rate",
    "2a00": "Device Name",
    "2a01": "Appearance",
    "2a04": "Peripheral Preferred Connection Parameters",
    "2a19": "Battery Level",
    "2a24": "Model Number String",
    "2a25": "Serial Number String",
    "2a26": "Firmware Revision String",
    "2a27": "Hardware Revision String",
    "2a28": "Software Revision String",
    "2a29": "Manufacturer Name String",
}

class BLELayeredProfiler:
    """
    Unified engine for top-to-bottom BLE profiling.
    """
    def __init__(self, session_id: str | None = None, debug_mode: bool = False):
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = self._setup_logger(debug_mode)

    def _setup_logger(self, debug_mode: bool) -> logging.Logger:
        logger = logging.getLogger(f"BLEProfiler_{self.session_id}")
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _run_command(self, cmd: list[str], timeout: int = 15) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=timeout).decode()
        except subprocess.CalledProcessError as e:
            # Handle exit status 124 (timeout command expiration) gracefully
            if e.returncode == 124 and e.output:
                return e.output.decode()
            self.logger.debug(f"Command failed: {cmd} - {e}")
            return e.output.decode() if e.output else ""
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd} - {e}")
            return ""

    def get_vendor(self, mac: str) -> str:
        prefix = mac.upper()[:8]
        return OUI_MAP.get(prefix, "Unknown Vendor")

    def decode_hex(self, hex_str: str) -> str:
        """Decodes GATT hex string to ASCII/Integer."""
        hex_str = hex_str.replace(" ", "").strip()
        try:
            return bytes.fromhex(hex_str).decode('utf-8', errors='ignore').strip()
        except:
            return hex_str

    def profile_device(self, mac: str) -> dict:
        """Deep profiles a single BLE device (L4 and L5)."""
        self.logger.info(f"Probing Layers 4-5 on {mac}...")
        
        # Layer 4: GATT Primary Services and Characteristics
        # We try both Public and Random address types as modern devices often use Random
        chars_output = ""
        for addr_type in ["public", "random"]:
            self.logger.debug(f"Attempting GATT connection ({addr_type}) to {mac}...")
            # Reduced timeout to 6s for better responsiveness
            chars_output = self._run_command(["gatttool", "-t", addr_type, "-b", mac, "--characteristics"], timeout=6)
            if chars_output:
                self.logger.debug(f"[+] Connection successful using {addr_type} address.")
                break

        profile = {
            "l4_characteristics": [],
            "l5_data": {}
        }

        if not chars_output:
            self.logger.debug(f"[-] Device {mac} unreachable or non-connectable.")
            return profile

        lines = chars_output.strip().split('\n')
        for line in lines:
            match = re.search(r"handle:\s+(0x[0-9a-f]+).*?uuid:\s+([0-9a-f-]+)", line)
            if match:
                handle = match.group(1)
                uuid_val = match.group(2)
                short_uuid = uuid_val.split("-")[0].lstrip("0")
                
                char_info = {
                    "handle": handle,
                    "uuid": uuid_val,
                    "translated_name": SIG_UUIDS.get(short_uuid, "Unknown Characteristic")
                }
                profile["l4_characteristics"].append(char_info)

                # Layer 5: Active Polling for standard read-only fields
                if short_uuid in ["2a00", "2a24", "2a25", "2a26", "2a27", "2a28", "2a29", "2a19"]:
                    self.logger.debug(f"Attempting L5 read on {char_info['translated_name']} ({handle})")
                    # Use the successful addr_type for subsequent reads
                    read_val = self._run_command(["gatttool", "-t", addr_type, "-b", mac, "--char-read", "-a", handle], timeout=4)
                    if "Characteristic value/descriptor:" in read_val:
                        raw_hex = read_val.split(":", 1)[1].strip()
                        if short_uuid == "2a19": # Battery Level is usually a single byte integer
                            try:
                                profile["l5_data"]["Battery Level"] = f"{int(raw_hex, 16)}%"
                            except:
                                profile["l5_data"]["Battery Level"] = raw_hex
                        else:
                            profile["l5_data"][char_info["translated_name"]] = self.decode_hex(raw_hex)

        return profile

    def scan_and_profile(self, duration: int = 15) -> list[dict]:
        """Orchestrates L2-L3 discovery and subsequent L4-L5 profiling."""
        self.logger.info(f"Initiating BLE Scan (hcitool) for {duration}s...")
        
        # hcitool lescan is more reliable for raw LE discovery than bluetoothctl
        # We use 'timeout' to stop it after the duration
        scan_cmd = ["timeout", "-s", "SIGINT", f"{duration}s", "hcitool", "lescan"]
        scan_output = self._run_command(scan_cmd, timeout=duration + 5)
        
        discovered_macs = {}
        for line in scan_output.strip().split('\n'):
            match = re.search(r"([0-9A-F:]{17})\s+(.*)", line)
            if match:
                mac = match.group(1)
                name = match.group(2).strip()
                if name == "(unknown)": name = "Unknown BLE Device"
                discovered_macs[mac] = name

        results = []
        for mac, name in discovered_macs.items():
            self.logger.info(f"[+] Found BLE Target: {mac} ({name})")
            
            # Fetch L3 Info via bluetoothctl (more descriptive)
            info_output = self._run_command(["bluetoothctl", "info", mac])
            
            device_data = {
                "mac": mac,
                "l2_link": {
                    "vendor": self.get_vendor(mac),
                    "rssi": "Unknown"
                },
                "l3_hci": {
                    "name": name,
                    "tx_power": "Unknown"
                },
                "l4_l5_profile": self.profile_device(mac)
            }
            
            # Extract RSSI and TX Power from info if present
            rssi_match = re.search(r"RSSI:\s+([-0-9]+)", info_output)
            if rssi_match: device_data["l2_link"]["rssi"] = f"{rssi_match.group(1)} dBm"
            
            tx_match = re.search(r"TxPower:\s+([-0-9]+)", info_output)
            if tx_match: device_data["l3_hci"]["tx_power"] = f"{tx_match.group(1)} dBm"
            
            results.append(device_data)

        return results

def Start():
    # Enforce Root Privileges
    if os.geteuid() != 0:
        print("[-] Error: Root privileges are required for BLE interaction. Please run with sudo.")
        return

    # Check for Dependencies
    dependencies = ["bluetoothctl", "gatttool", "hcitool"]
    missing = [d for d in dependencies if subprocess.call(["which", d], stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0]
    if missing:
        print(f"[-] Error: Missing required dependencies: {', '.join(missing)}")
        print("    Install them with: sudo apt install bluez")
        return

    profiler = BLELayeredProfiler(debug_mode=True)
    print("[*] Starting BLE Layer 5 Multi-Layer Profiler...")
    
    # Ensure Bluetooth is powered on and unblocked
    print("[*] Ensuring Bluetooth interface is powered on...")
    if subprocess.call(["which", "rfkill"], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
        subprocess.call(["rfkill", "unblock", "bluetooth"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    subprocess.call(["bluetoothctl", "power", "on"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)

    devices = profiler.scan_and_profile(duration=20)

    if not devices:
        print("[-] No BLE devices discovered. Ensure your Bluetooth adapter is plugged in and BLE devices are advertising.")
        return

    print(f"\n[+] Discovery Complete. Profiled {len(devices)} BLE targets.")
    
    target_updates = {}
    for dev in devices:
        mac = dev["mac"]
        print(f"\n[Target: {mac}]")
        print(f"  Layer 2 (Link): {dev['l2_link']['vendor']} | RSSI: {dev['l2_link']['rssi']}")
        print(f"  Layer 3 (HCI):  Name: {dev['l3_hci']['name']} | TX: {dev['l3_hci']['tx_power']}")
        
        l4_chars = dev["l4_l5_profile"]["l4_characteristics"]
        print(f"  Layer 4 (ATT):  {len(l4_chars)} Characteristics mapped.")
        
        l5_data = dev["l4_l5_profile"]["l5_data"]
        if l5_data:
            print(f"  Layer 5 (GATT): Decoded Attributes:")
            for k, v in l5_data.items():
                print(f"    -> {k}: {v}")

        # Map to Database Schema
        target_updates[mac] = {
            "status": "up",
            "hostname": dev["l3_hci"]["name"],
            "mac": mac,
            "vendor": dev["l2_link"]["vendor"],
            "discovery_method": "BLE Layer 5 Profiler",
            "ble_layered_profile": dev
        }

    # Save to database
    if target_updates and has_db_manager:
        print(f"[*] Synchronizing {len(target_updates)} profiles to database...")
        try:
            targets = DatabaseManagment.getTargets()
            for mac, info in target_updates.items():
                if mac not in targets: targets[mac] = info
                else: targets[mac].update(info)
            DatabaseManagment.updateTargets(targets)
            DatabaseManagment.sync_targets_to_disk()
            print("[+] Database updated.")
        except Exception as e:
            print(f"[-] DB Sync Error: {e}")

if __name__ == "__main__":
    Start()
