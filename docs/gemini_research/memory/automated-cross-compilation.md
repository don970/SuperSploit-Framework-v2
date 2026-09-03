# Automated Cross-Compilation Fix Plan

## Objective
Update the `SessionLoader._load_c()` method to intelligently cross-compile C payloads for the correct target architecture, specifically supporting ARM64 Android targets using the Android NDK toolchain.

## Background & Motivation
Currently, when the SuperSploit listener loads a `.c` exploit (like a kernel LPE), `SessionLoader._load_c()` compiles it using the native host `gcc`. On a typical Linux attacker machine, this generates an x86_64 binary. If this binary is then staged and executed in memory (via `_load_elf()`) on an ARM64 Android device, execution will fail silently or throw an architecture mismatch error.

To fully realize automated, in-memory C exploits against Android targets, the framework must compile the source code into an ARM64 executable before packaging it.

## Scope & Impact
- File to modify: `source/core/session_loader.py`
- Impact: C payloads will dynamically compile to the correct architecture based on the exploit's category (e.g., if the exploit is located in `exploits/android/`).

## Proposed Solution
1. **Target Detection**: Infer the target OS from the exploit's file path. If the path contains `/android/`, assume the target is Android ARM64.
2. **Compiler Resolution**: 
   - If the target is Android, dynamically locate the Android NDK Clang compiler (`aarch64-linux-android*-clang`) typically found in `~/.buildozer/`.
   - If the NDK is missing, attempt to fallback to a generic `aarch64-linux-gnu-gcc`.
   - If the target is standard Linux, default to native `gcc`.
3. **Compilation**: Execute the chosen compiler. For Android, ensure compilation flags are appropriate (e.g., `-O2`, `-pthread`).

## Implementation Steps
1. Modify `SessionLoader._load_c()` to accept the database/framework context or infer the target from the `file_path`.
2. Add a sub-routine to search `os.path.expanduser("~/.buildozer")` for the `aarch64-linux-android*-clang` binary.
3. Update the `subprocess.run()` call to use the resolved compiler.

## Verification
Loading an Android C exploit (e.g., `dirtycow.c` or `cve_2023_20963_binder_double_free.c`) should trigger the NDK Clang compiler instead of native `gcc`, resulting in a valid ARM64 ELF binary being staged.