import sqlite3
import os
import re
from .database import DatabaseManagment

def migrate_services(txt_path, db_path):
    """Parses Nmap service probes and migrates them to SQLite."""
    conn = sqlite3.connect(db_path)
    curr = conn.cursor()

    # Create Schema for Services
    curr.executescript('''
        CREATE TABLE IF NOT EXISTS service_probes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            protocol TEXT,
            name TEXT,
            payload TEXT,
            UNIQUE(protocol, name)
        );

        CREATE TABLE IF NOT EXISTS service_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            probe_id INTEGER,
            service TEXT,
            pattern TEXT,
            is_soft INTEGER DEFAULT 0,
            FOREIGN KEY(probe_id) REFERENCES service_probes(id),
            UNIQUE(probe_id, service, pattern)
        );
    ''')

    if not os.path.exists(txt_path):
        print(f"[!] Error: {txt_path} not found.")
        return

    with open(txt_path, 'r', encoding='latin-1') as f:
        current_probe_id = None
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse Probe Directive: Probe <protocol> <name> q|<payload>|
            if line.startswith('Probe '):
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    proto, name, q_payload = parts[1], parts[2], parts[3]
                    # Extract payload between delimiters (usually |)
                    delim = q_payload[1]
                    payload = q_payload.split(delim)[1]
                    
                    curr.execute('INSERT OR IGNORE INTO service_probes (protocol, name, payload) VALUES (?, ?, ?)',
                                 (proto, name, payload))
                    curr.execute('SELECT id FROM service_probes WHERE name = ? AND protocol = ?', (name, proto))
                    current_probe_id = curr.fetchone()[0]
                continue

            if current_probe_id is None:
                continue

            # Parse Match/Softmatch: match <service> m|<pattern>|<opts> [<versioninfo>]
            if line.startswith('match ') or line.startswith('softmatch '):
                is_soft = 1 if line.startswith('softmatch') else 0
                # Remove the directive name
                remaining = line.split(' ', 1)[1]
                parts = remaining.split(' ', 1)
                if len(parts) >= 2:
                    service_name = parts[0]
                    pattern_part = parts[1]
                    if pattern_part.startswith('m'):
                        delim = pattern_part[1]
                        try:
                            # Extract regex pattern
                            pattern = pattern_part.split(delim)[1]
                            curr.execute('''INSERT OR IGNORE INTO service_matches (probe_id, service, pattern, is_soft) 
                                         VALUES (?, ?, ?, ?)''', (current_probe_id, service_name, pattern, is_soft))
                        except IndexError:
                            continue

    conn.commit()
    conn.close()
    print(f"[+] Service migration complete: {db_path}")

if __name__ == "__main__":
    install_path = DatabaseManagment.getInstall()
    BASE_DIR = os.path.join(install_path, ".data", ".config")
    migrate_services(
        os.path.join(BASE_DIR, "nmap-service-probes.txt"),
        os.path.join(BASE_DIR, "signatures.db")
    )