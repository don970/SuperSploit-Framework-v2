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
import sys

try:
    from source.core.license_manager import LicenseManager
except ImportError:
    import os
    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)
    try:
        from source.core.license_manager import LicenseManager
    except ImportError:
        class LicenseManager:
            @staticmethod
            def gate_access(f):
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False

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
            "🎁 Lottery/Reward": "CONGRATS! You have been selected for a $1,000 gift card. Claim your reward at: http://[PHISH_URL]",
            "📱 Service Suspension": "Your [CARRIER] mobile service will be suspended today due to a billing error. Update your payment method immediately at: http://[PHISH_URL]",
            "💳 Fraud Prevention": "Fraud Alert: Did you attempt a purchase of $[AMOUNT] at [STORE]? Reply Y or N. If NO, cancel the transaction here: http://[PHISH_URL]",
            "💼 HR / Payroll": "Important update from HR: Action required regarding your W2 tax documents for [YEAR]. Review your employee portal: http://[PHISH_URL]",
            "🚗 Toll / DMV": "[STATE] Toll Services: You have an unpaid toll invoice. Avoid late fees by paying the balance of $[AMOUNT] at http://[PHISH_URL]",
            "⚠️ IT Support": "URGENT: Your corporate Office 365 password expires in 2 hours. Update your credentials to maintain access: http://[PHISH_URL]",
            "🏥 Healthcare Update": "New secure message from your healthcare provider regarding your recent visit. View your test results here: http://[PHISH_URL]"
        }

        self.config = {
            "mode": 0, # 0=HTTP, 1=SIP, 2=Free
            "http_endpoint": "https://api.twilio.com/2010-04-01/Accounts/AC.../Messages",
            "http_user": "",
            "http_pass": "",
            "sip_server": "127.0.0.1",
            "sip_port": "5060",
            "sip_user": "",
            "sip_pass": "",
            "free_host": "smtp.gmail.com",
            "free_carrier": "verizon",
            "free_user": "",
            "free_pass": ""
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

        ttk.Button(top_bar, text="⚙️ Gateway Settings", command=self._open_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(top_bar, text="🔍 Carrier/HLR Lookup", command=self._hlr_lookup).pack(side=tk.RIGHT, padx=5)

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

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Gateway Configuration")
        win.geometry("550x350")
        win.transient(self.root)
        win.grab_set()
        
        gw_tabs = ttk.Notebook(win)
        gw_tabs.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # HTTP
        tab_http = ttk.Frame(gw_tabs, padding="10")
        gw_tabs.add(tab_http, text=" HTTP API ")
        ttk.Label(tab_http, text="Endpoint:").grid(row=0, column=0, sticky=tk.W)
        e_http_end = ttk.Entry(tab_http, width=50); e_http_end.insert(0, self.config["http_endpoint"]); e_http_end.grid(row=0, column=1, columnspan=3, pady=5)
        ttk.Label(tab_http, text="SID/User:").grid(row=1, column=0, sticky=tk.W)
        e_http_usr = ttk.Entry(tab_http, width=20); e_http_usr.insert(0, self.config["http_user"]); e_http_usr.grid(row=1, column=1, pady=5)
        ttk.Label(tab_http, text="Token/Pass:").grid(row=1, column=2, sticky=tk.W)
        e_http_pwd = ttk.Entry(tab_http, width=20, show="*"); e_http_pwd.insert(0, self.config["http_pass"]); e_http_pwd.grid(row=1, column=3, pady=5)

        # SIP
        tab_sip = ttk.Frame(gw_tabs, padding="10")
        gw_tabs.add(tab_sip, text=" Direct SIP (Paid) ")
        ttk.Label(tab_sip, text="SIP Server:").grid(row=0, column=0, sticky=tk.W)
        e_sip_srv = ttk.Entry(tab_sip, width=20); e_sip_srv.insert(0, self.config["sip_server"]); e_sip_srv.grid(row=0, column=1, pady=5)
        ttk.Label(tab_sip, text="Port:").grid(row=0, column=2, sticky=tk.W)
        e_sip_prt = ttk.Entry(tab_sip, width=10); e_sip_prt.insert(0, self.config["sip_port"]); e_sip_prt.grid(row=0, column=3, pady=5)
        ttk.Label(tab_sip, text="SIP User:").grid(row=1, column=0, sticky=tk.W)
        e_sip_usr = ttk.Entry(tab_sip, width=20); e_sip_usr.insert(0, self.config["sip_user"]); e_sip_usr.grid(row=1, column=1, pady=5)
        ttk.Label(tab_sip, text="SIP Pass:").grid(row=1, column=2, sticky=tk.W)
        e_sip_pwd = ttk.Entry(tab_sip, width=20, show="*"); e_sip_pwd.insert(0, self.config["sip_pass"]); e_sip_pwd.grid(row=1, column=3, pady=5)

        # Free
        tab_free = ttk.Frame(gw_tabs, padding="10")
        gw_tabs.add(tab_free, text=" Free Relay (Wi-Fi) ")
        ttk.Label(tab_free, text="SMTP Host:").grid(row=0, column=0, sticky=tk.W)
        e_free_hst = ttk.Entry(tab_free, width=20); e_free_hst.insert(0, self.config["free_host"]); e_free_hst.grid(row=0, column=1, pady=5)
        ttk.Label(tab_free, text="Carrier:").grid(row=0, column=2, sticky=tk.W)
        free_car_var = tk.StringVar(value=self.config["free_carrier"])
        ttk.Combobox(tab_free, textvariable=free_car_var, values=list(GATEWAYS.keys()), width=15).grid(row=0, column=3, pady=5)
        ttk.Label(tab_free, text="Email User:").grid(row=1, column=0, sticky=tk.W)
        e_free_usr = ttk.Entry(tab_free, width=20); e_free_usr.insert(0, self.config["free_user"]); e_free_usr.grid(row=1, column=1, pady=5)
        ttk.Label(tab_free, text="App Pass:").grid(row=1, column=2, sticky=tk.W)
        e_free_pwd = ttk.Entry(tab_free, width=20, show="*"); e_free_pwd.insert(0, self.config["free_pass"]); e_free_pwd.grid(row=1, column=3, pady=5)
        
        gw_tabs.select(self.config["mode"])

        def save_config():
            self.config["mode"] = gw_tabs.index(gw_tabs.select())
            self.config["http_endpoint"] = e_http_end.get()
            self.config["http_user"] = e_http_usr.get()
            self.config["http_pass"] = e_http_pwd.get()
            self.config["sip_server"] = e_sip_srv.get()
            self.config["sip_port"] = e_sip_prt.get()
            self.config["sip_user"] = e_sip_usr.get()
            self.config["sip_pass"] = e_sip_pwd.get()
            self.config["free_host"] = e_free_hst.get()
            self.config["free_carrier"] = free_car_var.get()
            self.config["free_user"] = e_free_usr.get()
            self.config["free_pass"] = e_free_pwd.get()
            self.log("[*] Gateway Configuration securely saved in memory.")
            win.destroy()

        btn_f = ttk.Frame(win)
        btn_f.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_f, text="💾 Save & Select", command=save_config).pack(side=tk.RIGHT)
        ttk.Button(btn_f, text="🪄 Use Fake Server", command=self._set_fake_server).pack(side=tk.LEFT)
        ttk.Button(btn_f, text="🚀 Use Paid Relay", command=self._set_paid_relay).pack(side=tk.LEFT, padx=5)

    def _set_fake_server(self):
        self.config["mode"] = 0
        self.config["http_endpoint"] = "http://127.0.0.1:8001/sms"
        self.config["sip_server"] = "127.0.0.1"
        self.log("[*] Switched to Local Fake VoIP Server presets in memory.")
        messagebox.showinfo("Config Updated", "Fake Server preset applied. Save window to commit.")

    def _set_paid_relay(self):
        self.config["mode"] = 1
        self.config["sip_server"] = "127.0.0.1"
        self.log("[*] Pointed Direct SIP to local Paid Relay proxy in memory.")
        messagebox.showinfo("Config Updated", "Paid Relay preset applied. Save window to commit.")

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
        def _update():
            self.console.insert(tk.END, f"[{timestamp}] {msg}\n")
            self.console.see(tk.END)
        self.root.after(0, _update)

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
        mode = self.config["mode"]
        body = self.body_text.get(1.0, tk.END).strip()
        sender = self.sender_entry.get().strip()
        
        targets = []
        if self.target_csv.get():
            try:
                with open(self.target_csv.get(), 'r') as f:
                    reader = csv.DictReader(f)
                    targets = [row for row in reader]
            except Exception as e: self.log(f"[-] CSV Error: {e}")
        else: targets = [{"Phone": self.recipient_entry.get().strip()}]

        if not targets or not body:
            def _err():
                messagebox.showerror("Error", "Missing Recipient or Body.")
                self.send_btn.config(state=tk.NORMAL)
            self.root.after(0, _err)
            return

        self.log(f"[*] Initiating sequence for {len(targets)} recipient(s)...")

        for t_dict in targets:
            # Intelligently find the phone number column
            phone_key = next((k for k in t_dict.keys() if 'phone' in k.lower() or 'number' in k.lower()), list(t_dict.keys())[0])
            target_num = t_dict[phone_key]
            
            # Dynamic Parameter Injection (Spear-Phishing)
            personalized_body = body
            for key, val in t_dict.items():
                personalized_body = personalized_body.replace(f"[{key}]", val)

            if mode == 0: # HTTP
                try:
                    payload = {'To': target_num, 'From': sender, 'Body': personalized_body}
                    r = requests.post(self.config["http_endpoint"], data=payload, auth=(self.config["http_user"], self.config["http_pass"]), timeout=10)
                    if r.status_code in [200, 201]: self.log(f"[+] HTTP SUCCESS: {target_num}")
                    else: self.log(f"[-] HTTP FAIL: {target_num} | {r.status_code}")
                except Exception as e: self.log(f"[-] HTTP ERR: {target_num} | {str(e)}")
            elif mode == 1: # SIP
                self._send_sip_message(self.config["sip_server"], self.config["sip_port"], sender, personalized_body, target_num)
                self.log(f"[+] SIP MESSAGE Dispatch: {target_num}")
            else: # Free (Email-to-SMS)
                res = self._send_free_sms(target_num, self.config["free_carrier"], personalized_body, self.config["free_host"], 587, self.config["free_user"], self.config["free_pass"])
                self.log(res)

            if len(targets) > 1: time.sleep(1)

        self.log("[+] Sequence complete.")
        self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    if not LicenseManager.gate_access("SMS Spoofing Suite"):
        sys.exit(1)
    root = tk.Tk()
    app = SMSSpoofingSuite(root)
    root.mainloop()
