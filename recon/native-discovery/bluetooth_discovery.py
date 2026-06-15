"""
Bluetooth Discovery Engine v2.0
Enhanced scanning using bluetoothctl for Classic and BLE support.
Maps MAC addresses, names, vendors, and services.
Integrates discovered targets into the SuperSploit target database.
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

class BluetoothDiscoveryEngine:
    """
    An enhanced modular discovery engine for Bluetooth devices.
    """
    def __init__(self, session_id: str | None = None, debug_mode: bool = False):
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = self._setup_logger(debug_mode)

    def _setup_logger(self, debug_mode: bool) -> logging.Logger:
        logger = logging.getLogger(f"BTDiscovery_{self.session_id}")
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - [Session: {self.session_id}] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def _run_command(self, cmd: list[str]) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30).decode()
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd} - {e}")
            return ""

    def get_oui_vendor(self, mac: str) -> str:
        prefix = mac.upper()[:8]
        return OUI_MAP.get(prefix, "Unknown Vendor")

    def parse_device_info(self, mac: str) -> dict:
        info_output = self._run_command(["bluetoothctl", "info", mac])
        info = {
            "mac": mac,
            "name": "Unknown",
            "vendor": self.get_oui_vendor(mac),
            "class": "0x000000",
            "icon": "unknown",
            "services": [],
            "os_guess": "Unknown",
            "ble_support": False
        }

        if "Device" not in info_output:
            return info

        name_match = re.search(r"Name:\s+(.*)", info_output)
        if name_match:
            info["name"] = name_match.group(1).strip()

        class_match = re.search(r"Class:\s+(0x[0-9a-fA-F]+)", info_output)
        if class_match:
            info["class"] = class_match.group(1)

        icon_match = re.search(r"Icon:\s+(.*)", info_output)
        if icon_match:
            info["icon"] = icon_match.group(1).strip()

        uuids = re.findall(r"UUID:\s+(.*?)\s+\(0000([0-9a-fA-F]{4})", info_output)
        for svc_name, svc_id in uuids:
            info["services"].append(svc_name.strip())
            
        # OS Fingerprinting logic
        if info["vendor"] == "Apple, Inc." or "Apple" in str(info["services"]):
            info["os_guess"] = "iOS/macOS"
        elif "Handsfree Audio Gateway" in info["services"] or "phone" in info["icon"]:
            info["os_guess"] = "Android/Linux"
        elif "Computer" in info["icon"]:
            info["os_guess"] = "Linux/Windows"

        if "(le)" in info_output.lower() or "Generic Attribute Profile" in info["services"]:
            info["ble_support"] = True

        return info

    def scan(self, duration=15) -> list[dict]:
        """
        Scans for discoverable Bluetooth devices using bluetoothctl.
        """
        self.logger.info(f"Initiating Bluetooth scan (duration: {duration}s)...")
        
        # Start scanning in background
        scan_proc = subprocess.Popen(["bluetoothctl", "--timeout", str(duration), "scan", "on"], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration + 1)
        
        devices_output = self._run_command(["bluetoothctl", "devices"])
        discovered_devices = []

        device_lines = devices_output.strip().split('\n')
        for line in device_lines:
            match = re.search(r"Device\s+([0-9A-F:]{17})\s+(.*)", line)
            if match:
                mac = match.group(1)
                self.logger.debug(f"Found device: {mac}. Fetching details...")
                info = self.parse_device_info(mac)
                discovered_devices.append(info)

        return discovered_devices

def Start():
    engine = BluetoothDiscoveryEngine(debug_mode=True)
    print("[*] Starting Enhanced Bluetooth Discovery (v2.0)...")
    devices = engine.scan()

    if not devices:
        print("[-] No Bluetooth devices discovered.")
        return

    print(f"\n[+] Discovery Complete. Found {len(devices)} Bluetooth devices.")
    
    target_updates = {}
    for device in devices:
        mac = device['mac']
        print(f"[+] Target: {mac:<17} | Name: {device['name']:<20} | Vendor: {device['vendor']}")
        print(f"    -> OS Guess: {device['os_guess']:<15} | BLE: {device['ble_support']}")
        if device['services']:
            svc_str = ", ".join(device['services'][:3]) + ("..." if len(device['services']) > 3 else "")
            print(f"    -> Services: {svc_str}")
        
        target_updates[mac] = {
            "status": "up",
            "hostname": device['name'],
            "mac": mac,
            "os": device['os_guess'],
            "os_family": device['os_guess'],
            "architecture": "Unknown",
            "vendor": device['vendor'],
            "device_class": device['class'],
            "discovery_method": "Bluetoothctl",
            "bluetooth_services": device['services'],
            "ble_support": device['ble_support']
        }

    # Save to targets database
    if target_updates:
        print(f"[*] Saving {len(target_updates)} Bluetooth devices to the targets database...")
        try:
            if has_db_manager:
                existing_targets = DatabaseManagment.getTargets()
                for mac, info in target_updates.items():
                    if mac not in existing_targets or not isinstance(existing_targets[mac], dict):
                        existing_targets[mac] = info
                    else:
                        existing_targets[mac].update(info)
                
                DatabaseManagment.updateTargets(existing_targets)
                DatabaseManagment.sync_targets_to_disk()
                print("[+] Database updated successfully.")
                return
        except Exception as e:
            print(f"[-] Failed to update via DatabaseManagment: {e}")

        # Fallback to manual JSON write
        try:
            path_to_targets_db = os.path.join(framework_root, ".data", ".config", "targets.json")
            if not os.path.exists(os.path.dirname(path_to_targets_db)):
                 path_to_targets_db = os.path.expanduser("~/.SuperSploit/.data/.config/targets.json")
            
            existing_targets = {}
            if os.path.exists(path_to_targets_db):
                with open(path_to_targets_db, "r") as f:
                    try:
                        existing_targets = json.load(f).get("TARGETS", {})
                    except json.JSONDecodeError:
                        pass

            for mac, info in target_updates.items():
                if mac not in existing_targets or not isinstance(existing_targets[mac], dict):
                    existing_targets[mac] = info
                else:
                    existing_targets[mac].update(info)
            
            with open(path_to_targets_db, "w") as f:
                json.dump({"TARGETS": existing_targets}, f, sort_keys=True, indent=4)
            print("[+] Database updated successfully.")
        except Exception as e:
            print(f"[-] Failed to update database: {e}")

if __name__ == "__main__":
    Start()

#!#!#!
root: "true"
name: "Bluetooth Discovery & Profiling"
category: "Discovery"
desc: """Enhanced Bluetooth discovery using bluetoothctl. 
Supports Classic and BLE scanning, OUI/Vendor lookup, and deep service profiling for OS fingerprinting."""
author: "Donald Ford"
#!#!#!
