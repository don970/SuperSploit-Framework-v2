import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
import time

try:
    from gtts import gTTS
    has_gtts = True
except ImportError:
    has_gtts = False

# Import local SIP Client
try:
    from .sip_client import SIPClient
    from source.core.license_manager import LicenseManager
except ImportError:
    # Handle if run as standalone script - try to find the framework root
    import sys
    # vishing_gui.py is in source/tools/VoIP/
    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)

    try:
        from sip_client import SIPClient
        from source.core.license_manager import LicenseManager
    except ImportError:
        # Fallback for standalone if still not found
        class LicenseManager:
            @staticmethod
            def gate_access(f): 
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False
        # Need dummy SIPClient if still failing
        class SIPClient: pass

class VishingMimicGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Mimic - Deepfake Vishing Suite")
        self.root.geometry("900x850")

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

        # Button & Entry Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")

        self.audio_path = tk.StringVar()
        self.is_calling = False

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. SIP Server Configuration ---
        config_frame = ttk.LabelFrame(main_frame, text=" 🛰️ VoIP Gateway Configuration ", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_frame, text="SIP Server:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.sip_server = ttk.Entry(config_frame, width=30, font=("Helvetica", 11)); self.sip_server.insert(0, "127.0.0.1"); self.sip_server.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.sip_port = ttk.Entry(config_frame, width=10, font=("Helvetica", 11)); self.sip_port.insert(0, "5060"); self.sip_port.grid(row=0, column=3, padx=10, pady=5)

        ttk.Label(config_frame, text="SIP User:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.sip_user = ttk.Entry(config_frame, width=30, font=("Helvetica", 11)); self.sip_user.insert(0, "supersploit_user"); self.sip_user.grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(config_frame, text="SIP Pass:").grid(row=1, column=2, sticky=tk.W, padx=10, pady=5)
        self.sip_pass = ttk.Entry(config_frame, width=25, show="*", font=("Helvetica", 11)); self.sip_pass.insert(0, "password"); self.sip_pass.grid(row=1, column=3, padx=10, pady=5)

        # --- 2. Voice Generation (Mimic) ---
        voice_frame = ttk.LabelFrame(main_frame, text=" 🎭 Mimic Voice Generator ", padding="15")
        voice_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(voice_frame, text="Script:").pack(anchor=tk.W, padx=5, pady=(0, 5))
        self.script_text = tk.Text(voice_frame, height=5, font=("Helvetica", 11), bg="#313244", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT, padx=10, pady=10)
        self.script_text.insert(tk.END, "Hello, this is security from your bank. We have detected unauthorized activity. Please verify your identity.")
        self.script_text.pack(fill=tk.X, pady=5, expand=True)

        gen_btn_frame = ttk.Frame(voice_frame)
        gen_btn_frame.pack(fill=tk.X)
        ttk.Button(gen_btn_frame, text="🔊 Generate TTS Audio", command=self._generate_audio).pack(side=tk.LEFT, padx=5)
        ttk.Button(gen_btn_frame, text="📂 Load Custom WAV", command=self._browse_audio).pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(gen_btn_frame, text="No audio file loaded", foreground="#ff5555")
        self.file_label.pack(side=tk.LEFT, padx=10)

        # --- 3. Target & Execution ---
        target_frame = ttk.LabelFrame(main_frame, text=" 🎯 Target ", padding="15")
        target_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(target_frame, text="Recipient Number:").pack(side=tk.LEFT, padx=10, pady=5)
        self.target_num = ttk.Entry(target_frame, width=30, font=("Helvetica", 11)); self.target_num.insert(0, "15551234567"); self.target_num.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        # --- Action Banner Button ---
        self.call_btn = ttk.Button(main_frame, text="📞 INITIATE VISHING CALL", command=self._start_call)
        self.call_btn.pack(fill=tk.X, pady=(0, 10))

        # --- 4. Live Console ---
        console_frame = ttk.LabelFrame(main_frame, text=" 🖥️ Call Session Log ", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(console_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

        if not has_gtts:
            self.log("[-] WARNING: gTTS not installed. TTS generation disabled. Please 'pip install gTTS'.")

    def log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        def _update():
            self.console.insert(tk.END, f"[{timestamp}] {msg}\n")
            self.console.see(tk.END)
        self.root.after(0, _update)

    def _browse_audio(self):
        filename = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if filename:
            self.audio_path.set(filename)
            self.file_label.config(text=f"Loaded: {os.path.basename(filename)}", foreground="green")

    def _generate_audio(self):
        if not has_gtts:
            messagebox.showerror("Error", "gTTS is required for voice generation.")
            return
        
        script = self.script_text.get(1.0, tk.END).strip()
        if not script: return

        self.log("[*] Generating voice payload...")
        def run():
            try:
                tts = gTTS(text=script, lang='en')
                temp_path = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "mimic_voice.mp3")
                tts.save(temp_path)
                self.root.after(0, lambda: self.audio_path.set(temp_path))
                self.root.after(0, lambda: self.file_label.config(text="Loaded: Generated Voice", foreground="green"))
                self.root.after(0, lambda: self.log("[+] Voice generation complete."))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"[-] TTS Error: {e}"))
        
        threading.Thread(target=run, daemon=True).start()

    def _start_call(self):
        if not self.audio_path.get():
            messagebox.showwarning("Warning", "Load or generate an audio payload first.")
            return
        
        self.call_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._call_logic, daemon=True).start()

    def _call_logic(self):
        try:
            client = SIPClient(
                self.sip_server.get(),
                self.sip_port.get(),
                self.sip_user.get(),
                self.sip_pass.get()
            )
            client.make_call(
                self.target_num.get(),
                audio_file=self.audio_path.get(),
                log_callback=self.log
            )
        finally:
            self.root.after(0, lambda: self.call_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    if not LicenseManager.gate_access("Deepfake Vishing Suite"):
        sys.exit(1)
    root = tk.Tk()
    app = VishingMimicGUI(root)
    root.mainloop()
