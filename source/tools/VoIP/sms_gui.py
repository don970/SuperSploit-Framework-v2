import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
import csv
import time
import os
import socket
import random
import string
import ssl
import smtplib
from email.message import EmailMessage

# Carrier Gateway Mapping (for Free Relay)
GATEWAYS = {
    "verizon": "vtext.com",
    "att": "txt.att.net",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com",
    "boost": "myboostmobile.com",
    "cricket": "sms.cricketwireless.net",
    "uscellular": "email.uscc.net",
    "virgin": "vmobl.com"
}

class SMSSpoofingSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit SMS Suite v2.0 - DEEP INTERACTION")
        self.root.geometry("950x900")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.target_csv = tk.StringVar()
        
        # Predefined Templates
        self.templates = {
            "Select Template...": "",
            "🏦 Bank Alert (2FA)": "ALERT: Your [BANK_NAME] account has been locked due to suspicious activity. Verify identity here: http://[PHISH_URL]",
            "📦 Package Tracking": "Your package from [VENDOR] is held at our warehouse. Pay the $1.99 delivery fee to release: https://[PHISH_URL]",
            "🔐 Password Reset": "SuperSploit Security: A login was detected from a new device in [CITY]. If this was not you, reset your password: http://[PHISH_URL]",
            "🎁 Lottery/Reward": "CONGRATS! You have been selected for a $1,000 gift card. Claim your reward at: http://[PHISH_URL]"
        }

        self._build_ui()

    def _build_ui(self):
        # Action Buttons (Pack first at bottom to ensure visibility)
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.send_btn = ttk.Button(btn_frame, text="🚀 SEND NOW", command=self._start_delivery)
        self.send_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(btn_frame, text="🧹 Clear Log", command=lambda: self.console.delete(1.0, tk.END)).pack(side=tk.RIGHT)

        # Main scrollable area
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- 1. Top Bar: OSINT & Templates ---
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, pady=5)

        ttk.Label(top_bar, text="📖 Templates:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar(value="Select Template...")
        self.template_menu = ttk.OptionMenu(top_bar, self.template_var, *self.templates.keys(), command=self._apply_template)
        self.template_menu.pack(side=tk.LEFT, padx=5)

        ttk.Button(top_bar, text="🔍 Carrier/HLR Lookup", command=self._hlr_lookup).pack(side=tk.RIGHT, padx=5)

        # --- 2. Gateway Configuration ---
        config_frame = ttk.LabelFrame(main_frame, text=" ⚙️ Gateway Configuration ", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        self.gw_tabs = ttk.Notebook(config_frame)
        self.gw_tabs.pack(fill=tk.X)

        # Tab: HTTP API
        self.tab_http = ttk.Frame(self.gw_tabs, padding="10")
        self.gw_tabs.add(self.tab_http, text=" HTTP API ")

        ttk.Label(self.tab_http, text="Endpoint:").grid(row=0, column=0, sticky=tk.W)
        self.endpoint_entry = ttk.Entry(self.tab_http, width=60)
        self.endpoint_entry.insert(0, "https://api.twilio.com/2010-04-01/Accounts/AC.../Messages")
        self.endpoint_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=2)

        ttk.Label(self.tab_http, text="SID:").grid(row=1, column=0, sticky=tk.W)
        self.user_entry = ttk.Entry(self.tab_http, width=25)
        self.user_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.tab_http, text="Token:").grid(row=1, column=2, sticky=tk.W)
        self.pass_entry = ttk.Entry(self.tab_http, width=25, show="*")
        self.pass_entry.grid(row=1, column=3, padx=5, pady=2)

        # Tab: Direct SIP (Paid/Private)
        self.tab_sip = ttk.Frame(self.gw_tabs, padding="10")
        self.gw_tabs.add(self.tab_sip, text=" Direct SIP (Paid) ")

        ttk.Label(self.tab_sip, text="SIP Server:").grid(row=0, column=0, sticky=tk.W)
        self.sip_server = ttk.Entry(self.tab_sip, width=30)
        self.sip_server.insert(0, "127.0.0.1")
        self.sip_server.grid(row=0, column=1, padx=5)
        ttk.Label(self.tab_sip, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.sip_port = ttk.Entry(self.tab_sip, width=10)
        self.sip_port.insert(0, "5060")
        self.sip_port.grid(row=0, column=3, padx=5)

        ttk.Label(self.tab_sip, text="SIP User:").grid(row=1, column=0, sticky=tk.W)
        self.sip_user = ttk.Entry(self.tab_sip, width=30)
        self.sip_user.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.tab_sip, text="SIP Pass:").grid(row=1, column=2, sticky=tk.W)
        self.sip_pass = ttk.Entry(self.tab_sip, width=25, show="*")
        self.sip_pass.grid(row=1, column=3, padx=5)

        # Tab: Free Relay (Wi-Fi)
        self.tab_free = ttk.Frame(self.gw_tabs, padding="10")
        self.gw_tabs.add(self.tab_free, text=" Free Relay (Wi-Fi) ")

        ttk.Label(self.tab_free, text="SMTP Host:").grid(row=0, column=0, sticky=tk.W)
        self.smtp_host = ttk.Entry(self.tab_free, width=30)
        self.smtp_host.insert(0, "smtp.gmail.com")
        self.smtp_host.grid(row=0, column=1, padx=5)

        ttk.Label(self.tab_free, text="Carrier:").grid(row=0, column=2, sticky=tk.W)
        self.carrier_var = tk.StringVar(value="verizon")
        carriers = list(GATEWAYS.keys())
        ttk.OptionMenu(self.tab_free, self.carrier_var, carriers[0], *carriers).grid(row=0, column=3)

        ttk.Label(self.tab_free, text="Email User:").grid(row=1, column=0, sticky=tk.W)
        self.free_user = ttk.Entry(self.tab_free, width=30)
        self.free_user.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.tab_free, text="App Pass:").grid(row=1, column=2, sticky=tk.W)
        self.free_pass = ttk.Entry(self.tab_free, width=25, show="*")
        self.free_pass.grid(row=1, column=3, padx=5)

        ttk.Button(config_frame, text="🚀 Setup Paid Relay", command=self._set_paid_relay).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(config_frame, text="🪄 Use Local Fake Server", command=self._set_fake_server).pack(side=tk.LEFT, padx=5, pady=5)

        # --- 3. Message Composition ---
        msg_frame = ttk.LabelFrame(main_frame, text=" ✉️ Message Composition ", padding="10")
        msg_frame.pack(fill=tk.X, pady=5)

        ttk.Label(msg_frame, text="Sender ID (From):").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sender_entry = ttk.Entry(msg_frame, width=30)
        self.sender_entry.insert(0, "BANK_SECURE")
        self.sender_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(msg_frame, text="Recipient (To):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.recipient_entry = ttk.Entry(msg_frame, width=30)
        self.recipient_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)

        ttk.Label(msg_frame, text="Message Body:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.body_text = tk.Text(msg_frame, height=5, width=60, font=("Courier", 10))
        self.body_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

        # --- 4. Mass Blast (Batch) ---
        blast_frame = ttk.LabelFrame(main_frame, text=" 🚀 Mass Blast (CSV) ", padding="10")
        blast_frame.pack(fill=tk.X, pady=5)

        ttk.Label(blast_frame, text="Target List:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(blast_frame, textvariable=self.target_csv, width=40, state="readonly").pack(side=tk.LEFT, padx=5)
        ttk.Button(blast_frame, text="📂 Load CSV", command=self._load_csv).pack(side=tk.LEFT, padx=5)

        # --- 5. Delivery Log ---
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Delivery Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console = scrolledtext.ScrolledText(log_frame, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def _set_fake_server(self):
        self.endpoint_entry.delete(0, tk.END)
        self.endpoint_entry.insert(0, "http://127.0.0.1:8001/sms")
        self.sip_server.delete(0, tk.END)
        self.sip_server.insert(0, "127.0.0.1")
        self.log("[*] Switched to Local Fake VoIP Server presets.")

    def _set_paid_relay(self):
        self.gw_tabs.select(1)
        self.sip_server.delete(0, tk.END)
        self.sip_server.insert(0, "127.0.0.1")
        self.log("[*] Pointed Direct SIP to local Paid Relay proxy.")

    def _apply_template(self, selection):
        if selection in self.templates:
            self.body_text.delete(1.0, tk.END)
            self.body_text.insert(tk.END, self.templates[selection])

    def _hlr_lookup(self):
        number = self.recipient_entry.get().strip()
        if not number:
            messagebox.showwarning("Warning", "Enter a recipient number first.")
            return
        self.log(f"[*] Probing Carrier for {number}...")
        def probe():
            try:
                time.sleep(1)
                self.log(f"[+] HLR Result: {number} | Valid: True | Carrier: Simulated Carrier | Type: MOBILE")
            except:
                self.log(f"[-] HLR Lookup failed.")
        threading.Thread(target=probe, daemon=True).start()

    def _load_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.target_csv.set(filename)
            self.log(f"[*] Loaded batch list: {os.path.basename(filename)}")

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.console.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.console.see(tk.END)

    def _start_delivery(self):
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._delivery_logic, daemon=True).start()

    def _send_sip_message(self, server, port, user, body, to):
        try:
            call_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
            tag = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            sip_msg = (
                f"MESSAGE sip:{to}@{server} SIP/2.0\r\n"
                f"Via: SIP/2.0/UDP 127.0.0.1;branch=z9hG4bK{tag}\r\n"
                f"Max-Forwards: 70\r\n"
                f"From: <sip:{user}@{server}>;tag={tag}\r\n"
                f"To: <sip:{to}@{server}>\r\n"
                f"Call-ID: {call_id}\r\n"
                f"CSeq: 1 MESSAGE\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(body)}\r\n\r\n{body}"
            )
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(sip_msg.encode(), (server, int(port)))
            self.log(f"[*] SIP Packet Sent to {server}:{port}")
            return True
        except Exception as e:
            self.log(f"[-] SIP Error: {e}")
            return False

    def _send_free_sms(self, number, carrier, message, smtp_server, smtp_port, user, pwd):
        if carrier.lower() not in GATEWAYS:
            return f"[-] Error: Unknown carrier '{carrier}'"
        domain = GATEWAYS[carrier.lower()]
        recipient = f"{number}@{domain}"
        msg = EmailMessage()
        msg.set_content(message)
        msg['To'] = recipient
        msg['From'] = user
        msg['Subject'] = "SMS Message"
        try:
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls(context=ssl._create_unverified_context())
            server.ehlo()
            server.login(user, pwd)
            server.send_message(msg)
            server.quit()
            return f"[+] Free Relay: Successfully sent to {recipient}"
        except Exception as e:
            return f"[-] Free Relay SMTP Error: {e}"

    def _delivery_logic(self):
        mode = self.gw_tabs.index(self.gw_tabs.select()) # 0=HTTP, 1=SIP, 2=Free
        body = self.body_text.get(1.0, tk.END).strip()
        sender = self.sender_entry.get().strip()
        
        targets = []
        if self.target_csv.get():
            try:
                with open(self.target_csv.get(), 'r') as f:
                    reader = csv.reader(f)
                    targets = [row[0] for row in reader if row]
            except Exception as e: self.log(f"[-] CSV Error: {e}")
        else: targets = [self.recipient_entry.get().strip()]

        if not targets[0] or not body:
            messagebox.showerror("Error", "Missing Recipient or Body.")
            self.send_btn.config(state=tk.NORMAL)
            return

        self.log(f"[*] Initiating sequence for {len(targets)} recipient(s)...")

        for target in targets:
            if mode == 0: # HTTP
                try:
                    payload = {'To': target, 'From': sender, 'Body': body}
                    r = requests.post(self.endpoint_entry.get(), data=payload, auth=(self.user_entry.get(), self.pass_entry.get()), timeout=10)
                    if r.status_code in [200, 201]: self.log(f"[+] HTTP SUCCESS: {target}")
                    else: self.log(f"[-] HTTP FAIL: {target} | {r.status_code}")
                except Exception as e: self.log(f"[-] HTTP ERR: {target} | {str(e)}")
            elif mode == 1: # SIP
                self._send_sip_message(self.sip_server.get(), self.sip_port.get(), sender, body, target)
                self.log(f"[+] SIP MESSAGE Dispatch: {target}")
            else: # Free (Email-to-SMS)
                import smtplib
                res = self._send_free_sms(target, self.carrier_var.get(), body, self.smtp_host.get(), 587, self.free_user.get(), self.free_pass.get())
                self.log(res)

            if len(targets) > 1: time.sleep(1)

        self.log("[+] Sequence complete.")
        self.send_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SMSSpoofingSuite(root)
    root.mainloop()
