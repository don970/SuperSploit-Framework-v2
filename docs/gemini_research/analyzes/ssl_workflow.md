# SuperSploit Project Instructions

## Architecture: SSL/TLS Workflow (Deep Analysis)

This document outlines the workflow of how SSL/TLS encryption is established between the Command & Control (C2) listener and the deployed payloads within the SuperSploit framework. This ensures that all post-exploitation traffic remains encrypted and hidden from basic network inspection.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Certificate Generation** | The framework utilizes `openssl` to automatically generate ephemeral, self-signed RSA-4096 certificates if they are not already present in the configuration directory. |
| **Server-Side Context (`listener.py`)** | The C2 listener initializes an `ssl.SSLContext` configured as a `PROTOCOL_TLS_SERVER`. It loads the generated certificate chain and private key, waiting to wrap incoming raw TCP connections. |
| **Client-Side Context (Payloads)** | Payloads (like `android_messages_template.py`) initialize an `ssl.SSLContext` configured as a `PROTOCOL_TLS_CLIENT`. |
| **Certificate Verification Override** | Because the C2 server uses a self-signed certificate, payloads must explicitly disable hostname checking (`check_hostname = False`) and verification (`verify_mode = ssl.CERT_NONE`) to allow the handshake to succeed. |

### Automation Workflow

1. **Listener Initialization Phase**
    *   The listener thread starts and checks for existing certificates (`c2_cert.pem`, `c2_key.pem`) in `.data/.config/`.
    *   If they are missing, it dynamically spawns an `openssl` subprocess to generate new self-signed certificates.
    *   It initializes `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)` and loads the certificate and key.
    *   It creates a raw TCP socket, binds it, and starts listening.

2. **Payload Execution Phase**
    *   The deployed payload (e.g., `android_messages_template.py`) is executed on the target machine.
    *   The payload creates a raw TCP socket and initializes `ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)`.
    *   It disables security checks (`ctx.check_hostname = False`, `ctx.verify_mode = ssl.CERT_NONE`) to permit the use of the self-signed C2 certificate.
    *   It wraps the raw socket (`ctx.wrap_socket(...)`) and initiates the connection to the listener.

3. **TLS Handshake & Communication Phase**
    *   The listener accepts the raw TCP connection and wraps the client socket (`context.wrap_socket(raw_client, server_side=True)`).
    *   The TLS handshake is negotiated between the payload and the listener.
    *   Once successful, an encrypted tunnel is established.
    *   All subsequent C2 commands and responses are transmitted over this secure channel, inside of which the data is further obfuscated using XOR and Base64.
