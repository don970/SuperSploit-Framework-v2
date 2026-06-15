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

[1. Listener Initialization Phase]
    |
    +--> source/core/listener.py (listener_thread)
          |
          +--> Checks for existing certificates (`c2_cert.pem`, `c2_key.pem`) in `.data/.config/`.
          |
          +--> [If Missing]
          |     |
          |     +--> Spawns `subprocess.run(["openssl", "req", ...])` to generate them dynamically.
          |
          +--> Initializes `ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)`.
          |
          +--> Loads the cert and key into the context.
          |
          +--> Creates a raw TCP socket, binds it, and starts listening.

[2. Payload Execution Phase]
    |
    +--> Target machine executes the deployed payload (e.g., `android_messages_template.py`).
          |
          +--> Payload creates a raw TCP socket.
          |
          +--> Payload initializes `ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)`.
          |
          +--> Payload disables security checks (required for self-signed C2 certs):
          |     |
          |     +--> `ctx.check_hostname = False`
          |     |
          |     +--> `ctx.verify_mode = ssl.CERT_NONE`
          |
          +--> Payload wraps the raw socket: `ctx.wrap_socket(...)`.
          |
          +--> Payload initiates the connection: `s.connect(...)`.

[3. TLS Handshake & Communication Phase]
    |
    +--> source/core/listener.py (handle_client)
          |
          +--> Listener accepts the raw TCP connection.
          |
          +--> Listener wraps the client socket: `context.wrap_socket(raw_client, server_side=True)`.
          |
          +--> The TLS handshake is negotiated between the Payload and the Listener.
          |
          +--> [If Successful]
                |
                +--> An encrypted tunnel is established.
                |
                +--> All subsequent C2 commands and responses are transmitted over this secure channel, inside of which the data is further obfuscated using XOR and Base64.
