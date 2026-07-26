 Here is the comprehensive dependency profile for all tools located in /home/donald/.SuperSploit/source/tools. These have been extracted directly from the
  codebase's imports, header inclusions, and script commands.

  ---

  1. Python Third-Party Dependencies (Installable via pip)
  These external Python packages are required by the various graphical interfaces (GUIs), protocol scanners, and payload helpers:

  ┌─────────────────┬───────────────┬────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────┐
  │ Package Name    │ Module Import │ Associated Tools & Subdirectories              │ Purpose                                                              │
  ├─────────────────┼───────────────┼────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────┤
  │ pyusb           │ usb           │ HID_USB/ (aoa_hid_direct.py, mtp_discovery.py) │ Direct USB interface communication and enumeration.                  │
  │ PyBluez         │ bluetooth     │ BLuetooth/, Exploit-testets/                   │ Bluetooth socket creation, HFP profiling, and channel probing.       │
  │ PyOBEX          │ PyOBEX        │ BLuetooth/send_obex.py                         │ Bluetooth Object Exchange (OBEX) push client logic.                  │
  │ Pillow          │ PIL           │ Various GUI tools                              │ Image handling and formatting in graphical frontends.                │
  │ requests        │ requests      │ SE/se_sms_sender.py, VoIP/sms_gui.py           │ Executing outbound REST API requests (e.g., to SMS gateways).        │
  │ pure-python-adb │ ppadb         │ AndroidKernel/adb_proc_dump.py                 │ Python-native interface to interact with Android Debug Bridge (ADB). │
  │ pyserial        │ serial        │ Exploit-testets/test_at_injection.py           │ Controlling and sending AT injection commands via serial/UART.       │
  │ cryptography    │ cryptography  │ Core cryptographic tasks                       │ Secure hashing and symmetric cryptosystems.                          │
  │ qrcode          │ qrcode        │ SE/se_qr_generator.py                          │ Generating custom QR codes for social engineering vectors.           │
  │ gTTS            │ gtts          │ Voice / Vishing templates                      │ Google Text-to-Speech synthesis for vishing operations.              │
  │ nfcpy           │ nfc           │ Hardware/nfc_gui.py                            │ Near Field Communication (NFC) frame sending and reading.            │
  │ frida-tools     │ frida         │ Post-exploitation hooks                        │ Dynamic instrumentation of target processes and runtime hooking.     │
  │ PyPDF2          │ PyPDF2        │ OSINT/metadata_gui.py                          │ Extracting hidden metadata fields from PDF documents.                │
  │ python-docx     │ docx          │ OSINT/metadata_gui.py                          │ Analyzing MS Word files for author/organization metadata.            │
  │ python-pptx     │ pptx          │ OSINT/metadata_gui.py                          │ Reading PowerPoint structures for metadata enumeration.              │
  │ openpyxl        │ openpyxl      │ OSINT/metadata_gui.py                          │ Reading and writing MS Excel files.                                  │
  └─────────────────┴───────────────┴────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────┘
  ---

  2. External C Library Dependencies (Requires Compilation Link Flags)
  The compiled C tools (like the post-exploitation agents and platform-specific enumerators) link against the following libraries:

   * OpenSSL (libssl & libcrypto / -lssl -lcrypto)
       * Includes: <openssl/ssl.h>, <openssl/err.h>, <openssl/evp.h>, <openssl/sha.h>, <openssl/rand.h>
       * Required by: Exploit-testets/test_ssl.c, c2/phantom_agent.c
       * Purpose: Handles asymmetric/symmetric C2 tunnels, certificate checks, and high-performance SHA hashing.
   * Linux Capabilities Library (-lcap)
       * Includes: <sys/capability.h>
       * Required by: Linux_enum/linux-enum1.c
       * Purpose: Audits and checks POSIX thread/process capabilities.

  ---

  3. System Utilities and OS Commands
  Several automation scripts, deployment tools, and compilations rely on these being installed in the host's system path:

   * Android Debug Bridge (adb): Used heavily by deployment scripts (e.g., deploy_lpe.sh) to push payloads (minish, KASLR leaks) to connected targets and
     change execution permissions.
   * Asterisk (asterisk, asterisk-modules): Installed via apt in VoIP/setup_voip_server.sh to configure local SIP servers and PBX infrastructure.
   * Android NDK Compiler: Required to compile C files targeting Android endpoints (specifically referencing <sys/system_properties.h> and Android-specific
     kernel syscalls like in android_enum/android-enum3.c).

  ---

  4. Standard Language Libraries (Built-In)
  The following standard APIs are consistently imported or included across almost all tools:
   * Python Standards: os, sys, time, socket, socketserver, http.server, threading, asyncio, subprocess, shutil, json, csv, re, argparse, base64, struct, ssl,
     smtplib (and email/mime packages for SE spoofer scripts).
   * C / POSIX Standards: stdio.h, stdlib.h, string.h, unistd.h, fcntl.h, errno.h, dirent.h, sys/types.h, sys/stat.h, sys/socket.h, sys/utsname.h, sys/mman.h,
     arpa/inet.h, netinet/in.h, pthread.h.
