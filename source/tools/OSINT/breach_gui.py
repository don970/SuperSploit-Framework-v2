import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import urllib.parse
import webbrowser

class BreachMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit - Credential Breach Monitor")
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

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text=" Target Identity ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Email/Username:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(input_frame, width=30, font=("Helvetica", 12))
        self.target_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="HIBP API Key (Optional):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.api_entry = ttk.Entry(input_frame, width=25, show="*")
        self.api_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # --- Action Banner Button ---
        self.scan_btn = ttk.Button(main_frame, text="🚀 INITIATE BREACH SCAN", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # --- Results Notebook ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Breach Database
        self.tab_breaches = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_breaches, text=" Breach Database ")
        self._build_treeview(self.tab_breaches, "breach_tree", ("Breach Name", "Date", "Compromised Data"))

        # Tab 2: Dorks & Pastebins
        self.tab_dorks = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_dorks, text=" Pastebin & Dorks ")
        self._build_treeview(self.tab_dorks, "dorks_tree", ("Platform/Target", "Query URL (Double-Click to Open)"))
        self.dorks_tree.bind("<Double-1>", self._on_double_click)

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
            if "URL" in col or "Data" in col:
                tree.column(col, width=450, anchor=tk.W)
            else:
                tree.column(col, width=150, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        setattr(self, attr_name, tree)

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

    def _on_double_click(self, event):
        try:
            item = self.dorks_tree.selection()[0]
            url = self.dorks_tree.item(item, "values")[1]
            if url.startswith("http"):
                webbrowser.open(url)
        except IndexError:
            pass

    def _clear_ui(self):
        for item in self.breach_tree.get_children():
            self.breach_tree.delete(item)
        for item in self.dorks_tree.get_children():
            self.dorks_tree.delete(item)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target email or username.")
            return

        self._clear_ui()
        self.scan_btn.config(state=tk.DISABLED)
        self.notebook.select(self.tab_log)
        
        api_key = self.api_entry.get().strip()
        threading.Thread(target=self._scan_thread, args=(target, api_key), daemon=True).start()

    def _scan_thread(self, target, api_key):
        self.log(f"[*] Initializing Credential Breach Monitor for: {target}")
        
        self._generate_dorks(target)
        self._check_hibp(target, api_key)
        
        self.log("\n[+] Breach Enumeration Complete.")
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def _check_hibp(self, target, api_key):
        if not api_key:
            self.log("[!] No HIBP API Key provided. Skipping authenticated breach lookup.")
            self.log("    (Hint: You can still use the generated Pastebin Dorks tab).")
            self._add_tree_item(self.breach_tree, ("API Key Required", "N/A", "Please provide a HaveIBeenPwned API key to view breaches."))
            return
            
        self.log("[*] Querying HaveIBeenPwned API for exposed databases...")
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{urllib.parse.quote(target)}?truncateResponse=false"
        headers = {
            "hibp-api-key": api_key,
            "user-agent": "SuperSploit-OSINT-Framework"
        }
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code == 200:
                breaches = resp.json()
                self.log(f"[+] CRITICAL: Target found in {len(breaches)} known data breaches!")
                for b in breaches:
                    name = b.get("Name", "Unknown")
                    date = b.get("BreachDate", "Unknown")
                    data_classes = ", ".join(b.get("DataClasses", []))
                    self._add_tree_item(self.breach_tree, (name, date, data_classes))
            elif resp.status_code == 404:
                self.log("[+] Target is clean. No known HIBP breaches found.")
                self._add_tree_item(self.breach_tree, ("CLEAN", "N/A", "No breached data found for this target."))
            elif resp.status_code == 401:
                self.log("[-] Invalid HIBP API Key provided.")
            else:
                self.log(f"[-] HIBP API returned HTTP {resp.status_code}")
        except Exception as e:
            self.log(f"[-] HIBP query failed: {e}")

    def _generate_dorks(self, target):
        self.log("[*] Generating intelligent text-dump OSINT Dorks...")
        
        target_enc = urllib.parse.quote(f'"{target}"')
        
        dorks = [
            ("Pastebin", f"https://www.google.com/search?q=site:pastebin.com+{target_enc}"),
            ("ControlC", f"https://www.google.com/search?q=site:controlc.com+{target_enc}"),
            ("GitHub Gists", f"https://www.google.com/search?q=site:gist.github.com+{target_enc}"),
            ("TextBin", f"https://www.google.com/search?q=site:textbin.net+{target_enc}"),
            ("Generic Dumps", f"https://www.google.com/search?q={target_enc}+password+OR+pass+OR+pwd")
        ]
        
        for platform, url in dorks:
            self._add_tree_item(self.dorks_tree, (platform, url))
            
if __name__ == "__main__":
    root = tk.Tk()
    app = BreachMonitorGUI(root)
    root.mainloop()