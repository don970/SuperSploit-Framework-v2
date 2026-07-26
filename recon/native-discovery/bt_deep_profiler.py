"""
Bluetooth Deep Profiler
Performs advanced SDP browsing and L2CAP PSM probing.
Extracts detailed service attributes and identifies non-standard protocols.
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

class BluetoothDeepProfiler:
    """
    Deep profiling engine for Bluetooth targets.
    """
    def __init__(self, target_mac: str, session_id: str | None = None, debug_mode: bool = False):
        self.target_mac = target_mac
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = self._setup_logger(debug_mode)

    def _setup_logger(self, debug_mode: bool) -> logging.Logger:
        logger = logging.getLogger(f"BTDeepProfiler_{self.session_id}")
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - [%(levelname)s] - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def _run_command(self, cmd: list[str], timeout: int = 15) -> str:
        try:
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=timeout).decode()
        except Exception as e:
            self.logger.debug(f"Command failed: {cmd} - {e}")
            return ""

    def browse_sdp(self) -> dict:
        """
        Browses all SDP records and parses them into a structured format.
        """
        self.logger.info(f"Initiating deep SDP browse on {self.target_mac}...")
        sdp_output = self._run_command(["sdptool", "browse", "--raw", self.target_mac])
        
        if not sdp_output:
            self.logger.warning("No SDP records retrieved.")
            return {}

        records = {}
        # Simple parsing for raw SDP output
        # A real parser would be more complex, but we'll extract UUIDs and Service Names
        current_record = None
        
        # Re-run browse without --raw for easier parsing of standard fields
        readable_output = self._run_command(["sdptool", "browse", self.target_mac])
        
        current_svc = ""
        for line in readable_output.split('\n'):
            line = line.strip()
            if line.startswith("Service Name:"):
                current_svc = line.split(":", 1)[1].strip()
                records[current_svc] = {}
            elif current_svc and ":" in line:
                key, val = line.split(":", 1)
                records[current_svc][key.strip()] = val.strip()

        self.logger.info(f"[+] Successfully mapped {len(records)} SDP services.")
        return records

    def probe_l2cap_psms(self) -> list[int]:
        """
        Attempts to connect to common L2CAP PSMs to identify open listeners.
        Note: This is an active probe and can be noisy.
        """
        common_psms = [
            1,    # SDP
            3,    # RFCOMM
            5,    # TCS-BIN
            17,   # HID Control
            19,   # HID Interrupt
            25,   # BNEP
            31,   # HID_Proxy
            33,   # AVCTP
            35,   # AVDTP
            39,   # AVCTP_Browsing
            65,   # ATT (BLE over BR/EDR)
        ]
        
        open_psms = []
        self.logger.info(f"Probing {len(common_psms)} common L2CAP PSMs...")
        
        for psm in common_psms:
            # We use 'l2ping' as a check for reachability first, 
            # but connecting to a PSM requires a socket.
            # Using python sockets for PSM probing
            import socket
            try:
                # AF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_L2CAP
                # These constants might not be available on all systems via socket module
                # but standard on Linux with BlueZ
                sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_SEQPACKET, socket.BTPROTO_L2CAP)
                sock.settimeout(2)
                sock.connect((self.target_mac, psm))
                self.logger.info(f"[+] PSM {psm} is OPEN")
                open_psms.append(psm)
                sock.close()
            except Exception:
                pass
                
        return open_psms

    def profile(self) -> dict:
        results = {
            "mac": self.target_mac,
            "sdp_records": self.browse_sdp(),
            "open_psms": self.probe_l2cap_psms(),
            "timestamp": time.time()
        }
        return results

def Start():
    # Prioritize command line argument
    target_mac = ""
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        target_mac = sys.argv[1]
    
    # Fallback to database
    if not target_mac and has_db_manager:
        target_mac = DatabaseManagment.get().get("R_MAC", "")

    if not target_mac:
        print("[-] Error: No target MAC specified. Set R_MAC or provide as argument.")
        return

    profiler = BluetoothDeepProfiler(target_mac, debug_mode=True)
    print(f"[*] Starting Deep Bluetooth Profiling on {target_mac}...")
    results = profiler.profile()

    print("\n[+] Deep Profile Results:")
    print(f"    - SDP Services Found: {len(results['sdp_records'])}")
    for svc, details in results['sdp_records'].items():
        print(f"      -> {svc}")
        if 'Service ID' in details:
            print(f"         ID: {details['Service ID']}")
    
    print(f"    - Open L2CAP PSMs:    {results['open_psms']}")

    # Save results to database
    if has_db_manager:
        targets = DatabaseManagment.getTargets()
        if target_mac in targets:
            targets[target_mac]["deep_profile"] = results
            # Extract more specific OS info if possible
            if "Android" in str(results['sdp_records']) or "Google" in str(results['sdp_records']):
                targets[target_mac]["os_family"] = "Android"
            elif "Apple" in str(results['sdp_records']) or "iOS" in str(results['sdp_records']):
                targets[target_mac]["os_family"] = "iOS/macOS"
                
            DatabaseManagment.updateTargets(targets)
            DatabaseManagment.sync_targets_to_disk()
            print("[*] Deep profile data synchronized to targets database.")

if __name__ == "__main__":
    Start()

#!#!#!
root: "true"
name: "Bluetooth Deep Profiler"
category: "Recon"
desc: """Deep protocol-level Bluetooth profiler. 
Performs comprehensive SDP browsing and L2CAP PSM probing to identify hidden services and transport-layer listeners."""
author: "Donald Ford"
#!#!#!
