#!/usr/bin/env python3
import sys
import base64

def xor_cipher(data: bytes, key: bytes) -> bytes:
    """
    Encrypts or decrypts data using a symmetric XOR operation with a repeating key.
    
    Args:
        data (bytes): The data to be encrypted/decrypted.
        key (bytes): The key used for the operation.
        
    Returns:
        bytes: The resulting XORed byte string.
    """
    if not key:
        raise ValueError("Key cannot be empty.")
        
    # Use a bytearray for efficient in-memory modifications
    output = bytearray(len(data))
    key_len = len(key)
    
    # Iterate through each byte and apply the XOR operational mask
    for i in range(len(data)):
        output[i] = data[i] ^ key[i % key_len]
        
    return bytes(output)

def main():
    print("========================================")
    print("       SuperSploit XOR Encrypter")
    print("========================================\n")
    
    file_path = input("Enter file path: ")
    encryption_key = input("Enter Key: ").encode()

    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
    except FileNotFoundError:
        print("[-] File not found.")
        sys.exit(1)

    choice = input("Decrypt or encrypt [d/e]: ").lower()
    
    if choice.startswith("d"):
        is_c2 = input("Is this SuperSploit C2 Traffic (Base64 + Newlines)? [y/N]: ").lower().startswith("y")
        decrypt(file_data, encryption_key, is_c2)
    else:
        encrypt(file_data, encryption_key)

def encrypt(plaintext_bytes, key_bytes):
    # Perform Encryption
    ciphertext_bytes = xor_cipher(plaintext_bytes, key_bytes)
    print(f"Ciphertext (Hex): {ciphertext_bytes.hex()}")

def decrypt(ciphertext_bytes, key_bytes, is_c2=False):
    if is_c2:
        lines = ciphertext_bytes.strip().split(b'\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            try:
                decoded = base64.b64decode(line)
                decrypted_bytes = xor_cipher(decoded, key_bytes)
                decrypted_text = decrypted_bytes.decode('utf-8', errors='ignore')
                print(f"\n--- Decrypted Payload {i+1} ---")
                print(decrypted_text)
            except Exception as e:
                print(f"\n[-] Failed to decrypt payload {i+1}: {e}")
    else:
        # Perform Decryption (Symmetric reverse pass)
        decrypted_bytes = xor_cipher(ciphertext_bytes, key_bytes)
        decrypted_text = decrypted_bytes.decode('utf-8', errors='ignore')
        print(f"Decrypted Text: {decrypted_text}")

if __name__ == "__main__":
    main()
