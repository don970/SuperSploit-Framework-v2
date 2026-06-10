# FRP Research: Samsung Android 11 Bypass

- **Target Profile:** Samsung Galaxy devices running Android 11, Kernel 4.4.199, Security Patch level May 2022.
- **Key Vulnerabilities:**
    - **CVE-2021-39685 ("Inspector Gadget"):** USB heap overflow in `composite.c` for Kernel RCE. Weaponized in `exploits/android/cve_2021_39685_inspector_gadget.py`.
    - **CVE-2022-20113:** Logic error to force MTP mode without user authentication, enabling stage-2 delivery.
    - **CVE-2025-21042 ("LANDFALL"):** OOB write in `libimagecodec.quram.so` via DNG thumbnail parsing over MTP.
- **Bypass Mechanism:** Use kernel-level shell to zero out the FRP storage partition (`/dev/block/persistent` or `/dev/block/frp`) using `dd if=/dev/zero ...`. This wipes the security token, allowing the Setup Wizard to skip account verification.
- **Status:** **FAILED**. Inspector Gadget and MTP bypass methods did not work on the target tablet.
- **New Direction:** Pivoting to **Unisoc (Spreadtrum) bootloader exploits**, specifically targeting the BROM handshake and potential CVE-2022-38694 vulnerabilities.
- **Detailed Report:** `/home/donald/.SuperSploit/docs/research/android_11_usb_vectors.md`
