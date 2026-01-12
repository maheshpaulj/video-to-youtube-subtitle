import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import threading
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import os
import webbrowser

# ASCII scales
CHARS_BLOCK = "█"
GSCALE = '$8obdpq0Lun1+"`'

class DetailedYTTConverter(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Subtitle Video Generator")
        self.geometry("650x700")
        self.minsize(650, 700)
        try:
            self.iconbitmap(os.path.join(os.path.dirname(__file__), "icon.png"))
        except Exception:
            try:
                from PIL import ImageTk
                ico = Image.open(os.path.join(os.path.dirname(__file__), "icon.png"))
                photo = ImageTk.PhotoImage(ico)
                self.wm_iconphoto(False, photo)
                self._icon_photo = photo
            except Exception:
                pass
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Variables
        self.input_path = ctk.StringVar()
        self.width_var = ctk.IntVar(value=50)
        self.fps_var = ctk.IntVar(value=10)
        self.use_source_fps = ctk.BooleanVar(value=False)
        self.threshold_var = ctk.IntVar(value=5)
        self.color_depth_var = ctk.IntVar(value=16)
        self.style_var = ctk.StringVar(value="ascii")
        self.bw_mode = ctk.StringVar(value="color")
        self.is_processing = False

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # 1. Header
        self.header = ctk.CTkLabel(self, text="Video to Subtitle Converter", font=("Roboto", 26, "bold"))
        self.header.grid(row=0, column=0, pady=(20, 5), sticky="ew")
        
        self.lbl_author = ctk.CTkLabel(self, text="Made by Mahesh Paul J", text_color="gray", cursor="hand2")
        self.lbl_author.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        self.lbl_author.bind("<Button-1>", lambda e: webbrowser.open("https://maheshpaul.is-a.dev"))

        # 2. File Selection
        self.frame_file = ctk.CTkFrame(self, corner_radius=10)
        self.frame_file.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_file.grid_columnconfigure(1, weight=1)
        
        self.btn_browse = ctk.CTkButton(self.frame_file, text="Select Video", width=120, height=35, command=self.browse_file)
        self.btn_browse.grid(row=0, column=0, padx=15, pady=15)
        
        self.entry_file = ctk.CTkEntry(self.frame_file, textvariable=self.input_path, placeholder_text="No file selected...", height=35)
        self.entry_file.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")

        # 3. Main Configuration Area
        self.frame_config = ctk.CTkFrame(self, corner_radius=10)
        self.frame_config.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_config.grid_columnconfigure(0, weight=1)
        self.frame_config.grid_columnconfigure(1, weight=1)
        self.frame_config.grid_rowconfigure(0, weight=1)

        # --- LEFT COLUMN: SLIDERS & INPUTS ---
        self.frame_controls = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_controls.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        
        # Helper to create editable sliders
        self.create_smart_control(self.frame_controls, "Resolution Width", self.width_var, 30, 100)
        self.create_smart_control(self.frame_controls, "FPS Limit", self.fps_var, 5, 60)
        
        self.check_source_fps = ctk.CTkCheckBox(self.frame_controls, text="Ignore FPS limit (Use Source)", 
                                                variable=self.use_source_fps, command=self.toggle_fps_slider)
        self.check_source_fps.pack(anchor="w", pady=(0, 15))

        self.create_smart_control(self.frame_controls, "Compression (%)", self.threshold_var, 0, 50)
        self.create_smart_control(self.frame_controls, "Color Depth (Levels)", self.color_depth_var, 4, 64)

        # --- RIGHT COLUMN: VISUAL STYLE ---
        self.frame_style = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_style.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        ctk.CTkLabel(self.frame_style, text="Visual Style", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(0, 10))

        self.r_block = ctk.CTkRadioButton(self.frame_style, text="Solid Blocks (█)", variable=self.style_var, value="block")
        self.r_block.pack(anchor="w", pady=5)
        
        self.r_ascii = ctk.CTkRadioButton(self.frame_style, text="Classic ASCII (Text)", variable=self.style_var, value="ascii")
        self.r_ascii.pack(anchor="w", pady=5)

        ctk.CTkLabel(self.frame_style, text="Color Mode", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20, 10))

        self.r_color = ctk.CTkRadioButton(self.frame_style, text="Full Color", variable=self.bw_mode, value="color", command=self.toggle_color_depth)
        self.r_color.pack(anchor="w", pady=5)

        self.r_grayscale = ctk.CTkRadioButton(self.frame_style, text="Grayscale", variable=self.bw_mode, value="grayscale", command=self.toggle_color_depth)
        self.r_grayscale.pack(anchor="w", pady=5)

        self.r_pure_bw = ctk.CTkRadioButton(self.frame_style, text="Pure B&W (Binary)", variable=self.bw_mode, value="pure_bw", command=self.toggle_color_depth)
        self.r_pure_bw.pack(anchor="w", pady=5)

        # 4. Progress Bar
        self.frame_progress = ctk.CTkFrame(self, corner_radius=10)
        self.frame_progress.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.lbl_status = ctk.CTkLabel(self.frame_progress, text="Ready", text_color="silver")
        self.lbl_status.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.progressbar = ctk.CTkProgressBar(self.frame_progress, height=15)
        self.progressbar.pack(fill="x", padx=20, pady=(5, 15))
        self.progressbar.set(0)

        # 5. Action Button
        self.btn_convert = ctk.CTkButton(self, text="GENERATE SUBTITLE FILE", height=50, 
                                         font=("Roboto", 16, "bold"), 
                                         fg_color="#1f6aa5", hover_color="#144870",
                                         command=self.start_thread)
        self.btn_convert.grid(row=5, column=0, padx=20, pady=(5, 20), sticky="ew")

    def create_smart_control(self, parent, label_text, variable, min_val, max_val):
        """Creates a Label, Editable Entry, and Slider linked together."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 10))
        
        # Top Row: Label + Entry
        top_frame = ctk.CTkFrame(frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 2))
        
        ctk.CTkLabel(top_frame, text=label_text, font=("Roboto", 12, "bold")).pack(side="left")
        
        # Validation command
        vcmd = (self.register(self.validate_number), '%P')
        
        entry = ctk.CTkEntry(top_frame, textvariable=variable, width=50, height=25, validate="key", validatecommand=vcmd)
        entry.pack(side="right")
        
        # Slider
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, variable=variable)
        slider.pack(fill="x", pady=(5, 0))
        

    def validate_number(self, value):
        """Ensures only numbers are typed into entries"""
        if value == "": return True
        return value.isdigit()

    def toggle_fps_slider(self):
        pass

    def toggle_color_depth(self):
        pass

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
        self.btn_convert.configure(state="disabled", text="Processing...")
        
        t = threading.Thread(target=self.process_video, args=(self.input_path.get(), save_path))
        t.daemon = True
        t.start()

    def rgb_to_hex(self, r, g, b):
        return f"#{r:02X}{g:02X}{b:02X}"

    def quantize(self, val, levels=16):
        if levels <= 1: return 255
        step = 256 // levels
        return min(255, (val // step) * step)

    def getAverageL(self, image):
        im = np.array(image)
        w, h = im.shape
        return np.average(im.reshape(w * h))

    def process_frame_ascii(self, frame_data):
        """Worker function for ThreadPool. Converts 1 frame to ASCII."""
        frame, cols, scale, color_mode, style, width = frame_data
        
        # Convert CV2 frame to PIL
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_frame = Image.fromarray(frame_rgb)

        # Apply Color Mode
        if color_mode == "grayscale":
            pil_frame = pil_frame.convert('L').convert('RGB')
        elif color_mode == "pure_bw":
            gray = pil_frame.convert('L')
            bw = gray.point(lambda x: 0 if x < 128 else 255, '1')
            pil_frame = bw.convert('RGB')

        ascii_chars = []
        ascii_colors = []

        if style == "block":
            W, H = pil_frame.size
            w_tile = W / cols
            h_tile = w_tile / scale
            rows = int(H / h_tile)
            
            for j in range(rows):
                y1 = int(j * h_tile)
                y2 = int((j + 1) * h_tile)
                if j == rows - 1: y2 = H
                row_chars = []
                row_colors = []
                for i in range(cols):
                    x1 = int(i * w_tile)
                    x2 = int((i + 1) * w_tile)
                    if i == cols - 1: x2 = W
                    
                    tile = pil_frame.crop((x1, y1, x2, y2))
                    color_avg = np.array(tile).mean(axis=(0, 1)).astype(int)
                    row_chars.append(CHARS_BLOCK)
                    row_colors.append(tuple(color_avg))
                ascii_chars.append(row_chars)
                ascii_colors.append(row_colors)
        else:
            # Standard ASCII Logic
            image = pil_frame.convert('L')
            W, H = image.size
            w = W / cols
            h = w / scale
            rows = int(H / h)
            
            for j in range(rows):
                y1 = int(j * h)
                y2 = int((j + 1) * h)
                if j == rows - 1: y2 = H
                row_chars = []
                row_colors = []
                for i in range(cols):
                    x1 = int(i * w)
                    x2 = int((i + 1) * w)
                    if i == cols - 1: x2 = W
                    
                    # Grayscale for char selection
                    img_gray = image.crop((x1, y1, x2, y2))
                    im_arr = np.array(img_gray)
                    avg = np.average(im_arr) if im_arr.size > 0 else 0
                    
                    # Color for text color
                    img_color = pil_frame.crop((x1, y1, x2, y2))
                    color_avg = np.array(img_color).mean(axis=(0, 1)).astype(int)
                    
                    gsval = GSCALE[int(((255 - avg) * 14) / 255)]
                    row_chars.append(gsval)
                    row_colors.append(tuple(color_avg))
                ascii_chars.append(row_chars)
                ascii_colors.append(row_colors)
                
        return ascii_chars, ascii_colors

    def process_video(self, input_file, output_file):
        try:
            cap = cv2.VideoCapture(input_file)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            if self.use_source_fps.get():
                tgt_fps = fps
            else:
                tgt_fps = self.fps_var.get()
            
            width = self.width_var.get()
            style = self.style_var.get()
            thresh = self.threshold_var.get()
            color_levels = self.color_depth_var.get()
            color_mode = self.bw_mode.get()
            scale = 0.43
            frame_step = max(1, int(fps / tgt_fps))
            
            pen_registry = {}
            next_pen_id = 0
            
            prev_frame_data = None
            buffered_xml = None
            buffered_start_ms = 0
            buffered_duration_ms = 0
            body_content = []

            frame_idx = 0
            curr_ms = 0
            
            # --- MULTITHREADING SETUP ---
            chunk_size = 10
            
            executor = ThreadPoolExecutor(max_workers=4)

            while True:
                frames_to_process = []
                for _ in range(chunk_size):
                    ret, frame = cap.read()
                    if not ret: break
                    
                    if frame_idx % frame_step == 0:
                        frames_to_process.append(
                            (frame, width, scale, color_mode, style, width)
                        )
                    
                    frame_idx += 1
                    
                if not frames_to_process:
                    break

                results = list(executor.map(self.process_frame_ascii, frames_to_process))

                for (ascii_chars, ascii_colors) in enumerate(results):
                    step_ms = (1000/fps) * frame_step
                    
                    is_duplicate = False
                    if prev_frame_data is not None and thresh > 0:
                        diff = 0
                        mid = len(ascii_colors)//2
                        row1 = prev_frame_data[mid]
                        row2 = ascii_colors[mid]
                        diff = sum(abs(sum(c1) - sum(c2)) for c1, c2 in zip(row1, row2))
                        
                        if diff < (thresh * 100):
                            is_duplicate = True

                    frame_duration = int(step_ms)

                    if is_duplicate:
                        buffered_duration_ms += frame_duration
                    else:
                        if buffered_xml is not None:
                            body_content.append(f'<p t="{int(buffered_start_ms)}" d="{int(buffered_duration_ms)}">{buffered_xml}</p>')

                        frame_xml = ""
                        for row_chars, row_colors in zip(ascii_chars, ascii_colors):
                            curr_hex = None
                            curr_span = ""
                            
                            for char, color in zip(row_chars, row_colors):
                                r, g, b = color
                                r = self.quantize(r, color_levels)
                                g = self.quantize(g, color_levels)
                                b = self.quantize(b, color_levels)
                                hex_c = self.rgb_to_hex(r, g, b)
                                
                                if hex_c not in pen_registry:
                                    pen_registry[hex_c] = next_pen_id
                                    next_pen_id += 1
                                
                                display_char = char
                                if char == '"': display_char = '" '
                                elif char == '`': display_char = '` '
                                
                                if hex_c == curr_hex:
                                    curr_span += display_char
                                else:
                                    if curr_hex is not None:
                                        pid = pen_registry[curr_hex]
                                        safe_txt = curr_span.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                        frame_xml += f'<s p="{pid}">{safe_txt}</s>'
                                    curr_hex = hex_c
                                    curr_span = display_char
                            
                            if curr_hex is not None:
                                pid = pen_registry[curr_hex]
                                safe_txt = curr_span.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                frame_xml += f'<s p="{pid}">{safe_txt}</s>'
                            frame_xml += "\n"

                        buffered_xml = frame_xml
                        buffered_start_ms = curr_ms
                        buffered_duration_ms = frame_duration
                        prev_frame_data = ascii_colors

                    curr_ms += step_ms
                
                prog = frame_idx / total
                self.progressbar.set(prog)
                self.lbl_status.configure(text=f"Processed: {int(prog*100)}% | Pens: {len(pen_registry)}")
            if buffered_xml is not None:
                body_content.append(f'<p t="{int(buffered_start_ms)}" d="{int(buffered_duration_ms)}">{buffered_xml}</p>')

            cap.release()
            executor.shutdown()
            
            # Save File
            self.lbl_status.configure(text="Saving XML file...")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n')
                f.write('<timedtext format="3">\n<head>\n')
                for color, pid in pen_registry.items():
                    f.write(f'  <pen id="{pid}" fc="{color}" ft="3" bo="0" ec="0" />\n')
                f.write('</head>\n<body>\n')
                f.write("\n".join(body_content))
                f.write('\n</body></timedtext>')
            
            file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
            self.progressbar.set(1)
            self.lbl_status.configure(text=f"Done! Size: {file_size_mb:.2f} MB")
            self.btn_convert.configure(state="normal", text="GENERATE SUBTITLE FILE")
            messagebox.showinfo("Success", f"Saved: {output_file}\nSize: {file_size_mb:.2f} MB")
            self.is_processing = False
            
        except Exception as e:
            self.lbl_status.configure(text=f"Error: {str(e)}")
            self.btn_convert.configure(state="normal")
            self.is_processing = False
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = DetailedYTTConverter()
    app.mainloop()