import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import smtplib
import ssl
import os
import threading
import sys
import io
import datetime
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default
import mimetypes

class SMTPLogger(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.after(0, lambda: self.text_widget.insert(tk.END, s))
        self.text_widget.after(0, lambda: self.text_widget.see(tk.END))
        return len(s)

class SuperSploitMailerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Mailer - Advanced SMTP Delivery")
        self.root.geometry("850x850")
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.attachments = []
        self.eml_path = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        # Action Buttons (Pack first at bottom to ensure visibility)
        btn_frame = ttk.Frame(self.root, padding="10")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.send_btn = ttk.Button(btn_frame, text="🚀 SEND SPOOFED EMAIL", command=self._start_send_thread)
        self.send_btn.pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="🧹 Clear Log", command=lambda: self.console.delete(1.0, tk.END)).pack(side=tk.RIGHT)

        # Main Scrollable/Expandable Area
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- 1. Server Configuration ---
        server_frame = ttk.LabelFrame(main_frame, text=" 🛡️ SMTP Server Configuration ", padding="10")
        server_frame.pack(fill=tk.X, pady=5)

        ttk.Label(server_frame, text="Host:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.host_entry = ttk.Entry(server_frame, width=30)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(server_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.port_entry = ttk.Entry(server_frame, width=10)
        self.port_entry.insert(0, "2525")
        self.port_entry.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(server_frame, text="User:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.user_entry = ttk.Entry(server_frame, width=30)
        self.user_entry.insert(0, "admin")
        self.user_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(server_frame, text="Pass:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.pass_entry = ttk.Entry(server_frame, width=15, show="*")
        self.pass_entry.insert(0, "password")
        self.pass_entry.grid(row=1, column=3, padx=5, pady=2)

        self.use_tls = tk.BooleanVar(value=False)
        ttk.Checkbutton(server_frame, text="Use STARTTLS", variable=self.use_tls).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        self.use_ssl = tk.BooleanVar(value=False)
        ttk.Checkbutton(server_frame, text="Use SSL/TLS", variable=self.use_ssl).grid(row=2, column=2, sticky=tk.W, padx=5)

        ttk.Button(server_frame, text="🪄 Gmail/Outlook Presets", command=self._apply_presets).grid(row=2, column=3, padx=5)

        # --- 2. Envelope & Headers ---
        envelope_frame = ttk.LabelFrame(main_frame, text=" 🎭 Spoofing & Delivery Settings ", padding="10")
        envelope_frame.pack(fill=tk.X, pady=5)

        ttk.Label(envelope_frame, text="Sender Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.sender_name = ttk.Entry(envelope_frame, width=30)
        self.sender_name.insert(0, "IT Support")
        self.sender_name.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(envelope_frame, text="Sender Email (Spoof):").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.sender_email = ttk.Entry(envelope_frame, width=30)
        self.sender_email.insert(0, "support@example.com")
        self.sender_email.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(envelope_frame, text="Recipient Email:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.recipient_email = ttk.Entry(envelope_frame, width=30)
        self.recipient_email.grid(row=2, column=1, padx=5, pady=2)

        # --- 3. Content Tabs ---
        content_frame = ttk.LabelFrame(main_frame, text=" 📧 Email Content ", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Live Compose
        self.tab_compose = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_compose, text=" Live Compose ")

        ttk.Label(self.tab_compose, text="Subject:").pack(anchor=tk.W)
        self.subject_entry = ttk.Entry(self.tab_compose)
        self.subject_entry.pack(fill=tk.X, pady=2)

        ttk.Label(self.tab_compose, text="Body (HTML supported):").pack(anchor=tk.W)
        self.body_text = tk.Text(self.tab_compose, height=8, font=("Courier", 10))
        self.body_text.pack(fill=tk.BOTH, expand=True, pady=2)

        attach_btn_frame = ttk.Frame(self.tab_compose)
        attach_btn_frame.pack(fill=tk.X)
        ttk.Button(attach_btn_frame, text="📎 Add Attachment", command=self._add_attachment).pack(side=tk.LEFT, pady=5)
        self.attach_label = ttk.Label(attach_btn_frame, text="No attachments")
        self.attach_label.pack(side=tk.LEFT, padx=10)

        # Tab 2: Load EML
        self.tab_eml = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.tab_eml, text=" Load .EML File ")

        ttk.Label(self.tab_eml, text="Selected Template:").pack(anchor=tk.W, pady=5)
        eml_entry_frame = ttk.Frame(self.tab_eml)
        eml_entry_frame.pack(fill=tk.X)
        ttk.Entry(eml_entry_frame, textvariable=self.eml_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(eml_entry_frame, text="📂 Browse", command=self._browse_eml).pack(side=tk.LEFT, padx=5)

        # --- 4. Delivery Console ---
        console_frame = ttk.LabelFrame(main_frame, text=" 🖥️ SMTP Transaction Log ", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.console = scrolledtext.ScrolledText(console_frame, height=6, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def _apply_presets(self):
        self.host_entry.delete(0, tk.END)
        self.host_entry.insert(0, "smtp.gmail.com")
        self.port_entry.delete(0, tk.END)
        self.port_entry.insert(0, "587")
        self.use_tls.set(True)
        self.use_ssl.set(False)
        self.console.insert(tk.END, "[*] Applied Gmail/Outlook secure presets (Port 587 + STARTTLS).\n")

    def _add_attachment(self):
        files = filedialog.askopenfilenames()
        if files:
            self.attachments.extend(files)
            self.attach_label.config(text=f"{len(self.attachments)} file(s) attached")

    def _browse_eml(self):
        filename = filedialog.askopenfilename(filetypes=[("Email Files", "*.eml"), ("All Files", "*.*")])
        if filename:
            self.eml_path.set(filename)

    def _start_send_thread(self):
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._send_email_logic, daemon=True).start()

    def _send_email_logic(self):
        try:
            # Setup Log Redirection
            logger = SMTPLogger(self.console)
            
            # Strip whitespace to prevent DNS resolution errors (like [Errno -2])
            host = self.host_entry.get().strip()
            port_str = self.port_entry.get().strip()
            
            if not host:
                raise ValueError("SMTP Host cannot be empty.")
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Invalid port number: '{port_str}'")

            user = self.user_entry.get().strip()
            raw_pwd = self.pass_entry.get().strip()
            
            # SMART CLEAN: If it looks like a Google App Password block, extract just the code
            # Example: "app password: xxxx xxxx xxxx xxxx" -> "xxxxxxxxxxxxxxxx"
            import re
            google_match = re.search(r'([a-z]{4}\s?[a-z]{4}\s?[a-z]{4}\s?[a-z]{4})', raw_pwd.lower())
            if google_match:
                pwd = google_match.group(1).replace(" ", "")
                self.console.insert(tk.END, "[*] Smart-Clean: Extracted 16-char App Password code.\n")
            else:
                pwd = raw_pwd.replace(" ", "") # Strip all spaces for standard SMTP passwords

            # Construct Message
            current_tab = self.notebook.index(self.notebook.select())
            
            if current_tab == 0: # Live Compose
                msg = EmailMessage()
                msg['Subject'] = self.subject_entry.get().strip()
                s_name = self.sender_name.get().strip()
                s_email = self.sender_email.get().strip()
                msg['From'] = f"{s_name} <{s_email}>"
                msg['To'] = self.recipient_email.get().strip()
                
                body = self.body_text.get(1.0, tk.END)
                if "<html>" in body.lower():
                    msg.set_content("HTML content below. Please use an HTML-capable mail client.")
                    msg.add_alternative(body, subtype='html')
                else:
                    msg.set_content(body)

                for path in self.attachments:
                    ctype, encoding = mimetypes.guess_type(path)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    with open(path, 'rb') as f:
                        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(path))
            else: # Load EML
                if not self.eml_path.get():
                    raise ValueError("No .eml file selected.")
                with open(self.eml_path.get(), 'rb') as f:
                    msg = BytesParser(policy=default).parse(f)
                
                # Override envelope if specified (spoofing)
                s_name = self.sender_name.get().strip()
                s_email = self.sender_email.get().strip()
                r_email = self.recipient_email.get().strip()

                if s_email:
                    if 'From' in msg: del msg['From']
                    msg['From'] = f"{s_name} <{s_email}>"
                if r_email:
                    if 'To' in msg: del msg['To']
                    msg['To'] = r_email

            # Connect and Send
            self.console.insert(tk.END, f"[*] Connecting to {host}:{port}...\n")
            
            if self.use_ssl.get():
                server = smtplib.SMTP_SSL(host, port, context=ssl._create_unverified_context())
            else:
                server = smtplib.SMTP(host, port)
                if self.use_tls.get():
                    server.starttls(context=ssl._create_unverified_context())
                    # CRITICAL: Re-identify to see AUTH extension after encryption
                    server.ehlo()

            server.set_debuglevel(1)
            # Redirect stderr (where smtplib debug goes) to our console widget
            old_stderr = sys.stderr
            sys.stderr = logger
            
            try:
                if user and pwd:
                    server.login(user, pwd)
                
                server.send_message(msg)
                self.console.insert(tk.END, "\n[+] SUCCESS: Email sent successfully!\n")
                messagebox.showinfo("Success", "Email has been dispatched.")
            finally:
                sys.stderr = old_stderr
                server.quit()

        except Exception as e:
            self.console.insert(tk.END, f"\n[-] ERROR: {str(e)}\n")
            messagebox.showerror("Transmission Error", str(e))
        finally:
            self.send_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SuperSploitMailerGUI(root)
    root.mainloop()
