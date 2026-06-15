import os
import traceback
import subprocess
import psutil
import socket
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from .encrypter import Encrypter
from .errors import Error
from .ToStdOut import ToStdout
from .help import Help
from .show import Show
from .set import SetV
from .use import use
from .search import Search
from .banners import Banners
from .inputfixes import Input_fixes
from .sessions import Sessions
from .clean import clean
from .database import DatabaseManagment, ExploitCache, exploitDetails
from .exploit_engine import ExploitHandler
import shlex
from .migrate_nmap_db import migrate_nmap_db
from .migrate_services import migrate_services
from .listener import Listener
from .recon_engine import Recon
from .auto_suggest import AutoSuggestCommand as ASC
from .android_kivy_generator import BuildozerPayloadGenerator
from .workspace import WorkspaceManager
from .jobs import JobManager
from .completer import SuperSploitCompleter

# set global variables
installation = DatabaseManagment.getInstall()
history = FileHistory(f'{installation}/.data/.history/history')
path = os.getenv("PATH", "").split(os.pathsep)
env = os.environ
Aliases = DatabaseManagment._UpdateAliases()


def get_network_info():
    host = socket.gethostname()
    # Iterate through all network interfaces
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            # Look for IPv4 addresses and ignore loopback (127.0.0.1)
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return addr.address, addr.netmask, host
    return None


class Input:

    @classmethod
    def _update(cls, data=None):
        ExploitCache.update()
        DatabaseManagment._UpdateAliases()

    @classmethod
    def _system_call(cls, cmd_list):
        """Executes a command by searching for it in the system's PATH."""
        try:
            command_name = cmd_list[0]
            for directory in path:
                if os.path.exists(os.path.join(directory, command_name)):
                    subprocess.run(cmd_list)
                    return True

            # Check if the user entered a direct file path that isn't executable
            if os.path.exists(command_name) and not os.access(command_name, os.X_OK):
                ToStdout.write(f"[-] '{command_name}' is not an executable command. Did you mean to use 'load' or 'exploit'?\n")
                return False

            Error(f"[!] Program not found: {command_name}")
            return False
        except OSError as e:
            ToStdout.write(f"OS Error during system call: {e}\n{traceback.format_exc()}")
            return False

    @classmethod
    def _auto_suggest(cls, data=None):
        db_data = DatabaseManagment.get()
        args = shlex.split(data) if data else []
        
        target_info = {}
        target_ip = "unknown"

        # Check if the user provided a Fingerprint string (key=value pairs)
        if len(args) > 1 and "=" in args[1]:
            # fingerprint parsing mode
            target_ip = "Fingerprint"
            for arg in args[1:]:
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    target_info[k.lower()] = v
        else:
            # Standard IP-based mode
            target_ip = args[1] if len(args) > 1 else db_data.get('R_HOST', db_data.get('TARGET', 'unknown'))
            targets_db = DatabaseManagment.getTargets()
            if target_ip in targets_db:
                target_info = targets_db[target_ip]
        
        suggester = ASC(ExploitCache)
        suggester.execute(target_ip, target_info)

    @classmethod
    def check(cls, data):
        # Sanitize and handle empty input
        clean_data = data.strip()
        # Check if there is data if not just return 0
        if not clean_data:
            return

        # Tokenize and apply aliases
        try:
            dataList = shlex.split(clean_data)
            if not dataList:
                return

            new_data_list = []
            for token in dataList:
                if token in Aliases:
                    # Re-tokenize the alias content to handle multi-word expansion
                    new_data_list.extend(shlex.split(Aliases[token]))
                else:
                    new_data_list.append(token)
            dataList = new_data_list
        except ValueError as e:
            Error(f"Failed to parse command: {e}")
            return

        # create a list to check for input fixes
        inputFixList = ["cd", "clear", "exit", "cat"]

        try:
            # Handle empty inputs (hitting Enter) gracefully
            if not dataList:
                return

            if "&&" in clean_data:
                # Recursively process each command in the chain. 
                # This allows internal framework commands and system calls to be mixed.
                for command in [c.strip() for c in clean_data.split("&&") if c.strip()]:
                    if cls.check(command) is False:
                        break
                return

            if ">" in clean_data:
                Input_fixes.out(clean_data)
                return

            if "|" in clean_data:
                Input_fixes.pipe(clean_data)
                return
            cmd_name = dataList[0]
            if cmd_name in inputFixList:
                if Input_fixes(dataList):
                    return

            # ==========================================
            # COMMAND REGISTRIES
            # ==========================================

            general_cmds = {
                "decrypt": Encrypter.decrypt_file,
                "encrypt": Encrypter.encrypt_file,
                "clean": clean,
                "shells": Show.shells,
                "help": Help.display,
                "show": Show.show,
                "set": SetV.SetV,
                "exploit": ExploitHandler,
                "edit": cls._handle_edit_command, # New: Command to edit profiles
                "use": use.execute,
                "search": Search.search,
                "banner": Banners,
                "import": cls._handle_import_command, # New: Command to import modules, profiles, and targets
                "workspace": WorkspaceManager.handle_command, # New: Command to manage isolated workspaces
                "jobs": JobManager.handle_command, # New: Command to view and terminate background tasks
                "delete": cls._handle_delete_command, # New: Command to delete specific profiles or targets
                "purge": cls._handle_purge_command,   # New: Command to wipe entire categories of user data
                "add": cls._handle_add_command, # Updated: Now handles profile imports
                "activate": cls._handle_activate_command, # New: Pro activation
                "update-info": cls._update,
                "debugdb": DatabaseManagment.Debug,
                "run": Recon,
                "sessions": Sessions.manage,
                "suggest": cls._auto_suggest,
                "up-nmap-db": cls._handle_migration,
                "up-service-db": cls._handle_service_migration,
                "generate-apk": cls._generate_apk,
                "generate-apk-buildozer": cls._generate_apk_buildozer,
                "generate-shellcode": cls._generate_shellcode,
                "compile": cls._compile_c_binary,
                "kaslr": cls._kaslr_calculator
            }

            # ==========================================
            # COMMAND EXECUTION ROUTER
            # ==========================================
            if cmd_name in general_cmds:
                general_cmds[cmd_name](data)

                # Trigger background shell listener if set
                if cmd_name == "set" and len(dataList) >= 3:
                    if dataList[1].lower() == "listener" and dataList[2].lower() == "true":
                        Listener.start(DatabaseManagment.get())

                # Trigger Recon Automation post-recon hooks if enabled
                if cmd_name == "run":
                    # The Recon class now handles internal hook triggering, 
                    # but we keep a generic trigger here for future module types.
                    pass
                return True
            else:
                # If not an internal command, treat as a system call
                return cls._system_call(dataList)

        except Exception:
            Error(traceback.format_exc())
            return False

    @classmethod
    def _handle_delete_command(cls, data):
        """Handles the 'delete' command for profiles and targets."""
        parts = shlex.split(data)
        if len(parts) < 3:
            Help.display("delete")
            return

        target_type = parts[1].lower()
        target_id = parts[2]

        if target_type in ["profile", "persona"]:
            DatabaseManagment.deleteProfile(target_id)
        elif target_type == "target":
            DatabaseManagment.deleteTarget(target_id)
        else:
            ToStdout.write(f"[-] Unknown delete type: {target_type}\n")
            Help.display("delete")

    @classmethod
    def _handle_purge_command(cls, data):
        """Handles the 'purge' command to wipe data categories."""
        parts = shlex.split(data)
        if len(parts) < 2:
            Help.display("purge")
            return

        target_type = parts[1].lower()
        DatabaseManagment.purgeData(target_type)

    @classmethod
    def _handle_activate_command(cls, data):
        """Handles the 'activate' command to unlock Pro features."""
        from .license_manager import LicenseManager
        parts = shlex.split(data)
        if len(parts) < 2:
            ToStdout.write(f"[*] Current HWID: {LicenseManager.get_hwid()}\n")
            ToStdout.write("[*] Usage: activate <LICENSE_KEY>\n")
            ToStdout.write("[*] Usage: activate status\n")
            return
            
        sub_cmd = parts[1].lower()
        if sub_cmd == "status":
            ToStdout.write(f"[*] Current HWID: {LicenseManager.get_hwid()}\n")
            if LicenseManager.check_pro_status():
                ToStdout.write("[+] Status: SuperSploit Pro [ACTIVATED]\n")
            else:
                ToStdout.write("[-] Status: SuperSploit Standard [NOT ACTIVATED]\n")
            return

        key = parts[1]
        if LicenseManager.activate(key):
            ToStdout.write("[+] SUCCESS: SuperSploit Pro Activated! All modules unlocked.\n")
        else:
            ToStdout.write("[-] ERROR: Invalid license key for this Hardware ID.\n")

    @classmethod
    def _handle_import_command(cls, data):
        """Handles the 'import' command for modules, profiles, and targets."""
        parts = shlex.split(data)
        if len(parts) < 3:
            Help.display("import")
            return

        import_type = parts[1].lower()
        import_path = parts[2]
        category = parts[3] if len(parts) > 3 else None

        # Resolve relative paths
        if not os.path.isabs(import_path):
            import_path = os.path.abspath(import_path)

        if import_type in ["profile", "profiles"]:
            DatabaseManagment.importProfileFromFile(import_path)
        elif import_type in ["target", "targets"]:
            DatabaseManagment.importTargetsFromFile(import_path)
        elif import_type in ["exploit", "payload"]:
            DatabaseManagment.importModule(import_type, import_path, category)
        elif import_type == "template":
            DatabaseManagment.importTemplate(import_path)
        else:
            ToStdout.write(f"[-] Unknown import type: {import_type}\n")
            Help.display("import")

    @classmethod
    def _handle_edit_command(cls, data):
        """Handles the 'edit' command, dispatching to appropriate sub-commands."""
        parts = shlex.split(data)
        if len(parts) < 2:
            Help.display("edit") # Display help for 'edit' command
            return

        sub_command = parts[1].lower()
        if sub_command == "profile":
            DatabaseManagment.editProfile(data)
        else:
            Help.display("edit") # Display help for 'edit' command
            ToStdout.write(f"[-] Unknown 'edit' sub-command: {sub_command}\n")

    @classmethod
    def _handle_add_command(cls, data):
        """Handles the 'add' command, supporting standard variables and profile imports."""
        parts = shlex.split(data)
        if len(parts) < 2:
            Help.display("add")
            return

        sub_command = parts[1].lower()
        if sub_command == "profile":
            # Syntax: add profile --import <IP>
            if len(parts) >= 4 and parts[2].lower() == "--import":
                target_ip = parts[3]
                DatabaseManagment.importFromTargets(target_ip)
            else:
                ToStdout.write("[-] Usage: add profile --import <IP>\n")
        else:
            # Fallback to standard variable addition
            DatabaseManagment.addVariableToDatabase(data)

    @classmethod
    def _handle_migration(cls, data):
        """Triggers the migration of the flat nmap-os-db.txt to signatures.db."""
        install = DatabaseManagment.getInstall()
        txt_path = os.path.join(install, ".data", ".config", "nmap-os-db.txt")
        db_path = os.path.join(install, ".data", ".config", "signatures.db")
        ToStdout.write("[*] Initializing OS signature database migration...\n")
        migrate_nmap_db(txt_path, db_path)

    @classmethod
    def _handle_service_migration(cls, data):
        """Triggers the migration of the flat nmap-service-probes.txt to signatures.db."""
        install = DatabaseManagment.getInstall()
        txt_path = os.path.join(install, ".data", ".config", "nmap-service-probes.txt")
        db_path = os.path.join(install, ".data", ".config", "signatures.db")
        ToStdout.write("[*] Initializing Service signature database migration...\n")
        migrate_services(txt_path, db_path)

    @classmethod
    def _generate_apk(cls, data):
        """Generates a custom Android APK Payload using the Native C Architecture."""
        import os
        import traceback
        import shlex
        from .database import DatabaseManagment
        from .native_apk_generator import NativeApkGenerator

        installation = DatabaseManagment.getInstall()
        db_data = DatabaseManagment.get()
        lhost = db_data.get("L_HOST", db_data.get("LHOST"))
        lport = db_data.get("L_PORT", db_data.get("LPORT"))
        output_name = db_data.get("OUTPUT_NAME", "payload.apk")
        template_type = db_data.get("ANDROID_PAYLOAD_TYPE", "drs")

        if not lhost or not lport:
            ToStdout.write("[-] L_HOST and L_PORT must be set to generate a payload. Use 'set L_HOST <ip>' and 'set L_PORT <port>'.\n")
            return

        parts = shlex.split(data)
        target_apk = None
        exploit_path = None

        if len(parts) > 1:
            for part in parts[1:]:
                if part.startswith("inject="):
                    target_apk = part.split("=", 1)[1]
                    if not os.path.isabs(target_apk):
                        target_apk = os.path.join(os.getcwd(), target_apk)
                elif part.startswith("exploit="):
                    exploit_path = part.split("=", 1)[1]
                    if not os.path.isabs(exploit_path):
                        exploit_path = os.path.join(os.getcwd(), exploit_path)
                elif part.lower() in ["drs", "beacon", "messages", "rootkit"]:
                    template_type = part.lower()
                else:
                    output_name = part

        # Register type for the generator
        db_data["ANDROID_PAYLOAD_TYPE"] = template_type
        
        # Native C Template
        template_file = "templates/native_drs.c"

        output_path = os.path.join(installation, "payloads", "android", output_name) if not os.path.isabs(output_name) else output_name

        # Ensure payloads directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        if target_apk:
            ToStdout.write(f"[*] Initializing Native Android Trojanization (Injecting into: {os.path.basename(target_apk)})...\n")
        elif exploit_path:
            ToStdout.write(f"[*] Initializing Native Android Exploit Embedding (Exploit: {os.path.basename(exploit_path)})...\n")
        else:
            ToStdout.write(f"[*] Initializing Native Android Payload Generator ({template_type.upper()})...\n")
        
        ToStdout.write(f"[*] LHOST: {lhost} | LPORT: {lport}\n")
        ToStdout.write(f"[*] Output: {output_path}\n")

        try:
            generator = NativeApkGenerator(output_apk_path=output_path, template_path=template_file, target_apk=target_apk, exploit_path=exploit_path)
            generator.generate()
        except Exception as e:
            ToStdout.write(f"[-] Payload generation failed: {e}\n")
            Error(traceback.format_exc())

    @classmethod
    def _generate_apk_buildozer(cls, data):
        """Generates an Android APK payload using the Kivy/Buildozer pipeline."""
        import os
        import traceback
        import shlex
        from .database import DatabaseManagment
        from .android_kivy_generator import BuildozerPayloadGenerator

        installation = DatabaseManagment.getInstall()
        db_data = DatabaseManagment.get()
        lhost = db_data.get("L_HOST", db_data.get("LHOST"))
        lport = db_data.get("L_PORT", db_data.get("LPORT"))
        output_name = db_data.get("OUTPUT_NAME", "FlappyBirds.apk")
        template_type = db_data.get("ANDROID_PAYLOAD_TYPE", "drs")

        if not lhost or not lport:
            ToStdout.write("[-] L_HOST and L_PORT must be set to generate a payload. Use 'set L_HOST <ip>' and 'set L_PORT <port>'.\n")
            return

        parts = shlex.split(data)

        if len(parts) > 1:
            if parts[1].lower() in ["drs", "beacon", "messages"]:
                template_type = parts[1].lower()
                if len(parts) > 2:
                    output_name = parts[2]
            else:
                output_name = parts[1]

        if template_type == "drs":
            template_file = "templates/payload/kivy/android_drs_template.py"
        elif template_type == "messages":
            template_file = "templates/payload/kivy/android_messages_template.py"
        else:
            template_file = "templates/payload/kivy/android_rootkit_template.py"

        output_path = os.path.join(installation, "payloads", "android", output_name) if not os.path.isabs(output_name) else output_name

        # Ensure payloads directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        ToStdout.write(f"[*] Initializing Buildozer Android Payload Generator ({template_type.upper()})...\n")
        ToStdout.write(f"[*] LHOST: {lhost} | LPORT: {lport}\n")
        ToStdout.write(f"[*] Output: {output_path}\n")

        try:
            generator = BuildozerPayloadGenerator(output_apk_path=output_path, template_path=template_file)
            generator.generate()
        except Exception as e:
            ToStdout.write(f"[-] Buildozer generation failed: {e}\n")
            Error(traceback.format_exc())

    @classmethod
    def _generate_shellcode(cls, data):
        """Generates raw shellcode and outputs it to the console."""
        db_data = DatabaseManagment.get()
        lhost = db_data.get("L_HOST", db_data.get("LHOST", "127.0.0.1"))
        lport = db_data.get("L_PORT", db_data.get("LPORT", 4444))

        parts = shlex.split(data)
        arch = "arm64" # Default
        
        if len(parts) > 1:
            arch = parts[1].lower()
            
        ToStdout.write(f"[*] Initializing Weaponized Shellcode Generator ({arch.upper()})...\n")
        ToStdout.write(f"[*] LHOST: {lhost} | LPORT: {lport}\n")
        
        try:
            from .shellcode_generator import ShellcodeGenerator
            if arch == "arm64":
                sc = ShellcodeGenerator.arm64_reverse_tcp(str(lhost), str(lport))
            elif arch in ["x86_64", "x64"]:
                sc = ShellcodeGenerator.x86_64_reverse_tcp(str(lhost), str(lport))
            else:
                ToStdout.write(f"[-] Unsupported architecture: {arch}\n")
                return
                
            formatted = "".join(f"\\x{b:02x}" for b in sc)
            ToStdout.write(f"[+] Generation successful. Shellcode Length: {len(sc)} bytes\n")
            ToStdout.write(f"{formatted}\n")
        except Exception as e:
            ToStdout.write(f"[-] Shellcode generation failed: {e}\n")
            Error(traceback.format_exc())

    @classmethod
    def _kaslr_calculator(cls, data):
        """Launches the KASLR slide calculator."""
        import sys
        import shlex
        parts = shlex.split(data)
        
        # Build command to call the tool
        cmd = [sys.executable, os.path.join(installation, "source", "tools", "kaslr_calculator.py")]
        
        # Pass any arguments provided after 'kaslr'
        if len(parts) > 1:
            cmd.extend(parts[1:])
            
        try:
            # We use subprocess.run to keep it in the same terminal and wait for it
            subprocess.run(cmd)
        except Exception as e:
            ToStdout.write(f"[-] Failed to launch KASLR calculator: {e}\n")

    @classmethod
    def _compile_c_binary(cls, data):
        """Cross-compiles a C payload into a binary executable."""
        import os
        import subprocess
        import shlex
        from .session_loader import SessionLoader

        parts = shlex.split(data)
        db = DatabaseManagment.get()
        
        target_file = None
        if len(parts) > 1:
            target_file = SessionLoader._resolve_index(parts[1])
        else:
            # Fallback to loaded exploit or payload
            exploit_path = db.get("EXPLOIT", "")
            payload_path = db.get("PAYLOAD", "")
            if exploit_path.endswith('.c') and os.path.exists(exploit_path):
                target_file = exploit_path
            elif payload_path.endswith('.c') and os.path.exists(payload_path):
                target_file = payload_path

        if not target_file or not os.path.exists(target_file):
            ToStdout.write("[-] Error: No valid C file provided or loaded.\n")
            ToStdout.write("[*] Usage: compile <path_to_c_file>\n")
            return

        if not target_file.endswith('.c'):
            ToStdout.write(f"[-] Error: Target file '{target_file}' is not a C source file (.c)\n")
            return

        comp_arch = str(db.get("COMP_ARCH", "native")).lower()
        comp_static = str(db.get("COMP_STATIC", "false")).lower() == "true"
        
        # PRO GATE: Cross-Arch and Static compilation are Pro features
        if comp_arch != "native" or comp_static:
            from .license_manager import LicenseManager
            if not LicenseManager.gate_access("Professional Compilation Suite (Cross-Arch/Static)"):
                return

        # Determine compiler based on COMP_ARCH
        compiler = "gcc"
        if comp_arch in ["arm64", "aarch64"]:
            check_arm = subprocess.run(['which', 'aarch64-linux-gnu-gcc'], capture_output=True)
            if check_arm.returncode == 0:
                compiler = 'aarch64-linux-gnu-gcc'
            else:
                ToStdout.write("[-] Error: aarch64-linux-gnu-gcc not found. Please install it.\n")
                return
        elif comp_arch in ["x86", "i686"]:
            check_x86 = subprocess.run(['which', 'i686-linux-gnu-gcc'], capture_output=True)
            if check_x86.returncode == 0:
                compiler = 'i686-linux-gnu-gcc'
            else:
                ToStdout.write("[-] Error: i686-linux-gnu-gcc not found. Please install it.\n")
                return
        elif comp_arch in ["x86_64", "x64"]:
            check_x64 = subprocess.run(['which', 'x86_64-linux-gnu-gcc'], capture_output=True)
            if check_x64.returncode == 0:
                compiler = 'x86_64-linux-gnu-gcc'
            elif subprocess.run(['which', 'gcc'], capture_output=True).returncode == 0:
                compiler = 'gcc'
        elif comp_arch == "android_arm64":
            ndk_compiler = None
            buildozer_root = os.path.expanduser("~/.buildozer")
            if os.path.exists(buildozer_root):
                import glob
                pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android*-clang")
                matches = glob.glob(pattern)
                if matches:
                    ndk_compiler = sorted(matches, reverse=True)[0]
            if ndk_compiler:
                compiler = ndk_compiler
            else:
                ToStdout.write("[-] Error: Android NDK aarch64 compiler not found in ~/.buildozer.\n")
                return
        elif comp_arch in ["android_arm", "android_v7"]:
            ndk_compiler = None
            buildozer_root = os.path.expanduser("~/.buildozer")
            if os.path.exists(buildozer_root):
                import glob
                pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/armv7a-linux-androideabi*-clang")
                matches = glob.glob(pattern)
                if matches:
                    ndk_compiler = sorted(matches, reverse=True)[0]
            if ndk_compiler:
                compiler = ndk_compiler
            else:
                ToStdout.write("[-] Error: Android NDK armv7a compiler not found in ~/.buildozer.\n")
                return
        elif comp_arch == "android_x86":
            ndk_compiler = None
            buildozer_root = os.path.expanduser("~/.buildozer")
            if os.path.exists(buildozer_root):
                import glob
                pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/i686-linux-android*-clang")
                matches = glob.glob(pattern)
                if matches:
                    ndk_compiler = sorted(matches, reverse=True)[0]
            if ndk_compiler:
                compiler = ndk_compiler
            else:
                ToStdout.write("[-] Error: Android NDK i686 compiler not found in ~/.buildozer.\n")
                return
        elif comp_arch == "android_x86_64":
            ndk_compiler = None
            buildozer_root = os.path.expanduser("~/.buildozer")
            if os.path.exists(buildozer_root):
                import glob
                pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/x86_64-linux-android*-clang")
                matches = glob.glob(pattern)
                if matches:
                    ndk_compiler = sorted(matches, reverse=True)[0]
            if ndk_compiler:
                compiler = ndk_compiler
            else:
                ToStdout.write("[-] Error: Android NDK x86_64 compiler not found in ~/.buildozer.\n")
                return

        default_out_dir = os.path.join(DatabaseManagment.getInstall(), "payloads")
        if not os.path.exists(default_out_dir):
            os.makedirs(default_out_dir)

        base_name = os.path.splitext(os.path.basename(target_file))[0]
        default_out_file = os.path.join(default_out_dir, f"{base_name}_{comp_arch}")
        
        out_file = db.get("COMP_OUT", default_out_file)

        ToStdout.write(f"[*] Compiling: {target_file}\n")
        ToStdout.write(f"[*] Architecture: {comp_arch}\n")
        ToStdout.write(f"[*] Static Linking: {comp_static}\n")
        ToStdout.write(f"[*] Compiler: {compiler}\n")
        ToStdout.write(f"[*] Output: {out_file}\n")

        ollvm_enabled = str(db.get("OLLVM_ENABLED", "false")).lower() == "true"
        
        # --- SMART VARIABLE INJECTION ---
        import re
        import tempfile
        
        lhost = db.get("LHOST", db.get("L_HOST", "127.0.0.1"))
        lport = str(db.get("LPORT", db.get("L_PORT", "5000")))
        xor_key = db.get("XOR_KEY", "SuperSploitKey")
        
        try:
            with open(target_file, 'r') as f:
                c_code = f.read()
            
            modified = False
            
            # Check for placeholders before modifying
            if any(p in c_code for p in ["{{LHOST}}", "{{LPORT}}", "{{XOR_KEY}}", "LHOST", "LPORT", "XOR_KEY"]):
                # Replace macro defines - but be careful not to break non-SS files
                # We only replace if they look like standard defines
                if re.search(r'#define LHOST\s+', c_code):
                    c_code = re.sub(r'#define LHOST\s+.*', f'#define LHOST "{lhost}"', c_code)
                    modified = True
                if re.search(r'#define LPORT\s+', c_code):
                    c_code = re.sub(r'#define LPORT\s+.*', f'#define LPORT {lport}', c_code)
                    modified = True
                if re.search(r'#define XOR_KEY\s+', c_code):
                    c_code = re.sub(r'#define XOR_KEY\s+.*', f'#define XOR_KEY "{xor_key}"', c_code)
                    modified = True
                
                # Replace Jinja-style placeholders
                if "{{LHOST}}" in c_code:
                    c_code = c_code.replace("{{LHOST}}", lhost)
                    modified = True
                if "{{LPORT}}" in c_code:
                    c_code = c_code.replace("{{LPORT}}", lport)
                    modified = True
                if "{{XOR_KEY}}" in c_code:
                    c_code = c_code.replace("{{XOR_KEY}}", xor_key)
                    modified = True
            
            if modified:
                # Create a temporary file for the patched source
                with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tmp:
                    tmp.write(c_code)
                    tmp_path = tmp.name
                compile_target = tmp_path
                ToStdout.write("[*] Patched placeholders with active C2 configuration.\n")
            else:
                compile_target = target_file
                tmp_path = None

            cmd = [compiler, compile_target, '-o', out_file, '-pthread', '-O2']
            
            # Add original directory to include path so local headers work
            cmd.extend(['-I', os.path.dirname(os.path.abspath(target_file))])
            
            # Add Android-specific linker flags ONLY for Android architectures
            if "android" in comp_arch:
                cmd.extend(['-pie', '-Wl,--hash-style=sysv'])
                
            if comp_static:
                cmd.append('-static')
            
            if ollvm_enabled:
                ToStdout.write("[*] OLLVM_ENABLED=true: Applying control flow flattening...\n")
                cmd.extend(["-mllvm", "-bcf", "-mllvm", "-sub", "-mllvm", "-fla"])

            compile_proc = subprocess.run(
                cmd,
                capture_output=True, text=True
            )
            
            # Cleanup temp file if created
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                
            if compile_proc.returncode != 0:
                ToStdout.write(f"[-] Compilation failed:\n{compile_proc.stderr}\n")
            else:
                ToStdout.write(f"[+] Compilation successful!\n")
                ToStdout.write(f"[*] Binary saved to: {out_file}\n")
        except Exception as e:
            ToStdout.write(f"[-] Execution error: {e}\n")

    @classmethod
    def get(cls):
        # load and initialize database backend
        cls.initial_db = DatabaseManagment.get()

        # update full exploit cache once at startup:
        ExploitCache.update()

        Banners(None)

        if str(cls.initial_db.get("listener", "")).lower() == "true":
            Listener.start(cls.initial_db)

        # initialize the custom word completetion
        custom_completer = SuperSploitCompleter(cls)

        while True:
            try:
                session = PromptSession(
                    history=history, 
                    auto_suggest=AutoSuggestFromHistory(), 
                    completer=custom_completer,
                    enable_history_search=True
                )
                inp = session.prompt(f"[SuperSploit]: ")
                cls.check(inp)
            except (KeyboardInterrupt, EOFError):
                DatabaseManagment._update()
                if input("[*] Are you sure you want to shutdown: ").startswith("y"):
                    print(f"\n[*] Gracefully shutting down...")
                    break
                pass
            except Exception:
                Error(traceback.format_exc())
                continue