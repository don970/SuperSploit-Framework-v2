import os
import sys
import subprocess
import shlex
from .ToStdOut import ToStdout

true = True
false = False
print = ToStdout.write

class Input_fixes:

    def __init__(self, dataList: list):
        self.list = dataList
        
        # Command Registry for cleaner execution
        self.fixes_registry = {
            "cd": self.cd,
            "clear": self.clear,
            "exit": self.exit,
            "cat": self.cat,
            # We remove ">" from here as it shouldn't be the *first* word in a command. 
            # Redirection is handled separately in `continues` or `out`
        }

        cmd_name = dataList[0]
        if cmd_name in self.fixes_registry:
            self.fixes_registry[cmd_name]()
        return

    @classmethod
    def continues(cls, data: str):
        def proc_one(cmd_string: str):
            # Sanitize the split! If " > " or ">" is used.
            if ">" in cmd_string:
                # Split cleanly on the first occurrence of ">"
                parts = cmd_string.split(">", 1)
                cmd_part = parts[0].strip()
                file_part = parts[1].strip()
                
                try:
                    # shlex.split sanitizes input and handles quotes safely
                    sanitized_cmd = shlex.split(cmd_part)
                    output = subprocess.run(sanitized_cmd, capture_output=True, text=True)
                    
                    with open(file_part, "a") as file:
                        file.write(output.stdout)
                    return 0
                except Exception as e:
                    print(f"[-] Error writing to file: {e}\n")
                    return 1

            try:
                if "help" in cmd_string:
                    return (1, cmd_string)
                
                sanitized_cmd = shlex.split(cmd_string)
                subprocess.run(sanitized_cmd)
                return 0
            except FileNotFoundError:
                print(f"[-] Command not found: {sanitized_cmd[0]}\n")
                return 1

        proc_exit_codes = []
        # Support "&&" even if spacing is weird
        chained_commands = [c.strip() for c in data.split("&&") if c.strip()]
        
        for x in chained_commands:
            i = proc_one(x)
            if i != 0: 
                return i 
        return 0

    def cat(self):
        # Sanitize missing arguments
        if len(self.list) < 2 or not self.list[1]:
            print("[-] Usage: cat <filename>\n")
            return False
            
        file_path = self.list[1]
        
        # Check if file exists before trying to open it
        if not os.path.isfile(file_path):
            print(f"[-] cat: {file_path}: No such file or directory\n")
            return False

        try:
            with open(file_path, "r") as file:
                print(file.read() + "\n")
        except PermissionError:
            print(f"[-] cat: {file_path}: Permission denied\n")
        except Exception as e:
            print(f"[-] Error reading file: {e}\n")
        return True

    @staticmethod
    def exit():
        sys.exit()

    def cd(self) -> int:
        # If user just types "cd", default to their HOME directory
        target_dir = self.list[1] if len(self.list) > 1 else os.getenv("HOME", "/")
        
        try:
            os.chdir(target_dir)
            return 0
        except FileNotFoundError:
            print(f"[-] cd: {target_dir}: No such file or directory\n")
            return 1
        except PermissionError:
            print(f"[-] cd: {target_dir}: Permission denied\n")
            return 1

    @staticmethod
    def clear():
        print("\033[H\033[J")

    @classmethod
    def out(cls, data: str):
        if ">" not in data:
            return

        parts = data.split(">", 1)
        cmd_part = parts[0].strip()
        file_part = parts[1].strip()

        if not file_part:
            print("[-] Error: No file specified for redirection.\n")
            return

        try:
            # shlex securely splits the command
            sanitized_cmd = shlex.split(cmd_part)
            output = subprocess.run(sanitized_cmd, capture_output=True, text=True)

            with open(file_part, "a") as file:
                file.write(output.stdout)
        except Exception as e:
            print(f"[-] Redirection Error: {e}\n")

    @classmethod
    def pipe(cls, data: str):
        """Executes a command string containing pipes (|) via a subshell."""
        if "|" not in data:
            return

        try:
            # We use shell=True to let the OS handle the complex pipe logic.
            # This ensures compatibility with grep, awk, sed, etc.
            subprocess.run(data, shell=True)
        except Exception as e:
            print(f"[-] Piping Error: {e}\n")