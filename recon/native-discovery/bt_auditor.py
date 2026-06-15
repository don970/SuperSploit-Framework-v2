"""
Bluetooth Active Auditor
Performs active vulnerability probing and service enumeration on Bluetooth targets.
Supports RFCOMM (Samsung Ch 4) and BLE (GATT enumeration).
"""

import json
import logging
import uuid
import os
import sys
import time
import subprocess
import re
import struct

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

class BluetoothAuditor:
    """
    Active auditing engine for Bluetooth targets.
    """
    def __init__(self, target_mac: str, session_id: str | None = None, debug_mode: bool = False):
        self.target_mac = target_mac
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = self._setup_logger(debug_mode)

    def _setup_logger(self, debug_mode: bool) -> logging.Logger:
        logger = logging.getLogger(f"BTAuditor_{self.session_id}")
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - [%(levelname)s] - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def _run_command(self, cmd: list[str], timeout: int = 10) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=timeout).decode()
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd} - {e}")
            return ""

    def probe_samsung_ch4(self) -> bool:
        """
        Probes for the Samsung IcService_New on RFCOMM Channel 4.
        """
        if not has_pybluez:
            self.logger.warning("PyBluez not found. Skipping RFCOMM probe.")
            return False

        channel = 4
        self.logger.info(f"Probing {self.target_mac} on RFCOMM channel {channel}...")
        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.settimeout(5)
            sock.connect((self.target_mac, channel))
            self.logger.info("[+] RFCOMM Channel 4 is OPEN (IcService_New likely present)")
            
            # Simple "Knock" probe
            sock.send(b"\x00\x00\x00\x01")
            try:
                resp = sock.recv(1024)
                if resp:
                    self.logger.info(f"[+] Received probe response: {resp.hex()}")
            except:
                pass
                
            sock.close()
            return True
        except Exception as e:
            self.logger.debug(f"RFCOMM probe failed: {e}")
            return False

    def enumerate_gatt(self) -> list[dict]:
        """
        Enumerates BLE GATT characteristics using gatttool.
        """
        self.logger.info(f"Attempting BLE GATT enumeration on {self.target_mac}...")
        chars_output = self._run_command(["gatttool", "-b", self.target_mac, "--characteristics"])
        
        characteristics = []
        if not chars_output:
            self.logger.debug("No GATT characteristics found or device unreachable.")
            return characteristics

        lines = chars_output.strip().split('\n')
        for line in lines:
            # Format: handle: 0x0002, char properties: 0x02, char value handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
            match = re.search(r"handle:\s+(0x[0-9a-f]+).*?uuid:\s+([0-9a-f-]+)", line)
            if match:
                handle = match.group(1)
                uuid_val = match.group(2)
                characteristics.append({"handle": handle, "uuid": uuid_val})
        
        self.logger.info(f"[+] Found {len(characteristics)} GATT characteristics.")
        return characteristics

    def audit(self) -> dict:
        results = {
            "mac": self.target_mac,
            "samsung_vuln_potential": False,
            "gatt_characteristics": [],
            "timestamp": time.time()
        }

        results["samsung_vuln_potential"] = self.probe_samsung_ch4()
        results["gatt_characteristics"] = self.enumerate_gatt()

        return results

def Start():
    # Prioritize command line argument
    target_mac = ""
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        target_mac = sys.argv[1]
    
    # Fallback to database if no arg or arg is just a flag
    if not target_mac and has_db_manager:
        target_mac = DatabaseManagment.get().get("R_MAC", "")

    if not target_mac:
        print("[-] Error: No target MAC specified. Set R_MAC or provide as argument.")
        return

    auditor = BluetoothAuditor(target_mac, debug_mode=True)
    print(f"[*] Starting Active Bluetooth Audit on {target_mac}...")
    results = auditor.audit()

    print("\n[+] Audit Results:")
    print(f"    - Samsung Vuln Potential (Ch 4): {results['samsung_vuln_potential']}")
    print(f"    - GATT Characteristics Found:    {len(results['gatt_characteristics'])}")
    
    if results['gatt_characteristics']:
        for char in results['gatt_characteristics'][:5]:
            print(f"      -> {char['handle']}: {char['uuid']}")
        if len(results['gatt_characteristics']) > 5:
            print("      -> ...")

    # Save results to database
    if has_db_manager:
        targets = DatabaseManagment.getTargets()
        if target_mac not in targets:
            targets[target_mac] = {"mac": target_mac, "status": "up", "discovery_method": "Bluetooth Auditor"}
        
        targets[target_mac]["audit_results"] = results
        # Ensure we don't wipe OS/Arch if they exist, but populate if missing
        if "os_family" not in targets[target_mac] and results["samsung_vuln_potential"]:
             targets[target_mac]["os_family"] = "Android (Samsung)"
        
        DatabaseManagment.updateTargets(targets)
        DatabaseManagment.sync_targets_to_disk()
        print("[*] Audit results synchronized to targets database.")

if __name__ == "__main__":
    Start()

#!#!#!
root: "true"
name: "Bluetooth Active Auditor"
category: "Recon"
desc: """Active Bluetooth auditing module. 
Performs RFCOMM probing for Samsung-specific services and enumerates BLE GATT characteristics."""
author: "Donald Ford"
#!#!#!
