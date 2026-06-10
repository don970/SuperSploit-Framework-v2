# Implementation Plan: iOS Bluetooth/Wireless 0-Day Suite

## Objective
To develop a comprehensive iOS wireless exploitation suite within the SuperSploit framework. This suite will target recent critical vulnerabilities: the "AirBorne" zero-click RCE (CVE-2025-24252) via AirPlay/Bluetooth discovery, and the unauthenticated "MagicKeyboard" keystroke injection (CVE-2024-0230).

## Key Files & Context
- `recon/native-discovery/bluetooth_discovery.py`: Existing module to be updated with iOS-specific service profiling.
- `exploits/apple/cve_2025_24252_airborne_rce.py` (New): The target script for the AirBorne zero-click RCE.
- `exploits/apple/cve_2024_0230_magickeyboard.py` (New): The target script for the unauthenticated keystroke injection.

## Proposed Strategy

### Phase 1: iOS Bluetooth Target Profiling
1.  **Update Recon Module:** Enhance `recon/native-discovery/bluetooth_discovery.py` to perform Service Discovery Protocol (SDP) queries or mDNS over Bluetooth PAN.
2.  **AirPlay Detection:** Specifically look for the AirPlay service UUID or Bonjour broadcasts that indicate a vulnerable iOS device.

### Phase 2: MagicKeyboard Keystroke Injection (CVE-2024-0230)
1.  **Create Exploit Module:** Develop `exploits/apple/cve_2024_0230_magickeyboard.py`.
2.  **Impersonation:** Utilize raw Bluetooth sockets or `pybluez` to spoof the MAC address and device class of a legitimate Apple Magic Keyboard.
3.  **Forced Pairing:** Implement the exploit logic that bypasses the iOS pairing confirmation prompt.
4.  **Payload Injection:** Inject a Ducky-style payload (e.g., opening Safari, navigating to a SuperSploit stager URL, and executing it) using HID scancodes.

### Phase 3: "AirBorne" Zero-Click RCE (CVE-2025-24252)
1.  **Create Exploit Module:** Develop `exploits/apple/cve_2025_24252_airborne_rce.py`.
2.  **Protocol Emulation:** Implement the AirPlay discovery handshake over Bluetooth LE or Wi-Fi Direct.
3.  **Memory Corruption Trigger:** Craft a malformed AirPlay broadcast packet designed to trigger the memory corruption vulnerability in the iOS `mediaremoted` or related daemons.
4.  **Payload Delivery:** Embed a compiled iOS shellcode (e.g., a reverse TCP connect-back) within the overflow buffer.

## Migration & Rollback
- New modules will be created in the `exploits/apple/` directory, ensuring no existing modules are affected.
- Updates to the recon module will be additive and backwards-compatible.

## Verification & Testing
- Use `SuperSploit`'s `sessions` command to verify that the injected keystrokes successfully trigger a callback for CVE-2024-0230.
- Ensure the AirBorne exploit successfully connects to the AirPlay service without prior authentication.