import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import sys
import os
import time
import csv
import webbrowser
import requests

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    HAS_PHONE = True
except ImportError:
    HAS_PHONE = False

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

class PhoneIntelligenceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit Phone Intelligence Suite")
        self.root.geometry("850x650")
        
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
        
        # Treeview (Tables) Styling
        self.style.configure("Treeview", background=self.bg_main, foreground=self.fg_main, fieldbackground=self.bg_main, borderwidth=0, rowheight=28)
        self.style.configure("Treeview.Heading", background=self.bg_sec, foreground=self.accent, font=("Helvetica", 10, "bold"), borderwidth=0)
        self.style.map("Treeview", background=[('selected', self.accent)], foreground=[('selected', '#ffffff')])
        
        self.results = []
        
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Section
        input_frame = ttk.LabelFrame(main_frame, text=" 🎯 Target Phone Number ", padding="15")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Target (e.g. +14155552671):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.target_entry = ttk.Entry(input_frame, width=25, font=("Helvetica", 12))
        self.target_entry.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        
        ttk.Label(input_frame, text="Numverify API (Optional):").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.api_entry = ttk.Entry(input_frame, width=20, font=("Helvetica", 10), show="*")
        self.api_entry.grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
        
        # Action Banner Button
        self.scan_btn = ttk.Button(main_frame, text="🚀 EXECUTE INTELLIGENCE SCAN", command=self._start_scan)
        self.scan_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Actions Frame
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        self.export_btn = ttk.Button(action_frame, text="💾 EXPORT TO CSV", command=self._export_csv, state=tk.DISABLED)
        self.export_btn.pack(side=tk.RIGHT)
        
        if not HAS_PHONE:
            ttk.Label(action_frame, text="⚠️ 'phonenumbers' library missing. Run: pip install phonenumbers", foreground="#ff5555").pack(side=tk.LEFT)

        # Results Treeview
        log_frame = ttk.LabelFrame(main_frame, text=" 📊 OSINT Correlation Report ", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Category", "Attribute", "Value")
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.tag_configure('oddrow', background=self.bg_main)
        self.tree.tag_configure('evenrow', background=self.bg_sec)
        
        self.tree.heading("Category", text="Category")
        self.tree.heading("Attribute", text="Attribute")
        self.tree.heading("Value", text="Value / Deep Link")
        
        self.tree.column("Category", width=150, anchor=tk.W)
        self.tree.column("Attribute", width=150, anchor=tk.W)
        self.tree.column("Value", width=450, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double click for opening URLs
        self.tree.bind("<Double-1>", self._on_double_click)

    def _on_double_click(self, event):
        item_id = self.tree.focus()
        if not item_id: return
        item = self.tree.item(item_id)
        val = item['values'][2]
        if val.startswith("http"):
            webbrowser.open(val)

    def _add_result(self, category, attr, value):
        self.results.append((category, attr, value))
        def _update():
            count = len(self.tree.get_children())
            tag = 'evenrow' if count % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=(category, attr, value), tags=(tag,))
            self.tree.yview_moveto(1)
        self.root.after(0, _update)

    def _start_scan(self):
        if not HAS_PHONE:
            messagebox.showerror("Dependency Error", "Missing 'phonenumbers' library.")
            return
            
        raw_number = self.target_entry.get().strip()
        if not raw_number:
            messagebox.showwarning("Input Error", "Please enter a target phone number.")
            return
            
        if not raw_number.startswith('+'):
            raw_number = '+' + raw_number
            
        self.scan_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.results.clear()
        
        threading.Thread(target=self._scan_thread, args=(raw_number,), daemon=True).start()

    def _scan_thread(self, raw_number):
        try:
            parsed_num = phonenumbers.parse(raw_number, None)
        except phonenumbers.NumberParseException as e:
            self._add_result("Error", "Validation", f"Failed to parse number: {e}")
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
            return
            
        is_valid = phonenumbers.is_valid_number(parsed_num)
        is_possible = phonenumbers.is_possible_number(parsed_num)
        
        # Formatting
        fmt_e164 = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        fmt_intl = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_natl = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        self._add_result("Format", "E.164 Standard", fmt_e164)
        self._add_result("Format", "International", fmt_intl)
        self._add_result("Format", "National", fmt_natl)
        
        # Verification
        self._add_result("Validation", "Is Valid", "Yes (Active format)" if is_valid else "No (Invalid)")
        self._add_result("Validation", "Is Possible", "Yes" if is_possible else "No")
        
        if not is_valid:
            self._add_result("Validation", "Warning", "Number does not match active dial plans. Might be spoofed.")

        # Telco & Location
        region = geocoder.description_for_number(parsed_num, "en")
        provider = carrier.name_for_number(parsed_num, "en")
        timezones = timezone.time_zones_for_number(parsed_num)
        num_type = phonenumbers.number_type(parsed_num)

        # --- API DEEP DIP OVERRIDE ---
        clean_num = fmt_e164.replace('+', '')
        api_key = self.api_entry.get().strip()
        if api_key:
            try:
                url = f"http://apilayer.net/api/validate?access_key={api_key}&number={clean_num}"
                resp = requests.get(url, timeout=10).json()
                if resp.get("valid"):
                    if resp.get("carrier"):
                        provider = resp.get("carrier")
                        self._add_result("OSINT API", "Resolved Carrier", provider)
                    if resp.get("line_type"):
                        api_line = resp.get("line_type").lower()
                        self._add_result("OSINT API", "Resolved Line Type", api_line.capitalize())
                        if "mobile" in api_line:
                            num_type = phonenumbers.PhoneNumberType.MOBILE
                        elif "landline" in api_line or "voip" in api_line:
                            num_type = phonenumbers.PhoneNumberType.VOIP
                elif "error" in resp:
                    self._add_result("OSINT API", "Warning", resp["error"].get("info", "Invalid API Key / Quota Reached"))
            except Exception as e:
                self._add_result("OSINT API", "Exception", str(e))

        self._add_result("Telecom", "Geographic Region", region if region else "Unknown")
        self._add_result("Telecom", "Carrier Network", provider if provider else "Unlisted (US/CA requires API)")
        self._add_result("Telecom", "Timezone(s)", ", ".join(timezones) if timezones else "Unknown")
        
        # Line Type Determination
        type_map = {
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Landline",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll-Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.VOIP: "VoIP / Virtual Number (Potential Burner)",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "Universal Access Number"
        }
        self._add_result("Telecom", "Line Type", type_map.get(num_type, "Unknown"))

        # Burner / Free App Detection Heuristics
        burner_keywords = [
            "bandwidth", "onvoy", "inteliquent", "twilio", "sinch", 
            "textnow", "enflick", "peerless", "voyant", "grand central", "google",
            "textme", "pinger", "talkatone", "plivo", "nexmo", "ringcentral",
            "ymax", "magicjack", "vonage", "skype"
        ]
        provider_lower = provider.lower() if provider else ""
        is_voip_carrier = any(keyword in provider_lower for keyword in burner_keywords)
        is_voip_type = (num_type == phonenumbers.PhoneNumberType.VOIP)
        
        burner_status = "⚠️ HIGH (Matches known free app / VoIP carrier network)" if (is_voip_carrier or is_voip_type) else "Low (Standard Mobile/Landline)"
        self._add_result("Risk Analysis", "Burner / Free App", burner_status)
        
        # Social Media & OSINT Pivots
        clean_num = fmt_e164.replace('+', '')
        self._add_result("OSINT Pivot (Double Click)", "WhatsApp", f"https://wa.me/{clean_num}")
        self._add_result("OSINT Pivot (Double Click)", "Telegram", f"https://t.me/+{clean_num}")
        self._add_result("OSINT Pivot (Double Click)", "Viber", f"viber://chat?number=%2B{clean_num}")
        self._add_result("OSINT Pivot (Double Click)", "Truecaller", f"https://www.truecaller.com/search/global/{clean_num}")
        self._add_result("OSINT Pivot (Double Click)", "Pipl Search", f"https://pipl.com/search/?q={fmt_intl.replace(' ', '+')}")
        
        self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.export_btn.config(state=tk.NORMAL))

    def _export_csv(self):
        if not self.results: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Attribute", "Value"])
                writer.writerows(self.results)
            messagebox.showinfo("Success", f"Intelligence exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

if __name__ == "__main__":
    if not LicenseManager.gate_access("Phone Intelligence Suite"): sys.exit(1)
    root = tk.Tk()
    app = PhoneIntelligenceGUI(root)
    root.mainloop()