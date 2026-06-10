# Plan: Online Database Enhancements for OS Fingerprinting

## Objective
Enhance the `native-Nmap-syle-os-fingerprint.py` module by integrating it with online databases. Since there is no public API to directly query an Nmap fingerprint string, we will leverage external data sources to validate and cross-reference the active fingerprinting results.

## Key Enhancements (Scope)

1.  **Dynamic Nmap DB Update**
    *   **Action:** Add a mechanism to download the latest `nmap-os-db.txt` directly from the official Nmap SVN repository (`https://svn.nmap.org/nmap/nmap-os-db`).
    *   **Logic:** Implement a check to see if the local database is missing or older than a specific threshold (e.g., 30 days). If so, fetch the latest version to ensure the fingerprint matching engine uses the most up-to-date signatures.

2.  **Shodan OS Correlation (Passive Check)**
    *   **Action:** Integrate with the Shodan API to retrieve passive intelligence about the target IP.
    *   **Logic:** Check for a `SHODAN_API_KEY` in the environment variables or the framework's database. If found, query Shodan for the target IP (`https://api.shodan.io/shodan/host/{ip}`).
    *   **Output:** Extract the `os` field from the Shodan response and compare it to our active Nmap fingerprinting result. Log both for the user.

3.  **Online MAC/OUI Lookup**
    *   **Action:** For targets on the local network, resolve their MAC address and query an online OUI database.
    *   **Logic:** Use Scapy's `arping` or similar ARP resolution to find the target's MAC address. If found, query a public API (e.g., `https://api.macvendors.com/{mac}`) to identify the hardware vendor.
    *   **Output:** The hardware vendor often provides strong hints about the underlying OS (e.g., Apple hardware implies iOS/macOS, Cisco implies specific network OS).

## Implementation Steps

1.  **Update `NmapDBMatcher`:**
    *   Add an `update_db()` method using the `urllib.request` library to download the latest database.
2.  **Create `OnlineCorrelator` Class:**
    *   **Method `shodan_lookup(target_ip)`:** Perform the REST API call to Shodan.
    *   **Method `mac_lookup(target_ip)`:** Perform the ARP request and the REST API call to `macvendors.com`.
3.  **Modify `Start` Class:**
    *   Check database age/existence before instantiating `NmapDBMatcher`.
    *   After the active fingerprinting is complete, run the `OnlineCorrelator` methods.
    *   Print the correlated results alongside the best Nmap DB match.
    *   Save all gathered intelligence (Active OS, Shodan OS, Hardware Vendor) to the `targets.json` database.

## Verification
*   Run the script against a known external IP to verify Shodan integration.
*   Run the script against a local IP to verify MAC/OUI lookup.
*   Temporarily delete the local `nmap-os-db.txt` and verify it automatically downloads the latest version.