import os
import re
from .database import DatabaseManagment, ExploitCache
from .ToStdOut import ToStdout
from .help import write

installation = f'{os.getenv("HOME")}/.SuperSploit'
print = ToStdout.write

class use:
    @classmethod
    def execute(cls, data):
        args = data.split()
        if len(args) < 3:
            print("[-] Usage: use <exploit|target|payload|stage2|recon> <index>\n")
            return
            
        category = args[1].lower()
        
        try:
            index = int(args[2])
        except ValueError:
            print("[-] Error: Index must be a number.\n")
            return

        if category == "exploit":
            exploits = DatabaseManagment.getExploits()
            if 0 <= index < len(exploits):
                exploit_path = exploits[index]
                DatabaseManagment.directlyModify(["exploit", exploit_path])
                ExploitCache._parse_details(exploit_path)  # Explicitly update the cache
                print(f"[*] Set exploit to {exploit_path}\n")
            else:
                print("[-] Invalid exploit index.\n")
                
        elif category == "target":
            try:
                targets = DatabaseManagment.getTargets()
                target_keys = list(targets.keys())
                if 0 <= index < len(target_keys):
                    selected_key = target_keys[index]
                    target_info = targets[selected_key]
                    
                    DatabaseManagment.directlyModify(["target", selected_key])
                    print(f"[*] Set R_HOST to {selected_key}\n")
                    
                    # Check for MAC address in key or metadata
                    mac_addr = ""
                    # regex to detect MAC address format
                    mac_regex = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
                    
                    if re.match(mac_regex, selected_key):
                        mac_addr = selected_key
                    elif isinstance(target_info, dict):
                        mac_addr = target_info.get("mac", target_info.get("mac_address", ""))
                    
                    if mac_addr:
                        DatabaseManagment.directlyModify(["r_mac", mac_addr])
                        print(f"[*] Set R_MAC to {mac_addr}\n")
                else:
                    print("[-] Invalid target index.\n")
            except FileNotFoundError:
                print("[-] Targets file not found.\n")
            except Exception as e:
                print(f"[-] Error selecting target: {e}\n")
                
        elif category == "payload":
            payloads = DatabaseManagment.getPayloads()
            if 0 <= index < len(payloads):
                DatabaseManagment.directlyModify(["payload", payloads[index]])
                print(f"[*] Set payload to {payloads[index]}\n")
            else:
                print("[-] Invalid payload index.\n")

        elif category in ["stage2", "stage_two"]:
            payloads = DatabaseManagment.getPayloads()
            if 0 <= index < len(payloads):
                DatabaseManagment.directlyModify(["stage2", payloads[index]])
                print(f"[*] Set STAGE_TWO to {payloads[index]}\n")
            else:
                print("[-] Invalid stage2 payload index.\n")

        elif category == "recon":
            recondb, paths = DatabaseManagment.UpdateReconDB()
            if 0 <= index < len(paths):
                name = paths[int(index)].split("/")[-1]
                print(f"[*] Set RECON_NAME to {name}\n")
                DatabaseManagment.directlyModify(["recon_name", name])
                print(f"[*] Set RECON_PATH to {paths[int(index)]}\n")
                DatabaseManagment.directlyModify(["recon_path", paths[int(index)]])
            else:
                print("[-] Invalid recon index.\n")

        elif category in ["profile", "profiles", "persona"]:
            profiles_db = DatabaseManagment.getProfiles()
            profile_list = list(profiles_db.keys())
            if 0 <= index < len(profile_list):
                selected_profile = profile_list[index]
                DatabaseManagment.directlyModify(["profile", selected_profile])
                print(f"[*] Set ACTIVE_PROFILE to {selected_profile}\n")
            else:
                print("[-] Invalid profile index.\n")
        else:
            print(f"[-] Unknown category: {category}\n")