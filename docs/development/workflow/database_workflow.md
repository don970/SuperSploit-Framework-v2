# Database Management Workflow

This document outlines the flow of data within the SuperSploit framework, managed by the `DatabaseManagment` class in `source/core/database.py`.

## 1. Data Write/Update Flow (SQLite Engine)

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
                                        +--> Modifies the `SQLiteDict` wrapper, directly executing an `UPDATE` or `INSERT` statement into `data.db`.

## 2. Target Synchronization & Background Caching

While operational configurations are written instantly to SQLite, dynamic target reconnaissance data is buffered in memory to prevent database lock contention.

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
                      +--> Uses a thread-safe `json.dump(indent=4)` to serialize the in-memory `TARGETS` dictionary to the file.
                      |
                      +--> The file is closed, persisting the changes.
