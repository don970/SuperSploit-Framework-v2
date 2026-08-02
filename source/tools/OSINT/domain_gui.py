import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests

try:
    import whois
    import dns.resolver
    HAS_LIBS = True
except ImportError:
    HAS_LIBS = False

class DomainScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit - Domain & Infrastructure Scanner")
        self.root.geometry("900x700")
        
        # Sentry/Modern Dark Color Palette
        self.bg_main = "#181825"      # Deep dark blue/gray
        self.bg_sec = "#1e1e2e"       # Lighter frame background
        self.accent = "#6c5fc7"       # Sentry-style purple accent
        self.accent_hover = "#8a7edb" # Lighter purple for active states
        self.fg_main = "#ffffff"      # Bright white text
        self.term_bg = "#0d0d14"      # Darker terminal background
        self.term_fg = "#00ffcc"      # Neon cyan for telemetry
        
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

        if not HAS_LIBS:
            messagebox.showwarning("Missing Dependencies", "Please run: pip install python-whois dnspython requests")
            
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text=" Target Infrastructure ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Domain (e.g. example.com):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.domain_entry = ttk.Entry(input_frame, width=30, font=("Helvetica", 12))
        self.domain_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="SecurityTrails API (Optional):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.api_entry = ttk.Entry(input_frame, width=25, show="*")
        self.api_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # --- Action Button ---
        self.scan_btn = ttk.Button(main_frame, text="🚀 ENUMERATE TARGET", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # --- Results Notebook ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: DNS Records
        self.tab_dns = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_dns, text=" DNS Records ")
        self._build_treeview(self.tab_dns, "dns_tree", ("Record Type", "Target / Value"))

        # Tab 2: Subdomains
        self.tab_sub = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_sub, text=" Subdomains ")
        self._build_treeview(self.tab_sub, "sub_tree", ("Subdomain", "Source"))

        # Tab 3: WHOIS Data
        self.tab_whois = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_whois, text=" WHOIS ")
        self.whois_text = tk.Text(self.tab_whois, wrap=tk.WORD, bg=self.term_bg, fg="#ffffff", font=("Consolas", 11), relief=tk.FLAT, insertbackground="#ffffff", padx=10, pady=10)
        self.whois_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 4: Telemetry Log
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
            tree.column(col, width=300, anchor=tk.W)
        
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

    def _clear_ui(self):
        for item in self.dns_tree.get_children():
            self.dns_tree.delete(item)
        for item in self.sub_tree.get_children():
            self.sub_tree.delete(item)
            
        self.whois_text.delete(1.0, tk.END)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_scan(self):
        domain = self.domain_entry.get().strip()
        if not domain:
            messagebox.showerror("Error", "Please enter a target domain.")
            return
            
        if not HAS_LIBS:
            messagebox.showerror("Error", "Missing required Python libraries.")
            return

        self._clear_ui()
        self.scan_btn.config(state=tk.DISABLED)
        self.notebook.select(self.tab_log)
        
        threading.Thread(target=self._scan_thread, args=(domain,), daemon=True).start()

    def _scan_thread(self, domain):
        self.log(f"[*] Initializing Infrastructure Scan for: {domain}")
        
        self._get_whois(domain)
        self._get_dns_records(domain)
        self._get_subdomains(domain)
        
        self.log("\n[+] Infrastructure Enumeration Complete.")
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def _get_whois(self, domain):
        self.log("[*] Querying WHOIS Registrar databases...")
        try:
            w = whois.whois(domain)
            whois_data = str(w)
            self.root.after(0, lambda: self.whois_text.insert(tk.END, whois_data))
            self.log("[+] WHOIS data successfully retrieved.")
        except Exception as e:
            self.log(f"[-] WHOIS lookup failed: {e}")
            self.root.after(0, lambda: self.whois_text.insert(tk.END, f"WHOIS Error:\n{e}"))

    def _get_dns_records(self, domain):
        self.log("[*] Probing DNS Configuration (A, AAAA, MX, TXT, NS, CNAME)...")
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype)
                for rdata in answers:
                    val = str(rdata).strip('"')
                    self._add_tree_item(self.dns_tree, (rtype, val))
                self.log(f"  [+] Found {len(answers)} {rtype} records.")
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NXDOMAIN:
                self.log(f"[-] Domain {domain} does not exist.")
                break
            except Exception as e:
                self.log(f"  [-] Error querying {rtype}: {e}")

    def _get_subdomains(self, domain):
        found_subs = set()
        
        # 1. crt.sh (Certificate Transparency)
        self.log("[*] Querying crt.sh (Certificate Transparency) for subdomains...")
        try:
            resp = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                for entry in data:
                    name_value = entry.get('name_value', '').lower()
                    # Handle multiline certs
                    for sub in name_value.split('\n'):
                        sub = sub.strip()
                        if sub and sub.endswith(domain) and sub not in found_subs:
                            if '*' not in sub: # filter wildcards
                                found_subs.add(sub)
                                self._add_tree_item(self.sub_tree, (sub, "crt.sh"))
                self.log(f"  [+] crt.sh discovered {len(found_subs)} unique subdomains.")
            else:
                self.log(f"[-] crt.sh returned HTTP {resp.status_code}")
        except Exception as e:
            self.log(f"[-] crt.sh query failed: {e}")

        # 2. SecurityTrails API (Optional)
        api_key = self.api_entry.get().strip()
        if api_key:
            self.log("[*] Querying SecurityTrails API for historical subdomains...")
            try:
                url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
                headers = {"APIKEY": api_key, "accept": "application/json"}
                resp = requests.get(url, headers=headers, timeout=20)
                
                if resp.status_code == 200:
                    st_subs = resp.json().get('subdomains', [])
                    new_count = 0
                    for sub in st_subs:
                        full_sub = f"{sub}.{domain}".lower()
                        if full_sub not in found_subs:
                            found_subs.add(full_sub)
                            self._add_tree_item(self.sub_tree, (full_sub, "SecurityTrails"))
                            new_count += 1
                    self.log(f"  [+] SecurityTrails discovered {new_count} additional subdomains.")
                elif resp.status_code in [401, 403]:
                    self.log("[-] SecurityTrails API Key is invalid or unauthorized.")
                else:
                    self.log(f"[-] SecurityTrails returned HTTP {resp.status_code}")
            except Exception as e:
                self.log(f"[-] SecurityTrails query failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DomainScannerGUI(root)
    root.mainloop()