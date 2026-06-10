# Listener and Session Management Workflow

This document outlines how the SuperSploit C2 listener is started and how it manages incoming agent connections.

## Listener Initialization

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
                      +--> Wraps the socket with the SSL/TLS context.
                      |
                      +--> Starts a new background thread (`listener_thread`) to handle incoming connections, allowing the main framework to remain interactive.

## Session Creation and Interaction

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
                +--> A banner is printed: `[+] Background Session X opened! Type 'sessions -i X' to interact.`

## Interacting with a Session

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
                                  +--> Relays user commands over the encrypted socket to the remote agent.
                                  |
                                  +--> Receives and displays the output from the agent.
                                  |
                                  +--> Typing `background` or `bg` breaks the interaction loop and returns to the main SuperSploit prompt.
