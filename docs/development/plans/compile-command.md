# Compile Command Plan

## Objective
Implement a new `compile` command in the framework that allows users to easily cross-compile C files directly from the CLI. This command will be configurable via new `COMP_ARCH` and `COMP_OUT` variables.

## Scope & Impact
- Add the `compile` command to the main input handling engine.
- Introduce `COMP_ARCH` and `COMP_OUT` as configurable variables via the `set` command.
- Implement the compilation logic to handle architecture-specific cross-compilers.
- Update help documentation for the new command and variables.

## Proposed Solution
1. **Command Registration**: Add `"compile": cls._compile_c_binary` to the `general_cmds` dictionary in `source/core/input_handling_engine.py`.
2. **Method Implementation**: Implement `_compile_c_binary(cls, data)` in `input_handling_engine.py`.
   - Parse the command arguments (e.g. `compile [file.c]`). If no file is provided, fall back to the currently loaded `EXPLOIT` or `PAYLOAD` if it ends in `.c`.
   - Retrieve `COMP_ARCH` from the database (defaulting to native `gcc`). Map `COMP_ARCH` to the appropriate compiler (e.g., `arm64` -> `aarch64-linux-gnu-gcc`, `x86` -> `i686-linux-gnu-gcc`, etc.). Include support for the Android NDK if applicable.
   - Retrieve `COMP_OUT` from the database, defaulting to `<install_dir>/payloads/compiled_binary`.
   - Execute the compiler via `subprocess.run()`.
3. **Variable Mapping**: Update `source/core/set.py` if necessary (though the current `SetV` logic allows arbitrary keys, we can document these explicitly).
4. **Documentation**:
   - Add a new help file `.data/.help/compile`.
   - Update `.data/.help/vars` to include `COMP_ARCH` and `COMP_OUT`.
   - Log the feature addition in `CHANGELOG.md`.

## Implementation Steps
1. Write the `_compile_c_binary` method in `input_handling_engine.py`.
2. Register the command in the `general_cmds` dictionary.
3. Write the help file for `compile`.
4. Update the `vars` help file.
5. Update `CHANGELOG.md` and `GEMINI.md` / `MEMORY.md` if required for new variables.

## Verification
Running `compile exploits/linux/cve_2021_4034_pwnkit.c` with `COMP_ARCH` set to `x86_64` should produce an executable in the `payloads/` directory.