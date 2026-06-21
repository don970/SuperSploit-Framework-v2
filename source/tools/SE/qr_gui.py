import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

try:
    import qrcode
    from PIL import Image, ImageTk
    HAS_QR = True
except ImportError:
    HAS_QR = False

class QRGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SuperSploit QR Generator - PHYSICAL ASSET DROP")
        self.root.geometry("500x650")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        if not HAS_QR:
            messagebox.showerror("Dependency Error", "Missing 'qrcode' or 'Pillow'. Run: pip install qrcode[pil]")
            self.root.destroy()
            return
            
        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        config_frame = ttk.LabelFrame(main_frame, text=" 🔗 Payload Configuration ", padding="10")
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="Target URL/URI:").pack(anchor=tk.W, pady=2)
        self.url_entry = ttk.Entry(config_frame, width=50)
        self.url_entry.insert(0, "https://my-supersploit-c2.com/payload.apk")
        self.url_entry.pack(fill=tk.X, pady=2)

        ttk.Label(config_frame, text="Output File:").pack(anchor=tk.W, pady=2)
        
        file_frame = ttk.Frame(config_frame)
        file_frame.pack(fill=tk.X)
        self.out_entry = ttk.Entry(file_frame, width=35)
        self.out_entry.insert(0, os.path.join(os.getenv("HOME"), "payload_drop.png"))
        self.out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self._browse).pack(side=tk.RIGHT, padx=5)

        ttk.Button(main_frame, text="⬛ GENERATE MALICIOUS QR", command=self._generate).pack(pady=10)

        self.preview_frame = ttk.LabelFrame(main_frame, text=" 👁️ Preview ", padding="10")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.img_label = ttk.Label(self.preview_frame)
        self.img_label.pack(expand=True)

    def _browse(self):
        f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if f:
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, f)

    def _generate(self):
        url = self.url_entry.get().strip()
        out = self.out_entry.get().strip()
        if not url or not out: return
        
        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            img.save(out)
            
            # Display in GUI
            img_tk = ImageTk.PhotoImage(img.resize((300, 300)))
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk # Keep ref
            messagebox.showinfo("Success", f"QR Asset saved to:\n{out}")
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = QRGUI(root)
    root.mainloop()