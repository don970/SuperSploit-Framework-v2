#!/usr/bin/env python3
import os
import sys
import platform
import subprocess

def install_cert(cert_path):
    """
    Cross-platform utility to add a certificate to the OS Trusted Root store.
    Requires Administrator / root privileges.
    """
    if not os.path.exists(cert_path):
        print(f"[-] Error: Certificate not found at {cert_path}")
        sys.exit(1)

    system = platform.system().lower()
    print(f"[*] Detected OS: {system}")
    print(f"[*] Attempting to install: {cert_path}")

    try:
        if system == "windows":
            # Windows: Uses certutil. Must be run in an elevated command prompt.
            cmd = ['certutil', '-addstore', '-f', 'Root', cert_path]
            print(f"[*] Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print("[+] Success: Certificate installed to Windows Trusted Root store.")

        elif system == "darwin":
            # macOS: Uses security. Will prompt the user for credentials if not run via sudo.
            cmd = ['sudo', 'security', 'add-trusted-cert', '-d', '-r', 'trustRoot', 
                   '-k', '/Library/Keychains/System.keychain', cert_path]
            print(f"[*] Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print("[+] Success: Certificate installed to macOS System Keychain.")

        elif system == "linux":
            # Linux: Handles both Debian/Ubuntu and RHEL/CentOS architectures
            if os.path.exists('/usr/local/share/ca-certificates'):
                # Debian / Ubuntu
                base_name = os.path.basename(cert_path)
                if not base_name.endswith('.crt'):
                    base_name = base_name.rsplit('.', 1)[0] + '.crt'
                dest_path = os.path.join('/usr/local/share/ca-certificates', base_name)
                
                print(f"[*] Copying certificate to {dest_path}")
                subprocess.run(['sudo', 'cp', cert_path, dest_path], check=True)
                subprocess.run(['sudo', 'chmod', '644', dest_path], check=True)
                
                print("[*] Updating CA certificates store...")
                subprocess.run(['sudo', 'update-ca-certificates'], check=True)
                print("[+] Success: Certificate installed on Linux (Debian-based).")
                
            elif os.path.exists('/etc/pki/ca-trust/source/anchors/'):
                # RHEL / CentOS / Fedora
                dest_path = os.path.join('/etc/pki/ca-trust/source/anchors/', os.path.basename(cert_path))
                print(f"[*] Copying certificate to {dest_path}")
                subprocess.run(['sudo', 'cp', cert_path, dest_path], check=True)
                
                print("[*] Updating CA trust...")
                subprocess.run(['sudo', 'update-ca-trust', 'extract'], check=True)
                print("[+] Success: Certificate installed on Linux (RHEL-based).")
            else:
                print("[-] Error: Unsupported Linux distribution. Could not find CA certificate paths.")
        else:
            print(f"[-] Error: Unsupported OS family '{system}'.")
            
    except subprocess.CalledProcessError as e:
        print(f"\n[-] Failed to install certificate. Did you run with sufficient privileges? (Error: {e})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <path_to_certificate.pem/.crt>")
        sys.exit(1)
    
    install_cert(sys.argv[1])