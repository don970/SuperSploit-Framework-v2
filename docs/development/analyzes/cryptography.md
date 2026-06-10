# SuperSploit Project Instructions

## Architecture: Cryptography System (Deep Analysis)

The Cryptography System handles the encryption and decryption of C2 communications and payload data. This logic is primarily implemented in `source/core/encrypter.py` and `source/tools/xor_encrypter.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **XOR Encryption** | A simple and fast XOR cipher is used to obfuscate data. The key is retrieved from the active database session. |
| **Base64 Encoding** | After XOR encryption, the data is Base64 encoded to ensure it can be safely transmitted over text-based protocols like HTTP. |
| **Custom Send/Recv Loops** | The `Listener` and payload templates use custom `send_enc()` and `recv_enc()` functions that automatically handle the XOR and Base64 layers, as well as message framing with a 4-byte length prefix. |

### Automation Workflow
- **Dynamic Keying**: The XOR key is dynamically injected into payload templates during generation, ensuring that each payload is keyed to the current C2 session.
- **Layered Obfuscation**: By combining XOR and Base64, the system provides a basic level of obfuscation that can bypass simple signature-based detection.
