# Reconnaissance Execution Workflow

[User Input: "run"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "run" command)
                |
                +--> Determines the currently active module (e.g., recon/native-discovery/host_discovery.py).
                |
                +--> Delegates execution to the `recon_engine.py`.
                      |
                      +--> source/core/recon_engine.py
                            |
                            +--> Reads the module file (e.g., host_discovery.py).
                            |
                            +--> Parses the metadata block (#!#!#!) at the end of the file.
                            |    |
                            |    +--> Finds the 'root: "true"' tag (if applicable).
                            |
                            +--> (Decision Point: Privilege Check)
                                 |
                                 +--> If 'root' is true, prepares to execute the script with elevated privileges.
                                 |
                                 +--> Constructs a new command: `sudo python3 /path/to/host_discovery.py`
                                 |
                                 +--> Executes the script in an isolated subprocess, prompting the user for their password if needed.
                                       |
                                       +--> [Isolated Sudo Subprocess: host_discovery.py]
                                             |
                                             +--> The script now runs with root permissions.
                                             |
                                             +--> It initializes the `HostDiscoveryEngine`.
                                             |
                                             +--> Performs its main tasks (e.g., crafting and sending raw ARP/ICMP packets via Scapy).
                                             |
                                             +--> Interacts with `source/core/database.py` (via a secondary import/state check) to manage data.
                                             |    |
                                             |    +--> Reads configuration settings (e.g., `R_HOST` CIDR range).
                                             |    |
                                             |    +--> Compiles results into a structured format.
                                             |    |
                                             |    +--> Writes newly discovered targets back to the database (`targets.json`).
                                             |
                                             +--> (Script execution finishes)
                                       |
                                       +--> (Subprocess terminates)
                |
                +--> Post-Recon Hook Triggered
                      |
                      +--> source/core/post_recon_hook.py
                            |
                            +--> Checks if `auto_suggest` is enabled in the configuration.
                            |
                            +--> If enabled, calls `source/core/auto_suggest.py` to analyze the new recon data and suggest relevant exploits.
                |
                +--> (Engine's task is complete)
          |
          +--> The main loop prints the prompt again, waiting for the next command.
                |
                +--> [User Prompt: "[SuperSploit]: "]
