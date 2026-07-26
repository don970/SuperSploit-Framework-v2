import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import time
import re
import zipfile
import xml.etree.ElementTree as ET
import csv

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import PyPDF2
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

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

class DeepMetadataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Deep Metadata & IOC Scraper")
        self.root.geometry("900x700")
        
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
        
        # Entry Styling
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")
        
        # Treeview (Tables) Styling
        self.style.configure("Treeview", background=self.bg_main, foreground=self.fg_main, fieldbackground=self.bg_main, borderwidth=0, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent)], foreground=[('selected', '#ffffff')])

        self.results = []

        self.IOC_REGEX = {
            "IPv4 Address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "Email Address": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
            "Domain": r'(?i)\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:com|net|org|io|gov|mil|edu)\b',
            "AWS Access Key": r'AKIA[0-9A-Z]{16}',
            "Google API Key": r'AIza[0-9A-Za-z\-_]{35}'
        }

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Target Selection
        tgt_frame = ttk.LabelFrame(main_frame, text=" 📂 Target Selection ", padding="15")
        tgt_frame.pack(fill=tk.X, pady=(0, 10))

        self.target_path = ttk.Entry(tgt_frame, width=60, font=("Helvetica", 11))
        self.target_path.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X, expand=True)

        ttk.Button(tgt_frame, text="📄 FILE", command=self._browse_file).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(tgt_frame, text="📁 FOLDER", command=self._browse_dir).pack(side=tk.LEFT, padx=5, pady=5)

        # Scan Options
        opt_frame = ttk.LabelFrame(main_frame, text=" 🔬 Extraction Engines ", padding="15")
        opt_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.chk_exif = tk.BooleanVar(value=True)
        self.chk_docs = tk.BooleanVar(value=True)
        self.chk_iocs = tk.BooleanVar(value=True)

        ttk.Checkbutton(opt_frame, text="EXIF & GPS Data (Images)", variable=self.chk_exif).grid(row=0, column=0, sticky=tk.W, pady=5, padx=10)
        ttk.Checkbutton(opt_frame, text="Hidden Properties (PDF/Office)", variable=self.chk_docs).grid(row=0, column=1, sticky=tk.W, pady=5, padx=20)
        ttk.Checkbutton(opt_frame, text="Deep Binary IOC Hunter (Strings/Regex)", variable=self.chk_iocs).grid(row=0, column=2, sticky=tk.W, pady=5, padx=20)

        # Action Banner Button
        self.scan_btn = ttk.Button(main_frame, text="🚀 START EXTRACTION", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Actions Frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        self.export_btn = ttk.Button(action_frame, text="💾 EXPORT TO CSV", command=self._export_csv, state=tk.DISABLED)
        self.export_btn.pack(side=tk.RIGHT)

        # Results Treeview
        log_frame = ttk.LabelFrame(main_frame, text=" 📊 Intelligence Report ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("File", "Category", "Data / Value")
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.tag_configure('oddrow', background=self.bg_main)
        self.tree.tag_configure('evenrow', background=self.bg_sec)
        
        self.tree.heading("File", text="File Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Data / Value", text="Extracted Data / Value")

        self.tree.column("File", width=200, anchor=tk.W)
        self.tree.column("Category", width=150, anchor=tk.W)
        self.tree.column("Data / Value", width=400, anchor=tk.W)

        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _browse_file(self):
        f = filedialog.askopenfilename()
        if f:
            self.target_path.delete(0, tk.END)
            self.target_path.insert(0, f)

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.target_path.delete(0, tk.END)
            self.target_path.insert(0, d)

    def _add_result(self, filename, category, value):
        self.results.append((filename, category, value))
        def _update():
            count = len(self.tree.get_children())
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=(filename, category, value), tags=(tag,))
            self.tree.yview_moveto(1)
        self.root.after(0, _update)

    def _start_scan(self):
        target = self.target_path.get().strip()
        if not os.path.exists(target):
            messagebox.showerror("Error", "Target path does not exist.")
            return

        self.scan_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results.clear()

        threading.Thread(target=self._scan_thread, args=(target,), daemon=True).start()

    def _scan_thread(self, target):
        files_to_scan = []
        if os.path.isfile(target):
            files_to_scan.append(target)
        else:
            for root_dir, _, files in os.walk(target):
                for f in files:
                    files_to_scan.append(os.path.join(root_dir, f))

        for file_path in files_to_scan:
            filename = os.path.basename(file_path)
            ext = filename.lower().split('.')[-1]

            if self.chk_exif.get() and ext in ['jpg', 'jpeg', 'png', 'tiff']:
                self._extract_exif(file_path, filename)

            if self.chk_docs.get():
                if ext == 'pdf':
                    self._extract_pdf(file_path, filename)
                elif ext in ['docx', 'xlsx', 'pptx']:
                    self._extract_office(file_path, filename)

            if self.chk_iocs.get():
                self._deep_ioc_hunt(file_path, filename)

        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))
        if not self.results:
            self._add_result("System", "Info", "Scan complete. No high-value metadata found.")

    def _get_decimal_from_dms(self, dms, ref):
        try:
            degrees = dms[0]
            minutes = dms[1] / 60.0
            seconds = dms[2] / 3600.0
            if ref in ['S', 'W']:
                degrees = -degrees
                minutes = -minutes
                seconds = -seconds
            return round(degrees + minutes + seconds, 5)
        except:
            return None

    def _extract_exif(self, file_path, filename):
        if not HAS_PIL:
            self._add_result(filename, "Error", "Pillow library missing. Cannot parse EXIF.")
            return
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if not exif_data: return

            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]

                    if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                        lat = self._get_decimal_from_dms(gps_data['GPSLatitude'], gps_data.get('GPSLatitudeRef', 'N'))
                        lon = self._get_decimal_from_dms(gps_data['GPSLongitude'], gps_data.get('GPSLongitudeRef', 'E'))
                        if lat and lon:
                            self._add_result(filename, "GPS Location", f"{lat}, {lon} (https://www.google.com/maps/place/{lat},{lon})")
                elif isinstance(value, str) and value.strip():
                    if tag_name in ['Make', 'Model', 'Software', 'DateTimeOriginal']:
                        self._add_result(filename, f"EXIF: {tag_name}", value.strip())
        except Exception as e:
            pass

    def _extract_pdf(self, file_path, filename):
        if not HAS_PDF:
            self._add_result(filename, "Error", "PyPDF2 missing. Cannot parse PDF metadata.")
            return
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                info = reader.metadata
                if info:
                    for key, value in info.items():
                        if value and isinstance(value, str):
                            clean_key = key.replace('/', '')
                            self._add_result(filename, f"PDF: {clean_key}", value.strip())
        except Exception:
            pass

    def _extract_office(self, file_path, filename):
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                if 'docProps/core.xml' in z.namelist():
                    core_data = z.read('docProps/core.xml')
                    root = ET.fromstring(core_data)
                    namespaces = {
                        'dc': 'http://purl.org/dc/elements/1.1/',
                        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                        'dcterms': 'http://purl.org/dc/terms/'
                    }

                    creator = root.find('dc:creator', namespaces)
                    if creator is not None and creator.text: self._add_result(filename, "Office: Creator", creator.text)

                    last_mod = root.find('cp:lastModifiedBy', namespaces)
                    if last_mod is not None and last_mod.text: self._add_result(filename, "Office: Last Modified By", last_mod.text)

                    created = root.find('dcterms:created', namespaces)
                    if created is not None and created.text: self._add_result(filename, "Office: Created Date", created.text)
        except Exception:
            pass

    def _deep_ioc_hunt(self, file_path, filename):
        try:
            # Read file as binary and extract ascii printable chunks
            with open(file_path, 'rb') as f:
                data = f.read()
                
            # Extremely fast regex for printable ASCII sequences > 5 chars
            ascii_strings = re.findall(b'[ -~]{5,}', data)
            decoded_text = b" ".join(ascii_strings).decode('utf-8', errors='ignore')
            
            found_iocs = set()
            for category, pattern in self.IOC_REGEX.items():
                matches = re.findall(pattern, decoded_text)
                for match in matches:
                    if match not in found_iocs:
                        found_iocs.add(match)
                        self._add_result(filename, f"IOC: {category}", match)
        except Exception:
            pass

    def _export_csv(self):
        if not self.results: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path: return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["File Name", "Category", "Data / Value"])
                writer.writerows(self.results)
            messagebox.showinfo("Success", f"Intelligence exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

if __name__ == "__main__":
    if not LicenseManager.gate_access("Deep Metadata Scraper"):
        sys.exit(1)
    root = tk.Tk()
    app = DeepMetadataGUI(root)
    root.mainloop()