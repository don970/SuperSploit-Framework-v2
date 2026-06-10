# Implementation Plan: Lateral Network Host Discovery Module

## Objective
Create a new reconnaissance module (`recon/native-discovery/lateral_discovery.py`) that leverages broadcast and multicast protocols to discover local hosts passively and actively. This provides an alternative to noisy ICMP/ARP sweeps, making it highly effective for lateral movement and evasion.

## Background & Motivation
Standard host discovery (like Nmap's `-sn` or our `host_discovery.py`) relies heavily on ARP and ICMP. While ARP is effective locally, ICMP is often blocked by host firewalls (like Windows Defender). Multicast and broadcast protocols such as mDNS, LLMNR, NBNS, and SSDP are frequently permitted by default to allow local network features (like file sharing, printers, and media casting) to function. By probing these protocols, we can discover live hosts, their hostnames, and sometimes the services they are running, bypassing standard security controls.

## Scope & Impact
- **New File**: `recon/native-discovery/lateral_discovery.py`
- **Framework Integration**: The module will include the standard `#!#!#!` metadata block and will require `root: "true"` to use Scapy for packet crafting and sniffing.
- **Database Persistence**: Discovered hosts and their hostnames/services will be automatically merged into the SuperSploit target database (`targets.json`).

## Proposed Solution

We will implement a `LateralDiscoveryEngine` class utilizing Scapy to perform four distinct sweeps:

1.  **mDNS (Multicast DNS)**:
    -   **Target**: `224.0.0.251` on UDP port `5353`.
    -   **Purpose**: Discover Apple devices, Linux machines (Avahi), and modern Windows devices. Often reveals hostnames and specific services (e.g., `_http._tcp.local`).
2.  **LLMNR (Link-Local Multicast Name Resolution)**:
    -   **Target**: `224.0.0.252` on UDP port `5355`.
    -   **Purpose**: Discover Windows machines. We will broadcast a query for a generic/non-existent name (like `WPAD` or `ISATAP`) to elicit responses from LLMNR-enabled hosts.
3.  **NBNS (NetBIOS Name Service)**:
    -   **Target**: Local broadcast address (e.g., `192.168.1.255`) on UDP port `137`.
    -   **Purpose**: Discover legacy Windows machines and their NetBIOS names by sending a NetBIOS Node Status Request.
4.  **SSDP (Simple Service Discovery Protocol)**:
    -   **Target**: `239.255.255.250` on UDP port `1900`.
    -   **Purpose**: Discover UPnP devices like routers, IoT devices, and media servers.

## Implementation Steps

1.  **Create `lateral_discovery.py`**:
    -   Set up the standard imports (`scapy.all`, `socket`, `json`, `os`, `ipaddress`).
    -   Include the `#!#!#!` metadata block for the `recon_engine.py` to parse.
2.  **Develop `LateralDiscoveryEngine`**:
    -   Implement `nbns_sweep(target_broadcast)`: Crafts an NBNS Node Status Request (`\x00` repeated) to grab the NetBIOS name.
    -   Implement `mdns_sweep()`: Crafts an mDNS query for `_services._dns-sd._udp.local` to elicit responses from mDNS responders.
    -   Implement `llmnr_sweep()`: Crafts an LLMNR query for a generic hostname.
    -   Implement `ssdp_sweep()`: Sends an `M-SEARCH * HTTP/1.1` over UDP to the SSDP multicast address.
3.  **Coordinate Execution (`Start` function)**:
    -   Determine the local broadcast address based on the current machine's IP/Subnet or an R_HOST parameter if applicable.
    -   Execute the sweeps concurrently or sequentially.
    -   Parse the Scapy responses to extract IPs, hostnames, and service banners.
4.  **Database Integration**:
    -   Deduplicate the discovered hosts based on IP address.
    -   Merge the new data (including discovered hostnames and protocols) into `DatabaseManagment.getTargets()` or `targets.json`, similar to `host_discovery.py`.

## Verification & Testing
1.  Run the module using the framework: `use recon/native-discovery/lateral_discovery`.
2.  Verify that it successfully executes without crashing and correctly identifies hosts on the local network that are broadcasting/responding to these protocols.
3.  Check the `targets.json` database to ensure the newly discovered hosts and their associated metadata (e.g., NetBIOS names) are saved correctly.

## Alternatives Considered
-   **Standard Sockets vs. Scapy**: We could use standard Python `socket` module to bind to multicast groups and send/receive. However, Scapy simplifies packet crafting and parsing significantly, especially for complex protocols like NBNS and LLMNR. Since `host_discovery.py` already uses Scapy and requires root, following that precedent maintains consistency.