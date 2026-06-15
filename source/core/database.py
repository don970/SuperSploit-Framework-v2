"""
Core Database and Cache Management Module
Handles file system traversals, YAML metadata extraction, and JSON configuration database interactions.
"""
import json
import os
import pathlib
import traceback
import sqlite3
from collections.abc import MutableMapping
from .errors import Error as error
from .ToStdOut import ToStdout
import yaml

# Framework Constants
# Base installation directory for the framework dynamically resolved
# (Calculates the path 2 directories up from source/core/database.py)
_current_dir = os.path.dirname(os.path.abspath(__file__))
install_location = os.path.abspath(os.path.join(_current_dir, "..", ".."))

# Check if the framework is being executed from a different working directory (e.g. dev workspace)
_cwd = os.getcwd()
if (os.path.exists(os.path.join(_cwd, ".data", ".config", "data.db")) or 
        os.path.exists(os.path.join(_cwd, ".data", ".config", "data.json"))):
    install_location = _cwd

installation = install_location

# Alias for the standard output writing function
write = ToStdout.write


class SQLiteDict(MutableMapping):
    def __init__(self, db_path, table_name="variables"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.table = table_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS {self.table} (key TEXT PRIMARY KEY, value TEXT)")
            conn.commit()
            
        # Migrate old JSON data if it exists
        old_json_path = self.db_path.replace(".db", ".json")
        if os.path.exists(old_json_path):
            try:
                with open(old_json_path, "r", encoding="utf-8") as file:
                    old_data = json.load(file)
                    for k, v in old_data.items():
                        self[k] = v
                os.rename(old_json_path, old_json_path + ".bak")
            except Exception:
                pass

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def __getitem__(self, key):
        with self._get_conn() as conn:
            cursor = conn.execute(f"SELECT value FROM {self.table} WHERE key=?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    return row[0]
            raise KeyError(key)

    def __setitem__(self, key, value):
        val_str = json.dumps(value) if isinstance(value, (dict, list, bool, int, float)) else str(value)
        with self._get_conn() as conn:
            conn.execute(f"INSERT OR REPLACE INTO {self.table} (key, value) VALUES (?, ?)", (key, val_str))
            conn.commit()

    def __delitem__(self, key):
        with self._get_conn() as conn:
            cursor = conn.execute(f"DELETE FROM {self.table} WHERE key=?", (key,))
            if cursor.rowcount == 0:
                raise KeyError(key)
            conn.commit()

    def __iter__(self):
        with self._get_conn() as conn:
            cursor = conn.execute(f"SELECT key FROM {self.table}")
            for row in cursor:
                yield row[0]

    def __len__(self):
        with self._get_conn() as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self.table}")
            return cursor.fetchone()[0]

    def __repr__(self):
        return repr(dict(self))
        
    def copy(self):
        return dict(self)


class ExploitCache:
    """Manages memory-resident YAML metadata for all framework modules."""
    # Holds detailed info for the currently active exploit
    details = {}
    metadata_index = {}  # Maps path -> YAML metadata summary
    all_exploits = []
    all_payloads = []

    @classmethod
    def update(cls, data=None):
        """Updates the exploit/payload file lists and rebuilds the metadata cache."""
        # 1. Update file lists from the filesystem
        cls.all_exploits = DatabaseManagment.getExploits()
        cls.all_payloads = DatabaseManagment.getPayloads()
        _, recon_modules = DatabaseManagment.UpdateReconDB()

        # 2. Index all metadata for the search engine to prevent loading during search
        for path in cls.all_exploits + cls.all_payloads + recon_modules:
            if os.path.isdir(path):
                continue
            if path not in cls.metadata_index:
                cls.metadata_index[path] = cls._quick_parse(path)

        # 3. Cache the active exploit's full details
        db = DatabaseManagment.get()
        if db and db.get("EXPLOIT"):
            cls._parse_details(db["EXPLOIT"])

    @classmethod
    def _quick_parse(cls, path):
        """Extracts basic metadata for search indexing without loading the full file."""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                # Split based on the custom delimiter to separate code from YAML metadata
                data = file.read().split("#!#!#!")
                if len(data) > 1:
                    # Parse the YAML block
                    meta = yaml.safe_load(data[1])
                    if not isinstance(meta, dict):
                        meta = {}
                    return {
                        "name": meta.get("name", os.path.basename(path)),
                        "cve": meta.get("cve", "N/A"),
                        "cwe": meta.get("cwe", "N/A"),
                        "desc": meta.get("description", "").lower(),
                        "cat": meta.get("category", meta.get("catogory", "N/A")),
                        "target": meta.get("target", ""),
                        "os": meta.get("os", ""),
                        "arch": meta.get("arch", ""),
                        "kernel": meta.get("kernel_versions", meta.get("kernel", "")),
                        "min_ver": meta.get("min_ver", ""),
                        "max_ver": meta.get("max_ver", ""),
                        "requirements": meta.get("requirements", []),
                        "keywords": meta.get("keywords", meta.get("auto_suggest", []))
                    }
        except Exception:
            # Metadata parsing failed (common with malformed YAML in some modules)
            pass
        return {"name": os.path.basename(path), "cve": "N/A", "desc": ""}

    @classmethod
    def _parse_details(cls, path):
        """Full YAML parser for the 'info' command."""
        cls.details = {}
        if not os.path.exists(path):
            # Mark as missing if the exploit file was removed or path is invalid
            cls.details = {"status": "missing"}
            return
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                # Split to isolate the YAML metadata section
                data = file.read().split("#!#!#!")
            
            meta = {}
            if len(data) > 1:
                try:
                    parsed_meta = yaml.safe_load(data[1])
                    if isinstance(parsed_meta, dict):
                        meta = parsed_meta
                except Exception:
                    pass
                
            # Populate the details dictionary with all relevant exploit properties
            cls.details = {
                "path": path,
                "name": meta.get("name", os.path.basename(path)),
                "info": meta.get("description", meta.get("desc", "No description provided.")),
                "options": meta.get("options", []),
                "cve": meta.get("cve", "N/A"),
                "cwe": meta.get("cwe", "N/A"),
                "target": meta.get("target", ""),
                "os": meta.get("os", ""),
                "kernel": meta.get("kernel_versions", meta.get("kernel", "")),
                "min_ver": meta.get("min_ver", ""),
                "max_ver": meta.get("max_ver", ""),
                "payload": meta.get("payload", ""),
                "author": meta.get("author", "N/A"),
                "category": meta.get("category", meta.get("catogory", "N/A")),
                "root": meta.get("root", "false"),
                "keywords": meta.get("keywords", []),
                "dev_status": meta.get("status", "known"),
                "status": "ok"
            }
        except Exception:
            cls.details = {"status": "error"}


class exploitDetails:
    """Handles the display of currently selected exploit metadata."""

    def __init__(self, *args):
        """Initializes the display and prints the cached exploit information."""
        db = DatabaseManagment.get()
        if "EXPLOIT" in db:
            ExploitCache._parse_details(db["EXPLOIT"])
             
        cache = ExploitCache.details
        # Validate that an exploit is selected and its cache loaded successfully
        if not cache or cache.get("status") != "ok":
            write("[!] Select a valid exploit first.\n")
            return

        # Print the core exploit details header
        write(f"[*] Exploit:     {cache.get('name', 'Unknown')}\n")
        write(f"[*] CVE:         {cache.get('cve', 'N/A')}\n")
        write(f"[*] CWE:         {cache.get('cwe', 'N/A')}\n")
        write(f"[*] Description: {cache.get('info', 'No description provided.')}\n")
        write(f"==================================\n")

        db = DatabaseManagment.get()
        # Dynamically print out all available options mapped in the cache
        for opt, value in cache.items():
            # Hide redundant internal framework keys from the CLI output
            if opt not in ["name", "cve", "info", "status", "path", "cwe"]:
                write(f"{opt.capitalize()}: {value}\n")


class DatabaseManagment:
    """
    Centralized utility for reading/writing configuration state
    and mapping module paths across the framework.
    """
    aliases = {}
    db = {}
    core_db = None
    profile_db = None
    _profile_db_loaded = False

    # --- STATE MANAGEMENT VARIABLES ---
    _targets_cache = None
    _targets_dirty = False
    _sync_thread = None
    _stop_sync = False
    _targets_last_mtime = 0
    _db_loaded = False

    @classmethod
    def get_active_workspace(cls):
        """Returns the name of the currently active workspace."""
        active_file = os.path.join(cls.getInstall(), ".data", ".config", "active_workspace")
        if os.path.exists(active_file):
            try:
                with open(active_file, "r") as f:
                    return f.read().strip()
            except Exception:
                pass
        return "default"

    @classmethod
    def get_db_path(cls, filename):
        """Helper to resolve database paths dynamically based on active installation and workspace."""
        workspace = cls.get_active_workspace()
        if workspace == "default":
            return os.path.join(cls.getInstall(), ".data", ".config", filename)
        
        ws_dir = os.path.join(cls.getInstall(), ".data", "workspaces", workspace)
        os.makedirs(ws_dir, exist_ok=True)
        return os.path.join(ws_dir, filename)

    @classmethod
    def _get_path_to_database(cls): return cls.get_db_path("data.db")

    @classmethod
    def _get_path_to_targets(cls): return cls.get_db_path("targets.json")

    @classmethod
    def _get_path_to_profiles(cls): return cls.get_db_path("profiles.db")

    @classmethod
    def reset_cache(cls):
        """Resets the memory cache to force a reload from disk, used when switching workspaces."""
        cls.core_db = None
        cls.profile_db = None
        cls._db_loaded = False
        cls._profile_db_loaded = False
        cls._targets_cache = None
        cls._targets_last_mtime = 0
        cls._targets_dirty = False

    @classmethod
    def _update(cls, data=None):
        # With SQLiteDict, real-time writes are handled by the __setitem__ wrapper.
        # We keep this method for backward compatibility in the framework so it doesn't crash 
        # when modules call DatabaseManagment._update(self.database).
        # SQLiteDict handles persistence automatically, so no explicit sync is needed.
        pass 

    @classmethod
    def getCVE(cls):
        """Retrieves the CVE from the current memory cache and syncs it to the JSON database."""
        cache = ExploitCache.details
        if cache and cache.get("status") == "ok":
            cve = cache.get("cve", "None")
            # Keep the database in sync for the banner
            cls.directlyModify(["CVE", cve])
            return cve
        return "None"

    @classmethod
    def getTargets(cls):
        """Reads targets from memory cache, but reloads if the disk file was updated by a subprocess."""
        targets_path = cls._get_path_to_targets()
        current_mtime = 0
        if os.path.exists(targets_path):
            current_mtime = os.path.getmtime(targets_path)

        if cls._targets_cache is None or current_mtime > cls._targets_last_mtime:
            if os.path.exists(targets_path):
                try:
                    with open(targets_path, "r", encoding="utf-8") as file:
                        cls._targets_cache = json.load(file).get("TARGETS", {})
                    cls._targets_last_mtime = current_mtime
                except Exception:
                    cls._targets_cache = {}
            else:
                cls._targets_cache = {}
        return cls._targets_cache

    @classmethod
    def updateTargets(cls, updated_targets):
        """Updates targets in memory and flags them to be written to disk in the background."""
        cls._targets_cache = updated_targets
        cls._targets_dirty = True

    @classmethod
    def sync_targets_to_disk(cls):
        """Forces an immediate write to disk if memory is dirty."""
        if cls._targets_dirty and cls._targets_cache is not None:
            targets_path = cls._get_path_to_targets()
            try:
                with open(targets_path, "w", encoding="utf-8") as file:
                    json.dump({"TARGETS": cls._targets_cache}, file, indent=4, sort_keys=True)
                cls._targets_dirty = False
                cls._targets_last_mtime = os.path.getmtime(targets_path)
            except Exception as e:
                write(f"[-] Failed to sync targets to disk: {e}")

    @classmethod
    def start_background_sync(cls, interval=60):
        """Starts a daemon thread that writes target data to disk every 60 seconds."""
        if cls._sync_thread is None:
            import threading
            import time
            cls._stop_sync = False

            def syncer():
                while not cls._stop_sync:
                    time.sleep(interval)
                    cls.sync_targets_to_disk()

            cls._sync_thread = threading.Thread(target=syncer, daemon=True)
            cls._sync_thread.start()

    @classmethod
    def socketedExploit(cls) -> bool:
        """Checks if the exploit uses the socket module."""
        exploit_path = cls.get().get("EXPLOIT", "")
        if not exploit_path or not os.path.exists(exploit_path):
            return False

        # Identify if the exploit script imports the native socket module
        with open(exploit_path, "r", encoding="utf-8", errors="ignore") as file:
            data = file.read()
            return "import socket" in data or "from socket import" in data

    @classmethod
    def get(cls):
        """Loads the current session database."""
        if not cls._db_loaded:
            cls.core_db = SQLiteDict(cls._get_path_to_database())
            cls._db_loaded = True
        return cls.core_db

    @classmethod
    def getProfiles(cls):
        """Loads the current profiles database."""
        if not cls._profile_db_loaded:
            cls.profile_db = SQLiteDict(cls._get_path_to_profiles(), table_name="profiles")
            cls._profile_db_loaded = True
        return cls.profile_db

    @staticmethod
    def getExploits():
        """Safe directory traversal for exploits."""
        exploits = []
        base_dir = os.path.join(install_location, "exploits")
        if os.path.exists(base_dir):
            # Iterate through categories (e.g., windows, linux, android)
            for x in sorted(os.listdir(base_dir)):
                sub_dir = os.path.join(base_dir, x)
                if os.path.isdir(sub_dir):
                    # Collect individual exploit script paths inside each category
                    for i in sorted(os.listdir(sub_dir)):
                        if i.endswith((".py", ".c", ".sh")) and not i.startswith("__"):
                            exploits.append(os.path.join(sub_dir, i))
        return exploits

    @staticmethod
    def getPayloads():
        """Safe directory traversal for payloads."""
        payloads = []
        base_dir = os.path.join(install_location, "payloads")
        if os.path.exists(base_dir):
            # Iterate through payload categories
            for x in sorted(os.listdir(base_dir)):
                sub_dir = os.path.join(base_dir, x)
                if os.path.isdir(sub_dir):
                    # Collect individual payload script paths
                    for i in sorted(os.listdir(sub_dir)):
                        if i.endswith((".py", ".c", ".sh")) and not i.startswith("__"):
                            payloads.append(os.path.join(sub_dir, i))
        return payloads

    @classmethod
    def directlyModify(cls, data: list):
        """Directly writes key-value pairs to the database."""
        if len(data) != 2:
            return

        try:
            variables = cls.get()

            # Map incoming human-readable keys to internal JSON database keys
            key_map = {
                "cve": "CVE",
                "exploit": "EXPLOIT",
                "payload": "PAYLOAD",
                "target": "R_HOST",
                "rhost": "R_HOST",
                "r_mac": "R_MAC",
                "mac": "R_MAC",
                "port": "R_PORT",
                "verbose": "VERBOSE_LOGGING",
                "dev_mode": "DEV_MODE",
                "sessionId": "SESSION_ID",
                "recon_name": "RECON_NAME",
                "recon_path": "RECON_PATH",
                "profile": "ACTIVE_PROFILE",
                "stage2": "STAGE_TWO",
                "stage_two": "STAGE_TWO"
            }

            # Update the mapped key if it matches the first item in the input data
            for k, mapped_key in key_map.items():
                if k in data[0].lower():
                    variables[mapped_key] = data[1]

            cls._update(variables)
        except Exception:
            error(traceback.format_exc())

    @classmethod
    def addProfile(cls, profile_data: dict):
        """Adds or updates a person profile in the profiles database."""
        if not profile_data.get("name"):
            write("[-] Error: Profile data must include a 'name'.")
            return
        try:
            profiles = cls.getProfiles()
            # Use the name as the primary key for simplicity
            profiles[profile_data["name"]] = profile_data
            # No explicit _update needed for SQLiteDict as __setitem__ handles persistence
            write(f"[*] Profile for '{profile_data['name']}' updated in persistent database.")
        except Exception:
            error(traceback.format_exc())

    @classmethod
    def importFromTargets(cls, ip):
        """Imports a target from the targets database and creates a profile."""
        targets = cls.getTargets()
        if ip not in targets:
            write(f"[-] Error: IP {ip} not found in targets database.")
            return None
        
        target_info = targets[ip]
        profile_data = {
            "name": target_info.get("hostname", ip),
            "ip": ip,
            "os": target_info.get("os_family", "N/A"),
            "arch": target_info.get("architecture", "N/A"),
            "kernel": target_info.get("kernel_version", "N/A"),
            "ports": target_info.get("ports", []),
            "research": []
        }
        cls.addProfile(profile_data)
        return profile_data

    @classmethod
    def editProfile(cls, data: str):
        """
        Edits an existing person profile in the profiles database.
        Syntax: edit profile "<Profile Name>" <field> "<value>"
        Example: edit profile "John Doe" phone "+1234567890"
        Example: edit profile "John Doe" social_medias add "twitter.com/johndoe"
        Example: edit profile "John Doe" social_medias remove "old-social.com"
        Example: edit profile "John Doe" research add "CVE-2023-1234 analysis"
        """
        import shlex  # Import locally to avoid circular dependency if Input needs DatabaseManagment
        parts = shlex.split(data)

        # Expected format: edit profile <name> <field> <value>
        if len(parts) < 5:
            write("[-] Usage: edit profile \"<Profile Name>\" <field> \"<value>\"")
            write("[-] For social_medias: edit profile \"<Profile Name>\" social_medias add \"<URL>\"")
            write("[-] For research: edit profile \"<Profile Name>\" research add \"<Info>\"")
            return

        # parts[0] is "edit", parts[1] is "profile"
        profile_name = parts[2]
        field = parts[3].lower()

        profiles_db = cls.getProfiles()
        if profile_name not in profiles_db:
            write(f"[-] Error: Profile '{profile_name}' not found.")
            return

        profile_data = profiles_db[profile_name]  # Get a mutable copy

        try:
            if field == "social_medias":
                if len(parts) < 6:  # edit profile <name> social_medias <action> <value>
                    write("[-] Usage: edit profile \"<Profile Name>\" social_medias add/remove \"<URL>\"")
                    return
                action = parts[4].lower()
                social_url = parts[5]

                if action == "add":
                    if social_url not in profile_data.get("social_medias", []):
                        profile_data.setdefault("social_medias", []).append(social_url)
                        write(f"[*] Added social media '{social_url}' to '{profile_name}'.")
                    else:
                        write(f"[*] Social media '{social_url}' already exists for '{profile_name}'.")
                elif action == "remove":
                    if social_url in profile_data.get("social_medias", []):
                        profile_data["social_medias"].remove(social_url)
                        write(f"[*] Removed social media '{social_url}' from '{profile_name}'.")
                    else:
                        write(f"[*] Social media '{social_url}' not found for '{profile_name}'.")
                else:
                    write("[-] Invalid action for social_medias. Use 'add' or 'remove'.")
                    return
            elif field == "research":
                if len(parts) < 6:
                    write("[-] Usage: edit profile \"<Profile Name>\" research add/remove \"<Info>\"")
                    return
                action = parts[4].lower()
                research_info = parts[5]

                if action == "add":
                    if research_info not in profile_data.get("research", []):
                        profile_data.setdefault("research", []).append(research_info)
                        write(f"[*] Added research note to '{profile_name}'.")
                    else:
                        write(f"[*] Research note already exists for '{profile_name}'.")
                elif action == "remove":
                    if research_info in profile_data.get("research", []):
                        profile_data["research"].remove(research_info)
                        write(f"[*] Removed research note from '{profile_name}'.")
                    else:
                        write(f"[*] Research note not found for '{profile_name}'.")
                else:
                    write("[-] Invalid action for research. Use 'add' or 'remove'.")
                    return
            else:
                value = parts[4]
                profile_data[field] = value
                write(f"[*] Updated '{field}' for '{profile_name}' to '{value}'.")

            cls.addProfile(profile_data)  # This will save the updated profile
        except Exception:
            error(traceback.format_exc())
            write(f"[-] Failed to edit profile '{profile_name}'.")

    @classmethod
    def importProfileFromFile(cls, path):
        """Imports a profile from a JSON or Markdown file."""
        if not os.path.exists(path):
            write(f"[-] Error: File {path} does not exist.\n")
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                if path.lower().endswith('.md'):
                    content = f.read()
                    targets = cls._parse_markdown_targets(content)
                    if targets:
                        for name, data in targets.items():
                            # Ensure the data is formatted as a profile (has a name)
                            profile_data = data.copy()
                            profile_data["name"] = name
                            cls.addProfile(profile_data)
                        write(f"[*] Successfully imported {len(targets)} profiles from {path}\n")
                    else:
                        write(f"[-] No valid profiles found in {path}\n")
                else:
                    data = json.load(f)
                    if isinstance(data, list):
                        for p in data:
                            cls.addProfile(p)
                    elif isinstance(data, dict):
                        cls.addProfile(data)
                    else:
                        write("[-] Error: Invalid profile data format.\n")
        except Exception as e:
            write(f"[-] Failed to import profile: {e}\n")

    @classmethod
    def _parse_markdown_targets(cls, content):
        """Parses a Markdown file to extract target profiles using regex, preserving raw content."""
        import re
        targets = {}
        current_ip = None
        current_target = {}
        current_raw = []

        # Look for headers like "# Target Profile: 192.168.1.50" or "# Target: 192.168.1.50"
        header_pattern = re.compile(r'^#+\s*Target(?: Profile)?\s*:\s*([^\s]+)', re.IGNORECASE)
        
        # Look for list items like "- **IP:** 192.168.1.50" or "* OS: Android"
        kv_pattern = re.compile(r'^[\*\-]\s*(?:\*\*)?([^:\*]+)(?:\*\*)?:\s*(.+)', re.IGNORECASE)

        lines = content.split('\n')
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            
            header_match = header_pattern.match(stripped_line)
            if header_match:
                # Save previous target if exists
                if current_ip or current_target:
                    ip_key = current_ip if current_ip else f"target_{len(targets)+1}"
                    current_target['raw_content'] = '\n'.join(current_raw).strip()
                    targets[ip_key] = current_target
                
                current_ip = header_match.group(1)
                current_target = {}
                current_raw = [] # Reset raw accumulator for new target
                # We don't add the header to current_raw as it's the identifier
                continue

            if current_ip is not None:
                current_raw.append(line)

            if not stripped_line:
                continue

            kv_match = kv_pattern.match(stripped_line)
            if kv_match:
                key = kv_match.group(1).strip().lower()
                value = kv_match.group(2).strip()

                # Map common markdown keys to internal database keys for suggestion engine
                if key in ['ip', 'ip address']:
                    if not current_ip:
                         current_ip = value
                elif key in ['os', 'os family', 'platform']:
                    current_target['os_family'] = value
                elif key in ['arch', 'architecture']:
                    current_target['architecture'] = value
                elif key in ['kernel', 'kernel version']:
                    current_target['kernel_version'] = value
                elif key in ['ports', 'open ports']:
                    current_target['ports'] = [int(p.strip()) for p in value.split(',') if p.strip().isdigit()]
                elif key in ['cves', 'vulnerabilities']:
                    current_target['cves'] = [c.strip() for c in value.split(',')]
                elif key in ['environment', 'env']:
                    current_target['environment'] = [e.strip() for e in value.split(',')]
                else:
                    clean_key = key.replace(' ', '_')
                    current_target[clean_key] = value

        # Save the last target found in the file
        if current_ip or current_target:
            ip_key = current_ip if current_ip else f"target_{len(targets)+1}"
            current_target['raw_content'] = '\n'.join(current_raw).strip()
            targets[ip_key] = current_target

        return targets

    @classmethod
    def importTargetsFromFile(cls, path):
        """Imports targets from a JSON or Markdown file and merges them into the targets database."""
        if not os.path.exists(path):
            # Check common locations if not found
            alt_path = os.path.join(cls.getInstall(), ".data", ".config", os.path.basename(path))
            if os.path.exists(alt_path):
                path = alt_path
            else:
                write(f"[-] Error: File {path} does not exist.\n")
                return
        try:
            new_targets = {}
            with open(path, "r", encoding="utf-8") as f:
                # Detect Markdown files by extension
                if path.lower().endswith('.md'):
                    content = f.read()
                    new_targets = cls._parse_markdown_targets(content)
                else:
                    # Fallback to standard JSON parsing
                    data = json.load(f)
                    
                    # Handle different JSON structures
                    if isinstance(data, dict):
                        if "TARGETS" in data:
                            new_targets = data["TARGETS"]
                        else:
                            new_targets = data
                    elif isinstance(data, list):
                        # Convert list of targets to dict keyed by IP
                        for item in data:
                            if isinstance(item, dict):
                                ip = item.get("ip") or item.get("IP") or item.get("ip_address")
                                if ip:
                                    new_targets[ip] = item
                
                if new_targets:
                    current_targets = cls.getTargets()
                    current_targets.update(new_targets)
                    cls.updateTargets(current_targets)
                    cls.sync_targets_to_disk()
                    write(f"[+] Successfully imported and merged {len(new_targets)} targets from {path}\n")
                else:
                    write(f"[-] No valid targets found in {path}\n")
        except Exception as e:
            write(f"[-] Failed to import targets: {e}\n")

    @classmethod
    def importModule(cls, module_type, source_path, category=None):
        """Imports an exploit or payload module, validating its metadata."""
        if not os.path.exists(source_path):
            write(f"[-] Error: Source file {source_path} does not exist.\n")
            return

        # Validate metadata
        try:
            with open(source_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if "#!#!#!" not in content:
                    write(f"[-] Warning: Module {source_path} is missing #!#!#! metadata block.\n")
                
                # Try to parse category from YAML if not provided
                if not category:
                    parts = content.split("#!#!#!")
                    if len(parts) > 1:
                        try:
                            meta = yaml.safe_load(parts[1])
                            if isinstance(meta, dict):
                                category = meta.get("category", meta.get("catogory", "misc"))
                            else:
                                category = "misc"
                        except Exception:
                            category = "misc"
                    else:
                        category = "misc"
        except Exception as e:
            write(f"[-] Error parsing metadata from {source_path}: {e}\n")
            category = category or "misc"

        # Sanitize category
        category = "".join(c for c in category if c.isalnum() or c in ("_", "-")).lower()
        
        # Determine destination
        dest_base = os.path.join(cls.getInstall(), f"{module_type}s", category)
        os.makedirs(dest_base, exist_ok=True)
        dest_path = os.path.join(dest_base, os.path.basename(source_path))

        import shutil
        try:
            shutil.copy2(source_path, dest_path)
            write(f"[*] Successfully imported {module_type} to {dest_path}\n")
            # Update cache
            ExploitCache.update()
        except Exception as e:
            write(f"[-] Failed to import {module_type}: {e}\n")

    @classmethod
    def importTemplate(cls, path):
        """Imports a C or Python template."""
        if not os.path.exists(path):
            write(f"[-] Error: File {path} does not exist.\n")
            return
        
        dest_base = os.path.join(cls.getInstall(), "templates")
        os.makedirs(dest_base, exist_ok=True)
        dest_path = os.path.join(dest_base, os.path.basename(path))

        import shutil
        try:
            shutil.copy2(path, dest_path)
            write(f"[*] Successfully imported template to {dest_path}\n")
        except Exception as e:
            write(f"[-] Failed to import template: {e}\n")

    @classmethod
    def getInstall(cls):
        try:
            if cls.get()["DEV_MODE"]:
                """Returns the framework's base installation path."""
                return cls.get()["DEV_DICT"]
            return install_location
        except Exception:
            return install_location

    @classmethod
    def deleteProfile(cls, name):
        """Deletes a profile from the profiles database."""
        try:
            profiles = cls.getProfiles()
            if name in profiles:
                del profiles[name]
                write(f"[*] Profile '{name}' deleted.\n")
                
                # Clear active profile if it was the one deleted
                db = cls.get()
                if db.get("ACTIVE_PROFILE") == name:
                    db["ACTIVE_PROFILE"] = None
            else:
                write(f"[-] Profile '{name}' not found.\n")
        except Exception as e:
            write(f"[-] Error deleting profile: {e}\n")

    @classmethod
    def deleteTarget(cls, ip):
        """Deletes a target from the targets database."""
        try:
            targets = cls.getTargets()
            if ip in targets:
                del targets[ip]
                cls.updateTargets(targets)
                cls.sync_targets_to_disk()
                write(f"[*] Target '{ip}' deleted.\n")
            else:
                write(f"[-] Target '{ip}' not found.\n")
        except Exception as e:
            write(f"[-] Error deleting target: {e}\n")

    @classmethod
    def purgeData(cls, target_type):
        """Wipes profiles, targets, or both."""
        target_type = target_type.lower()
        if target_type in ["profiles", "personas", "all"]:
            try:
                path = cls._get_path_to_profiles()
                if os.path.exists(path):
                    cls.profile_db = None
                    cls._profile_db_loaded = False
                    os.remove(path)
                    write("[*] All profiles purged.\n")
                    
                    # Clear active profile ref
                    db = cls.get()
                    db["ACTIVE_PROFILE"] = None
            except Exception as e:
                write(f"[-] Error purging profiles: {e}\n")

        if target_type in ["targets", "all"]:
            try:
                path = cls._get_path_to_targets()
                if os.path.exists(path):
                    cls._targets_cache = {}
                    cls._targets_dirty = False
                    os.remove(path)
                    write("[*] All targets purged.\n")
            except Exception as e:
                write(f"[-] Error purging targets: {e}\n")

    @classmethod
    def addVariableToDatabase(cls, data):
        """Parses a command string to add a custom variable to the JSON database."""
        # Expects format: "command key value"
        parts = data.split(" ", 2)
        if len(parts) < 3:
            # Print the help menu if the arguments are incomplete
            help_path = f"{install_location}/.data/.help/add"
            if os.path.exists(help_path):
                with open(help_path, 'r', encoding="utf-8") as file:
                    print(file.read())
            return

        try:
            database = cls.get()

            # Set the key-value pair dynamically
            database[parts[1]] = parts[2]

            cls._update(database)
        except Exception as e:
            print(f"[-] Database Error: {e}")

    @classmethod
    def findTerm(cls):
        """Locates an available terminal emulator on the host system based on a predefined list."""
        try:
            # Read preferred terminals list
            with open(f"{install_location}/.data/.config/.terminals", "r", encoding="utf-8") as file:
                terms = [line.strip() for line in file if line.strip()]

            # Also check a hardcoded fallback list just in case the file is missing or corrupted
            fallback_terms = [
                "gnome-terminal", "konsole", "xfce4-terminal", "lxterminal", 
                "mate-terminal", "xterm", "uxterm"
            ]
            
            # Combine lists, prioritizing the file
            all_terms = terms + [t for t in fallback_terms if t not in terms]

            import shutil
            for term in all_terms:
                if shutil.which(term):
                    return term
        except Exception:
            pass
            
        # Absolute last resort fallback
        import shutil
        if shutil.which("xterm"):
            return "xterm"
            
        return None

    @classmethod
    def Debug(cls, data=None):
        """Dumps all primary data structures to standard output for debugging purposes."""
        db = cls.get()
        targets = cls.getTargets()
        payloads = cls.getPayloads()
        exploitdetails = ExploitCache.details
        exploitcache = ExploitCache.metadata_index

        print(json.dumps(dict(db), indent=4))
        print(json.dumps(dict(targets), indent=4))
        print(json.dumps(payloads, indent=4))
        print(json.dumps(dict(exploitdetails), indent=4))
        print(json.dumps(dict(cls.getProfiles()), indent=4))  # Dump profiles
        print(json.dumps(dict(exploitcache), indent=4))

    @classmethod
    def _UpdateAliases(cls):
        if len(cls.aliases) > 0:
            return cls.aliases
        try:
            with open(os.path.join(cls.getInstall(), ".data", ".config", "Aliases.json"), "rb") as f:
                cls.aliases = json.load(f)
                return cls.aliases
        except FileNotFoundError:
            write("[!] Error: Aliases.json not found.")
            return {}

    @classmethod
    def getAliases(cls):
        return cls.aliases

    @classmethod
    def UpdateReconDB(cls):
        db = cls.db
        allfiles = []
        base_dir = os.path.join(install_location, "recon")
        if os.path.exists(base_dir):
            for x in sorted(os.listdir(base_dir)):
                sub_dir = os.path.join(base_dir, x)
                if os.path.isdir(sub_dir) and not x.startswith("__"):
                    files = []
                    for i in sorted(os.listdir(sub_dir)):
                        if i.endswith((".py", ".c", ".sh")) and not i.startswith("__"):
                            full_path = os.path.join(sub_dir, i)
                            allfiles.append(full_path)
                            files.append(full_path)
                    db[x] = files
        return db, allfiles

    @classmethod
    def _reconDB(cls):
        return cls.db
