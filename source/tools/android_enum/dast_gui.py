# TODO: add 'frida-tools' to requirements.txt

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
import os
import time

try:
    import frida

    HAS_FRIDA = True
except ImportError:
    HAS_FRIDA = False

try:
    from source.core.license_manager import LicenseManager
    from source.core.payload_dict import FRIDA_PAYLOADS
except ImportError:
    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)
    try:
        from source.core.license_manager import LicenseManager
        from source.core.payload_dict import FRIDA_PAYLOADS
    except ImportError:
        FRIDA_PAYLOADS = {"None": ""}
        class LicenseManager:
            @staticmethod
            def gate_access(f):
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False


class APKDastGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit APK DAST Scanner (Dynamic Analysis)")
        self.root.geometry("850x750")
        
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
        
        # Button, Entry & Combobox Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")
        self.style.configure("TCombobox", fieldbackground="#313244", foreground="#ffffff", background=self.bg_sec, borderwidth=0, arrowcolor=self.fg_main)
        self.style.map("TCombobox", fieldbackground=[("readonly", "#313244")], selectbackground=[("readonly", self.accent)], selectforeground=[("readonly", "#ffffff")])
        
        self.session = None
        self.script = None
        self.is_running = False
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Target Config
        tgt_frame = ttk.LabelFrame(main_frame, text=" 🎯 Target Application ", padding="15")
        tgt_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(tgt_frame, text="Package Name (e.g., com.target.app):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.target_pkg = ttk.Entry(tgt_frame, width=45, font=("Helvetica", 11))
        self.target_pkg.insert(0, "com.android.chrome")
        self.target_pkg.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Dynamic Hooks
        opt_frame = ttk.LabelFrame(main_frame, text=" 🪝 Dynamic Instrumentation Hooks ", padding="15")
        opt_frame.pack(fill=tk.X, pady=(0, 10))

        self.chk_crypto = tk.BooleanVar(value=True)
        self.chk_network = tk.BooleanVar(value=True)
        self.chk_intents = tk.BooleanVar(value=True)

        ttk.Checkbutton(opt_frame, text="Intercept Cryptography (Dump AES/DES Keys)", variable=self.chk_crypto).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Checkbutton(opt_frame, text="Intercept Network (java.net.URL & OkHttp3)", variable=self.chk_network).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Checkbutton(opt_frame, text="Sniff Android Intents (Activity Monitoring)", variable=self.chk_intents).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=20)

        if not HAS_FRIDA:
            ttk.Label(opt_frame, text="⚠️ 'frida' missing! Run: pip install frida-tools", foreground="#ff5555").grid(
                row=1, column=1, sticky=tk.W, padx=20)
                
        # Custom Payload Config
        custom_frame = ttk.LabelFrame(main_frame, text=" 💉 Custom Frida Payload ", padding="15")
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(custom_frame, text="Select Module:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.payload_combo = ttk.Combobox(custom_frame, values=list(FRIDA_PAYLOADS.keys()), state="readonly", width=55, font=("Helvetica", 11))
        self.payload_combo.set("None" if "None" in FRIDA_PAYLOADS else list(FRIDA_PAYLOADS.keys())[0])
        self.payload_combo.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # Actions
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = ttk.Button(btn_frame, text="🚀 SPAWN & HOOK", command=self._start_dast)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.stop_btn = ttk.Button(btn_frame, text="🛑 DETACH", command=self._stop_dast, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 📜 Live Execution Telemetry ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        def _update():
            # Clean output formatting
            timestamp = time.strftime("[%H:%M:%S]")
            self.console.insert(tk.END, f"{timestamp} {msg}\n")
            self.console.see(tk.END)

        self.root.after(0, _update)

    def _on_message(self, message, data):
        if message['type'] == 'send':
            self.log(message['payload'])
        elif message['type'] == 'error':
            self.log(f"[FRIDA ERROR] {message['description']}")

    def _build_frida_script(self):
        script = "Java.perform(function() {\n"
        script += "    console.log('[*] Frida Agent successfully injected into Dalvik/ART runtime.');\n"

        # Helper to convert signed Java bytes to Hex string safely
        script += """
            function bytesToHex(arr) {
                var hex = '';
                for (var i = 0; i < arr.length; i++) {
                    var v = (arr[i] & 0xFF).toString(16);
                    hex += (v.length === 1 ? '0' : '') + v;
                }
                return hex;
            }
        """

        if self.chk_crypto.get():
            script += """
            try {
                var SecretKeySpec = Java.use('javax.crypto.spec.SecretKeySpec');
                SecretKeySpec.$init.overload('[B', 'java.lang.String').implementation = function(key, algo) {
                    send("[🔑 CRYPTO] Key Initialized (" + algo + "). Raw Hex: " + bytesToHex(key));
                    this.$init(key, algo); // Corrected: Do not return from a constructor
                };
            } catch (e) { send("[-] Crypto hook failed: " + e); }
            """

        if self.chk_network.get():
            script += """
            // Hook standard URL connections
            try {
                var URL = Java.use('java.net.URL');
                URL.$init.overload('java.lang.String').implementation = function(url) {
                    send("[🌐 NETWORK] Outbound Request (java.net.URL): " + url);
                    this.$init(url); // Corrected: Do not return from constructor
                };
            } catch (e) { send("[-] java.net.URL hook failed: " + e); }

            // Hook OkHttp3 Request Builder
            try {
                var Builder = Java.use('okhttp3.Request$Builder');
                Builder.url.overload('java.lang.String').implementation = function(url) {
                    send("[🌐 NETWORK] Outbound Request (OkHttp3): " + url);
                    return this.url(url); // Builder returns itself
                };
            } catch (e) { /* OkHttp3 might not be in the app, ignore silently */ }
            """

        if self.chk_intents.get():
            script += """
            try {
                var Intent = Java.use('android.content.Intent');
                var Activity = Java.use('android.app.Activity');
                Activity.startActivity.overload('android.content.Intent').implementation = function(intent) {
                    send("[🚀 INTENT] Activity Started: " + intent.toUri(0));
                    return this.startActivity(intent);
                };
            } catch (e) { send("[-] Intent hook failed: " + e); }
            """

        script += "});\n"
        
        # Dynamically append custom user JS from centralized dictionary
        selected_payload = self.payload_combo.get()
        if selected_payload and selected_payload != "None" and selected_payload in FRIDA_PAYLOADS:
            script += "\n// === CUSTOM USER SCRIPT ===\n"
            script += FRIDA_PAYLOADS[selected_payload]
            script += "\n// === END CUSTOM SCRIPT ===\n"
            self.log(f"[+] Successfully injected custom JS module: {selected_payload}")
                
        return script

    def _start_dast(self):
        # SECURE DRM CHECK: Execute authorization strictly when the user attempts an operation
        if not LicenseManager.gate_access("APK DAST Scanner"):
            messagebox.showerror("License Invalid", "This action requires an active SuperSploit Pro license.")
            return

        if not HAS_FRIDA:
            messagebox.showerror("Dependency Error", "Frida is not installed. Please run: pip3 install frida-tools")
            return

        target = self.target_pkg.get().strip()
        if not target: return

        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.is_running = True

        threading.Thread(target=self._dast_thread, args=(target,), daemon=True).start()

    def _dast_thread(self, target):
        self.log(f"[*] Locating USB Device...")
        try:
            device = frida.get_usb_device()
            self.log(f"[+] Device connected: {device.name}")

            self.log(f"[*] Spawning package: {target}...")
            pid = device.spawn([target])
            self.session = device.attach(pid)

            self.log("[*] Compiling dynamic instrumentation payload...")
            js_code = self._build_frida_script()

            self.script = self.session.create_script(js_code)
            self.script.on('message', self._on_message)
            self.script.load()

            self.log("[*] Resuming main thread...")
            device.resume(pid)

        except Exception as e:
            self.log(f"[-] DAST Engine Error: {e}")
            self.log("[!] Ensure the device is connected over USB and frida-server is running as root.")
            self.root.after(0, self._stop_dast)

    def _stop_dast(self):
        self.is_running = False
        if self.session:
            try:
                self.session.detach()
            except:
                pass
        self.log("[-] Detached from target application.")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)


if __name__ == "__main__":
    # DRM check removed from here. The UI will launch, but the 'Spawn & Hook'
    # button is now properly protected by the LicenseManager.
    root = tk.Tk()
    app = APKDastGUI(root)
    root.mainloop()

# === TOOL_META ===
# name: APK DAST Scanner (Frida)
# description: Dynamic Analysis UI utilizing Frida to spawn Android applications, hooking memory in real-time to intercept cryptographic keys, network traffic, and Intents.
# author: Donald Ford
# category: tool
# keywords: [dast, frida, android, dynamic, analysis, hooking, crypto, network, intents, apk]
# root: true
# =================