import os
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
                targetList = []
                for k, v in enumerate(targets):
                    targetList.append(v)
                if 0 <= index < len(targetList):
                    selected_target = str(targetList[index])
                    DatabaseManagment.directlyModify(["target", selected_target])
                    DatabaseManagment.directlyModify(["rhost", selected_target])
                    print(f"[*] Set R_HOST to {selected_target}\n")
                else:
                    print("[-] Invalid target index.\n")
            except FileNotFoundError:
                print("[-] Targets file not found.\n")
                
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