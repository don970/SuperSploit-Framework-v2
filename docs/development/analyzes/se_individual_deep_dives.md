# SuperSploit Framework - SE Tools (Developer & Debug Deep Dive)

*This document provides a reverse-engineering, developer-level analysis of the Social Engineering & Delivery Suite. It outlines low-level mechanics, edge cases, logic flaws, and architectural improvements for framework hardening.*

---

## 1. Web Stager & AitM Proxy (`web_stager_gui.py` & `dns_patcher_gui.py`)

**Architecture:** Subclasses `http.server.BaseHTTPRequestHandler` wrapped in a multi-threaded `socketserver.TCPServer`. Handles upstream proxying via `requests`. DNS spoofing is handled via an asynchronous Scapy `sniff` daemon.

### Capabilities & Exploitation Vectors
- **Transparent TLS Bridging:** Intercepts traffic and issues self-signed or Let's Encrypt certs locally while maintaining an encrypted bridge to the upstream target, completely bypassing HSTS (if the client trusts the root CA or clicks through).
- **Dynamic DOM Manipulation:** Injects Keyloggers or BeEF hooks via regex (`re.sub`) immediately before the `</body>` tag of the upstream response.
- **Rogue DNS MITM:** Uses packet forgery to instantly beat legitimate DNS servers in answering IPv4 `A` record queries (`UDP/53`).

### Unforeseen Logic Errors & Edge Cases (The "Bugs")
1. **Content-Length Truncation Error:** The proxy alters the upstream DOM (injecting `<script>`), but it blindly passes back the upstream `Content-Length` header if it exists. By adding 100 bytes of JS, the client browser will truncate the last 100 bytes of the HTML page, potentially breaking CSS/JS rendering visually.
2. **Chunked Transfer Encoding Failure:** Stripping `transfer-encoding` is correct, but if the upstream target *mandates* chunking, `requests` will buffer the entire response into memory before returning it. For large files or streams, this causes immense latency or OOM crashes in the proxy thread.
3. **SPA Routing Breaks:** Modern Single Page Applications (React, Angular) load via XHR/Fetch after the initial DOM load. The AitM proxy doesn't rewrite relative paths (`/api/v1/auth`) to absolute paths. If the SPA queries the root domain, it hits the proxy, but if it's hardcoded to query an external CDN, the proxy misses the traffic entirely.

### Architectural Improvements
- **Recalculate `Content-Length`:** After DOM manipulation, compute `len(content.encode('utf-8'))` and explicitly overwrite the header before `self.send_header()`.
- **WebSocket Support:** The current `http.server` implementation drops `Upgrade: websocket` headers. We must implement raw socket handovers (`self.connection`) to proxy WebSocket streams, otherwise live-chat/MFA push notification features on targets like Office365 will fail.

---

## 2. Evil Twin AP Deployer & Captive Portal (`evil_twin_gui.py` & `se_captive_portal.py`)

**Architecture:** System-level daemon orchestrator managing `hostapd` (Access Point), `dnsmasq` (DHCP/DNS Sinkhole), and `aireplay-ng` (Deauth).

### Capabilities & Exploitation Vectors
- **Absolute Network Control:** Forces targets onto a `192.168.99.1/24` subnet. 
- **DNS Blackholing:** `dnsmasq` is configured with `address=/#/192.168.99.1`, meaning *any* domain the victim requests (Google, Apple Captive probes) resolves instantly to the attacker's HTTP server.
- **Continuous Deauth:** Asynchronous subprocess execution of `aireplay-ng` allows continuous MAC-spoofed disassociation frames to knock victims off legitimate BSSIDs.

### Unforeseen Logic Errors & Edge Cases (The "Bugs")
1. **Monitor Mode Pre-requisite Crash:** `aireplay-ng -0 0 -a <BSSID> <iface>` will instantly fail and close if `<iface>` is not in monitor mode. The script does not automatically transition the NIC via `airmon-ng start <iface>`, meaning the Deauth Engine relies on the operator setting this up manually beforehand.
2. **Daemon Massacre (Process Zombie Risk):** `subprocess.run(["sudo", "killall", "dnsmasq", "hostapd"])` is aggressive. If the attacker is using the framework on a Linux host that relies on `dnsmasq` for its own network manager (like Ubuntu/NetworkManager), this command kills the host's internet connection. 
3. **Rfkill Block:** If the Wi-Fi card is soft-blocked by `rfkill`, `ifconfig up` will fail silently, causing `hostapd` to throw a fatal interface error and exit.

### Architectural Improvements
- **PID Tracking:** Instead of `killall`, capture the PID of the spawned `Popen` objects and kill *only* those specific instances during teardown.
- **Interface Pre-Flight:** Add `rfkill unblock wifi` and `iw dev <iface> set type monitor` automatically to the Deauth engine startup logic.

---

## 3. SMS Spoofing & SIP Injection Suite (`sms_gui.py` & `se_sms_sender.py`)

**Architecture:** Multi-modal telecommunications suite utilizing `requests` (API), `smtplib` (Email-to-SMS), and raw UDP socket crafting (`socket.SOCK_DGRAM`) for direct SIP signaling.

### Capabilities & Exploitation Vectors
- **Direct SIP Injection:** Bypasses the need for complex VoIP stacks (like `pjsip`) by manually assembling and injecting `MESSAGE sip:` UDP payloads. Excellent for hitting misconfigured or open SIP trunks (Port 5060).
- **Variable Spear-Phishing:** Parses CSV columns on the fly, transforming generic payloads into highly targeted, uniquely crafted messages per recipient.

### Unforeseen Logic Errors & Edge Cases (The "Bugs")
1. **SIP Authentication Void:** The Direct SIP engine is "fire and forget". It blasts the UDP packet and closes. If the upstream SIP server responds with `401 Unauthorized` or `407 Proxy Authentication Required` (which 99% of paid trunks do), the script fails to handle the digest authentication challenge, resulting in silent delivery failure.
2. **CSV Column Guessing Crash:** The logic `phone_key = next((k for k in t_dict.keys() if 'phone' in k.lower() ...))` crashes with `StopIteration` if the CSV lacks a header matching "phone" or "number" (e.g., if the header is "Target").
3. **Carrier Rate Limiting:** The `time.sleep(1)` in the `Free Carrier Relays` mode is vastly insufficient. Gateways like `vtext.com` will aggressively IP ban senders pushing more than 10 messages a minute from dynamic/residential IPs.

### Architectural Improvements
- **SIP State Machine:** Implement a lightweight SIP Digest Auth calculator (MD5 hashing of username, realm, password, nonce, uri) to respond to `401` challenges.
- **Jitter Algorithms:** Replace static `sleep(1)` with randomized jitter (e.g., `random.uniform(5, 15)`) to evade carrier heuristic spam-traps.

---

## 4. Advanced SMTP Spoofing Suite (`smtp_gui.py` & `se_smtp_spoofer.py`)

**Architecture:** Leverages `email.mime` tree construction, base64 encoding for binaries, and `smtplib` for synchronized TLS transport.

### Capabilities & Exploitation Vectors
- **Header Forgery:** Manipulates envelope properties (`From`, `Reply-To`, `X-Mailer: Microsoft Outlook 16.0`) to evade rudimentary spam-filter heuristics.
- **Binary Attachment Streaming:** Safely handles arbitrary file attachments (APKs, PDFs) by forcing `application/octet-stream` and `Content-Disposition`, allowing seamless integration with the framework's generated payloads.
- **Asynchronous Log Redirection:** Subclasses `io.StringIO` to intercept `sys.stderr` from synchronous libraries (`smtplib`), bridging blocking C-extensions into the asynchronous `tkinter` UI thread flawlessly.

### Unforeseen Logic Errors & Edge Cases (The "Bugs")
1. **Double TLS Wrapping Crash:** If an operator selects `Use SSL/TLS` (usually Port 465) AND `Use STARTTLS` concurrently, the code executes `SMTP_SSL()` and then immediately calls `.starttls()`. This causes an OpenSSL protocol violation and crashes the thread.
2. **Google App Password Truncation:** The `google_match` regex extracts passwords grouped like `xxxx xxxx xxxx xxxx`. If the user pastes a standard 16-character string *without* spaces, the regex fails, and the script falls back to stripping spaces, which is fine, but the regex logic is overly rigid.
3. **Sender Policy Framework (SPF) Rejection:** Sending mail claiming to be `support@microsoft.com` from an unauthorized Mailgun IP will result in an immediate `550 5.7.1 Unauthenticated email from domain...` error. The script does not currently warn the operator of DMARC/SPF misalignment prior to blasting.

### Architectural Improvements
- **Pre-flight DMARC Check:** Use `dns.resolver` to query the TXT record of the spoofed domain. If `v=spf1 -all` is found and the relay host isn't authorized, pop up a warning to the operator to prevent burning the campaign.
- **Connection Pooling:** For mass blasts (CSV), opening and closing the `smtplib` connection for *every single target* is highly inefficient and risks triggering rate limits. The connection should be opened once, the loop executes `send_message()`, and then it quits.

---

## 5. Native iMessage/RCS Injector (`imessage_gui.py`)

**Architecture:** Python `subprocess` interacting with the macOS-native `osascript` (AppleScript) binary to hook the `Messages.app` daemon.

### Capabilities & Exploitation Vectors
- **E2E Encryption Bypass:** By injecting at the UI/OS level *after* the OS has established cryptographic trust with Apple's servers, the payload is delivered as a highly trusted "Blue Bubble" from a verified Apple ID.
- **Network Evasion:** Traffic never traverses standard SMS gateways or Twilio APIs. It is routed natively through APNS (Apple Push Notification Service), rendering it invisible to carrier DPI (Deep Packet Inspection).

### Unforeseen Logic Errors & Edge Cases (The "Bugs")
1. **UI Thread Blocking (macOS Sandbox):** The first time `osascript` attempts to control `Messages.app`, macOS throws an aggressive TCC (Transparency, Consent, and Control) prompt: "Terminal wants access to control Messages". The `subprocess.run` call will hang indefinitely waiting for the user to click "Allow".
2. **AppleScript Exception Handling:** If the `targetBuddy` (the victim's phone number/Apple ID) is invalid, or if it resolves to a Green Bubble (SMS) and the host Mac doesn't have SMS Forwarding enabled via iPhone, AppleScript throws a runtime error. The current script merely logs "Injection failed," but doesn't gracefully differentiate between a banned Apple ID and a non-iMessage target.
3. **Process Rate Limiting:** Firing `osascript` 100 times in a loop for a CSV blast creates 100 rapid-fire AppleEvents. The macOS `lsmd` (LaunchServices) daemon will throttle or kill the script for malicious behavior.

### Architectural Improvements
- **Batch AppleScript Execution:** Instead of spawning `osascript` in a Python `for` loop, dynamically construct a single AppleScript file containing a list of targets and a loop, then execute it once.
- **TCC Pre-Check:** Add a payload stage that checks `sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db` to verify Terminal has `kTCCServiceAppleEvents` permissions before launching the campaign.