import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import subprocess
import time
import csv
import sys
import os

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

class IMessageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit iMessage Injector - NATIVE BRIDGING")
        self.root.geometry("700x700")
        
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
        
        # Button Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        
        # Entry Styling
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")

        self.target_csv = tk.StringVar()
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Targets
        tgt_frame = ttk.LabelFrame(main_frame, text=" 🎯 Targets (Apple IDs / Phones) ", padding="15")
        tgt_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(tgt_frame, text="📂 BROWSE CSV", command=self._load_csv).grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(tgt_frame, textvariable=self.target_csv, width=45, state="readonly").grid(row=0, column=1, columnspan=2, padx=10, pady=5)
        
        ttk.Label(tgt_frame, text="Single Target:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.single_target = ttk.Entry(tgt_frame, width=45)
        self.single_target.grid(row=1, column=1, columnspan=2, padx=10, pady=5)

        # Message
        msg_frame = ttk.LabelFrame(main_frame, text=" 💬 iMessage Payload ", padding="15")
        msg_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.body_text = tk.Text(msg_frame, height=6, width=60, font=("Helvetica", 11), bg="#313244", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT, padx=10, pady=10)
        self.body_text.pack(fill=tk.BOTH, expand=True)

        # Action Banner Button
        self.send_btn = ttk.Button(main_frame, text="🚀 INJECT iMESSAGES", command=self._start_injection)
        self.send_btn.pack(fill=tk.X, pady=(0, 10))

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Injection Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        def _update():
            self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.console.see(tk.END)
        self.root.after(0, _update)

    def _load_csv(self):
        f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if f: self.target_csv.set(f)

    def _start_injection(self):
        self.send_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._injection_logic, daemon=True).start()

    def _injection_logic(self):
        targets = []
        if self.target_csv.get():
            try:
                with open(self.target_csv.get(), 'r') as f:
                    targets = [row[0] for row in csv.reader(f) if row]
            except Exception as e: self.log(f"[-] CSV Error: {e}")
        elif self.single_target.get():
            targets = [self.single_target.get().strip()]

        body = self.body_text.get(1.0, tk.END).strip()
        if not targets or not body:
            self.log("[-] ERROR: Missing targets or message payload.")
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
            return

        self.log(f"[*] Beginning native osascript injection for {len(targets)} targets...")
        
        for t in targets:
            script = f'tell application "Messages"\n set tSvc to 1st service whose service type = iMessage\n set tBud to buddy "{t}" of tSvc\n send "{body}" to tBud\n end tell'
            res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            
            if res.returncode == 0: self.log(f"[+] SUCCESS: Dispatched to {t}")
            else: self.log(f"[-] ERROR on {t}: {res.stderr.strip()}")
            
            if len(targets) > 1: time.sleep(1)

        self.log("[+] Sequence Complete.")
        self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    if not LicenseManager.gate_access("iMessage Injector"):
        sys.exit(1)
    root = tk.Tk()
    app = IMessageGUI(root)
    root.mainloop()