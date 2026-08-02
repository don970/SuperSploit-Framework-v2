# Third-Party Notices

The SuperSploit Framework ("The Software") incorporates, interfaces with, or dynamically links to several open-source and third-party libraries, tools, and frameworks.

In accordance with their respective licensing terms, we acknowledge and thank the developers of the following projects:

---

## 1. Core Cryptography & Low-Level Libraries
**OpenSSL**
*   **Description:** A robust, commercial-grade, and full-featured toolkit for TLS and SSL protocols, utilized for AES-256-GCM Payload Cryptography.
*   **License:** OpenSSL License (BSD-style) and SSLeay License (BSD-style)
*   **Copyright:** The OpenSSL Project Authors
*   **Link:** [https://github.com/openssl/openssl](https://github.com/openssl/openssl)

**cryptography (Python)**
*   **Description:** Cryptographic recipes and primitives for Python developers, powering the SuperSploit C2 Server encryption.
*   **License:** Apache License 2.0 / BSD License
*   **Copyright:** The Python Cryptographic Authority and developers
*   **Link:** https://cryptography.io/

---

## 2. Python Third-Party Libraries

**pyusb**
*   **Description:** Python module for USB access.
*   **License:** GNU Lesser General Public License v2.1 (LGPLv2.1)
*   **Copyright:** Wander Lairson Costa and others
*   **Link:** https://github.com/pyusb/pyusb

**PyBluez**
*   **Description:** Python wrapper for Bluetooth sockets.
*   **License:** GNU Lesser General Public License v2.1 (LGPLv2.1)
*   **Copyright:** Albert Huang and others
*   **Link:** https://github.com/pybluez/pybluez

**PyOBEX**
*   **Description:** Python library for Object Exchange (OBEX) protocol.
*   **License:** GNU Lesser General Public License v2.1 (LGPLv2.1)
*   **Copyright:** Christian E. Schafmeister and others
*   **Link:** https://github.com/pybluez/pybluez/tree/master/PyOBEX

**Pillow**
*   **Description:** The friendly PIL fork (Python Imaging Library).
*   **License:** HPPL (Pillow License)
*   **Copyright:** Alex Clark and contributors
*   **Link:** https://python-pillow.org/

**requests**
*   **Description:** Elegant and simple HTTP library for Python.
*   **License:** Apache License 2.0
*   **Copyright:** Kenneth Reitz and others
*   **Link:** https://requests.readthedocs.io/

**pure-python-adb**
*   **Description:** Pure Python implementation of the Android Debug Bridge (ADB) protocol.
*   **License:** Apache License 2.0
*   **Copyright:** Swind and others
*   **Link:** https://github.com/Swind/pure-python-adb

**pyserial**
*   **Description:** Python serial port access library.
*   **License:** BSD 3-Clause License
*   **Copyright:** Chris Liechti
*   **Link:** https://pyserial.readthedocs.io/

**qrcode**
*   **Description:** QR Code generator for Python.
*   **License:** BSD 3-Clause License
*   **Copyright:** Lincoln Loop and others
*   **Link:** https://github.com/lincolnloop/python-qrcode

**PyPDF2**
*   **Description:** A utility to read and write PDFs with Python.
*   **License:** BSD 3-Clause License
*   **Copyright:** Phaseit, Inc. and others
*   **Link:** https://pypdf2.readthedocs.io/

**python-docx**
*   **Description:** Read, write and create .docx files with Python.
*   **License:** MIT License
*   **Copyright:** Steve Canny
*   **Link:** https://python-docx.readthedocs.io/

**python-pptx**
*   **Description:** Create and update PowerPoint (.pptx) files.
*   **License:** MIT License
*   **Copyright:** Steve Canny
*   **Link:** https://python-pptx.readthedocs.io/

**openpyxl**
*   **Description:** A Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files.
*   **License:** MIT License
*   **Copyright:** Eric Gazoni and others
*   **Link:** https://openpyxl.readthedocs.io/

**Rich**
*   **Description:** Python library for rich text and beautiful formatting in the terminal.
*   **License:** MIT License
*   **Copyright:** Will McGugan
*   **Link:** https://github.com/Textualize/rich

**prompt_toolkit**
*   **Description:** Library for building powerful interactive command lines in Python.
*   **License:** BSD 3-Clause License
*   **Copyright:** Jonathan Slenders
*   **Link:** https://github.com/prompt-toolkit/python-prompt-toolkit

**phonenumbers**
*   **Description:** Python port of Google's libphonenumber.
*   **License:** Apache License 2.0
*   **Copyright:** Google
*   **Link:** https://github.com/daviddrysdale/python-phonenumbers

---

## 3. Dynamic Analysis & Android Exploitation
**Frida**
*   **Description:** Dynamic instrumentation toolkit for developers, reverse-engineers, and security researchers, powering the SuperSploit DAST and SSL Shatter engines.
*   **License:** wxWindows Library Licence, Version 3.1
*   **Copyright:** Ole André Vadla Ravnäs
*   **Link:** [https://frida.re/](https://frida.re/)

**Apktool**
*   **Description:** A tool for reverse engineering Android apk files, utilized by the SuperSploit Polymorphic Crypter and Trust Store Patcher.
*   **License:** Apache License 2.0
*   **Copyright:** Connor Tumbleson (iBotPeaches) & Ryszard Wiśniewski (brutall)
*   **Link:** [https://apktool.org/](https://apktool.org/)

**Buildozer & Kivy**
*   **Description:** Python-for-Android packaging tools utilized by the Python/Kivy payload generation pipeline.
*   **License:** MIT License
*   **Copyright:** Kivy Team and Contributors
*   **Link:** https://kivy.org/

---

## 4. Network Reconnaissance & Proximity Hardware
**Scapy**
*   **Description:** A powerful interactive packet manipulation program, powering the OS Fingerprinting, AWDL proximity exploits, and native Port Scanner.
*   **License:** GNU General Public License v2.0 (GPLv2)
*   **Copyright:** Philippe Biondi and the Scapy Community
*   **Link:** [https://scapy.net/](https://scapy.net/)

**nfcpy**
*   **Description:** A Python module to read and write NFC tags, powering the NFC Attack Suite.
*   **License:** EUPL 1.1 (European Union Public Licence)
*   **Copyright:** Stephen Tiedemann

**Aircrack-ng Suite (aireplay-ng)**
*   **Description:** Wi-Fi security auditing tools utilized by the Evil Twin Deauthentication engine.
*   **License:** GNU General Public License v2.0 (GPLv2)
*   **Copyright:** Thomas d'Otreppe

---

## 5. Network Reconnaissance Data
**Nmap Security Scanner Data Files**
*   **Description:** This project bundles and utilizes heuristic data files (`nmap-service-probes`, `nmap-os-db`) created by the **Nmap Project** to facilitate asynchronous network reconnaissance.
*   **Copyright:** Nmap is copyrighted by Insecure.Com LLC.
*   **Trademark:** Nmap is a registered trademark of Insecure.Com LLC.
*   **License:** The Nmap data files are licensed under the Nmap Public Source License (NPSL). A copy of the NPSL is available on the official Nmap website. By utilizing the Nmap data files within this framework, you agree to comply with the terms of the NPSL.
*   **Link:** https://nmap.org/

---

## 6. Intelligence & OSINT Modules
**phonenumbers**
*   **License:** Apache License 2.0 (Google)

**gTTS (Google Text-to-Speech)**
*   **License:** MIT License (Pierre Nicolas Durette)

**FPDF**
*   **License:** LGPL (GNU Lesser General Public License)