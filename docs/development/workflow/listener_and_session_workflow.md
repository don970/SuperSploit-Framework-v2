# SuperSploit Listener & Session Management Workflow (End-to-End)

This document outlines the complete, end-to-end workflow for how the SuperSploit C2 listener is started, how it manages incoming agent connections, and how operators interact with established sessions.

---

## 1. Stager Generation & Handler Deployment

**Trigger:** User runs an exploit that requires a handler (e.g., a reverse shell).

1.  **Exploit Engine (`exploit_engine.py`)**:
    *   The `python()` method in `ExploitHandler` detects that a `handler` is required by parsing the exploit's metadata.
    *   It calls `Listener.start()` to initialize the C2 listener in a background thread.

2.  **Listener Initialization (`listener.py`)**:
    *   **Cleanup**: Checks for and terminates any previously active listener sockets to free up the port.
    *   **Certificate Generation**: Automatically generates a self-signed SSL/TLS certificate (`c2_cert.pem`, `c2_key.pem`) if one doesn't exist.
    *   **Socket Binding**: Creates a new TCP socket and binds it to the configured `LHOST` and `LPORT`. It sets `SO_REUSEADDR` and `SO_REUSEPORT` to prevent "Address already in use" errors.
    *   **Asynchronous Handling**: Spawns a new background thread (`listener_thread`) to handle incoming connections, ensuring the main SuperSploit CLI remains interactive.

3.  **Stager Generation (`stager_generator.py`)**:
    *   If the exploit uses a stager, the `StagerGenerator` reads the appropriate template file.
    *   It injects the active `LHOST`, `LPORT`, and `XOR_KEY` from the database into the template.
    *   The finalized stager is then delivered to the target as part of the exploit's execution.

---

## 2. Session Creation & Automated Enumeration

**Trigger:** A payload (stager) is executed on a target machine and connects back to the listener.

1.  **Connection Acceptance (`listener.py`)**:
    *   The `server.accept()` call in the `listener_thread` receives the new connection.
    *   A new thread is spawned via `handle_client()` to manage the session independently.

2.  **Session Handshake & Registration**:
    *   **TLS Wrapping**: The listener peeks at the first byte of the incoming connection. If it's a TLS `ClientHello` (`0x16`), the raw socket is wrapped in the SSL context, completing the handshake.
    *   **Stage 2 Injection**: If the `deploy_stage2` flag is set, the listener compresses (zlib), encrypts (XOR), and Base64-encodes the Stage 2 payload. It then sends this payload to the stager, which executes it entirely in memory.
    *   **Session Registry**: The new connection is assigned a unique `session_id` and stored in the `active_sessions` dictionary, which tracks the socket object and the target's address.
    *   A notification is printed to the console: `[+] Background Session X opened! Type 'sessions -i X' to interact.`

3.  **Automated Enumeration (`AUTO_ENUM`)**:
    *   If the `AUTO_ENUM` setting is enabled in the framework database, the listener automatically begins post-exploitation.
    *   It detects the target's OS (Android) and architecture (`uname -m`).
    *   It cross-compiles the appropriate enumeration tool (e.g., `android-enum3.c`) for the target's architecture.
    *   The compiled binary is uploaded to `/data/local/tmp`, executed, and then deleted.
    *   The enumeration report is parsed for critical vulnerabilities, which are then automatically added to the target's profile in `profiles.db`.

---

## 3. Session Interaction & C2 Communication

**Trigger:** User enters `sessions -i <session_id>` into the main CLI.

1.  **Command Routing (`input_handling_engine.py`)**:
    *   The input engine parses the `sessions` command and identifies the `-i` flag for interaction.
    *   It calls `Listener.interact()` with the specified session ID.

2.  **Interactive C2 Shell (`listener.py`)**:
    *   The `interact()` method retrieves the correct socket object from the `active_sessions` dictionary.
    *   It drops the operator into a dedicated command loop for that session, displaying a session-specific prompt (e.g., `Session 1> `).
    *   The session is marked as "busy" to prevent heartbeat race conditions during interaction.

3.  **C2 Command & Control Loop**:
    *   **Local Commands**: The C2 shell first checks if the command is a local handler (e.g., `upload`, `download`, `load`, `background`, `exit`). If so, it's handled directly by the listener's Python code.
    *   **Remote Commands**: If the command is not a local handler, it's assumed to be a command for the remote agent.
    *   **Cryptography Layer**: The command is encrypted using the active `XOR_KEY` and Base64 encoded.
    *   **Transmission**: The encrypted command is sent over the TLS-wrapped socket to the remote agent.
    *   **Response Handling**: The listener waits for, decrypts, and displays the output from the agent.

---

## 4. Session Termination

1.  **Graceful Exit**:
    *   When `exit` or `quit` is typed in a session, the listener sends a shutdown command to the remote agent.
    *   The agent terminates itself, the listener closes the socket, and the session is removed from the `active_sessions` dictionary.

2.  **Backgrounding**:
    *   Typing `background` or `bg` breaks the interaction loop and returns the operator to the main SuperSploit prompt, leaving the session alive.

3.  **Heartbeat Monitoring**:
    *   A background `heartbeat_monitor` thread periodically sends 0-byte frames to all non-interactive sessions.
    *   If a session fails to respond (due to a network drop or crash), the socket is closed, and the session is automatically purged from the registry.

4.  **Forced Termination**:
    *   The `sessions -k <id>` command allows an operator to forcefully kill a session. The listener closes the socket and removes the session from the registry.

---

## Quick-Reference Workflow

[User runs an exploit that requires a handler (e.g., a reverse shell)]
    |
    +--> source/core/exploit_engine.py
          |
          +--> The `python()` method detects that a handler is needed.
          |
          +--> Calls `Listener.start()`
                |
                +--> source/core/listener.py (Listener.start)
                      |
                      +--> Checks for and cleans up any previously active listener sockets.
                      |
                      +--> Auto-generates a self-signed SSL/TLS certificate if one doesn't exist.
                      |
                      +--> Creates a new TCP socket and binds it to the configured LHOST and LPORT.
                      |
                      +--> Wraps the socket with the `ssl.PROTOCOL_TLS_SERVER` context.
                      |
                      +--> Starts a new background thread (`listener_thread`) to handle incoming connections, allowing the main framework to remain interactive.

[A payload is executed on a target machine and connects back to the listener]
    |
    +--> source/core/listener.py (listener_thread)
          |
          +--> The `server.accept()` call receives the new connection.
          |
          +--> A new thread is spawned to handle the client via `handle_client()`.
                |
                +--> The raw socket is wrapped in the SSL context, completing the TLS handshake.
                |
                +--> The connection is assigned a unique `session_id`.
                |
                +--> The session (socket object, address, ID) is stored in the `active_sessions` dictionary.
                |
                +--> **AUTO_ENUM Trigger**: The listener checks framework configurations for `AUTO_ENUM`.
                     |
                     +--> If enabled, automatically cross-compiles and deploys `android-enum3.c` or `linux_enum.c` to the target.
                     |
                     +--> Parses vulnerabilities from the enum output and updates `profiles.db`.
                |
                +--> A banner is printed: `[+] Background Session X opened!`
<<<<<<< Updated upstream

## Interacting with a Session
=======
>>>>>>> Stashed changes

[User Input: "sessions -i 1"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "sessions" command)
                |
                +--> Identifies the `-i` flag for interaction.
                |
                +--> Calls `Listener.interact()` with the specified session ID.
                      |
                      +--> source/core/listener.py (Listener.interact)
                            |
                            +--> Retrieves the correct socket object from the `active_sessions` dictionary.
                            |
                            +--> Enters a dedicated command loop for that session.
                                  |
                                  +--> Displays the session-specific prompt (e.g., `Session 1> `).
                                  |
                                  +--> Intercepts commands (e.g., `upload`, `download`, `auto_root`).
                                  |
                                  +--> **Cryptography Layer**: Encrypts the payload/command using AES-256-GCM (with dynamic 12-byte Nonce/IV) and Base64 encodes the stream.
                                  |
                                  +--> Transmits the length-prefixed packet over the TLS socket.
                                  |
                                  +--> Receives and displays the output from the agent.
                                  |
                                  +--> Typing `background` or `bg` breaks the interaction loop and returns to the main SuperSploit prompt.