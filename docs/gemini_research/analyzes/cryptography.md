# SuperSploit Project Instructions

## Architecture: Cryptography System (Deep Analysis)

The Cryptography System handles the encryption and decryption of C2 communications and payload data. This logic is primarily implemented in `source/core/encrypter.py` and `source/tools/xor_encrypter.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **XOR Encryption** | A simple and fast XOR cipher is used to obfuscate data. The key is retrieved from the active database session. |
| **Base64 Encoding** | After XOR encryption, the data is Base64 encoded to ensure it can be safely transmitted over text-based protocols like HTTP. |
| **SSL/TLS Tunneling** | To secure the XOR'd data stream, all communication between the active C2 listener and deployed payloads is wrapped inside an SSL/TLS tunnel using dynamically generated self-signed certificates. |
| **Custom Send/Recv Loops** | The `Listener` and payload templates use custom `send_enc()` and `recv_enc()` functions that automatically handle the XOR and Base64 layers, as well as message framing with a 4-byte length prefix. |

### Automation Workflow
- **Dynamic Keying**: The XOR key is dynamically injected into payload templates during generation, ensuring that each payload is keyed to the current C2 session.
- **Layered Security**: The framework relies on SSL/TLS for transport security (protecting against MITM and network analysis) and uses XOR/Base64 primarily for in-memory payload obfuscation and basic EDR evasion.
- **Automated Certificate Generation**: If `c2_cert.pem` and `c2_key.pem` are missing, the listener automatically spawns an `openssl` subprocess to generate them before binding the port.