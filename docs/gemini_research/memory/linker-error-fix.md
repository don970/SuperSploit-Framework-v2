# Android Linker Error Fix Plan

## Objective
Resolve the `CANNOT LINK EXECUTABLE` error that occurs when executing system binaries (like `id` or `ls`) from within the Kivy-based Android payloads.

## Background & Motivation
The user reported an error when running `id` in the rootkit session: 
`CANNOT LINK EXECUTABLE "id": cannot locate symbol "OpenSSL_add_all_algorithms" referenced by "/system/lib/libselinux.so"...`

This is a known issue with Android Python environments (like Kivy/Python-for-Android). The app bundles its own libraries (including OpenSSL) and sets the `LD_LIBRARY_PATH` environment variable so Python can load them. When the payload spawns a system shell command via `subprocess.run`, this modified environment is inherited. System binaries then attempt to link against the app's bundled libraries instead of the system's libraries, causing symbol lookup failures.

## Scope & Impact
This issue affects all Android payload templates (`android_rootkit_template.py`, `android_drs_template.py`, `android_beacon_template.py`) where `subprocess.run` or `subprocess.Popen` is used to execute arbitrary shell commands.

## Proposed Solution
Sanitize the environment before executing shell commands. Specifically, we will create a copy of the current environment and remove `LD_LIBRARY_PATH`. This clean environment will be passed to the `env` parameter of `subprocess.run()`.

Example implementation:
```python
clean_env = self._o.environ.copy()
if 'LD_LIBRARY_PATH' in clean_env:
    del clean_env['LD_LIBRARY_PATH']
```

## Implementation Steps
1.  **Update Rootkit Payload**: Modify `_run_root` and the subprocess fallback block in `android_rootkit_template.py` to use a sanitized environment.
2.  **Update DRS Payload**: Modify the subprocess execution block in `android_drs_template.py` to use a sanitized environment.
3.  **Update Beacon Payload**: Modify `_execute_command` in `android_beacon_template.py` to use a sanitized environment.
4.  **Update Project Memory**: Document this specific Android environment quirk and the applied fix in the `MEMORY.md` index or related notes.

## Verification
Executing a system command like `id` or `su` should no longer return linker errors related to shared objects (`.so`).