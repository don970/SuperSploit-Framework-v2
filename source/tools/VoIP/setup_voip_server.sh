#!/bin/bash

# SuperSploit Private VoIP Server Setup (Asterisk)
# This script automates the installation and basic configuration of an Asterisk PBX 
# for standalone SMS (SIP MESSAGE) delivery.

echo "=========================================================="
echo "   SUPERSPLOIT VOIP SERVER SETUP - VERSION 1.0           "
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "[-] This script must be run as root (sudo)." 
   exit 1
fi

echo "[*] Phase 1: Installing Asterisk and Dependencies..."
apt update -y && apt upgrade -y
apt install asterisk asterisk-modules -y

echo "[*] Phase 2: Configuring SIP Settings (sip.conf)..."
cat <<EOF > /etc/asterisk/sip.conf
[general]
context=default
allowguest=no
udpbindaddr=0.0.0.0
tcpenable=yes
tcpbindaddr=0.0.0.0
transport=udp,tcp
srvlookup=yes
accept_outofcall_message=yes
outofcall_message_context=messages
auth_message_requests=no

[supersploit_user]
type=friend
host=dynamic
secret=SuperSecretPass123
context=messages
EOF

echo "[*] Phase 3: Configuring Dialplan for SMS (extensions.conf)..."
cat <<EOF > /etc/asterisk/extensions.conf
[messages]
exten => _.,1,NoOp(SMS received from \${MESSAGE(from)} to \${MESSAGE(to)})
exten => _.,n,Log(NOTICE, SMS Content: \${MESSAGE(body)})
exten => _.,n,MessageSend(sip:\${EXTEN}@\${MESSAGE(to):4}, \${MESSAGE(from)})
exten => _.,n,Hangup()

[default]
EOF

echo "[*] Phase 4: Starting VoIP Services..."
systemctl enable asterisk
systemctl restart asterisk

echo "=========================================================="
echo "[+] SUCCESS: Private VoIP Server is online!"
echo "[*] Server IP: $(hostname -I | awk '{print $1}')"
echo "[*] Default SIP User: supersploit_user"
echo "[*] Default SIP Pass: SuperSecretPass123"
echo "=========================================================="
echo "[!] IMPORTANT: Ensure Port 5060 (UDP/TCP) is open in your VPS firewall."
echo "=========================================================="
