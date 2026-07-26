import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading
import os
import sys
import time
import re
import subprocess
import shutil
import xml.etree.ElementTree as ET
import queue

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


class APKSastGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit APK SAST Scanner")
        self.root.geometry("850x700")

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

        self.log_queue = queue.Queue()
        self._build_ui()
        self._flush_logs()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Target Config
        tgt_frame = ttk.LabelFrame(main_frame, text=" 📂 Target Selection (APK or Decompiled Dir) ", padding="15")
        tgt_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(tgt_frame, text="Raw APK File (.apk):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.apk_path_entry = ttk.Entry(tgt_frame, width=45, font=("Helvetica", 11))
        self.apk_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Button(tgt_frame, text="📄 BROWSE APK", command=self._browse_apk).grid(row=0, column=2, padx=10, pady=5)

        ttk.Label(tgt_frame, text="OR Decompiled Dir:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.target_dir = ttk.Entry(tgt_frame, width=45, font=("Helvetica", 11))
        self.target_dir.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Button(tgt_frame, text="📁 BROWSE DIR", command=self._browse_dir).grid(row=1, column=2, padx=10, pady=5)

        # Scan Options
        opt_frame = ttk.LabelFrame(main_frame, text=" 🔍 Analysis Modules ", padding="15")
        opt_frame.pack(fill=tk.X, pady=(0, 10))

        self.chk_manifest = tk.BooleanVar(value=True)
        self.chk_secrets = tk.BooleanVar(value=True)
        self.chk_crypto = tk.BooleanVar(value=True)
        self.chk_network = tk.BooleanVar(value=True)

        ttk.Checkbutton(opt_frame, text="Manifest Analysis (Exported Components, Debug, Backup)",
                        variable=self.chk_manifest).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Checkbutton(opt_frame, text="Hardcoded Secrets (AWS, Google API, JWTs)", variable=self.chk_secrets).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Checkbutton(opt_frame, text="Weak Cryptography (MD5, DES, AES/ECB)", variable=self.chk_crypto).grid(row=0,
                                                                                                                column=1,
                                                                                                                sticky=tk.W,
                                                                                                                pady=5,
                                                                                                                padx=20)
        ttk.Checkbutton(opt_frame, text="Insecure Network Configs (Cleartext HTTP)", variable=self.chk_network).grid(
            row=1, column=1, sticky=tk.W, pady=5, padx=20)

        # Actions
        self.scan_btn = ttk.Button(main_frame, text="🚀 EXECUTE SAST PIPELINE", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 📜 Vulnerability Report ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.log_queue.put(msg)
        
    def _flush_logs(self):
        messages = []
        try:
            for _ in range(100): # Process in batches to prevent UI queue flooding
                messages.append(self.log_queue.get_nowait())
        except queue.Empty:
            pass
            
        if messages:
            self.console.insert(tk.END, "\n".join(messages) + "\n")
            self.console.see(tk.END)
            
        self.root.after(100, self._flush_logs)

    def _browse_apk(self):
        f = filedialog.askopenfilename(filetypes=[("APK Files", "*.apk")])
        if f:
            self.apk_path_entry.delete(0, tk.END)
            self.apk_path_entry.insert(0, f)

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.target_dir.delete(0, tk.END)
            self.target_dir.insert(0, d)

    def _start_scan(self):
        # SECURE DRM CHECK: Ensure execution is gated at the action level, not the import/launch level
        if not LicenseManager.gate_access("APK SAST Scanner"):
            messagebox.showerror("License Invalid", "This action requires an active SuperSploit Pro license.")
            return

        apk_path = self.apk_path_entry.get().strip()
        target = self.target_dir.get().strip()

        if not apk_path and not target:
            messagebox.showerror("Error", "Please provide either a raw APK file or a decompiled directory.")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.console.delete(1.0, tk.END)
        threading.Thread(target=self._scan_thread, args=(apk_path, target), daemon=True).start()

    def _scan_thread(self, apk_path, target):
        self.log(f"[*] Initializing SAST Pipeline...")
        self.log(f"[*] Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("-" * 60)

        # Decompilation Phase
        if apk_path and os.path.isfile(apk_path) and apk_path.endswith('.apk'):
            self.log(f"[*] Raw APK detected: {os.path.basename(apk_path)}")
            self.log("[*] Engaging Apktool for dynamic decompilation...")

            workspace_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "sast_workspace")
            os.makedirs(workspace_dir, exist_ok=True)
            out_dir = os.path.join(workspace_dir, os.path.basename(apk_path).replace(".apk", "_decompiled"))

            if shutil.which("apktool"):
                try:
                    self.log(f"[*] Decompiling to: {out_dir}")
                    self.log("[*] Please wait, this may take a minute...")

                    process = subprocess.Popen(["apktool", "d", "-f", apk_path, "-o", out_dir],
                                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    for line in iter(process.stdout.readline, ''):
                        if "I:" in line or "W:" in line:
                            self.log(f"    {line.strip()}")
                    process.wait()

                    if process.returncode == 0:
                        self.log("[+] APK Decompilation Successful.")
                        target = out_dir
                    else:
                        self.log("[-] Apktool encountered an error.")
                        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
                        return
                except Exception as e:
                    self.log(f"[-] Decompilation failed: {e}")
                    self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
                    return
            else:
                self.log("[-] Apktool is not installed or not in PATH. Cannot decompile.")
                self.log("[!] Run: sudo apt install apktool")
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
                return

        if not target or not os.path.isdir(target):
            self.log("[-] Invalid analysis directory. Aborting.")
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
            return

        self.log(f"\n[*] Commencing Static Analysis on: {target}")

        if self.chk_manifest.get():
            self._analyze_manifest(target)

        if self.chk_secrets.get() or self.chk_crypto.get() or self.chk_network.get():
            self._grep_smali(target)

        self.log("-" * 60)
        self.log("[+] SAST Scan Complete.")
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def _analyze_manifest(self, target):
        manifest_path = os.path.join(target, "AndroidManifest.xml")
        if not os.path.exists(manifest_path):
            self.log("[-] AndroidManifest.xml not found. Skipping Manifest Analysis.")
            return

        self.log("\n[📌] Manifest Analysis:")
        try:
            tree = ET.parse(manifest_path)
            root = tree.getroot()
            ns = {'android': 'http://schemas.android.com/apk/res/android'}
            package_name = root.attrib.get('package', '')

            app = root.find('application')
            if app is not None:
                # Debuggable
                if app.attrib.get(f"{{{ns['android']}}}debuggable") == "true":
                    self.log("  [CRITICAL] Application is Debuggable (android:debuggable=\"true\")")

                # Allow Backup
                if app.attrib.get(f"{{{ns['android']}}}allowBackup") == "true":
                    self.log("  [HIGH] Application allows ADB backups (android:allowBackup=\"true\")")

                # Cleartext Traffic
                if app.attrib.get(f"{{{ns['android']}}}usesCleartextTraffic") == "true":
                    self.log("  [MEDIUM] Cleartext HTTP traffic allowed (android:usesCleartextTraffic=\"true\")")

                # Network Security Config Analysis (Android 9+)
                nsc = app.attrib.get(f"{{{ns['android']}}}networkSecurityConfig")
                if nsc:
                    self.log(f"  [INFO] Network Security Config found: {nsc}")
                    if nsc.startswith("@xml/"):
                        xml_file = nsc.replace("@xml/", "") + ".xml"
                        nsc_path = os.path.join(target, "res", "xml", xml_file)
                        if os.path.exists(nsc_path):
                            try:
                                nsc_tree = ET.parse(nsc_path)
                                nsc_root = nsc_tree.getroot()
                                base_config = nsc_root.find('base-config')
                                if base_config is not None and base_config.attrib.get("cleartextTrafficPermitted") == "true":
                                    self.log(f"  [MEDIUM] Cleartext HTTP permitted in base-config ({xml_file})")
                                for trust_anchor in nsc_root.findall('.//trust-anchors/certificates'):
                                    if trust_anchor.attrib.get("src") == "user":
                                        self.log(f"  [LOW] App trusts user-installed certificates ({xml_file})")
                            except Exception as e:
                                self.log(f"  [-] Failed to parse Network Security Config: {e}")

            # Exported Components (Including Implicit Exports)
            for comp_type in ['activity', 'service', 'receiver', 'provider']:
                for comp in app.findall(comp_type):
                    exported = comp.attrib.get(f"{{{ns['android']}}}exported")
                    name = comp.attrib.get(f"{{{ns['android']}}}name", "Unknown")

                    # Detect Implicit Exports (Pre-Android 12 behavior)
                    has_intent_filter = comp.find('intent-filter') is not None
                    is_exported = False

                    if exported == "true":
                        is_exported = True
                    elif exported is None and has_intent_filter:
                        is_exported = True
                        self.log(f"  [WARNING] Implicitly exported component detected (Pre-Android 12): {name}")

                    if is_exported:
                        perm = comp.attrib.get(f"{{{ns['android']}}}permission")
                        if not perm:
                            # Map to smali path for operator convenience
                            full_name = name
                            if name.startswith('.'):
                                full_name = package_name + name
                            elif package_name and not name.startswith(package_name):
                                full_name = package_name + "." + name
                            smali_path = "smali*/" + full_name.replace('.', '/') + ".smali"
                            self.log(f"  [HIGH] Exported {comp_type.capitalize()} without permission check: {name}\n      -> Map: {smali_path}")
        except Exception as e:
            self.log(f"  [-] Failed to parse manifest: {e}")

    def _grep_smali(self, target):
        self.log("\n[🧬] Code & Resource Analysis:")

        patterns = []
        if self.chk_secrets.get():
            patterns.extend([
                (r'AKIA[0-9A-Z]{16}', "[CRITICAL] Possible AWS Access Key"),
                (r'AIza[0-9A-Za-z\-_]{35}', "[HIGH] Possible Google API Key"),
                (r'ey[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*', "[HIGH] Possible JWT Token")
            ])
        if self.chk_crypto.get():
            patterns.extend([
                (r'const-string\s+[vp]\d+,\s+"AES/ECB/.*?[\s\S]{1,1500}Ljavax/crypto/Cipher;->getInstance', "[MEDIUM] Weak Cryptography Executed (AES ECB Mode)"),
                (r'const-string\s+[vp]\d+,\s+"MD5"[\s\S]{1,1500}Ljava/security/MessageDigest;->getInstance', "[MEDIUM] Weak Cryptography Executed (MD5 Hashing)"),
                (r'const-string\s+[vp]\d+,\s+"DES"[\s\S]{1,1500}Ljavax/crypto/Cipher;->getInstance', "[MEDIUM] Weak Cryptography Executed (DES)")
            ])
        if self.chk_network.get():
            # Applied Negative Lookahead to filter out standard schemas to reduce false positives
            patterns.append((r'http://(?!schemas\.android|www\.w3\.org|purl\.org)[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}',
                             "[LOW] Cleartext HTTP URL Hardcoded"))

        compiled_patterns = [(re.compile(p[0]), p[1]) for p in patterns]

        search_dirs = [os.path.join(target, "res", "values")]
        if os.path.exists(target):
            for d in os.listdir(target):
                if d.startswith("smali") and os.path.isdir(os.path.join(target, d)):
                    search_dirs.append(os.path.join(target, d))

        for s_dir in search_dirs:
            if not os.path.exists(s_dir): continue
            for root_dir, _, files in os.walk(s_dir):
                for file in files:
                    if not file.endswith(".smali") and not file.endswith(".xml"): continue
                    file_path = os.path.join(root_dir, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            for regex, desc in compiled_patterns:
                                matches = regex.findall(content)
                                for match in set(matches):
                                    rel_path = os.path.relpath(file_path, target)
                                    self.log(f"  {desc} -> {match}\n      File: {rel_path}")
                    except Exception:
                        pass


if __name__ == "__main__":
    # DRM check removed from import level. UI runs, action is gated.
    root = tk.Tk()
    app = APKSastGUI(root)
    root.mainloop()