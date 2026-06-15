# Command Execution Workflow

[User Input: "run"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "run" command)
                |
                +--> Determines the currently active module (e.g., recon/native-portscan/port_scanner.py).
                |
                +--> Delegates execution to the appropriate engine based on module type.
                      |
                      +--> source/core/recon_engine.py (or exploit_engine.py)
                            |
                            +--> Reads the module file (e.g., port_scanner.py).
                            |
                            +--> Parses the metadata block (#!#!#!) at the end of the file.
                            |    |
                            |    +--> Finds the 'root: "true"' tag.
                            |
                            +--> (Decision Point: Privilege Check)
                                 |
                                 +--> Because 'root' is true, it prepares to execute the script with elevated privileges.
                                 |
                                 +--> Constructs a new command: `sudo python3 /path/to/port_scanner.py`
                                 |
                                 +--> Executes the script in an isolated subprocess, prompting the user for their password if needed.
                                       |
                                       +--> [Isolated Sudo Subprocess: port_scanner.py]
                                             |
                                             +--> The script now runs with root permissions.
                                             |
                                             +--> It performs its main task (e.g., async port scanning).
                                             |
                                             +--> Interacts with source/core/database.py to manage data.
                                             |    |
                                             |    +--> Reads configuration settings (e.g., R_HOST).
                                             |    |
                                             |    +--> Writes results back to the database (e.g., open ports).
                                             |
                                             +--> (Script execution finishes)
                                       |
                                       +--> (Subprocess terminates)
                |
                +--> (Engine's task is complete)
          |
          +--> The main loop prints the prompt again, waiting for the next command.
                |
                +--> [User Prompt: "[SuperSploit]: "]
