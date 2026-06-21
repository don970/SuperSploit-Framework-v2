import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import subprocess
import time
import csv

class IMessageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit iMessage Injector - NATIVE BRIDGING")
        self.root.geometry("600x600")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.target_csv = tk.StringVar()
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Targets
        tgt_frame = ttk.LabelFrame(main_frame, text=" 🎯 Targets (Apple IDs / Phones) ", padding="10")
        tgt_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(tgt_frame, text="📂 Load CSV", command=self._load_csv).grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(tgt_frame, textvariable=self.target_csv, width=35, state="readonly").grid(row=0, column=1, columnspan=2)
        
        ttk.Label(tgt_frame, text="Single Target:").grid(row=1, column=0, sticky=tk.E, padx=5)
        self.single_target = ttk.Entry(tgt_frame, width=35)
        self.single_target.grid(row=1, column=1, columnspan=2, pady=2)

        # Message
        msg_frame = ttk.LabelFrame(main_frame, text=" 💬 iMessage Payload ", padding="10")
        msg_frame.pack(fill=tk.X, pady=5)
        
        self.body_text = tk.Text(msg_frame, height=5, width=60, font=("Courier", 10))
        self.body_text.pack(fill=tk.BOTH, padx=5, pady=5)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.send_btn = ttk.Button(btn_frame, text="🍏 INJECT iMESSAGES", command=self._start_injection)
        self.send_btn.pack(side=tk.RIGHT)

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Injection Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console = scrolledtext.ScrolledText(log_frame, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.console.see(tk.END)

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
            self.send_btn.config(state=tk.NORMAL)
            return

        self.log(f"[*] Beginning native osascript injection for {len(targets)} targets...")
        
        for t in targets:
            script = f'tell application "Messages"\n set tSvc to 1st service whose service type = iMessage\n set tBud to buddy "{t}" of tSvc\n send "{body}" to tBud\n end tell'
            res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            
            if res.returncode == 0: self.log(f"[+] SUCCESS: Dispatched to {t}")
            else: self.log(f"[-] ERROR on {t}: {res.stderr.strip()}")
            
            if len(targets) > 1: time.sleep(1)

        self.log("[+] Sequence Complete.")
        self.send_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = IMessageGUI(root)
    root.mainloop()