import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import time
import smtplib
import ssl
import os
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

try:
    from source.core.license_manager import LicenseManager
except ImportError:
    import sys
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

class SMTPSpoofingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit SMTP Suite - ADVANCED PHISHING")
        self.root.geometry("800x850")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.target_csv = tk.StringVar()
        self.attachment_path = tk.StringVar()
        self.template_path = tk.StringVar()
        
        self.config = {
            "host": "smtp.mailgun.org",
            "port": "587",
            "user": "",
            "pass": "",
            "use_tls": True,
            "use_ssl": False
        }
        
        self.templates = {
            "Select Template...": "",
            "⚠️ IT Support: Password Reset": "<html><body><h2>IT Support Alert</h2><p>Your corporate password expires in 2 hours. Update it here: <a href='http://[PHISH_URL]'>Reset Password</a></p></body></html>",
            "💼 HR: Policy Update": "<html><body><h2>HR Notice</h2><p>Dear [NAME], please review the updated company policy attached. Or visit: <a href='http://[PHISH_URL]'>HR Portal</a></p></body></html>",
            "🧾 Finance: Invoice Overdue": "<html><body><h2>Invoice Overdue</h2><p>Your invoice for $[AMOUNT] is overdue. Please pay immediately: <a href='http://[PHISH_URL]'>View Invoice</a></p></body></html>",
            "🏦 Bank Alert": "<html><body><h2>Fraud Alert</h2><p>Did you attempt a purchase at [STORE]? If not, cancel the transaction: <a href='http://[PHISH_URL]'>Cancel Transaction</a></p></body></html>",
            "📦 Shipping: Delivery Failed": "<html><body><h2>Delivery Attempt Failed</h2><p>Your package from [VENDOR] could not be delivered. Please update your shipping address and pay the $1.99 redelivery fee: <a href='http://[PHISH_URL]'>Reschedule Delivery</a></p></body></html>",
            "🔒 Security: Unusual Login": "<html><body><h2>Security Alert</h2><p>A new login was detected from [CITY]. If this wasn't you, secure your account immediately: <a href='http://[PHISH_URL]'>Secure Account</a></p></body></html>",
            "🎁 Reward: Gift Card Winner": "<html><body><h2>Congratulations!</h2><p>Dear [NAME], you've won a $500 [STORE] gift card. Claim your reward before it expires: <a href='http://[PHISH_URL]'>Claim Reward</a></p></body></html>",
            "⚖️ Legal: Copyright Takedown": "<html><body><h2>DMCA Takedown Notice</h2><p>Your account has been flagged for copyright infringement regarding a recent post. Review the formal complaint: <a href='http://[PHISH_URL]'>View Complaint</a></p></body></html>",
            "📅 Calendar: Meeting Invite": "<html><body><h2>Mandatory Team Meeting</h2><p>Dear [NAME], please join the mandatory Q3 review meeting. Review the agenda and RSVP here: <a href='http://[PHISH_URL]'>Join Meeting</a></p></body></html>",
        }
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top Bar
        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill=tk.X, pady=5)
        
        ttk.Button(top_bar, text="⚙️ SMTP Settings", command=self._open_settings).pack(side=tk.RIGHT, padx=5)
        
        ttk.Label(top_bar, text="📖 Quick Templates:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar(value="Select Template...")
        self.template_menu = ttk.OptionMenu(top_bar, self.template_var, *self.templates.keys(), command=self._apply_template)
        self.template_menu.pack(side=tk.LEFT, padx=5)

        # Spoofing Details
        spoof_frame = ttk.LabelFrame(main_frame, text=" 🎭 Spoofing Details ", padding="10")
        spoof_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(spoof_frame, text="From Name:").grid(row=0, column=0, sticky=tk.W)
        self.from_name = ttk.Entry(spoof_frame, width=25)
        self.from_name.insert(0, "IT Support")
        self.from_name.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(spoof_frame, text="From Email:").grid(row=0, column=2, sticky=tk.W)
        self.from_email = ttk.Entry(spoof_frame, width=25)
        self.from_email.insert(0, "support@company.com")
        self.from_email.grid(row=0, column=3, padx=5)
        
        ttk.Label(spoof_frame, text="Subject:").grid(row=1, column=0, sticky=tk.W)
        self.subject_entry = ttk.Entry(spoof_frame, width=60)
        self.subject_entry.insert(0, "Important Security Update")
        self.subject_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        # Payload & Targets
        payload_frame = ttk.LabelFrame(main_frame, text=" 📦 Payload & Targets ", padding="10")
        payload_frame.pack(fill=tk.X, pady=5)

        ttk.Button(payload_frame, text="📂 Load Target CSV", command=lambda: self._load_file(self.target_csv, "CSV", "*.csv")).grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(payload_frame, textvariable=self.target_csv, width=45, state="readonly").grid(row=0, column=1, columnspan=2)
        
        ttk.Label(payload_frame, text="Single Target:").grid(row=1, column=0, sticky=tk.E, padx=5)
        self.single_target = ttk.Entry(payload_frame, width=45)
        self.single_target.grid(row=1, column=1, columnspan=2, pady=2)

        ttk.Button(payload_frame, text="📄 Load HTML Template", command=lambda: self._load_file(self.template_path, "HTML", "*.html")).grid(row=2, column=0, padx=5, pady=2)
        ttk.Entry(payload_frame, textvariable=self.template_path, width=45, state="readonly").grid(row=2, column=1, columnspan=2)

        ttk.Button(payload_frame, text="📎 Load Attachment", command=lambda: self._load_file(self.attachment_path, "All", "*.*")).grid(row=3, column=0, padx=5, pady=2)
        ttk.Entry(payload_frame, textvariable=self.attachment_path, width=45, state="readonly").grid(row=3, column=1, columnspan=2)

        # Action & Console
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.send_btn = ttk.Button(btn_frame, text="🚀 INITIATE MASS BLAST", command=self._start_delivery)
        self.send_btn.pack(side=tk.RIGHT)

        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Delivery Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console = scrolledtext.ScrolledText(log_frame, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("SMTP Relay Configuration")
        win.geometry("450x300")
        win.transient(self.root)
        win.grab_set()

        frame = ttk.Frame(win, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=5)
        e_host = ttk.Entry(frame, width=30); e_host.insert(0, self.config["host"]); e_host.grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        e_port = ttk.Entry(frame, width=10); e_port.insert(0, str(self.config["port"])); e_port.grid(row=1, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="User:").grid(row=2, column=0, sticky=tk.W, pady=5)
        e_user = ttk.Entry(frame, width=30); e_user.insert(0, self.config["user"]); e_user.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Pass:").grid(row=3, column=0, sticky=tk.W, pady=5)
        e_pass = ttk.Entry(frame, width=30, show="*"); e_pass.insert(0, self.config["pass"]); e_pass.grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)

        v_tls = tk.BooleanVar(value=self.config["use_tls"])
        ttk.Checkbutton(frame, text="STARTTLS", variable=v_tls).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        v_ssl = tk.BooleanVar(value=self.config["use_ssl"])
        ttk.Checkbutton(frame, text="SSL/TLS", variable=v_ssl).grid(row=4, column=2, sticky=tk.W, pady=5)

        def save():
            self.config["host"] = e_host.get(); self.config["port"] = e_port.get()
            self.config["user"] = e_user.get(); self.config["pass"] = e_pass.get()
            self.config["use_tls"] = v_tls.get(); self.config["use_ssl"] = v_ssl.get()
            self.log("[*] SMTP Configuration securely saved in memory.")
            win.destroy()

        def presets():
            e_host.delete(0, tk.END); e_host.insert(0, "smtp.gmail.com")
            e_port.delete(0, tk.END); e_port.insert(0, "587"); v_tls.set(True); v_ssl.set(False)

        btn_f = ttk.Frame(win); btn_f.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_f, text="💾 Save Settings", command=save).pack(side=tk.RIGHT)
        ttk.Button(btn_f, text="🪄 Gmail/Outlook Presets", command=presets).pack(side=tk.LEFT)

    def _apply_template(self, selection):
        if selection in self.templates and selection != "Select Template...":
            temp_path = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "temp_email.html")
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, "w") as f: f.write(self.templates[selection])
            self.template_path.set(temp_path)
            self.subject_entry.delete(0, tk.END)
            if "IT Support" in selection: self.subject_entry.insert(0, "Action Required: Password Expiry")
            elif "HR" in selection: self.subject_entry.insert(0, "Important: Policy Update")
            elif "Finance" in selection: self.subject_entry.insert(0, "URGENT: Invoice Overdue")
            elif "Bank" in selection: self.subject_entry.insert(0, "Security Alert: Suspicious Login")
            elif "Shipping" in selection: self.subject_entry.insert(0, "Action Required: Package Delivery Failed")
            elif "Security" in selection: self.subject_entry.insert(0, "Critical: Unusual Login Attempt Detected")
            elif "Reward" in selection: self.subject_entry.insert(0, "You've Received a New Reward!")
            elif "Legal" in selection: self.subject_entry.insert(0, "URGENT: Copyright Infringement Notice")
            elif "Calendar" in selection: self.subject_entry.insert(0, "Invitation: Mandatory Team Meeting")
            self.log(f"[*] Loaded template '{selection}' into payload pipeline.")

    def _load_file(self, var, ftype_name, ftype_ext):
        f = filedialog.askopenfilename(filetypes=[(f"{ftype_name} Files", ftype_ext)])
        if f: var.set(f)

    def log(self, msg):
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.console.see(tk.END)

    def _start_delivery(self):
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._delivery_logic, daemon=True).start()

    def _delivery_logic(self):
        targets = []
        if self.target_csv.get():
            try:
                with open(self.target_csv.get(), 'r') as f:
                    reader = csv.DictReader(f)
                    targets = [row for row in reader]
            except Exception as e: self.log(f"[-] CSV Error: {e}")
        elif self.single_target.get():
            targets = [{"Email": self.single_target.get().strip()}]

        if not targets:
            self.log("[-] ERROR: No targets loaded.")
            self.send_btn.config(state=tk.NORMAL)
            return

        self.log(f"[*] Compiling payload for {len(targets)} targets...")
        
        base_html = "Please see the attached document."
        if self.template_path.get() and os.path.exists(self.template_path.get()):
            with open(self.template_path.get(), 'r') as f:
                base_html = f.read()

        try:
            port = int(self.config["port"])
            self.log(f"[*] Connecting to {self.config['host']}:{port}...")
            if self.config["use_ssl"]:
                server = smtplib.SMTP_SSL(self.config["host"], port, context=ssl._create_unverified_context())
            else:
                server = smtplib.SMTP(self.config["host"], port)
                if self.config["use_tls"]:
                    server.starttls(context=ssl._create_unverified_context())
                    server.ehlo()
            
            if self.config["user"] and self.config["pass"]:
                server.login(self.config["user"], self.config["pass"])
                self.log("[+] Authentication successful.")

            for t_dict in targets:
                email_key = next((k for k in t_dict.keys() if 'email' in k.lower()), list(t_dict.keys())[0])
                target_email = t_dict[email_key]
                
                personalized_html = base_html
                personalized_subj = self.subject_entry.get()
                personalized_name = self.from_name.get()
                
                for key, val in t_dict.items():
                    personalized_html = personalized_html.replace(f"[{key}]", val)
                    personalized_subj = personalized_subj.replace(f"[{key}]", val)
                    personalized_name = personalized_name.replace(f"[{key}]", val)

                msg = MIMEMultipart()
                msg['From'] = f"{personalized_name} <{self.from_email.get()}>"
                msg['To'] = target_email
                msg['Subject'] = personalized_subj
                msg['Reply-To'] = self.from_email.get()
                msg.attach(MIMEText(personalized_html, 'html'))

                if self.attachment_path.get() and os.path.exists(self.attachment_path.get()):
                    with open(self.attachment_path.get(), "rb") as a:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(a.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attachment_path.get())}")
                    msg.attach(part)

                server.send_message(msg)
                self.log(f"[+] Dispatched to: {target_email}")
                if len(targets) > 1: time.sleep(1)

            server.quit()
            self.log("[+] Campaign Complete.")
        except Exception as e:
            self.log(f"[-] Fatal SMTP Error: {e}")
            
        self.send_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    import sys
    if not LicenseManager.gate_access("Advanced SMTP Suite"):
        sys.exit(1)
    root = tk.Tk()
    app = SMTPSpoofingGUI(root)
    root.mainloop()