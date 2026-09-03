# LPE Enumeration Roadmap

## Current State
- **Linux**: Robust `lpe_enum` script checking SUID, writable configs, and sudo perms.
- **Android**: Specialized `lpe_enum` command in DRS template checking root paths, SELinux, and build props.

## Future Goals
- **Windows**: Implement a `windows_lpe_enum.py` using `powershell` or `cmd` built-ins (e.g., `whoami /priv`, `accesschk`).
- **Automation**: Integrate the "Privilege Escalation Suggester" from Phase 3 of the Roadmap. This would automatically parse the output of `lpe_enum` and suggest specific modules like `cve_2022_0847_dirtypipe`.
- **Credential Harvesting**: Add modules to search for cleartext credentials in `/home` (Linux) or `AppData` (Windows).
