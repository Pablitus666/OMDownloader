# OMDownloader - Gestor de Imágenes Asíncrono y de Alto Rendimiento
import os
import threading
from PIL import Image, ImageTk, ImageFilter
import customtkinter as ctk
import tkinter as tk
from utils.resources import image_path
from config import settings
from core.services import services
from utils.logger import logger

def add_shadow(image: Image.Image, offset=(3, 3), shadow_color=(0, 0, 0, 90), blur_radius=3, border=5):
    """Añade una sombra paralela profesional (Réplica Wordy)."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    pad = max(abs(offset[0]), abs(offset[1])) + border
    total_width = image.width + 2 * pad
    total_height = image.height + 2 * pad
    
    canvas = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    shadow_layer = Image.new('RGBA', image.size, shadow_color)
    canvas.paste(shadow_layer, (pad + offset[0], pad + offset[1]), image.getchannel('A'))
    
    if blur_radius > 0:
        canvas = canvas.filter(ImageFilter.GaussianBlur(blur_radius))
    
    canvas.paste(image, (pad, pad), image)
    return canvas

def add_relief(image: Image.Image, intensity=2):
    """Aplica un efecto de relieve de 3 capas (Réplica Wordy)."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    width, height = image.size
    light_layer = Image.new('RGBA', (width, height), (255, 255, 255, 120))
    dark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 120))
    relief_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    relief_canvas.paste(dark_layer, (intensity, intensity), image.getchannel('A'))
    relief_canvas.paste(light_layer, (-intensity, -intensity), image.getchannel('A'))
    relief_canvas.paste(image, (0, 0), image)
    return relief_canvas

class ImageManager:
    """Gestiona la carga de imágenes asíncrona y con caché (Fase 7 - Gestión RAM)."""
    
    def __init__(self, root):
        self.root = root
        self.cache_ctk = {}
        self.cache_tk = {}
        self.lock = threading.Lock()

    def clear_cache(self):
        """Libera la memoria de todas las imágenes cacheadas."""
        with self.lock:
            self.cache_ctk.clear()
            self.cache_tk.clear()
            logger.info("ImageManager: Caché de imágenes liberada.")

    def load(self, filename, size=None):
        """Retorna una CTkImage de forma síncrona (para elementos críticos de UI)."""
        cache_key = (filename, size)
        with self.lock:
            if cache_key in self.cache_ctk:
                return self.cache_ctk[cache_key]

        path = image_path(filename)
        if not os.path.exists(path): return None

        try:
            img = Image.open(path).convert("RGBA")
            if filename not in ["logo.png", "robot.png"]:
                img = add_relief(img, intensity=2)
                img = add_shadow(img, offset=(3, 3), blur_radius=3)
            
            display_size = size if size else img.size
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=display_size)
            
            with self.lock:
                self.cache_ctk[cache_key] = ctk_img
            return ctk_img
        except Exception as e:
            logger.error(f"Error cargando imagen {filename}: {e}")
            return None

    def load_async(self, filename, size=None, callback=None):
        """Carga una imagen en segundo plano (Fase 8) y ejecuta un callback al terminar."""
        def task():
            img = self.load(filename, size)
            if callback:
                self.root.after(0, lambda: callback(img))
        
        services.executor.submit(task)

    def load_tk(self, filename, size=None, is_button=False):
        """Retorna una PhotoImage de forma síncrona."""
        cache_key = (filename, size, is_button)
        with self.lock:
            if cache_key in self.cache_tk:
                return self.cache_tk[cache_key]

        path = image_path(filename)
        if not os.path.exists(path): return None

        try:
            img = Image.open(path).convert("RGBA")
            if size:
                img = img.resize(size, Image.LANCZOS)
            
            if filename not in ["logo.png", "robot.png"]:
                if is_button:
                    img = add_shadow(img, offset=(3, 3), shadow_color=(0, 0, 0, 100), blur_radius=3, border=5)
                else:
                    img = add_relief(img, intensity=2)
                    img = add_shadow(img, offset=(3, 3), shadow_color=(0, 0, 0, 90), blur_radius=3)
                
            tk_img = ImageTk.PhotoImage(img)
            with self.lock:
                self.cache_tk[cache_key] = tk_img
            return tk_img
        except Exception as e:
            logger.error(f"Error cargando TK imagen {filename}: {e}")
            return None

def get_real_bg(widget):
    curr = widget
    while curr:
        try:
            color = None
            if hasattr(curr, "cget"):
                for attr in ["fg_color", "bg"]:
                    try:
                        val = curr.cget(attr)
                        if val and val != "transparent":
                            color = val
                            break
                    except: continue
            
            if color:
                if isinstance(color, (list, tuple)):
                    import customtkinter as ctk
                    appearance_mode = ctk.get_appearance_mode()
                    return color[0] if appearance_mode == "Light" else color[1]
                return color
        except: pass
        
        parent = getattr(curr, "master", None)
        if parent == curr: break
        curr = parent
    return settings.COLOR_BG

def create_image_button(parent, text, command, image_manager, img_name, size, text_color="#FFFFFF"):
    photo = image_manager.load_tk(img_name, size=size, is_button=True)
    real_bg = get_real_bg(parent)
    
    btn = tk.Button(parent, text=text, image=photo, compound="center",
                   command=command, bg=real_bg, fg=text_color,
                   activebackground=real_bg, activeforeground="#fcbf49",
                   bd=0, relief="flat", highlightthickness=0,
                   padx=0, pady=0, borderwidth=0, takefocus=0,
                   cursor="hand2", font=("Segoe UI", 12, "bold"))
    
    btn.image = photo 
    btn.bind("<Enter>", lambda e: btn.config(fg="#fcbf49"))
    btn.bind("<Leave>", lambda e: btn.config(fg=text_color))
    
    def on_press(e): btn.config(anchor="s")
    def on_release(e): btn.config(anchor="center")
    
    btn.bind("<Button-1>", on_press)
    btn.bind("<ButtonRelease-1>", on_release)
    
    return btn
