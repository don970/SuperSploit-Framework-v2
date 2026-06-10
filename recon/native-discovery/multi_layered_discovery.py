"""
Advanced Multi-Layered Network Discovery Module
Identifies nested network layers (hops) and performs discovery on both inner and outer subnets.
Optimized for scenarios where a device (like a phone) is acting as a repeater/hotspot.
"""

import os
import sys
import ipaddress
import subprocess
import json
import socket
import logging
from scapy.all import IP, ICMP, sr1, conf, ARP, Ether, srp, sr

# Dynamically resolve paths for SuperSploit integration
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
source_dir = os.path.join(framework_root, "source")
if source_dir not in sys.path:
    sys.path.append(source_dir)

try:
    from core.database import DatabaseManagment
    has_db_manager = True
except ImportError:
    has_db_manager = False

# Suppress Scapy's default routing and runtime warnings
conf.verb = 0
logging.getLogger("scapy").setLevel(logging.ERROR)

class MultiLayerDiscovery:
    def __init__(self):
        self.layers = []
        self.discovered_hosts = {}
        self.gateway_macs = {}

    def get_local_mac(self, ip):
        """Get the MAC address of a local IP via ARP."""
        try:
            ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=0)
            if ans:
                return ans[0][1].hwsrc
        except Exception:
            pass
        return "Unknown"

    def guess_os(self, ttl):
        """Estimate OS based on ICMP TTL values."""
        if ttl <= 64:
            return "Linux/Android/iOS"
        elif ttl <= 128:
            return "Windows"
        elif ttl <= 254:
            return "Solaris/Cisco"
        return "Unknown"

    def get_route_hops(self, target="8.8.8.8", max_hops=10):
        """Perform a traceroute to identify network layers and guess device types."""
        print(f"[*] Mapping network layers via traceroute to {target}...")
        hops = []
        for ttl in range(1, max_hops + 1):
            pkt = IP(dst=target, ttl=ttl) / ICMP()
            reply = sr1(pkt, timeout=2, verbose=0)
            if reply is None:
                print(f"  Hop {ttl}: * (No Response)")
                continue
            
            hop_ip = reply.src
            os_guess = self.guess_os(reply.ttl)
            
            # Special handling for the first hop (The Phone)
            mac = "N/A"
            if ttl == 1:
                mac = self.get_local_mac(hop_ip)
                print(f"  Hop {ttl}: {hop_ip:<15} | [Phone/Gateway] | MAC: {mac} | OS: {os_guess}")
            else:
                print(f"  Hop {ttl}: {hop_ip:<15} | [Router/Hop]    | OS: {os_guess}")
            
            hops.append({"ip": hop_ip, "ttl": ttl, "mac": mac, "os": os_guess})
            
            if hop_ip == target:
                break
        return hops

    def scan_subnet_parallel(self, subnet):
        """Perform parallel ICMP discovery on a specific subnet."""
        print(f"[*] Initiating parallel sweep on: {subnet}")
        try:
            network = ipaddress.IPv4Network(subnet, strict=False)
            ips = [str(ip) for ip in network.hosts()]
            
            # Optimization: Cap at 254 for safety in this module
            if len(ips) > 254:
                ips = ips[:254]

            packets = [IP(dst=ip) / ICMP() for ip in ips]
            ans, unans = sr(packets, timeout=2, inter=0.01, retry=0, verbose=0)
            
            found = []
            for snd, rcv in ans:
                found.append({
                    "ip": rcv.src,
                    "ttl": rcv.ttl,
                    "os": self.guess_os(rcv.ttl)
                })
            return found
        except Exception as e:
            print(f"  [-] Scan error: {e}")
            return []

    def start_discovery(self):
        # 1. Identify Hops
        self.layers = self.get_route_hops()
        
        if not self.layers:
            print("[-] Could not identify any network layers.")
            return

        print(f"\n[+] Network Topology: {len(self.layers)} visible layers.")
        
        # 2. Analyze and Scan Layers
        for i, hop_data in enumerate(self.layers):
            hop_ip = hop_data["ip"]
            is_private = ipaddress.IPv4Address(hop_ip).is_private
            
            # Skip the public target if we reached it
            if not is_private: continue

            type_label = "Inner Hotspot (Phone)" if i == 0 else f"Outer Layer {i+1}"
            print(f"\n[*] Scanning {type_label}: Gateway {hop_ip}")
            
            # Subnet Heuristic
            target_subnet = ".".join(hop_ip.split(".")[:-1]) + ".0/24"
            found_hosts = self.scan_subnet_parallel(target_subnet)
            
            for host in found_hosts:
                ip = host["ip"]
                # Don't overwrite the gateway info if we found it in the sweep
                if ip == hop_ip:
                    self.discovered_hosts[ip] = {
                        "status": "up",
                        "layer": i + 1,
                        "type": "Gateway",
                        "mac": hop_data["mac"],
                        "os": hop_data["os"]
                    }
                else:
                    self.discovered_hosts[ip] = {
                        "status": "up",
                        "layer": i + 1,
                        "type": "Client",
                        "os": host["os"]
                    }
                print(f"    [+] {ip:<15} | Type: {self.discovered_hosts[ip]['type']:<8} | OS: {host['os']}")

        # 3. Persistence
        if self.discovered_hosts and has_db_manager:
            print(f"\n[*] Saving {len(self.discovered_hosts)} targets to database...")
            targets = DatabaseManagment.getTargets()
            # Update targets intelligently
            for ip, info in self.discovered_hosts.items():
                if ip in targets:
                    targets[ip].update(info)
                else:
                    targets[ip] = info
            
            DatabaseManagment.updateTargets(targets)
            DatabaseManagment.sync_targets_to_disk()
            print("[+] Discovery results persisted.")

def Start():
    discovery = MultiLayerDiscovery()
    discovery.start_discovery()

if __name__ == "__main__":
    Start()

#!#!#!
root: "true"
name: "Multi-Layered Network Discovery"
category: "Discovery"
desc: "Advanced hop-by-hop discovery for nested networks (Hotspots/Repeaters). Maps layers via TTL analysis and scans outer subnets."
author: "Gemini CLI"
#!#!#!
