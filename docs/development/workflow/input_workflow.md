[User Input: "run"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses "run" command)
                |
                +--> source/core/exploit_engine.py (ExploitHandler)
                      |
                      |--> [1. Payload Generation Phase]
                      |    |
                      |    +--> Checks if a PAYLOAD is set in the database.
                      |    |
                      |    +--> Calls `generate_payload()`
                      |          |
                      |          +--> source/core/stager_generator.py (StagerGenerator)
                      |                |
                      |                +--> Reads the payload template (e.g., android_messages_template.py).
                      |                |
                      |                +--> Replaces placeholders like {{LHOST}} and {{XOR_KEY}}.
                      |                |
                      |                +--> Returns a one-liner stager.
                      |
                      |--> [2. Exploit Execution Phase]
                      |    |
                      |    +--> Determines exploit type (e.g., .py, .sh, .c).
                      |    |
                      |    +--> Calls the appropriate runner (e.g., `python()`).
                      |          |
                      |          +--> [If Python]
                      |                |
                      |                +--> Asks user to run as a module.
                      |                |
                      |                +--> Asks user if a handler is needed.
                      |                      |
                      |                      +--> [If Handler Needed]
                      |                            |
                      |                            +--> source/core/listener.py (Listener.start)
                      |                                  |
                      |                                  +--> Starts the SSL/TLS listener in a background thread.
                      |
                      |--> [3. Payload Detonation Phase (on Target)]
                           |
                           +--> The generated one-liner stager is executed on the target machine.
                                 |
                                 +--> The stager connects back to the SuperSploit listener.
                                       |
                                       +--> source/core/listener.py (handle_client)
                                             |
                                             +--> Accepts the new connection.
                                             |
                                             +--> [If Stage 2 Enabled]
                                             |     |
                                             |     +--> Reads the Stage 2 payload from disk.
                                             |     |
                                             |     +--> Compresses, XORs, and Base64 encodes it.
                                             |     |
                                             |     +--> Sends the final blob to the stager.
                                             |
                                             +--> Registers the new connection as an active session.
                                             |
                                             +--> Prints "[+] Background Session X opened!"