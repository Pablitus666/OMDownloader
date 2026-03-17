# OMDownloader - Diálogos y Mensajes Premium
import tkinter as tk
import customtkinter as ctk
import os
from config import settings

class MessageWindow(tk.Toplevel):
    """Ventana de mensaje profesional centrada con iconografía de alta calidad."""
    def __init__(self, master, title, message, image_manager, **kwargs):
        super().__init__(master)
        self.withdraw() # Ocultar mientras se configura
        
        self.title(title)
        self.geometry("420x200") # Un poco más ancha para el icono
        self.resizable(False, False)
        self.configure(bg=settings.COLOR_BG)
        
        # Blindaje para que no aparezca en la barra de tareas
        self.transient(master)
        self.grab_set()

        # Icono de ventana (Barra de título)
        try:
            if settings.LOGO_ICO and os.path.exists(settings.LOGO_ICO):
                self.iconbitmap(settings.LOGO_ICO)
        except:
            pass
            
        self._create_widgets(title, message, image_manager)
        self._center_window()
        self.deiconify()

    def _create_widgets(self, title, message, image_manager):
        container = tk.Frame(self, bg=settings.COLOR_BG)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Determinar si es una alerta para mostrar el icono de alerta.png
        content_frame = tk.Frame(container, bg=settings.COLOR_BG)
        content_frame.pack(fill="x", expand=True)

        if "ALERTA" in title.upper() or "WARNING" in title.upper() or "ERROR" in title.upper():
            # Cargar imagen de alerta.png desde png_master (automático vía image_manager)
            alert_img = image_manager.load_tk("alerta.png", size=(60, 60))
            if alert_img:
                icon_label = tk.Label(content_frame, image=alert_img, bg=settings.COLOR_BG)
                icon_label.image = alert_img
                icon_label.pack(side="left", padx=(0, 15))

        # Mensaje
        msg_label = tk.Label(
            content_frame, text=message, 
            bg=settings.COLOR_BG, 
            fg="#FFFFFF", 
            font=("Segoe UI", 11, "bold"),
            wraplength=280 if "ALERTA" in title.upper() else 350, 
            justify="left" if "ALERTA" in title.upper() else "center"
        )
        msg_label.pack(side="left", fill="both", expand=True)

        # Botón de Cierre
        from utils.image_manager import create_image_button
        btn_close = create_image_button(
            container, "Cerrar", self.destroy,
            image_manager, "boton_blue.png", (120, 35)
        )
        btn_close.pack(side="bottom", pady=(10, 0))

    def _center_window(self):
        self.update_idletasks()
        width = 420
        height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

def show_message(master, title_key, message_key, image_manager):
    from core.i18n import _
    title = _(title_key) if "." in title_key else title_key
    message = _(message_key) if "." in message_key else message_key
    MessageWindow(master, title, message, image_manager)
