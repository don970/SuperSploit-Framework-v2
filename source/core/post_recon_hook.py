from .database import DatabaseManagment, ExploitCache
from .auto_suggest import AutoSuggestCommand as ASC
import os

class PostReconHook:
    """
    Automated hook system that triggers exploit suggestions after a recon module finishes.
    """
    
    @classmethod
    def run_hook(cls, target_ip=None):
        """
        Main entry point for the post-recon hook.
        Analyzes the current target state and decides if suggestions should be shown.
        """
        db = DatabaseManagment.get()
        
        # 1. Check if auto_suggest is globally enabled
        # Supports both 'auto_suggest' and legacy 'suggest' variable names
        auto_suggest_enabled = db.get("auto_suggest", db.get("suggest", False))
        if not (auto_suggest_enabled is True or str(auto_suggest_enabled).lower() == "true"):
            return

        # 2. Identify the target IP to analyze
        # Priority: Explicit IP -> Current R_HOST -> All newly discovered targets
        if target_ip:
            targets_to_analyze = [target_ip]
        elif db.get('R_HOST'):
            targets_to_analyze = [db.get('R_HOST')]
        else:
            # Fallback to all targets in the database if no specific one is active
            targets_to_analyze = list(DatabaseManagment.getTargets().keys())

        if not targets_to_analyze:
            return

        print("\n" + "="*40)
        print("[*] POST-RECON AUTOMATION: Analyzing Targets")
        print("="*40)

        suggester = ASC(ExploitCache)
        targets_db = DatabaseManagment.getTargets()

        for ip in targets_to_analyze:
            if ip in targets_db:
                target_info = targets_db[ip]
                # Only suggest if the target actually has data (ports/os/etc)
                if target_info:
                    suggester.execute(ip, target_info)
            else:
                print(f"[-] Target {ip} not found in database. Skipping automation.")
        
        print("\n[*] Post-Recon Automation complete.\n")

    @classmethod
    def check_for_new_targets(cls, previous_target_count: int):
        """
        Compares current target count against a previous state to detect new discoveries.
        """
        current_targets = DatabaseManagment.getTargets()
        if len(current_targets) > previous_target_count:
            # New targets were discovered!
            print(f"[*] Post-Recon: {len(current_targets) - previous_target_count} new host(s) discovered.")
            cls.run_hook()
