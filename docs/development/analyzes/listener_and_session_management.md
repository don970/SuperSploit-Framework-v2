# SuperSploit Project Instructions

## Architecture: Listener & Session Management (Deep Analysis)

The Listener acts as the Command & Control (C2) server, managing incoming connections and routing operator commands. This logic is primarily implemented in `source/core/listener.py`.

### Connection Handlers & Mechanisms

| Feature | Description |
| :--- | :--- |
| **TLS/SSL Encryption** | Generates ephemeral, self-signed certificates to establish secure tunnels, wrapping raw TCP sockets to prevent network sniffing. |
| **Stage 2 Deployment** | Intercepts initial connections, compresses (zlib), XOR encrypts, and Base64 encodes the Stage 2 payload before injecting it into the agent. |
| **Heartbeat Monitor** | Background daemon thread that periodically sends 0-byte frames to purge dead or hung sessions automatically. |
| **Keepalive Optimization** | Modifies OS-level socket options (`SO_KEEPALIVE`, `TCP_KEEPIDLE`) to maintain stable connections across network NATs and firewalls. |

### Automation Workflow
- **Background Execution**: Operates asynchronously via daemon threads, allowing the operator to continue interacting with the main SuperSploit framework.
- **Port Reclamation**: Implements `SO_REUSEADDR` and `SO_REUSEPORT` to forcefully unbind sockets, preventing "Address already in use" errors during rapid exploit testing.
- **Session Registry**: Automatically tracks active connections (Socket, IP, Session ID) and maps them into an interactive console matrix (`sessions -i <id>`).
