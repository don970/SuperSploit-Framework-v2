# Target Profile & Automated Enumeration System

## Overview
SuperSploit now features an integrated Target Profile system that bridges the gap between reconnaissance and persistent research. This system allows for the creation of rich "Persona Profiles" that track target-specific metadata, vulnerability reports, and research notes. Additionally, the framework now automates post-exploitation enumeration for newly captured C2 sessions.

---

## 👤 Target Profile System

The Target Profile system is managed via `source/core/database.py` and provides a persistent SQLite-backed store for target data.

### Key Features
- **Target Import**: Quickly create a profile from an existing scan result.
- **Persistent Metadata**: Tracks IP, OS, Architecture, Kernel Version, and Open Ports.
- **Research Logging**: A dedicated field for attaching analysis, CVE correlation, and LPE findings.
- **Integrated View**: Use `show profiles` to see a consolidated view of all identified personas.

### Command Syntax
| Action | Command |
| :--- | :--- |
| **Import Target** | `add profile --import <IP>` |
| **Edit Metadata** | `edit profile "<Name>" <field> "<value>"` |
| **Add Research** | `edit profile "<Name>" research add "<Note>"` |
| **Remove Research**| `edit profile "<Name>" research remove "<Note>"` |
| **View Profiles** | `show profiles` |

---

## 🤖 Automated C2 Enumeration

The automated enumeration system (Auto-Enum) is built into the C2 Listener (`source/core/listener.py`). It triggers automatically upon session capture to provide immediate technical intelligence.

### Workflow
1. **Device Identification**: Upon connection, the listener identifies the target (e.g., Android model, OS version).
2. **Dynamic Compilation**: The listener checks the target architecture (`aarch64`, `armv7l`) and cross-compiles the `android-enum3.c` (Version 5.0) tool using the embedded NDK or system compilers.
3. **Silent Deployment**: The tool is uploaded to `/data/local/tmp` and executed.
4. **Report Parsing**: The framework parses the output for "micro-cracks" (pointers, info leaks, writable nodes, insecure mounts, and listening ports).
5. **Profile Enrichment**: Critical findings are automatically appended to the target's profile under the `research` section.

### Configuration
- **AUTO_ENUM**: Toggle the automation in `.data/.help/vars` (Default: `true`).
- **Tool Source**: `source/tools/android-enum3.c`.
- **Output Cache**: `.data/.cache/android-enum3_<arch>`.

---

## 🛠️ Developer Implementation Details

### Database Management (`database.py`)
- `importFromTargets(ip)`: Handles the logic for mapping `targets.json` data into the `profiles.db` SQLite structure.
- `editProfile(data)`: Enhanced to support list-based operations for the `research` and `social_medias` fields.

### Listener Integration (`listener.py`)
- `_auto_enumerate(...)`: A background thread handler that manages the entire identification -> compilation -> execution -> parsing lifecycle.
- Uses `glob` and `shutil` to dynamically locate NDK toolchains in `~/.buildozer`.

### CLI Interface (`show.py` & `input_handling_engine.py`)
- `Show._show_profiles()`: Updated to render complex profile structures, including system info and research lists.
- `Input._handle_add_command()`: Routes the new `add profile --import` syntax.
