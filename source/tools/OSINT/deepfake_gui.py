import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import json
import requests

try:
    from PIL import Image, ImageTk, ImageChops, ImageEnhance, ExifTags
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class DeepfakeVerifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit - Deepfake & Synthetic Media Verifier")
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
        
        self.image_path = None
        self.ela_photo = None  # Reference to prevent GC
        
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
        
        # Notebook (Tabs) Styling
        self.style.configure("TNotebook", background=self.bg_main, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.bg_sec, foreground=self.fg_main, padding=(15, 6), font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", self.accent)], foreground=[("selected", "#ffffff")])
        
        # Treeview (Tables) Styling
        self.style.configure("Treeview", background=self.bg_main, foreground=self.fg_main, fieldbackground=self.bg_main, borderwidth=0, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent)], foreground=[('selected', '#ffffff')])

        if not HAS_PIL:
            messagebox.showwarning("Missing Library", "Pillow is required for ELA analysis. Please run: pip install Pillow")

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text=" Target Media ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Image File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.target_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        self.browse_btn = ttk.Button(input_frame, text="📁 BROWSE", command=self._browse_image)
        self.browse_btn.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(input_frame, text="Hive API (Optional):").grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        self.api_entry = ttk.Entry(input_frame, width=15, show="*")
        self.api_entry.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        # --- Action Banner Button ---
        self.scan_btn = ttk.Button(main_frame, text="🚀 ANALYZE MEDIA AUTHENTICITY", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # --- Results Notebook ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Authenticity Overview
        self.tab_overview = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_overview, text=" Authenticity Overview ")
        self._build_treeview(self.tab_overview, "overview_tree", ("Metric / Check", "Status / Result"))

        # Tab 2: Error Level Analysis (Visual)
        self.tab_ela = tk.Frame(self.notebook, bg=self.term_bg)
        self.notebook.add(self.tab_ela, text=" ELA Noise Map ")
        self.ela_label = tk.Label(self.tab_ela, bg=self.term_bg, text="No ELA Map Generated", fg="#444444", font=("Helvetica", 14))
        self.ela_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 3: Telemetry Log
        self.tab_log = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_log, text=" Telemetry Log ")
        self.log_text = tk.Text(self.tab_log, state=tk.DISABLED, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _build_treeview(self, parent, attr_name, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        tree.tag_configure('oddrow', background=self.bg_main)
        tree.tag_configure('evenrow', background=self.bg_sec)
        
        for col in columns:
            tree.heading(col, text=col)
            if col == "Status / Result":
                tree.column(col, width=450, anchor=tk.W)
            else:
                tree.column(col, width=250, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        setattr(self, attr_name, tree)

    def _browse_image(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.tiff")])
        if f:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, f)
            self.image_path = f

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]")
        full_msg = f"{timestamp} {message}\n"
        def _append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, full_msg)
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def _add_tree_item(self, tree, values):
        def _insert():
            count = len(tree.get_children())
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            tree.insert("", tk.END, values=values, tags=(tag,))
        self.root.after(0, _insert)

    def _clear_ui(self):
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        self.ela_label.config(image='', text="Analyzing...")

    def _start_scan(self):
        if not self.image_path or not os.path.exists(self.image_path):
            self.image_path = self.target_entry.get().strip()
            if not self.image_path or not os.path.exists(self.image_path):
                messagebox.showerror("Error", "Please select a valid image file.")
                return
                
        if not HAS_PIL:
            messagebox.showerror("Error", "Pillow library is missing. ELA cannot run.")
            return

        self._clear_ui()
        self.scan_btn.config(state=tk.DISABLED)
        self.notebook.select(self.tab_log)
        
        api_key = self.api_entry.get().strip()
        threading.Thread(target=self._scan_thread, args=(self.image_path, api_key), daemon=True).start()

    def _scan_thread(self, img_path, api_key):
        self.log(f"[*] Initializing Synthetic Media Verification for: {os.path.basename(img_path)}")
        
        ai_score = 0
        flags = []

        # 1. Metadata Signature Interrogation
        self.log("[*] Interrogating EXIF & Proprietary Color Profiles...")
        try:
            with Image.open(img_path) as img:
                raw_exif = img.getexif()
                meta_str = ""
                if raw_exif:
                    for tag_id, value in raw_exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        meta_str += f"{tag}:{value} ".lower()
                        
                # Check for proprietary AI generator footprints
                ai_signatures = ["midjourney", "stable diffusion", "dall-e", "novelai", "comfyui", "openai", "automatic1111"]
                found_sigs = [sig for sig in ai_signatures if sig in meta_str]
                
                if found_sigs:
                    ai_score += 85
                    flags.append(f"AI Metadata Found: {', '.join(found_sigs).upper()}")
                    self.log(f"[!] CRITICAL: Known AI Generator tags detected in metadata: {found_sigs}")
                elif not raw_exif:
                    flags.append("EXIF Data Missing/Stripped (Common in AI/Social Media)")
                    self.log("[-] No EXIF data found. Image may be stripped or synthetically generated.")
                else:
                    self.log("[+] EXIF data looks natural (No explicit AI tags found).")
        except Exception as e:
            self.log(f"[-] EXIF Parsing Error: {e}")

        # 2. Error Level Analysis (ELA) Generation
        self.log("[*] Rendering Error Level Analysis (ELA) Map...")
        try:
            ela_img = self._generate_ela(img_path)
            self.log("[+] ELA visual heat map generated successfully.")
            
            # Display in UI
            self._render_ela_to_ui(ela_img)
            
            # Heuristic check on ELA image
            extrema = ela_img.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            if max_diff < 50:
                ai_score += 40
                flags.append("Flat Compression Gradient (High likelihood of AI generation)")
                self.log("[!] ELA reveals abnormally flat compression levels. Typical of synthetic rendering.")
            else:
                self.log("[+] ELA variance is high. Check map for localized bright spots (Photoshop).")
                flags.append("High ELA Variance (Check map for localized splices)")
        except Exception as e:
            self.log(f"[-] ELA Rendering Error: {e}")

        # Final Overview Assessment
        self.log(f"\n[*] Final Synthentic Likelihood Score: {min(ai_score, 99)}%")
        
        self._add_tree_item(self.overview_tree, ("Target File", os.path.basename(img_path)))
        status_color = "🔴 HIGH" if ai_score >= 50 else "🟢 LOW"
        self._add_tree_item(self.overview_tree, ("Synthetic / Deepfake Risk", f"{min(ai_score, 99)}% ({status_color})"))
        
        for flag in flags:
            self._add_tree_item(self.overview_tree, ("Anomaly Flag", flag))
            
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
        self.log("\n[+] Verification Complete. Review the ELA Noise Map tab for manual forensic inspection.")

    def _generate_ela(self, img_path):
        """
        Re-saves the image at 90% quality and calculates the absolute difference.
        Enhances the brightness of the difference to make anomalies pop.
        """
        temp_path = "temp_ela_artifact.jpg"
        original = Image.open(img_path).convert('RGB')
        original.save(temp_path, 'JPEG', quality=90)
        
        compressed = Image.open(temp_path)
        diff = ImageChops.difference(original, compressed)
        
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0:
            max_diff = 1
            
        scale = 255.0 / max_diff
        ela_image = ImageEnhance.Brightness(diff).enhance(scale)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return ela_image

    def _render_ela_to_ui(self, pil_image):
        # Resize to fit within the Tkinter frame while maintaining aspect ratio
        pil_image.thumbnail((800, 600), Image.Resampling.LANCZOS)
        self.ela_photo = ImageTk.PhotoImage(pil_image)
        self.root.after(0, lambda: self.ela_label.config(image=self.ela_photo, text=""))

if __name__ == "__main__":
    root = tk.Tk()
    app = DeepfakeVerifierGUI(root)
    root.mainloop()