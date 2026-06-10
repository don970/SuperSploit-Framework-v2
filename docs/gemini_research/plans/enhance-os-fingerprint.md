# Plan: Enhance Nmap-Style OS Fingerprinting

## Objective
Upgrade the `native-Nmap-syle-os-fingerprint.py` reconnaissance module to provide higher fidelity OS detection. By aligning the Python Scapy implementation more closely with Nmap's C++ parsing rules, the engine will generate fingerprints that match the `nmap-os-db.txt` signatures with greater accuracy.

## Key Enhancements (Scope)

1.  **High-Fidelity TCP Parsing**
    *   **TCP Options (`O=`):** Replace the simplified option string generation with Nmap's exact formatting (e.g., `M<hex>N W<hex> N T11 S` for MSS, NOP, WScale, NOP, Timestamp, SackOK).
    *   **TCP Flags (`F=`):** Capture the full combination of flags returned in responses (e.g., `SA`, `AR`, `R`) instead of boolean checks for just `S` and `A`.
    *   **Sequence/Ack Analysis (`S=`, `A=`):** Calculate relative Sequence and Acknowledgment responses (e.g., is the returned ACK equal to the SYN's SEQ+1?).

2.  **IPID Sequence Generation Analysis**
    *   **`TI` (TCP IPID):** Analyze the `IPID` array captured during the `SEQ` probes. Determine if the host generates IDs sequentially (`I`), randomly (`R`), as broken little-endian (`BI`), or keeps them at zero (`Z`).

3.  **Deeper UDP (U1) and ICMP (IE) Inspection**
    *   **U1 Probe:** Extract the returned IP header encapsulated within the ICMP Port Unreachable error. Parse attributes like `RIPL` (Returned IP Length) and `RID` (Returned IP ID).
    *   **IE Probes:** Extract the ICMP Code (`CD`) from the response to determine if the target modifies the code field when replying to an echo request with a non-zero code.

## Implementation Steps

1.  **Modify `_parse_response`**:
    *   Add logic to parse and encode TCP options natively (MSS, WScale, Timestamp, SACK).
    *   Extract and stringify all TCP flags.
    *   Pass the original probe packet to calculate relative `S=` and `A=` attributes.
2.  **Modify `_calculate_seq_metrics`**:
    *   Analyze the `ipids` array alongside sequence numbers to calculate the `TI` value.
3.  **Modify `_probe_u1`**:
    *   Dissect the `ICMP.payload` to analyze the encapsulated IP layer and assign `RIPL`, `RID`, etc.
4.  **Modify `_probe_ie`**:
    *   Capture the returned `ICMP.code` and assign it to the `CD` attribute.

## Verification
*   Run the script against local and remote targets to ensure it executes without syntax errors.
*   Verify that the output `Fingerprint` string contains the newly implemented attributes (e.g., `O=M5B4...`, `TI=I`).
*   Confirm that the accuracy score and OS match rate improve for standard targets (like Linux or Windows).