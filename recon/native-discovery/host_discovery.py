#!#!#!
name: "Async Host Discovery"
description: "Blazing fast concurrent ICMP/ARP sweep."
author: "SuperSploit"
root: "true"
#!#!#!

import asyncio
import ipaddress
import json
import os
import platform
import sqlite3
import sys
import subprocess

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

# Limit concurrent tasks to prevent file descriptor exhaustion
CONCURRENCY_LIMIT = 250

async def ping_host(ip, semaphore):
    """Asynchronously execute a ping command for a single host."""
    # Dynamically handle flags based on the host OS
    param, timeout_flag = ('-n', '-w') if platform.system().lower() == 'windows' else ('-c', '-W')
    timeout_val = '1000' if platform.system().lower() == 'windows' else '1'

    command = ['ping', param, '1', timeout_flag, timeout_val, str(ip)]

    async with semaphore:
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            await proc.wait()
            # Return the IP and a boolean indicating if the ping was successful
            return str(ip), proc.returncode == 0
        except Exception:
            return str(ip), False

async def sweep_icmp(network_cidr):
    """Perform concurrent ICMP ping sweep."""
    try:
        network = ipaddress.ip_network(network_cidr, strict=False)
    except ValueError as e:
        print(f"[-] Invalid CIDR: {e}")
        return []

    print(f"[*] Initiating Layer 3 (ICMP) sweep against {network_cidr}...")
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    # Create an asynchronous task for every host in the subnet
    tasks = [ping_host(ip, semaphore) for ip in network.hosts()]
    results = await asyncio.gather(*tasks)

    return [ip for ip, is_up in results if is_up]

def sweep_arp(active_ips):
    """Retrieve Layer 2 (MAC) mappings from the local ARP cache."""
    print("[*] Initiating Layer 2 (ARP) mapping from local cache...")
    arp_cmd = ['arp', '-a']

    try:
        result = subprocess.run(arp_cmd, capture_output=True, text=True)
        arp_entries = {}
        for line in result.stdout.splitlines():
            for ip in active_ips:
                # Check standard ARP formats depending on OS output
                if f"({ip})" in line or f" {ip} " in line:
                    arp_entries[ip] = line.strip()
        return arp_entries
    except Exception as e:
        print(f"[-] Failed to read ARP table: {e}")
        return {}

def get_target():
    """Retrieve R_HOST from the SuperSploit database."""
    if has_db_manager:
        try:
            return DatabaseManagment.get().get("R_HOST")
        except Exception:
            pass

    # Fallback to manual SQLite read if DB manager is unavailable
    try:
        db_path = os.path.join(framework_root, ".data", ".config", "data.db")
        if not os.path.exists(db_path):
            db_path = os.path.expanduser("~/.SuperSploit/.data/.config/data.db")

        if not os.path.exists(db_path):
            return None
        
        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table[0]
                cursor.execute(f'SELECT value FROM "{table_name}" WHERE key=?', ("R_HOST",))
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except (json.JSONDecodeError, TypeError):
                        return row[0]
        except Exception:
            pass
        finally:
            if conn: conn.close()
    except Exception:
        pass
    return None

def save_targets(active_hosts, arp_mappings):
    """Save discovered targets to the framework's targets database."""
    if has_db_manager:
        try:
            targets = DatabaseManagment.getTargets()
            new_count = 0
            for ip in active_hosts:
                if ip not in targets:
                    targets[ip] = {}
                    new_count += 1
                targets[ip]["status"] = "up"
                targets[ip]["os_family"] = "Unknown"
                targets[ip]["architecture"] = "Unknown"
                mac_info = arp_mappings.get(ip)
                if mac_info:
                    targets[ip]["arp_record"] = mac_info
            
            DatabaseManagment.updateTargets(targets)
            DatabaseManagment.sync_targets_to_disk()
            if new_count > 0:
                print(f"[+] Successfully added {new_count} new targets to the database.")
            else:
                print(f"[*] Target database updated (no new IPs added).")
            return
        except Exception as e:
            print(f"[-] Failed to save via DatabaseManagment: {e}")

    # Fallback to manual JSON write
    try:
        targets_path = os.path.join(framework_root, ".data", ".config", "targets.json")
        if not os.path.exists(os.path.dirname(targets_path)):
            targets_path = os.path.expanduser("~/.SuperSploit/.data/.config/targets.json")

        existing_data = {"TARGETS": {}}
        if os.path.exists(targets_path):
            try:
                with open(targets_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    if "TARGETS" not in existing_data:
                        existing_data["TARGETS"] = {}
            except Exception:
                pass

        targets = existing_data["TARGETS"]
        new_count = 0
        for ip in active_hosts:
            if ip not in targets:
                targets[ip] = {}
                new_count += 1
            targets[ip]["status"] = "up"
            mac_info = arp_mappings.get(ip)
            if mac_info:
                targets[ip]["arp_record"] = mac_info

        with open(targets_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, sort_keys=True)
        if new_count > 0:
            print(f"[+] Successfully added {new_count} new targets to the database.")
        else:
            print(f"[*] Target database updated.")
    except Exception as e:
        print(f"[-] Failed to write to target database: {e}")

async def main():
    target = get_target()
    if not target:
        print("[-] R_HOST is not set. Please use 'set target <IP/CIDR>' in SuperSploit.")
        return

    active_hosts = await sweep_icmp(target)
    print(f"[+] Discovered {len(active_hosts)} active hosts via ICMP.")

    arp_mappings = sweep_arp(active_hosts)

    print("\n[*] Discovery Results:")
    for ip in active_hosts:
        mac_info = arp_mappings.get(ip, "No ARP entry found")
        print(f"    -> {ip} : {mac_info}")
        
    save_targets(active_hosts, arp_mappings)

def Start():
    if platform.system().lower() == 'windows':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())

if __name__ == "__main__":
    Start()
