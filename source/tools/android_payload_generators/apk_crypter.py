#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import argparse
import re
import base64

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

def inject_decryptor(build_dir):
    """Drops the Smali decryption class into the decompiled APK."""
    crypto_dir = os.path.join(build_dir, "smali", "org", "supersploit", "crypto")
    os.makedirs(crypto_dir, exist_ok=True)
    
    decryptor_smali = """.class public Lorg/supersploit/crypto/Decryptor;
.super Ljava/lang/Object;

.method public static d(Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    const/4 v0, 0x0
    invoke-static {p0, v0}, Landroid/util/Base64;->decode(Ljava/lang/String;I)[B
    move-result-object p0

    new-instance v0, Ljava/lang/String;
    invoke-direct {v0, p0}, Ljava/lang/String;-><init>([B)V

    return-object v0
.end method
"""
    with open(os.path.join(crypto_dir, "Decryptor.smali"), "w") as f:
        f.write(decryptor_smali)
    print("  [+] Decryptor class injected into Smali tree.")

def obfuscate_strings(build_dir):
    """Recursively encrypts strings in all Smali files and injects decode calls."""
    import glob
    smali_files = glob.glob(os.path.join(build_dir, "smali*", "**", "*.smali"), recursive=True)
    
    # Matches: const-string v0, "payload"
    pattern = re.compile(r'const-string(?:/jumbo)?\s+([vp]\d+),\s+"([^"\\]*(?:\\.[^"\\]*)*)"')
    
    obfuscated_count = 0

    def replacer(match):
        nonlocal obfuscated_count
        reg = match.group(1)
        raw_str = match.group(2)

        # Smart Filtering: Skip empty strings, framework bindings, and Smali type signatures
        if len(raw_str) < 3: return match.group(0)
        if raw_str.startswith("L") and raw_str.endswith(";"): return match.group(0)
        if raw_str.startswith("["): return match.group(0)
        if raw_str.startswith("android.") or raw_str.startswith("java.") or raw_str.startswith("dalvik."): return match.group(0)

        try:
            # Safely encode the string payload
            b64_encoded = base64.b64encode(raw_str.encode('utf-8')).decode('utf-8')
            
            # Assembly stub to dynamically decode the string in memory
            new_inst = f'const-string {reg}, "{b64_encoded}"\n'
            new_inst += f'    invoke-static {{{reg}}}, Lorg/supersploit/crypto/Decryptor;->d(Ljava/lang/String;)Ljava/lang/String;\n'
            new_inst += f'    move-result-object {reg}'
            obfuscated_count += 1
            return new_inst
        except Exception:
            return match.group(0)

    for smali_file in smali_files:
        # Do not obfuscate our own decryptor class!
        if "Decryptor.smali" in smali_file: continue
        
        with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        new_content = pattern.sub(replacer, content)
        
        if content != new_content:
            with open(smali_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
    print(f"  [+] Obfuscated {obfuscated_count} sensitive strings across the APK.")

def pack_apk(apk_path, output_path):
    if not os.path.exists(apk_path):
        print(f"[-] Error: File {apk_path} not found.")
        sys.exit(1)

    apk_name = os.path.basename(apk_path)
    build_dir = f"/tmp/apk_crypter_workspace_{apk_name.replace('.apk', '')}"
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)

    print(f"[*] Phase 1: Decompiling {apk_name} via apktool...")
    run_cmd(["apktool", "d", apk_path, "-o", build_dir, "-f"])

    print("[*] Phase 2: Injecting Polymorphic Crypter Engine...")
    inject_decryptor(build_dir)
    obfuscate_strings(build_dir)

    print("[*] Phase 3: Rebuilding the obfuscated APK...")
    unaligned_apk = f"/tmp/unaligned_crypted_{apk_name}"
    run_cmd(["apktool", "b", build_dir, "-o", unaligned_apk])

    print("[*] Phase 4: Zipaligning the APK...")
    aligned_apk = f"/tmp/aligned_crypted_{apk_name}"
    if os.path.exists(aligned_apk): os.remove(aligned_apk)
    run_cmd(["zipalign", "-p", "-f", "4", unaligned_apk, aligned_apk])

    print("[*] Phase 5: Signing the crypted APK...")
    keystore_path = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "debug.keystore")
    run_cmd(["apksigner", "sign", "--ks", keystore_path, "--ks-pass", "pass:supersploit", "--out", output_path, aligned_apk])

    shutil.rmtree(build_dir)
    os.remove(unaligned_apk)
    os.remove(aligned_apk)

    print(f"\n[+] SUCCESS! APK Payload successfully packed and obfuscated.")
    print(f"[+] Output saved to: {output_path}")

if __name__ == "__main__":
    if not LicenseManager.gate_access("APK Polymorphic Crypter"): sys.exit(1)
    parser = argparse.ArgumentParser(description="Packs and obfuscates an Android APK payload.")
    parser.add_argument("-i", "--input", required=True, help="Path to the original APK")
    parser.add_argument("-o", "--output", required=True, help="Path to save the crypted APK")
    args = parser.parse_args()
    pack_apk(args.input, args.output)