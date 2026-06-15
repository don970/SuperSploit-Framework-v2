import os
import json
from cryptography.fernet import Fernet
from prompt_toolkit import prompt

installation = f'{os.getenv("HOME")}/.SuperSploit'

class Encrypter:
    @classmethod
    def load_key(cls, path):
        with open(path, "rb") as file:
            return file.read()

    @classmethod
    def get_target_file(cls, path_str):
        args = path_str.split()
        if len(args) < 2:
            print("[-] Usage: encrypt/decrypt <file_path>")
            return None
        return args[1]

    @classmethod
    def encrypt_file(cls, path_str):
        target_file = cls.get_target_file(path_str)
        if not target_file or not os.path.exists(target_file):
            print(f"[-] File not found: {target_file}")
            return False

        keys_dir = f"{installation}/.data/.security"
        os.makedirs(keys_dir, exist_ok=True)
        keys = [f"{keys_dir}/{x}" for x in os.listdir(keys_dir) if "key" in x]
        
        saved_key = False
        key = None

        if keys and prompt("[?] Would you like to use a saved key [y/n]: ").lower().startswith("y"):
            saved_key = True
            for idx, k in enumerate(keys):
                print(f"{idx}: {k}")
            try:
                choice = int(prompt("[*] Please enter the index of the key: "))
                key = cls.load_key(keys[choice]) # Fixed Typo
                print("[*] Key loaded")
            except (ValueError, IndexError):
                print("[-] Invalid selection.")
                return False
        else:
            print("[*] Generating new key")
            key = Fernet.generate_key()
            keyname = f"key_{len(keys)}"
            with open(f"{keys_dir}/{keyname}", "wb") as file:
                file.write(key)

        try:
            enc = Fernet(key)
            print(f"[*] Encrypting {target_file} ...")
            with open(target_file, "rb") as raw:
                data = raw.read()
                
            enc_data = enc.encrypt(data)
            
            with open(target_file, "wb") as raw0:
                raw0.write(enc_data)
                
            print("[*] Encryption successful.")
            return True
        except Exception as e:
            print(f"[!] Encryption failed: {e}")
            return False

    @classmethod
    def decrypt_file(cls, path_str):
        target_file = cls.get_target_file(path_str)
        if not target_file or not os.path.exists(target_file):
            print(f"[-] File not found: {target_file}")
            return False

        keys_dir = f"{installation}/.data/.security"
        keys = [f"{keys_dir}/{x}" for x in os.listdir(keys_dir) if "key" in x]
        
        if not keys:
            print("[-] No saved keys found.")
            return False

        print(f"[*] Showing stored keys")
        for idx, k in enumerate(keys):
            print(f"{idx}: {k}")

        try:
            choice = int(prompt("[*] Please enter the index of the key: "))
            key = cls.load_key(keys[choice]) # Fixed Typo
        except (ValueError, IndexError):
            print("[-] Invalid selection.")
            return False

        try:
            decoder = Fernet(key)
            with open(target_file, "rb") as file:
                data = file.read()

            print(f"[*] Decrypting {target_file}")
            decrypted_data = decoder.decrypt(data) # Removed .decode() for binary safety
            
            with open(target_file, "wb") as file: # Switched to 'wb'
                file.write(decrypted_data)
                
            print("[*] Decryption successful.")
            return True
        except Exception as e:
            print(f"[-] Decryption failed. Incorrect key? Error: {e}")
            return False