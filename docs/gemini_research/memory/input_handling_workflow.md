# Input Handling Workflow

This document outlines how the SuperSploit framework parses and routes user commands.

[User Input: e.g., "use exploits/Windows/Eternalblue.py"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> The raw input string is passed to the Input Handling Engine.
          |
          +--> source/core/input_handling_engine.py
                |
                +--> The engine splits the input into a base command and arguments ("use", "exploits/Windows/Eternalblue.py").
                |
                +--> It checks the base command against a dictionary of known commands ("help", "show", "set", "use", "run", "search", etc.).
                |
                +--> (Decision Point: Command Routing)
                      |
                      +--> If the command is "use":
                      |    |
                      |    +--> Delegates to `source/core/use.py`.
                      |
                      +--> If the command is "run":
                      |    |
                      +--> Delegates to `source/core/exploit_engine.py` or `source/core/recon_engine.py`.
                      |
                      +--> If the command is "set":
                      |    |
                      |    +--> Delegates to `source/core/set.py`.
                      |
                      +--> If the command is not found in the primary dictionary:
                           |
                           +--> It checks against a secondary dictionary of aliases stored in `.data/.config/Aliases.json`.
                           |
                           +--> If an alias is found, the original command is replaced with the alias's value and the process restarts.
                           |
                           +--> If no command or alias is found, it prints an "Unknown command" error.
