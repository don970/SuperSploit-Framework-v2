"""
Bluetooth Discovery Engine
Scans for nearby Bluetooth devices and maps their MAC addresses, names, and services.
Integrates discovered targets into the SuperSploit target database.
"""

import json
import logging
import uuid
import os
import sys
import time


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

try:
    import bluetooth
    has_pybluez = True
except ImportError:
    has_pybluez = False

install_location = f'{os.getenv("HOME")}/.SuperSploit'
path_to_targets_db = f"{install_location}/.data/.config/targets.json"

class BluetoothDiscoveryEngine:
    """
    A modular discovery engine for Bluetooth devices with service profiling.
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

    def scan(self, duration=10) -> list[dict]:
        """
        Scans for discoverable Bluetooth devices and enumerates services.
        """
        self.logger.info(f"Initiating Bluetooth scan (duration: {duration}s)...")
        discovered_devices = []

        if has_pybluez:
            try:
                nearby_devices = bluetooth.discover_devices(duration=duration, lookup_names=True, flush_cache=True, lookup_class=True)
                for addr, name, device_class in nearby_devices:
                    services_found = []
                    os_guess = "Unknown"
                    
                    self.logger.debug(f"Device found: {addr} - {name} ({hex(device_class)}). Enumerating services...")
                    try:
                        services = bluetooth.find_service(address=addr)
                        for svc in services:
                            svc_name = svc.get("name", "Unknown")
                            if svc_name:
                                services_found.append(svc_name)
                            # Basic OS profiling based on common Apple services
                            if svc_name and ("Apple" in svc_name or "AirPlay" in svc_name or "Wireless iAP" in svc_name):
                                os_guess = "iOS/macOS"
                    except Exception as e:
                        self.logger.debug(f"Could not enumerate services for {addr}: {e}")

                    discovered_devices.append({
                        "mac": addr,
                        "name": name,
                        "class": hex(device_class),
                        "protocol": "Bluetooth",
                        "services": services_found,
                        "os_guess": os_guess
                    })
            except Exception as e:
                self.logger.error(f"PyBluez scan error: {e}")
        else:
            self.logger.warning("PyBluez not found. Attempting to use system 'hcitool'...")
            try:
                import subprocess
                output = subprocess.check_output(["hcitool", "scan"], stderr=subprocess.STDOUT).decode()
                lines = output.split('\n')
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            addr = parts[1].strip()
                            name = parts[2].strip()
                            discovered_devices.append({
                                "mac": addr,
                                "name": name,
                                "class": "unknown",
                                "protocol": "Bluetooth",
                                "services": [],
                                "os_guess": "Unknown"
                            })
                            self.logger.debug(f"Device found (hcitool): {addr} - {name}")
            except Exception as e:
                self.logger.error(f"hcitool scan error: {e}")
                print("[-] Error: Bluetooth scanning failed. Ensure Bluetooth is enabled and hcitool or pybluez is installed.")

        return discovered_devices

def Start():
    engine = BluetoothDiscoveryEngine(debug_mode=True)
    print("[*] Starting Bluetooth Discovery with Service Profiling...")
    devices = engine.scan()

    if not devices:
        print("[-] No Bluetooth devices discovered.")
        return

    print(f"\n[+] Discovery Complete. Found {len(devices)} Bluetooth devices.")
    
    target_updates = {}
    for device in devices:
        mac = device['mac']
        svc_str = ", ".join(device['services'][:3]) + ("..." if len(device['services']) > 3 else "")
        print(f"[+] Target: {mac:<17} | Name: {device['name']:<20} | OS: {device['os_guess']}")
        if svc_str:
            print(f"    -> Services: {svc_str}")
        
        target_updates[mac] = {
            "status": "up",
            "hostname": device['name'],
            "mac": mac,
            "os": device['os_guess'] if device['os_guess'] != "Unknown" else "Android/Bluetooth",
            "device_class": device['class'],
            "discovery_method": "Bluetooth",
            "bluetooth_services": device['services']
        }

    # Save to targets database
    if target_updates:
        print(f"[*] Saving {len(target_updates)} Bluetooth devices to the targets database...")
        try:
            if has_db_manager:
                existing_targets = DatabaseManagment.getTargets()
            else:
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
            
            if has_db_manager:
                DatabaseManagment.updateTargets(existing_targets)
                DatabaseManagment.sync_targets_to_disk()
            else:
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
desc: """Scans for discoverable Bluetooth devices using pybluez or hcitool. 
Maps MAC addresses, names, device classes, and performs SDP queries to identify services and OS (e.g., iOS via AirPlay)."""
author: "Donald Ford"
#!#!#!
