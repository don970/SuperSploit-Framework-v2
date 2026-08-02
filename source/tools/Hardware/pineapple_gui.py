import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
import os
import time
import json

try:
    import requests
    HAS_REQ = True
except ImportError:
    HAS_REQ = False

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

class PineappleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Pineapple & Karma Integration")
        self.root.geometry("800x650")
        
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
        self.style.configure("TCheckbutton", background=self.bg_sec, foreground=self.fg_main)
        
        # Button & Entry Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")

        self.token = ""
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Connection Config
        cfg_frame = ttk.LabelFrame(main_frame, text=" 🍍 API Connection ", padding="15")
        cfg_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cfg_frame, text="Pineapple IP:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.ip_ent = ttk.Entry(cfg_frame, width=20, font=("Helvetica", 11))
        self.ip_ent.insert(0, "172.16.42.1")
        self.ip_ent.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(cfg_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.port_ent = ttk.Entry(cfg_frame, width=10, font=("Helvetica", 11))
        self.port_ent.insert(0, "1471")
        self.port_ent.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(cfg_frame, text="Password / API Token:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.pass_ent = ttk.Entry(cfg_frame, width=30, show="*", font=("Helvetica", 11))
        self.pass_ent.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky=tk.W)
        
        self.auth_btn = ttk.Button(cfg_frame, text="🔐 AUTHENTICATE", command=self._auth_pineapple)
        self.auth_btn.grid(row=2, column=0, columnspan=4, sticky=tk.EW, pady=(10, 0))

        # PineAP Controls
        pine_frame = ttk.LabelFrame(main_frame, text=" 📡 PineAP / Karma Attack Control ", padding="15")
        pine_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.karma_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(pine_frame, text="Enable Karma (Probe Response)", variable=self.karma_var).pack(anchor=tk.W, padx=10, pady=5)
        
        self.beacon_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(pine_frame, text="Enable Beacon Responses", variable=self.beacon_var).pack(anchor=tk.W, padx=10, pady=5)
        
        btn_frame = ttk.Frame(pine_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.pineap_btn = ttk.Button(btn_frame, text="🚀 LAUNCH PINEAP", command=lambda: self._toggle_pineap(True))
        self.pineap_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.pineap_stop = ttk.Button(btn_frame, text="🛑 STOP PINEAP", command=lambda: self._toggle_pineap(False))
        self.pineap_stop.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

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

    def _auth_pineapple(self):
        ip = self.ip_ent.get()
        port = self.port_ent.get()
        pwd = self.pass_ent.get()
        self.log(f"[*] Authenticating with Wi-Fi Pineapple at http://{ip}:{port}...")
        threading.Thread(target=self._auth_thread, args=(ip, port, pwd), daemon=True).start()
        
    def _auth_thread(self, ip, port, pwd):
        if not HAS_REQ:
            time.sleep(1)
            self.token = "simulated_token_12345"
            self.log("[+] Authentication successful (Simulated Mode).")
            return
            
        try:
            url = f"http://{ip}:{port}/api/login"
            r = requests.post(url, json={"username": "root", "password": pwd}, timeout=5)
            if "token" in r.json():
                self.token = r.json()["token"]
                self.log("[+] API Token Acquired. Pineapple is linked.")
            else:
                self.log("[-] Authentication failed. Invalid credentials.")
        except Exception as e:
            self.log(f"[-] API Error: {e}")
            
    def _toggle_pineap(self, enable):
        if not self.token:
            self.log("[-] Error: You must authenticate with the Pineapple first.")
            return
            
        ip = self.ip_ent.get()
        port = self.port_ent.get()
        karma = self.karma_var.get()
        beacon = self.beacon_var.get()
        
        self.log(f"[*] {'Enabling' if enable else 'Disabling'} PineAP Engine...")
        threading.Thread(target=self._pineap_thread, args=(ip, port, enable, karma, beacon), daemon=True).start()

    def _pineap_thread(self, ip, port, enable, karma, beacon):
        if not HAS_REQ:
            time.sleep(1)
            self.log(f"[+] PineAP State Updated. Karma: {karma}, Beacons: {beacon}")
            return
            
        try:
            url = f"http://{ip}:{port}/api/pineap/settings"
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {"enable": enable, "karma": karma, "beaconResponses": beacon}
            r = requests.put(url, json=payload, headers=headers, timeout=5)
            if r.status_code == 200:
                self.log("[+] PineAP configuration successfully pushed to hardware.")
            else:
                self.log(f"[-] API Error: {r.text}")
        except Exception as e:
            self.log(f"[-] Request failed: {e}")

if __name__ == "__main__":
    if not LicenseManager.gate_access("Pineapple Automation Engine"):
        sys.exit(1)
    root = tk.Tk()
    app = PineappleGUI(root)
    root.mainloop()