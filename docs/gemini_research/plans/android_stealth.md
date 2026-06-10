# Android Stealth Strategies

## Icon Hiding
The framework utilizes the Android `PackageManager` via `jnius` to disable the main launcher activity.
```python
pm.setComponentEnabledSetting(component, COMPONENT_ENABLED_STATE_DISABLED, DONT_KILL_APP)
```
This ensures the app remains installed and running but disappears from the user's view.

## UI Stealth
By setting `SHOW_UI=false`, the Kivy application returns a blank `Widget` instead of a `Label`. This prevents the user from seeing any "System Update" text, making the app appear to have crashed or closed immediately, while the beacon loop persists in a background thread.

## Communication Evasion
- **Encryption**: XOR + Base64 over HTTP.
- **Jitter**: Randomized sleep intervals (5-30s) to avoid timing signatures.
- **Dynamic Imports**: Base64 encoded module names to bypass static string analysis.
