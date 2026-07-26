import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import time
import hashlib
import webbrowser
import io

try:
    import requests
    HAS_REQ = True
except ImportError:
    HAS_REQ = False

try:
    from PIL import Image, ImageTk, ExifTags
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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

class ReverseImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Advanced Reverse Image OSINT")
        self.root.geometry("850x650")
        
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
        
        # Button Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.image_path = None
        
        # Dictionary to store {sha256_hash: staged_url} for instant re-queries
        self.session_cache = {}
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top Section: Image Selection & Preview
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        preview_frame = ttk.LabelFrame(top_frame, text=" 🖼️ Target Intelligence Image ", padding="15")
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.preview_lbl = ttk.Label(preview_frame, text="No Image Selected", anchor=tk.CENTER)
        self.preview_lbl.pack(fill=tk.BOTH, expand=True, pady=10)
        
        btn_sel = ttk.Button(preview_frame, text="📁 BROWSE IMAGE", command=self._browse_image)
        btn_sel.pack(pady=(0, 10))

        # Engines Selection
        engine_frame = ttk.LabelFrame(top_frame, text=" 🔍 OSINT Correlation Engines ", padding="15")
        engine_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.chk_google = tk.BooleanVar(value=True)
        self.chk_yandex = tk.BooleanVar(value=True)
        self.chk_bing = tk.BooleanVar(value=True)
        self.chk_tineye = tk.BooleanVar(value=True)
        self.chk_saucenao = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(engine_frame, text="Google Lens (Locations/Objects/Products)", variable=self.chk_google).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(engine_frame, text="Yandex (Facial Recognition / Deep Web)", variable=self.chk_yandex).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(engine_frame, text="Bing Visual Search (General Web Correlation)", variable=self.chk_bing).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(engine_frame, text="TinEye (Historical Image Tracking)", variable=self.chk_tineye).pack(anchor=tk.W, pady=5)
        ttk.Checkbutton(engine_frame, text="SauceNAO (Digital Art / Image Boards)", variable=self.chk_saucenao).pack(anchor=tk.W, pady=5)

        # Action Banner Button
        self.scan_btn = ttk.Button(main_frame, text="🚀 EXECUTE MULTI-ENGINE REVERSE SEARCH", command=self._start_search)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 📜 Operation Telemetry ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        def _update():
            self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.console.see(tk.END)
        self.root.after(0, _update)

    def _browse_image(self):
        f = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if f:
            self.image_path = f
            self.log(f"[*] Selected Target Image: {os.path.basename(f)}")
            if HAS_PIL:
                try:
                    img = Image.open(f)
                    img.thumbnail((250, 250))
                    photo = ImageTk.PhotoImage(img)
                    self.preview_lbl.config(image=photo, text="")
                    self.preview_lbl.image = photo
                except Exception as e:
                    self.preview_lbl.config(text="Preview Unavailable")
                    self.log(f"[-] Preview error: {e}")
            else:
                self.preview_lbl.config(text=os.path.basename(f))

    def _start_search(self):
        if not self.image_path or not os.path.exists(self.image_path):
            messagebox.showerror("Error", "Please select a valid image file first.")
            return
            
        if not HAS_REQ:
            messagebox.showerror("Dependency Error", "Missing 'requests' library. Run: pip install requests")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.console.delete(1.0, tk.END)
        threading.Thread(target=self._search_thread, daemon=True).start()

    def _search_thread(self):
        self.log("[*] Initializing Reverse Image OSINT Operation...")
        
        file_name = os.path.basename(self.image_path)
        file_bytes = None

        # 1. Local Hashing
        try:
            with open(self.image_path, "rb") as f:
                orig_bytes = f.read()
                md5_hash = hashlib.md5(orig_bytes).hexdigest()
                sha256_hash = hashlib.sha256(orig_bytes).hexdigest()
            self.log(f"[+] Local Image MD5: {md5_hash}")
            self.log(f"[+] Local Image SHA-256: {sha256_hash}")
        except Exception as e:
            self.log(f"[-] Hashing failed: {e}")

        # 1.2. EXIF & Perceptual Hashing (dHash)
        if HAS_PIL:
            self.log("[*] Analyzing image for embedded EXIF & visual fingerprints...")
            exif_found = False
            try:
                with Image.open(self.image_path) as img:
                    # Visual Fingerprinting (dHash)
                    gray = img.convert('L').resize((9, 8))
                    pixels = list(gray.getdata())
                    diff = [pixels[row*9 + col] > pixels[row*9 + col + 1] for row in range(8) for col in range(8)]
                    dhash_val = sum([2 ** i for (i, v) in enumerate(diff) if v])
                    self.log(f"[+] Visual dHash: {hex(dhash_val)[2:].rjust(16, '0')}")

                    # EXIF Extraction
                    exif = img._getexif()
                    if exif:
                        for tag_id, value in exif.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            if tag in ['GPSInfo', 'DateTimeOriginal', 'Make', 'Model', 'Software']:
                                self.log(f"    [!] EXIF {tag}: {value}")
                                exif_found = True
            except Exception as e:
                self.log(f"[-] Advanced parsing error: {e}")
                
            if not exif_found:
                self.log("    [-] No critical EXIF location/device data found (or stripped).")

        # 1.3 Session Caching Check
        staged_url = self.session_cache.get(sha256_hash)
        if staged_url:
            self.log("[*] Image hash matched in local session cache! Skipping re-upload.")
            self.log(f"[+] Cached URL: {staged_url}")
            
        if not staged_url:
            # 1.5. Compression & Optimization
            if HAS_PIL:
                self.log("[*] Compressing and optimizing image for upload...")
                try:
                    with Image.open(self.image_path) as img:
                        # Ensure format is RGB (drops alpha channels from PNGs for JPEG support)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        img.thumbnail((1920, 1920)) # Aggressively downscale massive photos
                        
                        img_byte_arr = io.BytesIO()
                        img.save(img_byte_arr, format='JPEG', quality=65, optimize=True)
                        file_bytes = img_byte_arr.getvalue()
                        
                        file_name = os.path.splitext(file_name)[0] + ".jpg"
                        self.log(f"[+] Image compressed to {len(file_bytes) / 1024:.2f} KB")
                except Exception as e:
                    self.log(f"[-] Compression failed: {e}. Using original file.")
    
            mime_type = "image/jpeg"
            if not file_bytes:
                with open(self.image_path, "rb") as f:
                    file_bytes = f.read()
                import mimetypes
                mime_type = mimetypes.guess_type(self.image_path)[0] or "application/octet-stream"
    
            # 2. Ephemeral Staging
            self.log("[*] Staging image securely to ephemeral dump server...")
            
            # Anti-WAF Headers to bypass Cloudflare 412 errors
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Origin": "https://catbox.moe"
            }
            
            # Redundant Staging Architectures
            hosts = [
                {
                    "name": "Uguu.se",
                    "url": "https://uguu.se/upload.php",
                    "data": {},
                    "files": {"files[]": (file_name, file_bytes, mime_type)},
                    "parse": lambda r: r.json()["files"][0]["url"] if r.json().get("success") else None
                },
                {
                    "name": "Litterbox",
                    "url": "https://litterbox.catbox.moe/user/api.php",
                    "data": {"reqtype": "fileupload", "time": "1h"},
                    "files": {"fileToUpload": (file_name, file_bytes, mime_type)},
                    "parse": lambda r: r.text.strip() if r.text.startswith("http") else None
                },
                {
                    "name": "Catbox.moe",
                    "url": "https://catbox.moe/user/api.php",
                    "data": {"reqtype": "fileupload"},
                    "files": {"fileToUpload": (file_name, file_bytes, mime_type)},
                    "parse": lambda r: r.text.strip() if r.text.startswith("http") else None
                },
                {
                    "name": "0x0.st",
                    "url": "https://0x0.st",
                    "data": {},
                    "files": {"file": (file_name, file_bytes, mime_type)},
                    "parse": lambda r: r.text.strip() if r.text.startswith("http") else None
                }
            ]
            
            try:
                for host in hosts:
                    self.log(f"[*] Attempting staging via {host['name']}...")
                    try:
                        resp = requests.post(host["url"], data=host["data"], files=host["files"], headers=headers, timeout=15)
                        if resp.status_code == 200:
                            try:
                                result = host["parse"](resp)
                                if result:
                                    staged_url = result
                                    break
                            except Exception:
                                self.log(f"[-] {host['name']} response parsing failed.")
                        else:
                            self.log(f"[-] {host['name']} rejected payload (HTTP {resp.status_code}).")
                    except Exception as e:
                        # Clean up ugly urllib3 tracebacks for the UI
                        err_repr = repr(e).lower()
                        if "timeout" in err_repr:
                            err_msg = "Connection timed out."
                        elif "101" in err_repr or "unreachable" in err_repr:
                            err_msg = "Network is unreachable (Blocked by ISP/VPN)."
                        else:
                            err_msg = "Connection dropped."
                        self.log(f"[!] {host['name']} connection failed: {err_msg}")
    
                if staged_url:
                    self.session_cache[sha256_hash] = staged_url
                    self.log(f"[+] Image successfully staged at: {staged_url}")
                else:
                    self.log("[-] Staging failed. All ephemeral hosts rejected the payload.")
                    self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
                    return
            except Exception as e:
                self.log(f"[-] Connection to staging server failed: {e}")
                self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
                return

        # 3. Correlation Execution
        self.log("[*] Constructing dynamic OSINT queries...")
        
        urls_to_open = []
        if self.chk_google.get():
            urls_to_open.append(f"https://lens.google.com/uploadbyurl?url={staged_url}")
        if self.chk_yandex.get():
            urls_to_open.append(f"https://yandex.com/images/search?rpt=imageview&url={staged_url}")
        if self.chk_bing.get():
            urls_to_open.append(f"https://www.bing.com/images/search?q=imgurl:{staged_url}&view=detailv2&iss=sbi")
        if self.chk_tineye.get():
            urls_to_open.append(f"https://tineye.com/search?url={staged_url}")
        if getattr(self, 'chk_saucenao', None) and self.chk_saucenao.get():
            urls_to_open.append(f"https://saucenao.com/search.php?db=999&url={staged_url}")

        if not urls_to_open:
            self.log("[-] No OSINT engines selected.")
        else:
            self.log("[+] Launching search queries in default browser...")
            for url in urls_to_open:
                webbrowser.open(url)
                time.sleep(0.5) # Prevent browser from choking on rapid tab opening
            
        self.log("\n[+] Operation Complete. Review your browser tabs for intelligence matches.")
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    if not LicenseManager.gate_access("Reverse Image OSINT Suite"): sys.exit(1)
    root = tk.Tk()
    app = ReverseImageGUI(root)
    root.mainloop()