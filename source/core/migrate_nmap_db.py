import sqlite3
import os
import re
from .database import DatabaseManagment

def migrate_nmap_db(txt_path, db_path):
    """Parses the flat Nmap OS DB and migrates it to a structured SQLite DB."""
    conn = sqlite3.connect(db_path)
    curr = conn.cursor()

    # Create Schema
    curr.executescript('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fingerprint_classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fp_id INTEGER,
            vendor TEXT,
            os_family TEXT,
            os_gen TEXT,
            device_type TEXT,
            FOREIGN KEY(fp_id) REFERENCES fingerprints(id),
            UNIQUE(fp_id, vendor, os_family, os_gen, device_type)
        );

        CREATE TABLE IF NOT EXISTS fingerprint_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fp_id INTEGER,
            test_name TEXT,
            test_values TEXT,
            FOREIGN KEY(fp_id) REFERENCES fingerprints(id),
            UNIQUE(fp_id, test_name, test_values)
        );
    ''')

    if not os.path.exists(txt_path):
        print(f"[!] Error: {txt_path} not found.")
        return

    with open(txt_path, 'r') as f:
        current_fp_id = None
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Start of a new fingerprint block
            if line.startswith('Fingerprint '):
                fp_name = line[12:]
                curr.execute('INSERT OR IGNORE INTO fingerprints (name) VALUES (?)', (fp_name,))
                curr.execute('SELECT id FROM fingerprints WHERE name = ?', (fp_name,))
                current_fp_id = curr.fetchone()[0]
                continue

            if current_fp_id is None:
                continue

            # Parse Classes
            if line.startswith('Class '):
                parts = [p.strip() for p in line[6:].split('|')]
                while len(parts) < 4: parts.append("")
                curr.execute('''INSERT OR IGNORE INTO fingerprint_classes (fp_id, vendor, os_family, os_gen, device_type) 
                             VALUES (?, ?, ?, ?, ?)''', (current_fp_id, parts[0], parts[1], parts[2], parts[3]))
            
            # Parse Tests (SEQ, T1, U1, etc.)
            elif '(' in line and line.endswith(')'):
                test_match = re.match(r'^([A-Z0-9]+)\((.*)\)$', line)
                if test_match:
                    test_name, test_vals = test_match.groups()
                    curr.execute('INSERT OR IGNORE INTO fingerprint_tests (fp_id, test_name, test_values) VALUES (?, ?, ?)',
                                 (current_fp_id, test_name, test_vals))

    conn.commit()
    conn.close()
    print(f"[+] Migration complete: {db_path}")

if __name__ == "__main__":
    # Dynamically locate the config directory based on framework install
    install_path = DatabaseManagment.getInstall()
    BASE_DIR = os.path.join(install_path, ".data", ".config")
    migrate_nmap_db(
        os.path.join(BASE_DIR, "nmap-os-db.txt"),
        os.path.join(BASE_DIR, "signatures.db")
    )