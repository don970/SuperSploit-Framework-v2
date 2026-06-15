#!#!#!
root: "true"
name: "Nmap OS Fingerprinting"
category: "reconnaissance"
description: "Performs OS fingerprinting using Nmap-style probes and matches against the nmap-os-db."
author: "Donald Ford"
#!#!#!
import asyncio
import logging
import os
import json
import re
import time
import math
import random
import sys
import urllib.request
import ssl
from scapy.all import IP, TCP, UDP, ICMP, sr1, sr, conf, arping

# --- Framework Integration ---
# Dynamically append the framework's source directory to sys.path
_scanner_dir = os.path.dirname(os.path.abspath(__file__))
_framework_root = os.path.abspath(os.path.join(_scanner_dir, "..", ".."))
_source_dir = os.path.join(_framework_root, "source")
if _source_dir not in sys.path:
    sys.path.append(_source_dir)

try:
    from core.database import DatabaseManagment
except ImportError as e:
    print(f"[*] Note: Framework core modules unavailable in sudo environment ({e}). Using native file I/O.")
    DatabaseManagment = None

# Suppress Scapy's verbose output and set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
conf.verb = 0

# --- Database Paths ---
path_to_db_config = os.path.join(_framework_root, ".data", ".config", "data.json")
path_to_nmap_db = os.path.join(_framework_root, ".data", ".config", "nmap-os-db.txt")
path_to_targets = os.path.join(_framework_root, ".data", ".config", "targets.json")

# ---------------------------------------------------------
# 1. NMAP MATCH POINTS (WEIGHTS)
# ---------------------------------------------------------
MATCH_POINTS = {
    "SEQ": {"SP": 25, "GCD": 75, "ISR": 25, "TI": 100, "CI": 50, "II": 100, "SS": 80, "TS": 100},
    "OPS": {"O1": 20, "O2": 20, "O3": 20, "O4": 20, "O5": 20, "O6": 20},
    "WIN": {"W1": 15, "W2": 15, "W3": 15, "W4": 15, "W5": 15, "W6": 15},
    "ECN": {"R": 100, "DF": 20, "T": 15, "TG": 15, "W": 15, "O": 15, "CC": 100, "Q": 20},
    "T1":  {"R": 100, "DF": 20, "T": 15, "TG": 15, "S": 20, "A": 20, "F": 30, "RD": 20, "Q": 20},
    "T2":  {"R": 80,  "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "T3":  {"R": 80,  "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "T4":  {"R": 100, "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "T5":  {"R": 100, "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "T6":  {"R": 100, "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "T7":  {"R": 80,  "DF": 20, "T": 15, "TG": 15, "W": 25, "S": 20, "A": 20, "F": 30, "O": 10, "RD": 20, "Q": 20},
    "U1":  {
        "R": 50, "DF": 20, "T": 15, "TG": 15, "IPL": 100, "UN": 100, 
        "RIPL": 100, "RID": 100, "RIPCK": 100, "RUCK": 50, "RUD": 100
    },
    "IE":  {"R": 50,  "DFI": 40, "T": 15, "TG": 15, "CD": 100}
}


class OSFingerprintEngine:
    """
    Executes Nmap-style OS Fingerprinting Probes using Scapy.
    Requires an open TCP port and a closed TCP port to run all tests accurately.
    """
    def __init__(self, target_ip: str, open_tcp: int, closed_tcp: int, closed_udp: int = 31337):
        self.target = target_ip
        self.open_tcp = open_tcp
        self.closed_tcp = closed_tcp
        self.closed_udp = closed_udp
        self.results = {}

    def run_all_probes(self):
        """Executes all probe types concurrently using asyncio."""
        logging.info(f"[*] Starting OS Fingerprint against {self.target}")
        return asyncio.run(self._async_run_all_probes())

    async def _async_run_all_probes(self):
        # asyncio.to_thread natively offloads blocking Scapy calls to background threads
        tasks = [
            asyncio.to_thread(self._probe_seq_ops_win),
            asyncio.to_thread(self._probe_ecn),
            asyncio.to_thread(self._probe_t1_t7),
            asyncio.to_thread(self._probe_u1),
            asyncio.to_thread(self._probe_ie)
        ]
        await asyncio.gather(*tasks)
        return self.results

    def _parse_response(self, pkt, probe_name, sent_pkt=None):
        """Helper to parse common TCP/IP header fields from a response packet."""
        if not pkt:
            return {"R": "N"}

        resp = {"R": "Y"}
        if pkt.haslayer(IP):
            resp["DF"] = "Y" if pkt[IP].flags.DF else "N"
            resp["T"] = hex(pkt[IP].ttl)[2:].upper()
            resp["TG"] = self._get_ttl_guess(pkt[IP].ttl)

        if pkt.haslayer(TCP):
            # Window size
            resp["W"] = hex(pkt[TCP].window)[2:].upper()

            # Flags: Nmap uses shorthand like SA, RA, etc.
            flags = str(pkt[TCP].flags)
            resp["F"] = flags.upper()

            # TCP Options parsing (Nmap-style shorthand)
            opts = []
            for opt, val in pkt[TCP].options:
                if opt == 'MSS':
                    opts.append(f"M{hex(val)[2:].upper()}")
                elif opt == 'NOP':
                    opts.append("N")
                elif opt == 'WScale':
                    opts.append(f"W{hex(val)[2:].upper()}")
                elif opt == 'Timestamp':
                    # Nmap T is followed by two 1-digit bits indicating if T1/T2 are non-zero
                    t1 = "1" if val[0] != 0 else "0"
                    t2 = "1" if val[1] != 0 else "0"
                    opts.append(f"T{t1}{t2}")
                elif opt == 'SAckOK':
                    opts.append("S")
            
            resp["O"] = "".join(opts)

            # Sequence and Ack Analysis
            if sent_pkt and sent_pkt.haslayer(TCP):
                if pkt[TCP].seq == 0:
                    resp["S"] = "Z"
                elif pkt[TCP].seq == sent_pkt[TCP].ack:
                    resp["S"] = "A"
                elif pkt[TCP].seq == sent_pkt[TCP].ack + 1:
                    resp["S"] = "A+"
                else:
                    resp["S"] = "O"

                if pkt[TCP].ack == 0:
                    resp["A"] = "Z"
                elif pkt[TCP].ack == sent_pkt[TCP].seq:
                    resp["A"] = "S"
                elif pkt[TCP].ack == sent_pkt[TCP].seq + 1:
                    resp["A"] = "S+"
                else:
                    resp["A"] = "O"

        return resp

    def _get_ttl_guess(self, ttl):
        """Guesses the initial TTL (standard Nmap TG field)."""
        if ttl <= 32:
            return "20"
        if ttl <= 64:
            return "40"
        if ttl <= 128:
            return "80"
        return "FF"

    def _calculate_seq_metrics(self, seqs, ipids):
        """Calculates Nmap-style Sequence Predictability (SP), GCD, ISR, and TI."""
        if len(seqs) < 2:
            return {}
            
        diffs = []
        for i in range(1, len(seqs)):
            diff = (seqs[i] - seqs[i-1]) % (2**32)
            if diff > 0:
                diffs.append(diff)
                
        metrics = {}
        if diffs:
            # GCD
            gcd_val = diffs[0]
            for d in diffs[1:]:
                gcd_val = math.gcd(gcd_val, d)
            metrics["GCD"] = hex(gcd_val)[2:].upper()
            
            # ISR
            avg_diff = sum(diffs) / len(diffs)
            rate = avg_diff / 0.1  
            isr_val = min(255, int(math.log2(rate) * 8)) if rate > 0 else 0
            metrics["ISR"] = hex(isr_val)[2:].upper()
            
            # SP
            mean = sum(diffs) / len(diffs)
            variance = sum((x - mean) ** 2 for x in diffs) / len(diffs)
            std_dev = math.sqrt(variance)
            sp_val = min(255, int(math.log2(std_dev) * 8)) if std_dev > 1 else 0
            metrics["SP"] = hex(sp_val)[2:].upper()
        
        # IPID Sequence (TI)
        if len(ipids) >= 2:
            i_diffs = [(ipids[i] - ipids[i-1]) % 65536 for i in range(1, len(ipids))]
            if all(d == 0 for d in i_diffs):
                metrics["TI"] = "Z"
            elif all(d < 10 for d in i_diffs):
                metrics["TI"] = "I"
            elif all(d % 256 == 0 and d // 256 < 10 for d in i_diffs):
                metrics["TI"] = "BI"
            else:
                metrics["TI"] = "R"
            
        return metrics

    def _probe_seq_ops_win(self):
        """Sends 6 TCP SYN packets to an open port to test SEQ, OPS, and WIN."""
        logging.info("[*] Sending SEQ/OPS/WIN Probes (6 packets)...")
        opts = [
            [('WScale', 10), ('NOP', None), ('MSS', 1460), ('Timestamp', (0xFFFFFFFF, 0)), ('SAckOK', '')],
            [('MSS', 1400), ('WScale', 0), ('SAckOK', ''), ('Timestamp', (0xFFFFFFFF, 0)), ('EOL', None)],
            [('Timestamp', (0xFFFFFFFF, 0)), ('NOP', None), ('NOP', None), ('WScale', 5), ('NOP', None), ('MSS', 1460)],
            [('SAckOK', ''), ('Timestamp', (0xFFFFFFFF, 0)), ('WScale', 10), ('EOL', None)],
            [('MSS', 536), ('SAckOK', ''), ('Timestamp', (0xFFFFFFFF, 0)), ('WScale', 10), ('EOL', None)],
            [('MSS', 265), ('SAckOK', ''), ('Timestamp', (0xFFFFFFFF, 0)), ('WScale', 10)],
        ]
        wins = [1, 63, 4, 4, 16, 512]
        responses = []
        raw_seqs = []

        for i in range(6):
            p = IP(dst=self.target, id=i + 1) / TCP(dport=self.open_tcp, flags="S", window=wins[i], options=opts[i])
            # Added verbose=0 to sr1 so Scapy doesn't flood your console output
            ans = sr1(p, timeout=2, verbose=0)
            responses.append(ans)
            time.sleep(0.1)

        # Safely initialize keys without wiping out existing state from other concurrent probes
        self.results.setdefault("OPS", {})
        self.results.setdefault("WIN", {})
        self.results.setdefault("SEQ", {})
        self.results.setdefault("IPID", {})  # Adding IPID tracking, crucial for native OS fingerprinting

        # Parse responses and capture ALL required fingerprinting data
        raw_ipids = []
        for i, r in enumerate(responses):
            if r and r.haslayer(TCP):
                # 1. Window size capture
                self.results["WIN"][f"W{i + 1}"] = hex(r[TCP].window)[2:].upper()

                # 2. Options string extraction
                # Re-using _parse_response to ensure O shorthand is consistent
                temp_resp = self._parse_response(r, f"W{i+1}")
                self.results["OPS"][f"O{i + 1}"] = temp_resp.get("O", "")

                # 3. Extract raw seqs to calculate mathematical metrics later
                raw_seqs.append(r[TCP].seq)

                # 4. FIX: Extract IP ID for sequence generation analysis
                if r.haslayer(IP):
                    raw_ipids.append(r[IP].id)
                    self.results["IPID"][f"I{i + 1}"] = r[IP].id
                    
        # 5. Calculate and inject actual Nmap DB Match Points
        if len(raw_seqs) >= 2:
            metrics = self._calculate_seq_metrics(raw_seqs, raw_ipids)
            self.results["SEQ"].update(metrics)

    def _probe_ecn(self):
        """Sends a TCP SYN/ECN packet to an open port."""
        logging.info("[*] Sending ECN Probe...")
        opts = [('WScale', 10), ('NOP', None), ('MSS', 1460), ('SAckOK', '')]
        p = IP(dst=self.target) / TCP(dport=self.open_tcp, flags="SEC", window=3, options=opts)
        ans = sr1(p, timeout=2, verbose=0)
        self.results["ECN"] = self._parse_response(ans, "ECN", p)
        if ans and ans.haslayer(TCP):
            self.results["ECN"]["CC"] = "Y" if 'E' in str(ans[TCP].flags) else "N"

    def _probe_t1_t7(self):
        """Sends the 7 TCP probes to open and closed ports."""
        logging.info("[*] Sending TCP T1-T7 Probes...")
        opts_t1 = [('WScale', 10), ('NOP', None), ('MSS', 1460), ('Timestamp', (0xFFFFFFFF, 0)), ('SAckOK', '')]
        probes = {
            "T1": IP(dst=self.target) / TCP(dport=self.open_tcp, flags="S", options=opts_t1),
            "T2": IP(dst=self.target) / TCP(dport=self.open_tcp, flags=""),
            "T3": IP(dst=self.target) / TCP(dport=self.open_tcp, flags="SFUP"),
            "T4": IP(dst=self.target) / TCP(dport=self.open_tcp, flags="A"),
            "T5": IP(dst=self.target) / TCP(dport=self.closed_tcp, flags="S"),
            "T6": IP(dst=self.target) / TCP(dport=self.closed_tcp, flags="A"),
            "T7": IP(dst=self.target) / TCP(dport=self.closed_tcp, flags="FPU"),
        }
        for name, pkt in probes.items():
            ans = sr1(pkt, timeout=2, verbose=0)
            self.results[name] = self._parse_response(ans, name, pkt)

    def _probe_u1(self):
        """Sends a UDP packet to a closed port."""
        logging.info("[*] Sending UDP U1 Probe...")
        p = IP(dst=self.target, id=0x1042) / UDP(dport=self.closed_udp) / (b"C" * 300)
        ans = sr1(p, timeout=3, verbose=0)
        if ans and ans.haslayer(ICMP) and ans[ICMP].type == 3 and ans[ICMP].code == 3:
            self.results["U1"] = {"R": "Y"}
            if ans.haslayer(IP):
                self.results["U1"]["DF"] = "Y" if ans[IP].flags.DF else "N"
                self.results["U1"]["T"] = hex(ans[IP].ttl)[2:].upper()
                self.results["U1"]["TG"] = self._get_ttl_guess(ans[IP].ttl)

            # Nmap checks the returned IP packet inside the ICMP payload.
            if IP in ans[ICMP].payload:
                ret_ip = ans[ICMP].payload[IP]
                self.results["U1"]["IPL"] = hex(len(ans))[2:].upper()
                self.results["U1"]["UN"] = "0"  # Usually zero
                self.results["U1"]["RIPL"] = hex(len(ret_ip))[2:].upper()
                self.results["U1"]["RID"] = hex(ret_ip.id)[2:].upper()
                self.results["U1"]["RIPCK"] = "G" if ret_ip.chksum == p[IP].chksum else "I"
                self.results["U1"]["RUCK"] = "G"  # Simplification
                self.results["U1"]["RUD"] = "G" if ret_ip.haslayer(UDP) else "I"
        else:
            self.results["U1"] = {"R": "N"}

    def _probe_ie(self):
        """Sends two ICMP Echo probes."""
        logging.info("[*] Sending ICMP IE Probes...")
        p1 = IP(dst=self.target, id=123, flags="DF") / ICMP(type=8, code=9, seq=295, id=123)
        p2 = IP(dst=self.target, id=124, tos=4) / ICMP(type=8, code=0, seq=296, id=124)
        
        self.results["IE"] = {"R": "N"}
        
        # Probe 1
        ans1 = sr1(p1, timeout=2, verbose=0)
        if ans1:
            self.results["IE"]["R"] = "Y"
            self.results["IE"]["T"] = hex(ans1[IP].ttl)[2:].upper()
            self.results["IE"]["TG"] = self._get_ttl_guess(ans1[IP].ttl)
            self.results["IE"]["DFI"] = "Y" if ans1[IP].flags.DF else "N"
            self.results["IE"]["CD"] = "Z" if ans1[ICMP].code == 0 else "S"  # S means it echoed the non-zero code
            
        # Probe 2
        ans2 = sr1(p2, timeout=2, verbose=0)
        if ans2 and self.results["IE"]["R"] == "N":  # If only P2 replied
            self.results["IE"]["R"] = "Y"
            # ... capture other IE metrics if needed


class NmapDBMatcher:
    """
    Scores the results generated by OSFingerprintEngine against nmap-os-db.txt
    using the exact weighting formulas.
    """
    def __init__(self, nmap_db_path: str, auto_update: bool = True):
        self.nmap_db_path = nmap_db_path
        self.fingerprints = []
        if auto_update:
            self.check_and_update_db()
        self.parse_db()

    def check_and_update_db(self):
        """Checks if the local database exists and is recent; updates if necessary."""
        update_url = "https://svn.nmap.org/nmap/nmap-os-db"
        needs_update = False
        
        if not os.path.exists(self.nmap_db_path):
            logging.info("[*] Nmap OS DB not found. Downloading latest version...")
            needs_update = True
        else:
            file_age_days = (time.time() - os.path.getmtime(self.nmap_db_path)) / (24 * 3600)
            if file_age_days > 30:
                logging.info(f"[*] Nmap OS DB is {int(file_age_days)} days old. Checking for updates...")
                needs_update = True

        if needs_update:
            try:
                # Bypass SSL verification for legacy environments if needed
                context = ssl._create_unverified_context()
                with urllib.request.urlopen(update_url, context=context) as response:
                    with open(self.nmap_db_path, 'wb') as f:
                        f.write(response.read())
                logging.info("[+] Successfully updated Nmap OS DB from SVN.")
            except Exception as e:
                logging.warning(f"[-] Failed to update Nmap OS DB: {e}")

    def parse_db(self):
        """Load nmap-os-db.txt into memory as a list of fingerprint dictionaries."""
        try:
            with open(self.nmap_db_path, 'r', encoding='utf-8', errors='ignore') as f:
                current_fp = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('MatchPoints'):
                        continue

                    if line.startswith('Fingerprint '):
                        if current_fp:
                            self.fingerprints.append(current_fp)
                        os_name = line[len('Fingerprint '):]
                        current_fp = {'name': os_name, 'probes': {}, 'class_info': [], 'cpe': []}
                        continue

                    if not current_fp:
                        continue

                    if line.startswith('Class '):
                        current_fp['class_info'].append(line[len('Class '):])
                        continue

                    if line.startswith('CPE '):
                        current_fp['cpe'].append(line[len('CPE '):])
                        continue

                    match = re.match(r'^([A-Z0-9]+)\((.*)\)$', line)
                    if match:
                        probe_name, probe_data = match.groups()
                        current_fp['probes'][probe_name] = {}
                        attributes = probe_data.split('%')
                        for attr in attributes:
                            if '=' in attr:
                                key, value = attr.split('=', 1)
                                current_fp['probes'][probe_name][key] = value

                if current_fp:  # Append the last one
                    self.fingerprints.append(current_fp)
            logging.info(f"[*] Successfully parsed {len(self.fingerprints)} OS fingerprints from DB.")
        except FileNotFoundError:
            logging.error(f"[-] Nmap OS DB not found at {self.nmap_db_path}")
        except Exception as e:
            logging.error(f"[-] Error parsing Nmap OS DB: {e}")

    def _match_nmap_value(self, target_val, db_val):
        """
        Matches a target value against an Nmap DB expression.
        Handles alternatives (|) and hex ranges (-).
        """
        if not target_val:
            target_val = ""
            
        parts = db_val.split('|')
        for part in parts:
            if part == target_val:
                return True
                
            if '-' in part:
                # Try hex range matching (Nmap ranges are natively hex)
                try:
                    min_str, max_str = part.split('-', 1)
                    if int(min_str, 16) <= int(target_val, 16) <= int(max_str, 16):
                        return True
                except ValueError:
                    pass  # Not a valid hex range, move to the next part
                    
        return False

    def score_target(self, target_results: dict):
        """
        Iterate through all loaded DB fingerprints. Compare the target_results
        to each signature. Use the MATCH_POINTS weights to add up the score.
        This is a simplified scoring engine that only does exact matches.
        """
        best_match = None
        highest_score = 0
        total_points = sum(sum(v.values()) for v in MATCH_POINTS.values())

        logging.info("[*] Scoring collected fingerprint against database...")
        for fp in self.fingerprints:
            current_score = 0
            for probe_name, attributes in target_results.items():
                if probe_name in fp['probes']:
                    db_probe = fp['probes'][probe_name]
                    for attr, value in attributes.items():
                        if attr in db_probe and self._match_nmap_value(value, db_probe[attr]):
                            current_score += MATCH_POINTS.get(probe_name, {}).get(attr, 0)

            if current_score > highest_score:
                highest_score = current_score
                best_match = fp

        if best_match:
            accuracy = (highest_score / total_points) * 100
            print(f"\n[+] Best Match Found: {best_match['name']}")
            print(f"    Accuracy: {accuracy:.2f}%")
            for c in best_match.get('class_info', []):
                print(f"    Class: {c}")
            for cpe in best_match.get('cpe', []):
                print(f"    CPE: {cpe}")
        else:
            print("[-] No matching OS fingerprint found.")

        return best_match


class OnlineCorrelator:
    """
    Correlates active fingerprinting results with online databases (Shodan, MACVendors).
    """
    def __init__(self, shodan_key: str = None):
        self.shodan_key = shodan_key

    def shodan_lookup(self, target_ip: str):
        """Passive OS lookup via Shodan API."""
        if not self.shodan_key:
            return None
            
        logging.info(f"[*] Querying Shodan for passive intelligence on {target_ip}...")
        try:
            url = f"https://api.shodan.io/shodan/host/{target_ip}?key={self.shodan_key}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get("os")
        except Exception as e:
            logging.debug(f"[-] Shodan lookup failed: {e}")
            return None

    def mac_lookup(self, target_ip: str):
        """Online MAC/OUI lookup to identify hardware vendor."""
        logging.info(f"[*] Attempting to resolve MAC address for {target_ip}...")
        try:
            # Resolve MAC via ARP
            ans, unans = arping(target_ip, timeout=2, verbose=0)
            if not ans:
                return None, None
                
            mac = ans[0][1].src
            logging.info(f"[+] Found MAC: {mac}. Querying OUI database...")
            
            # Query macvendors.co API (free tier)
            url = f"https://api.macvendors.com/{mac}"
            with urllib.request.urlopen(url, timeout=5) as response:
                vendor = response.read().decode().strip()
                return mac, vendor
        except Exception as e:
            logging.debug(f"[-] MAC/OUI lookup failed: {e}")
            return None, None


class Start:
    """
    Module entry point. Orchestrates the OS fingerprinting process.
    """
    def find_closed_tcp(self, target_ip: str):
        """Actively scans for a closed TCP port by looking for an RST response."""
        for _ in range(5):
            port = random.randint(30000, 60000)
            ans = sr1(IP(dst=target_ip)/TCP(dport=port, flags="S"), timeout=0.5, verbose=0)
            if ans and ans.haslayer(TCP) and 'R' in str(ans[TCP].flags):
                return port
        return None

    def find_closed_udp(self, target_ip: str):
        """Actively scans for a closed UDP port by looking for an ICMP Port Unreachable."""
        for _ in range(5):
            port = random.randint(30000, 60000)
            ans = sr1(IP(dst=target_ip)/UDP(dport=port), timeout=0.5, verbose=0)
            if ans and ans.haslayer(ICMP) and ans[ICMP].type == 3 and ans[ICMP].code == 3:
                return port
        return None

    def __init__(self, args=None):
        if DatabaseManagment:
            db = DatabaseManagment.get()
        else:
            try:
                import sqlite3
                db_path = os.path.join(_framework_root, ".data", ".config", "data.db")
                db = {}
                with sqlite3.connect(db_path) as conn:
                    for key, value in conn.execute("SELECT key, value FROM variables"):
                        try:
                            db[key] = json.loads(value)
                        except Exception:
                            db[key] = value
            except Exception:
                db = {}

        target_ip = db.get("R_HOST")
        open_port_str = db.get("R_PORT")
        shodan_key = db.get("SHODAN_API_KEY")
        advanced_os_id = str(db.get("ADVANCED_OS_ID", "false")).lower() == "true"

        if not target_ip or not open_port_str:
            print("[-] R_HOST and R_PORT must be set in the SuperSploit database.")
            return

        try:
            open_port = int(open_port_str)
        except ValueError:
            print(f"[-] Invalid R_PORT: {open_port_str}. Must be an integer.")
            return

        print(f"[*] Starting OS fingerprinting for {target_ip}")
        if advanced_os_id:
            print("[*] ADVANCED_OS_ID is enabled. Online checks and DB updates are active.")
        else:
            print("[*] ADVANCED_OS_ID is disabled. Using local database and offline analysis only.")

        try:
            print(f"[*] Searching for explicitly closed TCP/UDP ports to ensure accurate T5-T7/U1 probes...")
            closed_tcp = self.find_closed_tcp(target_ip)
            closed_udp = self.find_closed_udp(target_ip)
    
            if not closed_tcp:
                closed_tcp = open_port + 1 if open_port < 65535 else open_port - 1
                print(f"[-] Could not find a closed TCP port. Falling back to guess: {closed_tcp}")
            else:
                print(f"[+] Found closed TCP port: {closed_tcp}")
    
            if not closed_udp:
                closed_udp = 31337
                print(f"[-] Could not find a closed UDP port. Falling back to guess: {closed_udp}")
            else:
                print(f"[+] Found closed UDP port: {closed_udp}")
    
            print(f"[*] Using Open Port: {open_port}, Closed TCP: {closed_tcp}, Closed UDP: {closed_udp}")

            engine = OSFingerprintEngine(target_ip, open_port, closed_tcp, closed_udp)
            results = engine.run_all_probes()

            print("\n[*] Collected Fingerprint:")
            captured_fingerprint = []
            for probe, data in results.items():
                if data:
                    attrs = '%'.join([f"{k}={v}" for k, v in data.items()])
                    print(f"    {probe}({attrs})")
                    captured_fingerprint.append(f"{probe}({attrs})")

            matcher = NmapDBMatcher(path_to_nmap_db, auto_update=advanced_os_id)
            best_match_name = "Unknown"
            if matcher.fingerprints:
                best_match = matcher.score_target(results)
                if best_match:
                    best_match_name = best_match["name"]

            # --- Online Correlation Phase ---
            shodan_os = None
            mac = None
            vendor = None
            
            if advanced_os_id:
                print("\n[*] Running Online Correlation Phase...")
                correlator = OnlineCorrelator(shodan_key)
                shodan_os = correlator.shodan_lookup(target_ip)
                mac, vendor = correlator.mac_lookup(target_ip)

                if shodan_os:
                    print(f"[+] Shodan Passive Correlation: {shodan_os}")
                if vendor:
                    print(f"[+] Hardware Vendor Correlation: {vendor} ({mac})")
            else:
                print("\n[*] Skipping Online Correlation Phase (ADVANCED_OS_ID = false).")

            if DatabaseManagment:
                targets_db = DatabaseManagment.getTargets()
                target_entry = targets_db.setdefault(target_ip, {})
                if not isinstance(target_entry, dict):
                    target_entry = {}
                    targets_db[target_ip] = target_entry

                target_entry["fingerprint"] = "\n".join(captured_fingerprint)
                target_entry["best match"] = best_match_name
                if shodan_os:
                    target_entry["shodan_os"] = shodan_os
                if vendor:
                    target_entry["vendor"] = f"{vendor} ({mac})"

                DatabaseManagment.updateTargets(targets_db)
                DatabaseManagment.sync_targets_to_disk()
                print("[*] Successfully saved OS fingerprint and correlation data to targets database.")
            else:
                try:
                    with open(path_to_targets, 'r', encoding="utf-8") as f:
                        targets_db = json.load(f)
                        if not isinstance(targets_db, dict):
                            targets_db = {"TARGETS": {}}
                except (FileNotFoundError, json.JSONDecodeError):
                    targets_db = {"TARGETS": {}}

                targets_dict = targets_db.setdefault("TARGETS", {})
                target_entry = targets_dict.setdefault(target_ip, {})
                if not isinstance(target_entry, dict):
                    target_entry = targets_dict[target_ip] = {}

                target_entry["fingerprint"] = "\n".join(captured_fingerprint)
                target_entry["best match"] = best_match_name
                if shodan_os:
                    target_entry["shodan_os"] = shodan_os
                if vendor:
                    target_entry["vendor"] = f"{vendor} ({mac})"

                try:
                    with open(path_to_targets, 'w', encoding="utf-8") as f:
                        json.dump(targets_db, f, indent=4, sort_keys=True)
                    print("[*] Successfully saved OS fingerprint and correlation data to targets database.")
                except Exception as e:
                    print(f"[-] Failed to save to targets database: {e}")

        except PermissionError:
            print("\n[-] PermissionError: This script requires root/administrator privileges to craft raw packets.")
            print("[-] Please run SuperSploit with 'sudo'.")
        except Exception as e:
            print(f"\n[-] An unexpected error occurred: {e}")


if __name__ == "__main__":
    Start()
