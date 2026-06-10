# Plan: Test Enhanced Suggest Engine and Post-Recon Hooks

## Objective
Verify that the `suggest` engine accurately identifies vulnerabilities based on newly implemented scoring (OS, Ports, Services, Banners) and that the `PostReconHook` automatically triggers after reconnaissance.

## Verification Steps
1. **Manual Suggestion Test**:
   - Manually populate a target in `targets.json` with a specific service and banner (e.g., `192.158.151.158` with port `8080` and an `http` service).
   - Run the `suggest 192.158.151.158` command in SuperSploit.
   - **Expected Result**: SuperSploit should suggest `Ping Diagnostic OS Command Injection Test` with a High/Critical confidence score.

2. **Automated Hook Test**:
   - Enable `auto_suggest` in the framework configuration.
   - Execute the `recon/native-portscan/port_scanner.py` module against the target IP.
   - **Expected Result**: After the scan completes, the `PostReconHook` should automatically trigger and display the suggestion report without further user input.

3. **CWE/CVE Matching Test**:
   - Add a `cves` list to a target in the database.
   - Verify that exploits matching those CVEs/CWEs are ranked at the top of the report.

## Tools to Use
- `supersploit` CLI
- Manual editing of `.data/.config/targets.json` for controlled data injection.
- Recon modules for end-to-end testing.
