import base64
key = "SuperSploitKey"
# Trying both with and without the leading comma if it was part of the base64 (though comma isn't standard b64)
try:
    data = base64.b64decode("EhsUFx06FEwrOydrNhwgBhkKHGlQAAAKFScNFiABeg==")
    dec = bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])
    print(f"Decoded: {dec}")
except Exception as e:
    print(f"Error decoding: {e}")
