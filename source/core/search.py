from .database import DatabaseManagment, ExploitCache
import os
import shlex
from rich.console import Console
from rich.table import Table

from .ToStdOut import ToStdout

write = ToStdout.write
console = Console()

class Search:
    @classmethod
    def search(cls, data):
        # Ensure the metadata index is up-to-date before searching
        ExploitCache.update()

        try:
            parts = shlex.split(data)
        except ValueError as e:
            write(f"[-] Error parsing search command: {e}")
            return

        if len(parts) < 2:
            write("Usage: search <exploits|payloads|targets|recon|loadable|profiles> [keywords/filters]")
            return

        category = parts[1].lower()
        raw_terms = parts[2:]
        search_terms = []
        filters = {}

        for term in raw_terms:
            if "=" in term:
                k, v = term.split("=", 1)
                filters[k.lower()] = v.lower()
            else:
                search_terms.append(term.lower())
        
        if category in ["recon", "exploits", "payloads", "loadable"]:
            if category == "recon":
                _, path_list = DatabaseManagment.UpdateReconDB()
                source_list = path_list
            elif category == "loadable":
                source_list = ExploitCache.all_exploits + ExploitCache.all_payloads
            elif category == "exploits":
                source_list = ExploitCache.all_exploits
            elif category == "payloads":
                source_list = ExploitCache.all_payloads

            table = Table(show_header=True, header_style="bold magenta", title=f"Search Results: {category.capitalize()}")
            table.add_column("Idx", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Category")
            table.add_column("Vulnerability")
            table.add_column("Path", style="dim")

            match_count = 0
            for i, path in enumerate(source_list):
                if "__pycache__" in path:
                    continue

                meta = ExploitCache.metadata_index.get(path, {})
                reqs = " ".join(map(str, meta.get('requirements', []))) if isinstance(meta.get('requirements'), list) else str(meta.get('requirements', ""))
                keywords = " ".join(map(str, meta.get('keywords', []))) if isinstance(meta.get('keywords'), list) else str(meta.get('keywords', ""))

                match_pool = (
                    f"{path} {meta.get('name')} {meta.get('cve')} {meta.get('cwe')} "
                    f"{meta.get('desc')} {meta.get('cat')} {meta.get('target')} "
                    f"{meta.get('os')} {meta.get('arch')} {meta.get('kernel')} "
                    f"{meta.get('min_ver')} {meta.get('max_ver')} {reqs} {keywords}"
                ).lower()

                match_keywords = all(term in match_pool for term in search_terms)
                match_filters = all(v in str(meta.get(k, "")).lower() for k, v in filters.items())

                if match_keywords and match_filters:
                    cve_cwe = meta.get('cve', 'N/A')
                    if cve_cwe == 'N/A': cve_cwe = meta.get('cwe', 'N/A')
                    
                    # Truncate path for display
                    display_path = os.path.relpath(path, DatabaseManagment.getInstall())
                    
                    table.add_row(str(i), meta.get('name', 'Unknown'), meta.get('cat', 'N/A'), cve_cwe, display_path)
                    match_count += 1
            
            if match_count > 0:
                console.print(table)
            else:
                write("[-] No modules matched your search criteria.\n")
            return

        if category == "targets":
            try:
                targets = DatabaseManagment.getTargets()
                if not isinstance(targets, dict) or not targets:
                    write("[-] Targets database is empty.\n")
                    return
                
                table = Table(show_header=True, header_style="bold green", title="Search Results: Targets")
                table.add_column("Idx", style="dim", width=4)
                table.add_column("IP / Hostname", style="cyan")
                table.add_column("OS")
                table.add_column("Architecture")
                table.add_column("Ports")
                
                match_count = 0
                for i, (k, v) in enumerate(targets.items()):
                    target_match_pool = k.lower()
                    target_data = {'ip': k.lower()}
                    
                    if isinstance(v, dict):
                        target_match_pool += " " + " ".join(str(val).lower() for val in v.values())
                        target_data.update({key.lower(): str(val).lower() for key, val in v.items()})
                    else:
                        target_match_pool += " " + str(v).lower()
                        target_data["status"] = str(v).lower()

                    match_keywords = all(term in target_match_pool for term in search_terms)
                    match_filters = all(v_filt in target_data.get(k_filt, "") for k_filt, v_filt in filters.items())

                    if match_keywords and match_filters:
                        # Improved key mapping for diverse recon module outputs
                        # Use the original dict 'v' to preserve casing, but fallback to target_data (lowercase)
                        os_fam = v.get('os_family', v.get('os', v.get('os_guess', target_data.get('os_family', 'Unknown'))))
                        arch = v.get('architecture', v.get('arch', target_data.get('architecture', 'Unknown')))
                        
                        # Smart Port/Service display
                        ports_val = v.get('ports', v.get('open_ports', v.get('bluetooth_services', v.get('services', []))))
                        if isinstance(ports_val, list):
                            if len(ports_val) > 0:
                                if isinstance(ports_val[0], dict): # Port scanner format
                                    ports_summary = ", ".join([str(p.get('port', '')) for p in ports_val[:3]])
                                    if len(ports_val) > 3: ports_summary += "..."
                                else: # Simple list of names (Bluetooth services)
                                    ports_summary = f"{len(ports_val)} services"
                            else:
                                ports_summary = "None"
                        else:
                            ports_summary = str(ports_val)
                        
                        # Hostname display
                        hostname = v.get('hostname', v.get('name', k))
                        
                        table.add_row(str(i), str(hostname), str(os_fam), str(arch), ports_summary)
                        match_count += 1
                        
                if match_count > 0:
                    console.print(table)
                else:
                    write("[-] No targets matched your search criteria.\n")
            except Exception as e:
                write(f"[-] Error parsing targets database: {e}\n")
            return

        if category in ["profiles", "personas"]:
            try:
                profiles_db = DatabaseManagment.getProfiles()
                if not profiles_db:
                    write("[-] Profiles database is empty.\n")
                    return
                    
                table = Table(show_header=True, header_style="bold yellow", title="Search Results: Profiles")
                table.add_column("Idx", style="dim", width=4)
                table.add_column("Name", style="cyan")
                table.add_column("IP")
                table.add_column("System")
                table.add_column("Phone/Email")

                match_count = 0
                for i, (name, p) in enumerate(profiles_db.items()):
                    match_pool = f"{name} {p.get('ip', '')} {p.get('phone', '')} {p.get('email', '')} {p.get('address', '')} {p.get('geolocation', '')} {p.get('os', '')} {p.get('arch', '')}"
                    match_pool += " " + " ".join(p.get('social_medias', []))
                    match_pool += " " + " ".join(p.get('research', []))
                    match_pool = match_pool.lower()

                    match_keywords = all(term in match_pool for term in search_terms)
                    
                    if match_keywords:
                        system = f"{p.get('os', 'N/A')} {p.get('arch', '')}".strip()
                        contact = f"{p.get('phone', 'N/A')} / {p.get('email', 'N/A')}"
                        table.add_row(str(i), name, str(p.get('ip', 'N/A')), system, contact)
                        match_count += 1
                        
                if match_count > 0:
                    console.print(table)
                else:
                    write("[-] No profiles matched your search criteria.\n")
            except Exception as e:
                write(f"[-] Error searching profiles: {e}\n")
            return

        write("Usage: search <exploits|payloads|targets|recon|loadable|profiles> [keyword]")
