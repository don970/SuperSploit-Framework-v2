# Implementation Plan: Enhance Android Payload Features

## Objective
Update the `android_main_template.py` payload to include specific reverse shell commands for dumping SMS messages, dumping call logs, and programmatically hiding the app icon from the Android launcher without requiring root privileges.

## Key Files & Context
- `templates/payload/android_main_template.py`: The Kivy-based reverse shell payload template. We will modify the command execution loop inside the `reverse_shell` method to intercept new custom commands.

## Implementation Steps
1. **Intercept Custom Commands:** Modify the `while True` loop in the `reverse_shell` method to check for specific command strings (`dump_sms`, `dump_calls`, `hide_app`) before passing them to `/system/bin/sh`.
2. **Implement SMS and Call Dumping:** 
   - If the command is `dump_sms`, execute the Android content provider command: `content query --uri content://sms/inbox`.
   - If the command is `dump_calls`, execute: `content query --uri content://call_log/calls`.
3. **Implement App Hiding:**
   - If the command is `hide_app`, import PyJNIus (`jnius.autoclass`) inline.
   - Access the Android `PackageManager` and `ComponentName` classes.
   - Use `pm.setComponentEnabledSetting` to disable the launcher activity (typically `org.kivy.android.PythonActivity`), hiding the icon while setting `DONT_KILL_APP` to keep the shell alive.
   - Send the success or error message back over the socket socket.
4. **Integration:** Ensure the rest of the commands fall back to the standard `subprocess.Popen` execution.

## Verification & Testing
- Generate a payload using the updated template.
- Start a listener and connect the generated payload.
- Execute `dump_sms` and verify SMS data is returned.
- Execute `dump_calls` and verify call log data is returned.
- Execute `hide_app` and verify the icon disappears from the launcher, but the reverse shell remains active.
