# Auto Suggestion Workflow

This document outlines the workflow of the Suggestion Engine within the SuperSploit framework.

## Triggering the Engine

The suggestion engine can be triggered in two ways:
1.  **Manual Invocation:** The user executes the `suggest` command at the main prompt.
2.  **Post-Recon Hook:** Automatically triggered after a reconnaissance module completes, provided `auto_suggest` is enabled in the framework's configuration.

[Trigger Event]
    |
    +--> source/core/auto_suggest.py (SuggestionEngine)
          |
          +--> The engine initializes and retrieves the current target data from `targets.json` via `DatabaseManagment`.
          |
          +--> Retrieves a list of all available exploit modules in the framework.

## Analysis and Scoring

The core of the engine is a multi-factor scoring system that correlates target properties with exploit requirements.

[For each Exploit Module]
    |
    +--> The engine reads the exploit's metadata block (`#!#!#!`).
    |
    +--> Extracts requirements (OS, Architecture, Ports, Services, Vulnerabilities).
    |
    +--> Applies **Mandatory Filters (Pre-Qualification)**:
          |
          +--> Checks for OS Mismatch (e.g., Target is Linux, Exploit requires Windows). If mismatched, the exploit is discarded.
          |
          +--> Checks for Architecture Mismatch (e.g., Target is ARM, Exploit requires x86). If mismatched, the exploit is discarded.
    |
    +--> If pre-qualified, the engine begins **Scoring**:
          |
          +--> [For each Target in targets.json]
                |
                +--> **Direct CVE Match (+50):** Checks if the target has known CVEs (e.g., from an Nmap scan) that match the exploit's defined CVE.
                |
                +--> **Service/Port Match (+5):** Checks if the target has an open port that matches the exploit's required port (e.g., Port 445 for SMB).
                |
                +--> **Service Banner Match (+10 to +20):** Analyzes the target's service banners (if available) for keywords or version numbers that match the exploit's target software.
                |
                +--> **Requirement Match (+15 each):** Checks specific environmental requirements (e.g., target must have `/dev/binder` accessible).
                |
                +--> The total score for the Target/Exploit pair is calculated.

## Suggestion Output

[After all modules are scored against all targets]
    |
    +--> The engine filters out suggestions that fall below a certain confidence threshold.
    |
    +--> The remaining suggestions are sorted by score (highest to lowest).
    |
    +--> The engine formats the results and displays them to the user, highlighting the most likely successful exploits for specific targets.
