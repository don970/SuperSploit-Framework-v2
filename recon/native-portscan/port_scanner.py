import sys
import os
import asyncio
import re
import ipaddress

# Dynamically append the framework's source directory to sys.path
# so isolated sudo subprocesses can import the core database modules
_scanner_dir = os.path.dirname(os.path.abspath(__file__))
_framework_root = os.path.abspath(os.path.join(_scanner_dir, "..", ".."))
_source_dir = os.path.join(_framework_root, "source")
if _source_dir not in sys.path:
    sys.path.append(_source_dir)

# Try to import framework modules if running inside SuperSploit
try:
    from core.database import DatabaseManagment
    from core.logger import Logger
    from core.service_db_manager import ServiceDBManager
except ImportError as e:
    print(f"[*] Note: Framework core modules unavailable in sudo environment ({e}). Using native file I/O.")
    DatabaseManagment = None
    Logger = None
    ServiceDBManager = None

#!#!#!
root: "true"
name: "Async Port Scanner"
description: "High-speed asynchronous port scanner with active heuristic service detection."
category: "Scanner"
author: "Donald Ford"
#!#!#!

class ServiceDetector:
    """
    Asynchronous Heuristic Service and Protocol Detector.
    Performs active protocol signature matching and fallback heuristic detection directly over raw sockets.
    """
    
    # Heuristic fallbacks for well-known ports if active probing fails to identify the banner
    COMMON_PORTS = {
        20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
        25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
        111: "RPC", 135: "RPC", 139: "NetBIOS", 143: "IMAP",
        443: "HTTPS", 445: "SMB", 993: "IMAPS", 995: "POP3S",
        1433: "MSSQL", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL",
        5900: "VNC", 8000: "HTTP-Alt", 8080: "HTTP-Proxy", 8443: "HTTPS-Proxy"
    }

    # Active protocol signatures (Regex mapped against raw byte responses)
    SIGNATURES = {
        rb"^SSH-\d\.\d": "SSH",
        rb"^HTTP/1\.[01] \d\d\d": "HTTP",
        b"^220.*FTP": "FTP",
        b"^220.*SMTP": "SMTP",
        b"^220.*ESMTP": "SMTP",
        rb"^\+OK": "POP3",
        rb"^\* OK.*IMAP": "IMAP",
        b"mysql_native_password": "MySQL",
        rb"RFB \d{3}\.\d{3}": "VNC",
        b"^\x15\x03": "TLS/SSL",
        b"Server: Werkzeug": "Werkzeug (Python HTTP)",
        b"Server: Apache": "Apache HTTP",
        b"Server: nginx": "Nginx HTTP"
    }

    NMAP_COMPILED_SIGS = []
    _nmap_loaded = False

    @classmethod
    def load_nmap_db(cls):
        """Dynamically loads and compiles the Nmap service probes database."""
        if cls._nmap_loaded:
            return
            
        # Check if the database was already compiled and cached in the global sys module.
        # This prevents re-parsing the huge file if the framework reloads this module dynamically.
        if hasattr(sys, '_supersploit_nmap_cache'):
            cls.NMAP_COMPILED_SIGS = sys._supersploit_nmap_cache
            cls._nmap_loaded = True
            return
        
        try:
            # Prevent NameError if the core database modules failed to import
            if not ServiceDBManager:
                cls._nmap_loaded = True
                return
            db_manager = ServiceDBManager()
            all_matches = db_manager.get_all_matches()
            for service_name, pattern in all_matches:
                try:
                    # Clean pattern for Python regex
                    regex_str = pattern.replace('\\0', '\\x00')
                    compiled = re.compile(regex_str.encode('latin-1'), re.IGNORECASE)
                    cls.NMAP_COMPILED_SIGS.append((compiled, service_name))
                except Exception:
                    continue
            cls._nmap_loaded = True
        except Exception as e:
            print(f"[-] Database error loading service probes: {e}")

        # Save the compiled database to the global interpreter memory for instant future scans
        sys._supersploit_nmap_cache = cls.NMAP_COMPILED_SIGS

    @classmethod
    async def detect(cls, ip: str, port: int, timeout: float = 1.5):
        """
        Attempts to connect to a port, grab the banner, and detect the service.
        Uses a dual-probe approach (Passive listening -> Active HTTP/Generic payload).
        """
        service = "Unknown"
        banner_display = ""

        if not cls._nmap_loaded:
            cls.load_nmap_db()

        try:
            # DEBUG TIP: asyncio.wait_for wraps the TCP handshake to ensure dead IPs 
            # don't cause the asynchronous event loop to hang indefinitely.
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), 
                timeout=timeout
            )
            
            # 1. PASSIVE PROBE (Wait for the service to speak first, e.g., SSH or FTP)
            raw_banner = b""
            try:
                raw_banner = await asyncio.wait_for(reader.read(2048), timeout=timeout/3)
            except asyncio.TimeoutError:
                pass
            
            # 2. ACTIVE PROBE (If passive yields nothing, actively poke it)
            if not raw_banner:
                # Generic HTTP payload elicits responses from most HTTP/REST/Proxy servers
                probe = f"GET / HTTP/1.1\r\nHost: {ip}\r\nAccept: */*\r\n\r\n".encode()
                writer.write(probe)
                
                try:
                    await asyncio.wait_for(writer.drain(), timeout=timeout/3)
                except Exception:
                    pass
                
                try:
                    raw_banner = await asyncio.wait_for(reader.read(2048), timeout=timeout/3)
                except asyncio.TimeoutError:
                    pass
            
            # Clean up the socket
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), timeout=timeout/3)
            except Exception:
                pass
            
            # 3. SIGNATURE MATCHING
            if raw_banner:
                # Clean up the banner string to be terminal-friendly
                decoded_banner = raw_banner.decode('utf-8', errors='ignore').strip()
                
                # Extract key HTTP headers if present
                headers = {}
                if b"HTTP/" in raw_banner:
                    for line in decoded_banner.split('\n'):
                        if ": " in line:
                            k, v = line.split(": ", 1)
                            headers[k.lower().strip()] = v.strip()
                
                server = headers.get("server", "")
                powered = headers.get("x-powered-by", "")
                auth = headers.get("www-authenticate", "")
                
                banner_info = []
                if server: banner_info.append(f"Server: {server}")
                if powered: banner_info.append(f"Powered: {powered}")
                if auth: banner_info.append(f"Auth: {auth}")
                
                if not banner_info:
                    banner_display = decoded_banner.split('\r\n')[0].split('\n')[0][:80]
                else:
                    banner_display = " | ".join(banner_info)
                
                for sig, srv in cls.SIGNATURES.items():
                    if re.search(sig, raw_banner, re.IGNORECASE):
                        service = srv
                        break
                        
                # Fallback to the massive Nmap database if our hardcoded signatures fail
                if service == "Unknown" and cls.NMAP_COMPILED_SIGS:
                    for sig_regex, srv in cls.NMAP_COMPILED_SIGS:
                        if sig_regex.search(raw_banner):
                            service = srv
                            break
                        
            # 4. HEURISTIC FALLBACK
            if service == "Unknown" and port in cls.COMMON_PORTS:
                service = cls.COMMON_PORTS[port]
                
            # Quick TLS identification fallback if no banner was extracted
            if not banner_display and port in [443, 8443]:
                service = "HTTPS"
                
            return "OPEN", service, banner_display

        except (ConnectionRefusedError, OSError):
            # Port is definitively closed or unreachable
            return "CLOSED", "", ""
        except asyncio.TimeoutError:
            # TCP handshake timed out (Filtered / Dropped by Firewall)
            return "FILTERED", "", ""
        except Exception:
            return "CLOSED", "", ""


async def scan_port(ip, port, timeout, semaphore, open_ports):
    """Worker function constrained by an asyncio Semaphore to limit concurrent file descriptors."""
    async with semaphore:
        status, service, banner = await ServiceDetector.detect(ip, port, timeout)
        
        if status == "OPEN":
            open_ports.append({"port": port, "service": service, "banner": banner})
            banner_str = f" | Banner: {banner}" if banner else ""
            print(f"[+] Port {port:<5} | {service:<10} | OPEN {banner_str}")


async def scan_host(ip, ports, concurrency, timeout):
    print(f"[*] Starting Async Port Scan on {ip} ({len(ports)} ports)")
    print(f"[*] Concurrency Limit: {concurrency} tasks | Timeout: {timeout}s\n")
    
    semaphore = asyncio.Semaphore(concurrency)
    open_ports = []
    
    tasks = [scan_port(ip, port, timeout, semaphore, open_ports) for port in ports]
    await asyncio.gather(*tasks)
    
    return open_ports


def Start(args=None):
    # Dynamically pull scope configurations from the framework database
    if DatabaseManagment:
        db = DatabaseManagment.get()
        target_ip = db.get("R_HOST")
        if not target_ip:
            target_ip = "127.0.0.1"
        port_scope = str(db.get("PORT_RANGE", "1-65535"))
        concurrency = int(db.get("THREADS", db.get("CONCURRENCY", 500)))
        timeout = float(db.get("TIMEOUT", db.get("SCAN_TIMEOUT", 1.5)))
    else:
        # Fallback to direct file read if the core framework fails to import under sudo
        try:
            import json
            import sqlite3
            db_path = os.path.join(_framework_root, ".data", ".config", "data.db")
            db = {}
            with sqlite3.connect(db_path) as conn:
                for key, value in conn.execute("SELECT key, value FROM variables"):
                    try:
                        db[key] = json.loads(value)
                    except Exception:
                        db[key] = value
            target_ip = db.get("R_HOST", "127.0.0.1")
            port_scope = str(db.get("PORT_RANGE", "1-65535"))
            concurrency = int(db.get("THREADS", db.get("CONCURRENCY", 500)))
            timeout = float(db.get("TIMEOUT", db.get("SCAN_TIMEOUT", 1.5)))
        except Exception:
            target_ip = args[0] if args else "127.0.0.1"
            port_scope = "1-65535"
            concurrency = 500
            timeout = 1.5

    ports_list = []
    try:
        # Support for comma-separated ports and ranges (e.g., "80,443,1000-2000")
        for part in port_scope.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                ports_list.extend(range(start, end + 1))
            elif part: # Ensure part is not an empty string
                ports_list.append(int(part))
        # Remove duplicates and sort for clean, ordered scanning
        ports_list = sorted(list(set(ports_list)))
        if not ports_list:
            raise ValueError("No valid ports parsed from scope.")
    except ValueError:
        print(f"[!] Invalid PORT_RANGE '{port_scope}'. Defaulting to 1-1024.")
        ports_list = list(range(1, 1025))
        
    # Convert the target into a list of IPs to natively support CIDR (e.g. 192.168.0.1/24)
    try:
        network = ipaddress.ip_network(target_ip, strict=False)
        hosts = [str(ip) for ip in network.hosts()] if network.num_addresses > 1 else [str(network.network_address)]
    except ValueError:
        # Fallback for standard domain names like example.com
        hosts = [target_ip]

    for host in hosts:
        open_ports = asyncio.run(scan_host(host, ports_list, concurrency=concurrency, timeout=timeout))
        
        print(f"\n[+] Scan Complete. Found {len(open_ports)} open ports for {host}.")
        
        # Log discovery seamlessly to the Target Database cache
        if open_ports:
            if DatabaseManagment:
                print(f"[*] Saving port data for {host} to the targets database...")
                targets_db = DatabaseManagment.getTargets()

                target_entry = targets_db.setdefault(host, {})
                # Ensure target_entry is a dictionary (fixes crashes on corrupt/legacy data)
                if not isinstance(target_entry, dict):
                    target_entry = {}
                    targets_db[host] = target_entry

                # Intelligent merge to prevent overwriting existing discovered ports
                existing_ports = target_entry.get("open_ports", [])
                if not isinstance(existing_ports, list):
                    existing_ports = []
                    
                # Convert to dict for deduplication by port number
                port_map = {p["port"]: p for p in existing_ports}
                for new_port in open_ports:
                    port_map[new_port["port"]] = new_port
                    
                target_entry["open_ports"] = sorted(list(port_map.values()), key=lambda x: x["port"])

                DatabaseManagment.updateTargets(targets_db)
                DatabaseManagment.sync_targets_to_disk()
                print("[+] Database updated successfully.")
            else:
                # Native JSON fallback for sudo isolation
                try:
                    import json
                    targets_path = os.path.join(_framework_root, ".data", ".config", "targets.json")
                    print(f"[*] Saving port data for {host} directly to {targets_path}...")
                    try:
                        with open(targets_path, "r", encoding="utf-8") as f:
                            targets_data = json.load(f)
                    except Exception:
                        targets_data = {"TARGETS": {}}

                    target_entry = targets_data.setdefault("TARGETS", {}).setdefault(host, {})
                    # Ensure target_entry is a dictionary for the native fallback as well
                    if not isinstance(target_entry, dict):
                        target_entry = {}
                        targets_data["TARGETS"][host] = target_entry
                    
                    # Intelligent merge to prevent overwriting existing discovered ports natively
                    existing_ports = target_entry.get("open_ports", [])
                    if not isinstance(existing_ports, list):
                        existing_ports = []
                        
                    # Convert to dict for deduplication by port number
                    port_map = {p["port"]: p for p in existing_ports}
                    for new_port in open_ports:
                        port_map[new_port["port"]] = new_port
                        
                    target_entry["open_ports"] = sorted(list(port_map.values()), key=lambda x: x["port"])

                    with open(targets_path, "w", encoding="utf-8") as f:
                        json.dump(targets_data, f, indent=4, sort_keys=True)
                    print("[+] Database updated successfully.")
                except Exception as e:
                    print(f"[-] Failed to update targets natively: {e}")


if __name__ == "__main__":
    Start(sys.argv[1:])