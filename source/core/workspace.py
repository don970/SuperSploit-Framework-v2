import os
import shutil
from .database import DatabaseManagment
from .ToStdOut import ToStdout

write = ToStdout.write

class WorkspaceManager:
    @classmethod
    def get_workspaces_dir(cls):
        install_dir = DatabaseManagment.getInstall()
        ws_dir = os.path.join(install_dir, ".data", "workspaces")
        os.makedirs(ws_dir, exist_ok=True)
        return ws_dir

    @classmethod
    def list_workspaces(cls):
        ws_dir = cls.get_workspaces_dir()
        workspaces = []
        for d in os.listdir(ws_dir):
            if os.path.isdir(os.path.join(ws_dir, d)):
                workspaces.append(d)
        if "default" not in workspaces:
            workspaces.append("default")
        return sorted(list(set(workspaces)))

    @classmethod
    def create_workspace(cls, name):
        if not name or not name.isalnum():
            write("[-] Invalid workspace name. Use alphanumeric characters only.\n")
            return
        
        ws_dir = os.path.join(cls.get_workspaces_dir(), name)
        if os.path.exists(ws_dir):
            write(f"[-] Workspace '{name}' already exists.\n")
            return
        
        os.makedirs(ws_dir)
        write(f"[*] Workspace '{name}' created.\n")
        cls.switch_workspace(name)

    @classmethod
    def delete_workspace(cls, name):
        if name == "default":
            write("[-] Cannot delete the 'default' workspace.\n")
            return
            
        active = DatabaseManagment.get_active_workspace()
        if active == name:
            write("[-] Cannot delete the active workspace. Switch to a different one first.\n")
            return
            
        ws_dir = os.path.join(cls.get_workspaces_dir(), name)
        if os.path.exists(ws_dir):
            try:
                shutil.rmtree(ws_dir)
                write(f"[*] Workspace '{name}' deleted successfully.\n")
            except Exception as e:
                write(f"[-] Failed to delete workspace '{name}': {e}\n")
        else:
            write(f"[-] Workspace '{name}' does not exist.\n")

    @classmethod
    def switch_workspace(cls, name):
        if name not in cls.list_workspaces() and name != "default":
            write(f"[-] Workspace '{name}' does not exist. Create it first.\n")
            return
            
        active_file = os.path.join(DatabaseManagment.getInstall(), ".data", ".config", "active_workspace")
        os.makedirs(os.path.dirname(active_file), exist_ok=True)
        try:
            with open(active_file, "w") as f:
                f.write(name)
            
            # Reset Database cache so it reloads on next use
            DatabaseManagment.reset_cache()
            write(f"[*] Switched to workspace: {name}\n")
        except Exception as e:
            write(f"[-] Failed to switch workspace: {e}\n")

    @classmethod
    def handle_command(cls, data):
        import shlex
        parts = shlex.split(data)
        if len(parts) < 2:
            write("[-] Usage: workspace [list | use <name> | create <name> | delete <name>]\n")
            return

        action = parts[1].lower()
        
        if action == "list" or action == "ls":
            active = DatabaseManagment.get_active_workspace()
            workspaces = cls.list_workspaces()
            write("\n========== Workspaces ==========\n")
            for ws in workspaces:
                if ws == active:
                    write(f"  * {ws} (active)\n")
                else:
                    write(f"    {ws}\n")
            write("================================\n")
        
        elif action == "use" or action == "switch":
            if len(parts) < 3:
                write("[-] Usage: workspace use <name>\n")
                return
            cls.switch_workspace(parts[2])
            
        elif action == "create" or action == "add":
            if len(parts) < 3:
                write("[-] Usage: workspace create <name>\n")
                return
            cls.create_workspace(parts[2])
            
        elif action == "delete" or action == "rm":
            if len(parts) < 3:
                write("[-] Usage: workspace delete <name>\n")
                return
            cls.delete_workspace(parts[2])
            
        else:
            write(f"[-] Unknown workspace action: {action}\n")
