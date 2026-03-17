# IntelFetch - Ventana "Acerca de" RÉPLICA EXACTA DE WORDY
import tkinter as tk
from config import settings
from core.i18n import _
import os
from utils.image_manager import create_image_button

class AboutWindow(tk.Toplevel):
    """Réplica 1:1 de la ventana About de Wordy."""
    
    def __init__(self, parent, image_manager):
        super().__init__(parent)
        self.image_manager = image_manager
        
        # Ocultar inmediatamente para evitar flash visual
        self.withdraw()
        
        self.title(_("settings.about"))
        self.geometry("300x181")
        self.config(bg=settings.COLOR_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        # Icono HD Forzado (Usamos iconbitmap para que Windows elija la capa nítida)
        try:
            if settings.LOGO_ICO and os.path.exists(settings.LOGO_ICO):
                self.iconbitmap(settings.LOGO_ICO)
        except:
            pass
            
        self._create_widgets()
        self._center_window()
        self.deiconify()

    def _create_widgets(self):
        # Frame principal con padding exacto de Wordy
        frame_info = tk.Frame(self, bg=settings.COLOR_BG)
        frame_info.pack(pady=15, padx=15, fill="both", expand=True)

        frame_info.grid_columnconfigure(0, weight=0)
        frame_info.grid_columnconfigure(1, weight=1)

        # Robot: Imagen 120x120 exactos
        robot_photo = self.image_manager.load_tk("robot.png", size=(120, 120))
        if robot_photo:
            img_label = tk.Label(frame_info, image=robot_photo, bg=settings.COLOR_BG)
            img_label.image = robot_photo 
            img_label.grid(row=0, column=0, padx=(0, 10), rowspan=2, sticky="nsew")

        # Mensaje: Wraplength ajustado para que no se corte
        message = tk.Label(
            frame_info, 
            text=_("info.developed_by"),
            justify="center", 
            bg=settings.COLOR_BG, 
            fg="#FFFFFF", # Blanco puro
            font=("Segoe UI", 11, "bold"),
            wraplength=160 # Reducido un poco para dar margen lateral
        )
        message.grid(row=0, column=1, sticky="nsew", pady=(5, 10))

        # Botón Cerrar: Tamaño exacto de Wordy (110, 35)
        btn_close = create_image_button(
            frame_info, _("button.close"), self.destroy,
            self.image_manager, "boton_blue.png", (110, 35)
        )
        btn_close.grid(row=1, column=1, sticky="n")

    def _center_window(self):
        self.update_idletasks()
        width = 300
        height = 181
        # Centrar respecto a la pantalla
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        x = (pantalla_ancho // 2) - (width // 2)
        y = (pantalla_alto // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
