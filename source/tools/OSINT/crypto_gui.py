import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import re
import webbrowser
from datetime import datetime

class CryptoTracerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit - Crypto Ledger Tracer")
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
        input_frame = ttk.LabelFrame(main_frame, text=" Target Wallet ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="Wallet Address:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(input_frame, width=40, font=("Helvetica", 12))
        self.target_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(input_frame, text="Etherscan API (Optional):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.api_entry = ttk.Entry(input_frame, width=20, show="*")
        self.api_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)

        # --- Action Banner Button ---
        self.scan_btn = ttk.Button(main_frame, text="🚀 INTERROGATE BLOCKCHAIN LEDGER", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))

        # --- Results Notebook ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Tab 1: Ledger Overview
        self.tab_overview = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_overview, text=" Ledger Overview ")
        self._build_treeview(self.tab_overview, "overview_tree", ("Metric", "Value"))

        # Tab 2: Transaction History
        self.tab_txs = tk.Frame(self.notebook, bg=self.bg_main)
        self.notebook.add(self.tab_txs, text=" Transactions (Top 50) ")
        self._build_treeview(self.tab_txs, "tx_tree", ("Date", "Type", "Amount", "Counterparty Address"))
        self.tx_tree.bind("<Double-1>", self._on_double_click_tx)

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
            if col == "Counterparty Address":
                tree.column(col, width=350, anchor=tk.W)
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

    def _on_double_click_tx(self, event):
        try:
            item = self.tx_tree.selection()[0]
            addr = self.tx_tree.item(item, "values")[3]
            # Auto-paste the counterparty into the target box for quick pivoting
            if addr and addr != "N/A":
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, addr)
                self.log(f"[*] Pivoted to new target address: {addr}")
        except IndexError:
            pass

    def _clear_ui(self):
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _detect_crypto_type(self, address):
        if re.match(r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$', address):
            return "BTC"
        elif re.match(r'^0x[a-fA-F0-9]{40}$', address):
            return "ETH"
        return "UNKNOWN"

    def _start_scan(self):
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showerror("Error", "Please enter a target wallet address.")
            return

        self._clear_ui()
        self.scan_btn.config(state=tk.DISABLED)
        self.notebook.select(self.tab_log)
        
        api_key = self.api_entry.get().strip()
        threading.Thread(target=self._scan_thread, args=(target, api_key), daemon=True).start()

    def _scan_thread(self, address, api_key):
        self.log(f"[*] Initializing Ledger OSINT for: {address}")
        
        crypto_type = self._detect_crypto_type(address)
        self.log(f"[+] Detected Currency Type: {crypto_type}")
        self._add_tree_item(self.overview_tree, ("Currency", crypto_type))
        self._add_tree_item(self.overview_tree, ("Wallet Address", address))
        
        if crypto_type == "BTC":
            self._query_btc(address)
        elif crypto_type == "ETH":
            self._query_eth(address, api_key)
        else:
            self.log("[-] Unsupported or invalid wallet address format.")
            self._add_tree_item(self.overview_tree, ("Error", "Unknown cryptocurrency format."))
            
        self.log("\n[+] Blockchain OSINT Enumeration Complete.")
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))

    def _query_btc(self, address):
        self.log("[*] Querying Blockchain.info API for BTC Ledger...")
        try:
            resp = requests.get(f"https://blockchain.info/rawaddr/{address}", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                
                # Overview
                bal = data.get("final_balance", 0) / 100000000
                sent = data.get("total_sent", 0) / 100000000
                recv = data.get("total_received", 0) / 100000000
                tx_count = data.get("n_tx", 0)
                
                self._add_tree_item(self.overview_tree, ("Current Balance", f"{bal:.8f} BTC"))
                self._add_tree_item(self.overview_tree, ("Total Received", f"{recv:.8f} BTC"))
                self._add_tree_item(self.overview_tree, ("Total Sent", f"{sent:.8f} BTC"))
                self._add_tree_item(self.overview_tree, ("Transaction Count", str(tx_count)))
                
                self.log(f"[+] Successfully pulled ledger. Balance: {bal:.8f} BTC")
                
                # Txs
                txs = data.get("txs", [])[:50]
                for tx in txs:
                    dt = datetime.utcfromtimestamp(tx.get("time", 0)).strftime('%Y-%m-%d %H:%M:%S')
                    # Calculate flow relative to target
                    amount = 0
                    direction = "Unknown"
                    counterparty = "Multiple/Complex"
                    
                    # Simplified attribution logic
                    for out in tx.get("out", []):
                        if out.get("addr") == address:
                            amount += out.get("value", 0)
                            direction = "IN"
                    
                    if direction == "Unknown":
                        direction = "OUT" # If it didn't come in, it went out
                        
                    amt_btc = amount / 100000000
                    self._add_tree_item(self.tx_tree, (dt, direction, f"{amt_btc:.8f} BTC", counterparty))
                    
            else:
                self.log(f"[-] Blockchain.info API returned HTTP {resp.status_code}. (Rate limited?)")
        except Exception as e:
            self.log(f"[-] BTC Query failed: {e}")

    def _query_eth(self, address, api_key):
        if not api_key:
            api_key = "YourApiKeyToken" # Etherscan free-tier fallback
            
        self.log("[*] Querying Etherscan API for ETH Ledger...")
        try:
            # Get Balance
            bal_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
            resp_bal = requests.get(bal_url, timeout=15).json()
            if resp_bal.get("status") == "1":
                bal_eth = int(resp_bal["result"]) / 1e18
                self._add_tree_item(self.overview_tree, ("Current Balance", f"{bal_eth:.6f} ETH"))
                self.log(f"[+] Successfully pulled balance: {bal_eth:.6f} ETH")
            
            # Get Txs
            self.log("[*] Pulling recent transactions...")
            tx_url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey={api_key}"
            resp_tx = requests.get(tx_url, timeout=15).json()
            if resp_tx.get("status") == "1":
                txs = resp_tx["result"]
                self._add_tree_item(self.overview_tree, ("Recent Tx Count", str(len(txs))))
                
                for tx in txs:
                    dt = datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S')
                    val_eth = int(tx["value"]) / 1e18
                    direction = "IN" if tx["to"].lower() == address.lower() else "OUT"
                    counterparty = tx["from"] if direction == "IN" else tx["to"]
                    self._add_tree_item(self.tx_tree, (dt, direction, f"{val_eth:.6f} ETH", counterparty))
        except Exception as e:
            self.log(f"[-] ETH Query failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CryptoTracerGUI(root)
    root.mainloop()