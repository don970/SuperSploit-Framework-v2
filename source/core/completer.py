import os
from prompt_toolkit.completion import Completer, Completion
import shlex

class SuperSploitCompleter(Completer):
    def __init__(self, input_engine):
        self.input_engine = input_engine
        # Dynamically map the commands from the Input class's general_cmds
        self.commands = [
            "decrypt", "encrypt", "clean", "shells", "help", "show", "set", 
            "exploit", "edit", "use", "search", "banner", "import", "workspace", 
            "jobs", "delete", "purge", "add", "update-info", "debugdb", "run", 
            "sessions", "suggest", "up-nmap-db", "up-service-db", "generate-apk", 
            "generate-apk-buildozer", "generate-shellcode", "compile", "kaslr",
            "apk-crypter", "cd", "clear", "exit", "cat"
        ]

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        try:
            parts = shlex.split(text)
            if text.endswith(" "):
                parts.append("")
        except ValueError:
            # If shlex fails (e.g. unclosed quote), fallback to simple split
            parts = text.split(" ")
            if text.endswith(" "):
                parts.append("")

        if not parts:
            return

        current_word = parts[-1]
        
        # 1. Complete main commands if we are on the first word
        if len(parts) == 1:
            for cmd in self.commands:
                if cmd.startswith(current_word.lower()):
                    yield Completion(cmd, start_position=-len(current_word))
            return

        first_command = parts[0].lower()

        # 2. Complete 'use' with paths
        if first_command == "use" and len(parts) == 2:
            from .database import ExploitCache
            # Provide paths relative to payloads/ or exploits/
            install_dir = self.input_engine.DatabaseManagment.getInstall()
            all_modules = ExploitCache.all_exploits + ExploitCache.all_payloads
            
            for path in all_modules:
                # Strip the absolute path to make it relative for the user
                rel_path = os.path.relpath(path, install_dir)
                if rel_path.startswith(current_word):
                    yield Completion(rel_path, start_position=-len(current_word))
            return

        # 3. Complete 'workspace' actions and names
        if first_command == "workspace":
            from .workspace import WorkspaceManager
            actions = ["list", "use", "create", "delete", "ls", "switch", "add", "rm"]
            if len(parts) == 2:
                for a in actions:
                    if a.startswith(current_word.lower()):
                        yield Completion(a, start_position=-len(current_word))
            elif len(parts) == 3 and parts[1].lower() in ["use", "delete", "switch", "rm"]:
                workspaces = WorkspaceManager.list_workspaces()
                for ws in workspaces:
                    if ws.startswith(current_word):
                        yield Completion(ws, start_position=-len(current_word))
            return
            
        # 4. Complete 'show' options
        if first_command == "show" and len(parts) == 2:
            show_opts = ["options", "advanced", "targets", "profiles", "profile"]
            for opt in show_opts:
                if opt.startswith(current_word.lower()):
                    yield Completion(opt, start_position=-len(current_word))
            return
            
        # 5. Complete 'search' categories
        if first_command == "search" and len(parts) == 2:
            search_opts = ["exploits", "payloads", "targets", "recon", "loadable", "profiles"]
            for opt in search_opts:
                if opt.startswith(current_word.lower()):
                    yield Completion(opt, start_position=-len(current_word))
            return
