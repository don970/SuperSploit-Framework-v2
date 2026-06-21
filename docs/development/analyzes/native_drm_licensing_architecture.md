# Architectural Analysis: Native DRM & License Engine

## 1. The Vulnerability of Python DRM
Historically, DRM implemented in raw Python is trivial to bypass by simply modifying the `.py` source file or using `unittest.mock.patch` to force authentication functions to return `True`. 

## 2. The Native C Transition
**Component:** `LicenseManager` (Python) -> `supersploit_auth` (Compiled C Binary)

**Mechanism:**
The framework now offloads all licensing checks to a compiled binary utilizing `subprocess.run()`. 
1. **HWID Hashing:** The C binary uses the DJB2 hashing algorithm against strict hardware metrics (CPU serial, MAC addresses, motherboard UUID) to generate an immutable Hardware ID.
2. **JSON IPC Bridge:** The binary outputs structured JSON directly to `stdout`. The Python `LicenseManager` reads this output using `json.loads(result.stdout)`.

**Why this works:** An attacker cannot simply edit the Python file to return `True` anymore, because the Python `LicenseManager` expects a mathematically valid, cryptographically signed JSON blob from the C binary that dictates the `offline_mode` TTL (Time-to-Live) and specific unlocked feature flags.

## 3. Offline Caching (TTL)
**Mechanism:**
To support Red Teamers operating in air-gapped environments, the activation sequence drops a signed `license.key` file in `.data/.config/`. The C binary natively reads this file, verifies the signature using a hardcoded public key, and checks the `days_remaining`. If the offline TTL is valid, the framework boots without requiring a network connection to the SuperSploit Auth server.

## 4. Discord Webhook Vetting
**Mechanism:**
When an unanchored key is used (`needs_vetting` status), the Python wrapper kicks off a webhook payload directly to the Discord admin channel containing the user's `HWID` and `License Key`. This allows the developer to manually review the deployment environment before permanently anchoring the key in the remote database.