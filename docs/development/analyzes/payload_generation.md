# SuperSploit Project Instructions

## Architecture: Payload Generation (Deep Analysis)

The Payload Generator is responsible for dynamically assembling fileless stagers and customized agents. This logic is primarily implemented in `source/core/stager_generator.py` and invoked by the Exploit Engine.

### Generation Handlers & Mechanisms

| Mechanism | Description |
| :--- | :--- |
| **Template Processing** | Reads raw payload templates (e.g., Kivy UI wrappers, standard Python reverse shells) from the file system. |
| **Variable Injection** | Replaces Jinja-style placeholders (e.g., `{{LHOST}}`, `{{XOR_KEY}}`) with data pulled from the active framework database session. |
| **Dynamic Obfuscation** | Optionally scrambles the output payload, utilizing techniques like dynamic Base64 resolution and variable renaming to evade signature-based detection. |

### Automation Workflow
- **Database Mapping**: Automatically saves the final generated one-liner stager into the active database instance, making it seamlessly available for exploit injection strings.
- **Pre-execution Hook**: Bound directly into the Exploit Engine. If a module defines a payload dependency, generation happens implicitly before exploit detonation.
