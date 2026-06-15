"""
Lateral Network Host Discovery Engine
Utilizes broadcast and multicast protocols (NBNS, mDNS, LLMNR, SSDP) to discover hosts.
Bypasses standard ICMP-blocking firewalls by leveraging discovery protocols typically allowed.
"""

import json
import logging
import uuid
import os
import ipaddress
import socket
import sys
from scapy.all import IP, UDP, TCP, sr1, Ether, srp, sr, conf, DNS, DNSQR, NBNSQueryRequest, Raw
from scapy.error import Scapy_Exception

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

install_location = f'{os.getenv("HOME")}/.SuperSploit'
path_to_targets_db = f"{install_location}/.data/.config/targets.json"

# Suppress Scapy's default routing warnings
conf.verb = 0
logging.getLogger("scapy").setLevel(logging.ERROR)


class LateralDiscoveryEngine:
    """
    A modular discovery engine leveraging broadcast and multicast protocols.
    """
    def __init__(self, session_id: str | None = None, debug_mode: bool = False):
        self.session_id = session_id or str(uuid.uuid4())
        self.logger = self._setup_logger(debug_mode)

    def _setup_logger(self, debug_mode: bool) -> logging.Logger:
        logger = logging.getLogger(f"LateralDiscovery_{self.session_id}")
        logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - [Session: {self.session_id}] - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger

    def nbns_sweep(self, broadcast_addr: str) -> list[dict]:
        """
        NetBIOS Name Service (NBNS) Node Status Request.
        Discovers NetBIOS names and machine information on the local network.
        """
        self.logger.info(f"Initiating NBNS sweep on {broadcast_addr}...")
        live_hosts = []
        try:
            # NBNS Node Status Request
            # '*' (padded with spaces) is the wildcard name for "this host"
            query_name = "*" + " " * 15
            packet = IP(dst=broadcast_addr) / UDP(sport=137, dport=137) / NBNSQueryRequest(QUESTION_NAME=query_name, QUESTION_TYPE=0x0021)
            
            ans, unans = sr(packet, timeout=2, retry=1, verbose=0)
            
            for snd, rcv in ans:
                hostname = "Unknown"
                if rcv.haslayer(Raw):
                    # Basic extraction of the first name in the NBNS response
                    # NBNS responses are complex; this is a simplified heuristic extraction
                    raw_data = rcv.getlayer(Raw).load
                    if len(raw_data) > 57:
                        hostname = raw_data[57:72].decode('utf-8', errors='ignore').strip()

                live_hosts.append({
                    "ip": rcv.src,
                    "hostname": hostname,
                    "protocol": "NBNS"
                })
                self.logger.debug(f"Host up (NBNS): {rcv.src} - {hostname}")
                
        except Exception as e:
            self.logger.error(f"NBNS sweep error: {e}")
            
        return live_hosts

    def mdns_sweep(self) -> list[dict]:
        """
        Multicast DNS (mDNS) Service Discovery.
        Queries the standard mDNS multicast address for all services.
        """
        self.logger.info("Initiating mDNS (Bonjour/Avahi) sweep...")
        live_hosts = []
        mdns_ip = "224.0.0.251"
        try:
            # Query for _services._dns-sd._udp.local.
            packet = IP(dst=mdns_ip) / UDP(sport=5353, dport=5353) / DNS(rd=1, qd=DNSQR(qname="_services._dns-sd._udp.local"))
            
            ans, unans = sr(packet, timeout=2, retry=1, verbose=0)
            
            for snd, rcv in ans:
                hostname = "mDNS Responder"
                if rcv.haslayer(DNS) and rcv[DNS].ancount > 0:
                    # Try to find a name in the answers or additional records
                    for i in range(rcv[DNS].ancount):
                        res = rcv[DNS].an[i]
                        if res.type == 12:  # PTR record
                            name = res.rdata.decode('utf-8', errors='ignore').split('.')[0]
                            if name and not name.startswith('_'):
                                hostname = name
                                break
                
                live_hosts.append({
                    "ip": rcv.src,
                    "hostname": hostname,
                    "protocol": "mDNS"
                })
                self.logger.debug(f"Host up (mDNS): {rcv.src} - {hostname}")
                
        except Exception as e:
            self.logger.error(f"mDNS sweep error: {e}")
            
        return live_hosts

    def llmnr_sweep(self) -> list[dict]:
        """
        Link-Local Multicast Name Resolution (LLMNR) Probe.
        Queries for a common but often unassigned name to elicit responses from Windows hosts.
        """
        self.logger.info("Initiating LLMNR sweep...")
        live_hosts = []
        llmnr_ip = "224.0.0.252"
        try:
            # Query for 'WPAD' (Web Proxy Auto-Discovery)
            packet = IP(dst=llmnr_ip) / UDP(sport=5355, dport=5355) / DNS(rd=1, qd=DNSQR(qname="WPAD"))
            
            ans, unans = sr(packet, timeout=2, retry=1, verbose=0)
            
            for snd, rcv in ans:
                hostname = "Windows (LLMNR)"
                # LLMNR responses usually contain the host's actual name in the response
                if rcv.haslayer(DNS) and rcv[DNS].ancount > 0:
                    hostname = rcv[DNS].an[0].rrname.decode('utf-8', errors='ignore').split('.')[0]

                live_hosts.append({
                    "ip": rcv.src,
                    "hostname": hostname,
                    "protocol": "LLMNR"
                })
                self.logger.debug(f"Host up (LLMNR): {rcv.src} - {hostname}")
                
        except Exception as e:
            self.logger.error(f"LLMNR sweep error: {e}")
            
        return live_hosts

    def ssdp_sweep(self) -> list[dict]:
        """
        Simple Service Discovery Protocol (SSDP) M-SEARCH.
        Discovers UPnP/DLNA devices on the network.
        """
        self.logger.info("Initiating SSDP (UPnP) sweep...")
        live_hosts = []
        ssdp_ip = "239.255.255.250"
        ssdp_payload = (
            'M-SEARCH * HTTP/1.1\r\n'
            'HOST: 239.255.255.250:1900\r\n'
            'MAN: "ssdp:discover"\r\n'
            'MX: 2\r\n'
            'ST: ssdp:all\r\n'
            '\r\n'
        )
        try:
            packet = IP(dst=ssdp_ip) / UDP(sport=1900, dport=1900) / Raw(load=ssdp_payload)
            
            ans, unans = sr(packet, timeout=3, retry=1, verbose=0)
            
            for snd, rcv in ans:
                hostname = "UPnP Device"
                if rcv.haslayer(Raw):
                    load = rcv.getlayer(Raw).load.decode('utf-8', errors='ignore')
                    for line in load.split('\r\n'):
                        if line.upper().startswith("SERVER:"):
                            hostname = line.split(":", 1)[1].strip()
                            break
                        if line.upper().startswith("LOCATION:"):
                            # Use LOCATION as a fallback/hint if SERVER is missing
                            hostname = f"UPnP ({line.split(':', 1)[1].strip()})"

                live_hosts.append({
                    "ip": rcv.src,
                    "hostname": hostname,
                    "protocol": "SSDP"
                })
                self.logger.debug(f"Host up (SSDP): {rcv.src} - {hostname}")
                
        except Exception as e:
            self.logger.error(f"SSDP sweep error: {e}")
            
        return live_hosts


def Start():
    db = DatabaseManagment.get() if has_db_manager else {}
    target_cidr = str(db.get("R_HOST", ""))
    
    # Heuristic to determine broadcast address if not explicitly provided
    if target_cidr and "/" in target_cidr:
        try:
            network = ipaddress.IPv4Network(target_cidr, strict=False)
            broadcast_addr = str(network.broadcast_address)
        except ValueError:
            broadcast_addr = "255.255.255.255"
    else:
        # If it's a single IP or empty, default to global broadcast to find neighbors
        broadcast_addr = "255.255.255.255"

    engine = LateralDiscoveryEngine(debug_mode=True)
    print(f"[*] Starting Lateral Broadcast Discovery (Broadcast: {broadcast_addr})")

    # Run sweeps
    results = []
    results.extend(engine.nbns_sweep(broadcast_addr))
    results.extend(engine.mdns_sweep())
    results.extend(engine.llmnr_sweep())
    results.extend(engine.ssdp_sweep())

    # Deduplicate and merge results
    discovered = {}
    for host in results:
        ip = host['ip']
        if ip not in discovered:
            discovered[ip] = host
        else:
            # Merge hostname if current is Unknown
            if discovered[ip]['hostname'] == "Unknown" and host['hostname'] != "Unknown":
                discovered[ip]['hostname'] = host['hostname']
            # Append protocols
            if host['protocol'] not in discovered[ip]['protocol']:
                discovered[ip]['protocol'] += f", {host['protocol']}"

    print(f"\n[+] Discovery Complete. Found {len(discovered)} active hosts via broadcast/multicast.")
    
    target_updates = {}
    for ip, data in sorted(discovered.items(), key=lambda x: ipaddress.IPv4Address(x[0])):
        print(f"[+] Target: {ip:<15} | Hostname: {data['hostname']:<15} | Protocol: {data['protocol']}")
        target_updates[ip] = {
            "status": "up",
            "hostname": data['hostname'],
            "discovery_method": data['protocol']
        }

    # Save to targets database
    if target_updates:
        print(f"[*] Saving {len(target_updates)} hosts to the targets database...")
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

            for ip, info in target_updates.items():
                if ip not in existing_targets or not isinstance(existing_targets[ip], dict):
                    existing_targets[ip] = info
                else:
                    existing_targets[ip].update(info)
            
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
name: "Lateral Broadcast Discovery"
category: "Discovery"
desc: """Leverages broadcast and multicast protocols (NBNS, mDNS, LLMNR, SSDP) to 
discover local hosts and their hostnames. Extremely effective at bypassing 
standard host-based firewalls that block ICMP/ARP sweeps."""
author: "Donald Ford"
#!#!#!
