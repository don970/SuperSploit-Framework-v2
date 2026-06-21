#!#!#!
# name: Pro iMessage / RCS Injector
# author: "Donald Ford"
# description: Automates native macOS AppleScript to dispatch iMessages (Blue Bubbles) to target Apple IDs.
# type: se_delivery
# requirements: ["macOS Host or Bridged VM"]
# options:
#   - TARGET_APPLE_ID: "The victim's phone number or Apple ID email"
#   - MESSAGE: "The iMessage payload to send"
# pro_feature: true
#!#!#!

import subprocess
from core.ToStdOut import ToStdout
from core.license_manager import LicenseManager

def run(db):
    if not LicenseManager.gate_access("iMessage / RCS Injector"):
        return False
        
    target = db.get("TARGET_APPLE_ID")
    message = db.get("MESSAGE")
    
    if not target or not message:
        ToStdout.write("[-] ERROR: TARGET_APPLE_ID and MESSAGE are required.\n")
        return False
        
    ToStdout.write(f"[*] Preparing iMessage payload for {target}...\n")
    
    # Construct the AppleScript payload to interface with the Messages app
    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{target}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    
    ToStdout.write("[*] Injecting into macOS 'Messages' daemon via osascript...\n")
    
    try:
        result = subprocess.run(['osascript', '-e', applescript], capture_output=True, text=True)
        
        if result.returncode == 0:
            ToStdout.write(f"[+] SUCCESS: iMessage natively dispatched to {target}!\n")
            return True
        else:
            ToStdout.write(f"[-] ERROR: Injection failed. Is the host logged into an Apple ID?\n{result.stderr}\n")
            return False
    except FileNotFoundError:
        ToStdout.write("[-] ERROR: 'osascript' not found. This module must be run from a macOS host or SSH bridge.\n")
        return False