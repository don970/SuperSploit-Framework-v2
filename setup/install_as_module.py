#!/usr/bin/env python3
import subprocess
import sys
import os

def install_and_run():
    print("[*] SuperSploit Module Installer & Launcher")
    print("-" * 40)
    
    install_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(install_root)
    
    # 1. Install dependencies
    print("[*] Phase 1: Installing/Updating Dependencies...")
    try:
        # We use --break-system-packages for modern Debian/Ubuntu systems
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "setup/requirements.txt", "--break-system-packages"])
    except subprocess.CalledProcessError as e:
        print(f"[-] Dependency installation failed: {e}")
        return

    # 2. Install as editable module
    print("[*] Phase 2: Installing SuperSploit as a Python Module...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "--break-system-packages"])
    except subprocess.CalledProcessError as e:
        print(f"[-] Module installation failed: {e}")
        return

    # 3. Execution logic
    print("-" * 40)
    print("[+] Installation complete!")
    print("[*] You can now run SuperSploit from anywhere using: supersploit")
    print("[*] Or launch it now as a module...")
    print("-" * 40)
    
    # Set PYTHONPATH to the source directory to ensure imports work correctly
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(install_root, "source")
    
    try:
        subprocess.run([sys.executable, "-m", "main"], cwd=install_root, env=env)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

if __name__ == "__main__":
    install_and_run()
