import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import threading
import sys
import math
import numpy as np


CHARS_BLOCK = "█"

CHARS_ASCII = " .'`^,:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

class DetailedYTTConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Subtitle Video Generator (High Fidelity)")
        self.geometry("700x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.input_path = ctk.StringVar()
        self.width_var = ctk.IntVar(value=50)
        self.fps_var = ctk.IntVar(value=10)
        self.style_var = ctk.StringVar(value="ascii")
        self.is_processing = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(4, weight=1)

        self.header = ctk.CTkLabel(self, text="Video to Subtitle Converter", font=("Roboto", 26, "bold"))
        self.header.grid(row=0, column=0, pady=(25, 10))
        
        ctk.CTkLabel(self, text="Convert video into a playable subtitle file (.ytt)", text_color="gray").grid(row=1, column=0, pady=(0, 15))

        self.frame_file = ctk.CTkFrame(self, corner_radius=10)
        self.frame_file.grid(row=2, column=0, padx=25, pady=10, sticky="ew")
        
        self.btn_browse = ctk.CTkButton(self.frame_file, text="Select Video", width=120, height=35, command=self.browse_file)
        self.btn_browse.pack(side="left", padx=15, pady=15)
        
        self.entry_file = ctk.CTkEntry(self.frame_file, textvariable=self.input_path, placeholder_text="No file selected...", height=35)
        self.entry_file.pack(side="left", fill="x", expand=True, padx=(0, 15), pady=15)

        self.frame_config = ctk.CTkFrame(self, corner_radius=10)
        self.frame_config.grid(row=3, column=0, padx=25, pady=10, sticky="ew")
        self.frame_config.grid_columnconfigure(0, weight=1)
        self.frame_config.grid_columnconfigure(1, weight=1)

        self.frame_sliders = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_sliders.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        self.lbl_width = ctk.CTkLabel(self.frame_sliders, text=f"Resolution Width: {self.width_var.get()}", font=("Roboto", 12, "bold"))
        self.lbl_width.pack(anchor="w")
        self.slider_width = ctk.CTkSlider(self.frame_sliders, from_=30, to=80, variable=self.width_var, command=self.update_labels)
        self.slider_width.pack(fill="x", pady=(5, 15))

        self.lbl_fps = ctk.CTkLabel(self.frame_sliders, text=f"FPS Limit: {self.fps_var.get()}", font=("Roboto", 12, "bold"))
        self.lbl_fps.pack(anchor="w")
        self.slider_fps = ctk.CTkSlider(self.frame_sliders, from_=5, to=30, variable=self.fps_var, command=self.update_labels)
        self.slider_fps.pack(fill="x", pady=(5, 5))

        self.frame_style = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_style.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(self.frame_style, text="Visual Style", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(0, 10))


        self.r_block = ctk.CTkRadioButton(self.frame_style, text="Solid Blocks (█)", variable=self.style_var, value="block")
        self.r_block.pack(anchor="w", pady=5)
        ctk.CTkLabel(self.frame_style, text="  Best for flat colors/cartoons.", font=("Arial", 11), text_color="#aaaaaa").pack(anchor="w", pady=(0, 8))

        self.r_ascii = ctk.CTkRadioButton(self.frame_style, text="Classic ASCII (Text)", variable=self.style_var, value="ascii")
        self.r_ascii.pack(anchor="w", pady=5)

        self.frame_progress = ctk.CTkFrame(self, corner_radius=10)
        self.frame_progress.grid(row=4, column=0, padx=25, pady=10, sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(self.frame_progress, text="Ready", text_color="silver")
        self.lbl_status.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.progressbar = ctk.CTkProgressBar(self.frame_progress, height=12)
        self.progressbar.pack(fill="x", padx=20, pady=(5, 20))
        self.progressbar.set(0)

        self.btn_convert = ctk.CTkButton(self, text="GENERATE SUBTITLE FILE", height=55, 
                                         font=("Roboto", 16, "bold"), 
                                         fg_color="#1f6aa5", hover_color="#144870",
                                         command=self.start_thread)
        self.btn_convert.grid(row=5, column=0, padx=25, pady=25, sticky="ew")

    def update_labels(self, value=None):
        self.lbl_width.configure(text=f"Resolution Width: {int(self.width_var.get())}")
        self.lbl_fps.configure(text=f"FPS Limit: {int(self.fps_var.get())}")

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv")])
        if filename:
            self.input_path.set(filename)

    def start_thread(self):
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select a video file first.")
            return
        
        if self.is_processing: return

        save_path = filedialog.asksaveasfilename(defaultextension=".ytt", filetypes=[("YouTube Timed Text", "*.ytt")])
        if not save_path: return

        self.is_processing = True
        self.btn_convert.configure(state="disabled", text="Processing Video...")
        
        t = threading.Thread(target=self.process_video, args=(self.input_path.get(), save_path))
        t.daemon = True
        t.start()

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02X}{g:02X}{b:02X}"

    def quantize(self, val, levels=16):
        if levels <= 1: return 255
        step = 255 // (levels - 1)
        return (val // step) * step

    def get_char(self, pixel, style):
        if style == "block":
            return "█"
        
        b, g, r = pixel
        lum = 0.299*r + 0.587*g + 0.114*b
        normalized_lum = lum / 255.0
        boosted_lum = math.pow(normalized_lum, 0.55)
        
        chars = CHARS_ASCII
        
        # Clamp 0-1
        boosted_lum = max(0, min(1, boosted_lum))
        idx = int(boosted_lum * (len(chars) - 1))
        return chars[idx]

    def process_video(self, input_file, output_file):
        try:
            cap = cv2.VideoCapture(input_file)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            tgt_fps = self.fps_var.get()
            width = self.width_var.get()
            style = self.style_var.get()
            
            font_aspect = 0.6 
            frame_step = max(1, int(fps / tgt_fps))
            
            pen_registry = {}
            next_pen_id = 0
            body_content = ""
            
            frame_idx = 0
            curr_ms = 0

            sharpen_kernel = np.array([[0, -1, 0],
                                       [-1, 5,-1],
                                       [0, -1, 0]])
            
            while True:
                ret, frame = cap.read()
                if not ret: break
                
                if frame_idx % 20 == 0:
                    prog = frame_idx / total
                    self.progressbar.set(prog)
                    self.lbl_status.configure(text=f"Processed: {int(prog*100)}% | Pens Created: {len(pen_registry)}")

                if frame_idx % frame_step != 0:
                    frame_idx += 1
                    curr_ms += (1000/fps)
                    continue

                if frame.shape[1] > 0:
                    height = int(width * (frame.shape[0] / frame.shape[1]) * font_aspect)
                    small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
                    
                    # Apply Sharpening if we are in a detailed mode
                    if style != "block":
                        small = cv2.filter2D(small, -1, sharpen_kernel)
                
                frame_xml = ""
                
                for y in range(height):
                    curr_hex = None
                    curr_char = None
                    curr_span = ""
                    
                    for x in range(width):
                        pixel = small[y, x]
                        b, g, r = pixel
                        
                        b = self.quantize(b, 16)
                        g = self.quantize(g, 16)
                        r = self.quantize(r, 16)
                        
                        hex_c = self.rgb_to_hex(r, g, b)
                        
                        raw_pixel = small[y, x] 
                        char = self.get_char(raw_pixel, style)
                        
                        if hex_c not in pen_registry:
                            pen_registry[hex_c] = next_pen_id
                            next_pen_id += 1
                        
                        if hex_c == curr_hex and char == curr_char:
                            curr_span += char
                        else:
                            if curr_hex is not None:
                                pid = pen_registry[curr_hex]
                                safe_txt = curr_span.replace("<","&lt;").replace(">","&gt;")
                                frame_xml += f'<s p="{pid}">{safe_txt}</s>'
                            
                            curr_hex = hex_c
                            curr_char = char
                            curr_span = char
                            
                    if curr_hex is not None:
                        pid = pen_registry[curr_hex]
                        safe_txt = curr_span.replace("<","&lt;").replace(">","&gt;")
                        frame_xml += f'<s p="{pid}">{safe_txt}</s>'
                    
                    frame_xml += "\n"

                t_start = int(curr_ms)
                d_dur = int((1000/fps) * frame_step)
                body_content += f'<p t="{t_start}" d="{d_dur}">{frame_xml}</p>\n'
                
                frame_idx += 1
                curr_ms += (1000/fps)
                
            cap.release()
            
            self.lbl_status.configure(text="Saving XML file...")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('<timedtext format="3">\n<head>\n')
                
                for color, pid in pen_registry.items():
                    f.write(f'  <pen id="{pid}" fc="{color}" ft="3" bo="0" ec="0" />\n')
                    
                f.write('</head>\n<body>\n')
                f.write(body_content)
                f.write('</body></timedtext>')
            
            self.progressbar.set(1)
            self.lbl_status.configure(text="Done! Upload to YouTube as 'With Timing'.")
            self.btn_convert.configure(state="normal", text="GENERATE SUBTITLE FILE")
            messagebox.showinfo("Success", f"File saved:\n{output_file}")
            self.is_processing = False
            
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {str(e)}")
            self.btn_convert.configure(state="normal")
            self.is_processing = False
            print(e)

if __name__ == "__main__":
    app = DetailedYTTConverter()
    app.mainloop()