import os
import subprocess
import sys
import traceback
import tempfile
import shlex
import types
import ctypes
from .logger import Logger
from .database import DatabaseManagment
from .post_recon_hook import PostReconHook

install = DatabaseManagment.getInstall()


class Recon:
    """
    Handles the loading, parsing, and execution of reconnaissance modules.
    Securely isolates root-required modules via isolated sudo subprocesses
    and dynamically loads standard modules into memory using cleaned buffers.
    """

    def __init__(self, args=None):
        # Fetch the absolute latest database state
        self.db = DatabaseManagment.get()
        
        # Capture current target count for post-recon comparison
        prev_targets = DatabaseManagment.getTargets()
        previous_target_count = len(prev_targets)

        # Clean the raw file of metadata and create a buffer for execution
        self.buffer, self.metadata = self.createBuffer()

        # Determine if root is needed via metadata flag (handles spacing and case sensitivity)
        meta_lower = self.metadata.lower()
        self.requires_root = 'root: "true"' in meta_lower or 'root: true' in meta_lower

        # Force the cached memory version to write to the disk before spawning subprocesses
        DatabaseManagment._update(self.db)
        DatabaseManagment.sync_targets_to_disk()

        _, ext = os.path.splitext(self.db["RECON_PATH"])
        if ext.lower() == ".c":
            self.c()
        else:
            if self.requires_root:
                print("[*] Metadata indicates ROOT privileges are required.")
                self.exec_with_sub(self.buffer, use_sudo=True)
            else:
                # Standard prompt for non-root scripts
                self.module = False if input("[*] Run as a module in python [y/n]: ").lower().startswith("n") else True
                if not self.module:
                    self.exec_with_sub(self.buffer, use_sudo=False)
                else:
                    self.run()

        DatabaseManagment._update(self.db)
        # Reload the targets cache into memory in case the subprocess updated it natively
        # Force the mtime check to trigger by zeroing out the last known read time
        DatabaseManagment._targets_last_mtime = 0
        current_targets = DatabaseManagment.getTargets()
        
        # Execute post-recon hooks to suggest exploits based on newly discovered data
        PostReconHook.run_hook()

    def run(self):
        """Dynamically loads the cleaned script buffer into memory as a standard user."""
        print("[*] Running in memory as standard user...")

        # Safe argument parsing
        user_input = input(f'[*] Enter arguments for {self.db["RECON_PATH"]}: ')
        args = shlex.split(user_input)

        # Dynamic namespace to prevent collisions if multiple modules run
        module_namespace = f"recon_dynamic_{self.db['RECON_NAME']}"

        # 1. Create a blank, dynamic module object
        recon_module = types.ModuleType(module_namespace)

        # 2. Add it to sys.modules so it acts like a real loaded module
        sys.modules[module_namespace] = recon_module

        try:
            # 3. Execute the CLEANED buffer directly into the module's dictionary
            # This completely ignores the uncleaned file on the hard drive
            exec(self.buffer, recon_module.__dict__)

            if len(args) == 0:
                recon_module.Start()
            else:
                recon_module.Start(args)

        except Exception:
            # Log the exception, but do NOT fall back to a risky subprocess execution
            Logger.initializeReconMoodle(self.db["RECON_NAME"], self.db["RECON_PATH"], traceback.format_exc())
            print(f"[*] In-memory execution failed:\n{traceback.format_exc()}")

        finally:
            if module_namespace in sys.modules:
                del sys.modules[module_namespace]
            print("[*] Clean up complete")

    def c(self):
        """
        Handles compilation and execution of C-based recon modules.
        Compiles the raw .c file, then attempts fileless execution via memfd_create (Linux) 
        or standard subprocess execution.
        """
        compiled_bin = os.path.join(os.getcwd(), "recon_bin")
        try:
            print("[*] Starting Recon Module Compilation")
            raw_options = input("[Enter gcc options]: ")
            options = shlex.split(raw_options) if raw_options.strip() else []
            cmd = ["gcc"] + options + [self.db["RECON_PATH"], "-o", compiled_bin]

            # Compile step
            compile_proc = subprocess.run(cmd, capture_output=True, text=True)
            if compile_proc.returncode != 0:
                print(f'[!] Compilation Failed for {self.db["RECON_PATH"]}')
                print(compile_proc.stderr)
                return

            # Execution logic
            if self.requires_root:
                print("[*] Metadata indicates ROOT privileges are required. Executing via sudo...")
                run_proc = subprocess.run(["sudo", compiled_bin], capture_output=True, text=True)
                is_success = (run_proc.returncode == 0)
            elif sys.platform == "linux":
                try:
                    print("[*] Utilizing memfd_create for fileless execution...")
                    with open(compiled_bin, "rb") as f:
                        bin_data = f.read()
                    
                    if os.path.exists(compiled_bin):
                        os.remove(compiled_bin)

                    libc = ctypes.CDLL(None)
                    fd = libc.memfd_create(b"system_recon", 1)
                    
                    if fd == -1:
                        raise Exception("Failed to create memfd descriptor")

                    os.write(fd, bin_data)
                    run_proc = subprocess.run([f"/proc/self/fd/{fd}"], capture_output=True, text=True)
                    is_success = (run_proc.returncode == 0)
                except Exception as e:
                    print(f"[!] memfd execution failed: {e}. Falling back to standard execution.")
                    run_proc = subprocess.run([compiled_bin], capture_output=True, text=True)
                    is_success = (run_proc.returncode == 0)
            else:
                print("[*] Running Recon Module via standard subprocess...")
                run_proc = subprocess.run([compiled_bin], capture_output=True, text=True)
                is_success = (run_proc.returncode == 0)

            if run_proc.stdout:
                print("[+] Recon Module Output:")
                print(run_proc.stdout.strip())
            
            if run_proc.stderr:
                print("[-] Recon Module Errors:")
                print(run_proc.stderr.strip())

            print("[*] Recon Module completed")
            if not is_success:
                Logger.initializeReconMoodle(self.db["RECON_NAME"], self.db["RECON_PATH"], run_proc.stderr)

        except Exception:
            print(f"[!] Recon Module execution failed. Check error logs.")
            Logger.initializeReconMoodle(self.db["RECON_NAME"], self.db["RECON_PATH"], traceback.format_exc())
        finally:
            if os.path.exists(compiled_bin):
                os.remove(compiled_bin)

    def createBuffer(self):
        """Reads the recon file and strips out the metadata section delimited by '#!#!#!'."""
        with open(self.db["RECON_PATH"], "r") as file:
            raw_data = file.read().split("#!#!#!")

        if len(raw_data) >= 3:
            metadata = raw_data[1]
            clean_buffer = raw_data[0] + "".join(raw_data[2:])
        else:
            metadata = ""
            clean_buffer = raw_data[0]

        # Fix relative pathing: the subprocess runs from a /tmp/ temp file, which breaks __file__ resolving.
        # Replace __file__ with the true original script path so the isolated sudo reads the right disk paths!
        clean_buffer = clean_buffer.replace("__file__", f"r'{self.db['RECON_PATH']}'")

        return clean_buffer, metadata

    def exec_with_sub(self, clean_buffer, use_sudo=False):
        """Securely executes the cleaned module via a temporary file and subprocess."""

        # Sanitize arguments via shlex to prevent shell injection
        # FIX: Prompting for input BEFORE writing the temp file closes the TOCTOU race condition window!
        user_input = input(f'[*] Enter arguments for {self.db["RECON_NAME"]}: ')
        args = shlex.split(user_input)

        # Use NamedTemporaryFile to prevent static-path race conditions
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(clean_buffer)
            temp_exec_path = tmp.name

        try:
            # Isolated Python Mode (-I) prevents PYTHONPATH environment hijacking
            if use_sudo:
                print(f"[*] Executing {self.db['RECON_NAME']} via isolated sudo subprocess...")
                # -E flag is critical to preserve the $HOME env variable so the script finds ~/.SuperSploit databases
                cmd = ["sudo", "-E", "python3", "-I", temp_exec_path] + args
            else:
                print(f"[*] Executing {self.db['RECON_NAME']} via isolated subprocess...")
                cmd = ["python3", "-I", temp_exec_path] + args

            # check=True properly catches if the script itself crashes
            subprocess.run(cmd, check=True)

        except subprocess.CalledProcessError as e:
            print(f"[*] Target script crashed or exited with error code: {e.returncode}")
        except Exception as e:
            print(f"[*] Subprocess failed to launch: {e}")
            Logger.initializeReconMoodle(self.db["RECON_NAME"], self.db["RECON_PATH"], traceback.format_exc())
        finally:
            # Ensure the temporary execution file is ALWAYS cleaned up
            if os.path.exists(temp_exec_path):
                os.remove(temp_exec_path)