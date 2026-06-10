# SuperSploit Project Instructions

## Architecture: Android Payload Generator (Deep Analysis)

The Android Payload Generator manages the dynamic creation and compilation of pure-Python Android APK payloads using Kivy and Buildozer. This logic is primarily implemented in `source/tools/android_payload_generator.py`.

### Execution Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Workspace Preparation** | Creates an isolated build directory (`/tmp/supersploit_kivy_build`) to prevent collisions between multiple payload generation requests. |
| **Template Parsing & Injection** | Reads a base template (e.g., `android_beacon_template.py`), dynamically injecting C2 parameters like `{{LHOST}}` and `{{LPORT}}` to create the final `main.py` script. |
| **Buildozer Specification** | Generates a custom `buildozer.spec` file on the fly, configuring application metadata (name, package), permissions (`INTERNET`), and target architectures (`arm64-v8a`, `armeabi-v7a`). |
| **Cross-Compilation** | Executes `buildozer android debug` as a subprocess to handle the complex SDK/NDK toolchains, converting the Python code into a native Android APK. |
| **Extraction & Cleanup** | Locates the compiled `.apk` within the buildozer `bin/` directory, copies it to the requested output path, and purges the temporary workspace. |

### Automation Workflow
- **CLI Interface**: Can be run as a standalone command-line tool (`main()`) to generate APKs outside of the primary interactive console.
- **Fail-safe Cleanup**: Utilizes `finally` blocks to guarantee the `/tmp` build directory is destroyed even if compilation fails or crashes midway.
- **Default Resolution**: Automatically resolves the relative path to internal framework payload templates if a custom template path is not provided.