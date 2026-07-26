# Architectural Analysis: Advanced Stealth & Evasion Suite

## 1. Polymorphic Signature Rotation
**Component:** `NativeApkGenerator._polymorphic_patch_smali()`

**Mechanism:**
Standard Android AV engines flag static JNI method names and predictable `System.loadLibrary()` calls. To combat this, the framework now generates random alphanumeric strings for every build. 
It surgically patches the underlying `smali` bytecode before rebuilding the APK, dynamically swapping:
- `executeNative()` -> `v1exec[RANDOM]`
- `startNativeC2()` -> `v1c2[RANDOM]`
- `libpayload.so` -> `libcore[RANDOM].so`

**Impact:** Every generated APK has a unique cryptographic signature and uniquely named JNI bindings, completely neutralizing static string-based YARA rules.

## 2. Opportunistic OLLVM Integration
**Component:** `input_handling_engine.py` & `native_apk_generator.py`

**Mechanism:**
When the `OLLVM_ENABLED` variable is set to `true`, the compilation pipelines append specific LLVM passes (`-mllvm -bcf -mllvm -sub -mllvm -fla`) to the `clang` cross-compiler.
- **Bogus Control Flow (-bcf):** Injects junk code blocks that are never executed but confuse reverse engineering tools like IDA Pro and Ghidra.
- **Instruction Substitution (-sub):** Replaces standard operations (like addition or XOR) with mathematically equivalent but highly complex sequences of instructions.
- **Control Flow Flattening (-fla):** Destroys the standard block structure of functions, wrapping them in a massive `switch` statement driven by a state variable.

**Impact:** Dramatically increases the complexity of analyzing the `phantom_agent.c` and exploit binaries, preventing automated EDR analysis.

## 3. Network Domain Fronting & SNI Masking
**Component:** `minish.c`

**Mechanism:**
The `minish` micro-fetcher was upgraded to support Server Name Indication (SNI) spoofing. When connecting via HTTPS (`openssl/libssl`), it separates the DNS resolution host from the TLS SNI host.
By pointing the DNS resolution at a high-reputation CDN (e.g., Cloudflare) but requesting a specific backend host in the HTTP `Host` header and TLS Client Hello, the traffic appears to be going to a legitimate, trusted domain.

## 4. Environment Pinning & Anti-Debugging
**Component:** `phantom_agent.c`

**Mechanism:**
The C payloads now include `ptrace(PTRACE_TRACEME, 0, 1, 0)`. If a dynamic analyzer, sandbox, or debugger is already attached to the process, the `ptrace` call fails, and the agent silently terminates itself before exposing its C2 configuration or decryption keys in memory.