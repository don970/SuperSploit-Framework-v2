# Database Management Workflow

This document outlines the flow of data within the SuperSploit framework, managed by the `DatabaseManagment` class in `source/core/database.py`.

## Data Write/Update Flow

[User Input: "set R_HOST 192.168.1.1"]
    |
    +--> source/main.py (Main Application Loop)
          |
          +--> source/core/input_handling_engine.py (Parses the "set" command)
                |
                +--> Identifies the command as a database operation.
                |
                +--> Calls the `set` command handler.
                      |
                      +--> source/core/set.py
                            |
                            +--> Validates the key-value pair (e.g., "R_HOST", "192.168.1.1").
                            |
                            +--> Calls `DatabaseManagment.update()` to modify the in-memory state.
                                  |
                                  +--> source/core/database.py (DatabaseManagment.update)
                                        |
                                        +--> Updates the central `db` dictionary (e.g., `db["R_HOST"] = "192.168.1.1"`).

## Data Synchronization to Disk

The in-memory database is periodically synchronized to on-disk JSON files for persistence.

[Any action that modifies target data (e.g., a recon module run)]
    |
    +--> The module calls `DatabaseManagment.updateTargets()` or a similar update function.
          |
          +--> source/core/database.py (DatabaseManagment.updateTargets)
                |
                +--> The in-memory `TARGETS` dictionary is updated with new information (e.g., open ports, MAC addresses).
                |
                +--> Calls `DatabaseManagment.sync_targets_to_disk()`
                      |
                      +--> Opens the on-disk database file (e.g., `.data/.config/targets.json`).
                      |
                      +--> Uses `json.dump()` to write the entire in-memory `TARGETS` dictionary to the file, overwriting its previous contents.
                      |
                      +--> The file is closed, persisting the changes.
