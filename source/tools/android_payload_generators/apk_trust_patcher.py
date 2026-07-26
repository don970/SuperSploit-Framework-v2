#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import argparse
import re

try:
    from source.core.license_manager import LicenseManager
except ImportError:
    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)
    try:
        from source.core.license_manager import LicenseManager
    except ImportError:
        class LicenseManager:
            @staticmethod
            def gate_access(f): 
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False

def run_cmd(cmd):
    print(f"[*] Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"[-] Command failed: {e}")
        sys.exit(1)

def patch_apk(apk_path, output_path):
    if not os.path.exists(apk_path):
        print(f"[-] Error: File {apk_path} not found.")
        sys.exit(1)

    apk_name = os.path.basename(apk_path)
    build_dir = f"/tmp/apk_patch_workspace_{apk_name.replace('.apk', '')}"
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    print(f"[*] Phase 1: Decompiling {apk_name} via apktool...")
    run_cmd(["apktool", "d", apk_path, "-o", build_dir, "-f"])

    print("[*] Phase 2: Injecting Network Security Configuration...")
    # 1. Create the rogue network security config file
    xml_dir = os.path.join(build_dir, "res", "xml")
    os.makedirs(xml_dir, exist_ok=True)
    
    rogue_nsc_path = os.path.join(xml_dir, "rogue_network_security_config.xml")
    nsc_payload = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
</network-security-config>
"""
    with open(rogue_nsc_path, "w") as f:
        f.write(nsc_payload)
    print(f"  [+] Dropped rogue network config: {rogue_nsc_path}")

    # 2. Patch the AndroidManifest.xml to use our rogue config
    manifest_path = os.path.join(build_dir, "AndroidManifest.xml")
    with open(manifest_path, "r") as f:
        manifest_data = f.read()

    # Remove existing network security config if present
    manifest_data = re.sub(r'android:networkSecurityConfig="[^"]+"', '', manifest_data)
    
    # Inject our new config into the <application> tag
    if "<application" in manifest_data:
        manifest_data = manifest_data.replace(
            "<application", 
            '<application android:networkSecurityConfig="@xml/rogue_network_security_config"'
        )
        with open(manifest_path, "w") as f:
            f.write(manifest_data)
        print("  [+] Successfully patched AndroidManifest.xml")
    else:
        print("[-] Error: <application> tag not found in Manifest.")
        sys.exit(1)

    print("[*] Phase 3: Rebuilding the APK...")
    unaligned_apk = f"/tmp/unaligned_{apk_name}"
    run_cmd(["apktool", "b", build_dir, "-o", unaligned_apk])

    print("[*] Phase 4: Zipaligning the APK...")
    aligned_apk = f"/tmp/aligned_{apk_name}"
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)
    run_cmd(["zipalign", "-p", "-f", "4", unaligned_apk, aligned_apk])

    print("[*] Phase 5: Signing the trojanized APK...")
    keystore_path = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "debug.keystore")
    
    # Generate a default keystore if the framework doesn't have one yet
    if not os.path.exists(keystore_path):
        print("  [*] Generating new SuperSploit debug keystore...")
        run_cmd(["keytool", "-genkey", "-v", "-keystore", keystore_path, "-alias", "supersploit", "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000", "-storepass", "supersploit", "-keypass", "supersploit", "-dname", "CN=SuperSploit,O=SuperSploit,C=US"])

    run_cmd(["apksigner", "sign", "--ks", keystore_path, "--ks-pass", "pass:supersploit", "--out", output_path, aligned_apk])

    # Cleanup
    shutil.rmtree(build_dir)
    os.remove(unaligned_apk)
    os.remove(aligned_apk)

    print(f"\n[+] SUCCESS! User Trust Store bypass injected.")
    print(f"[+] Output saved to: {output_path}")

if __name__ == "__main__":
    print("========================================")
    print("   SuperSploit APK Trust Store Patcher")
    print("========================================\n")
    
    if not LicenseManager.gate_access("APK Trust Store Patcher"):
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Injects User Certificate Trust into an Android APK.")
    parser.add_argument("-i", "--input", required=True, help="Path to the original APK")
    parser.add_argument("-o", "--output", required=True, help="Path to save the patched APK")
    
    args = parser.parse_args()
    
    # Check for required tools
    for tool in ["apktool", "zipalign", "apksigner", "keytool"]:
        if shutil.which(tool) is None:
            print(f"[-] Error: '{tool}' is not installed or not in PATH.")
            sys.exit(1)
            
    patch_apk(args.input, args.output)