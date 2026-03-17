# OMDownloader - Entry Point (Versión Senior Final)
import customtkinter as ctk
import sys
import os
from tkinterdnd2 import TkinterDnD
from gui.app import OMDownloaderApp
from utils.logger import logger
from config import settings
from core.services import services
from core.fonts import load_custom_fonts
from utils.resources import get_resource_path

def main():
    """Arranque blindado del sistema."""
    try:
        # FASE -1: Forzar AppID para icono nítido en Barra de Tareas (Windows)
        if sys.platform == "win32":
            import ctypes
            myappid = f"pablotellez.{settings.APP_NAME}.{settings.VERSION}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # FASE 0: Cargar fuentes profesionales (Segoe UI Historic)
        fonts_dir = get_resource_path("assets/fonts")
        load_custom_fonts(fonts_dir)
        
        # Inicializar entorno DnD
        root = TkinterDnD.Tk()
        
        # Ocultar ventana durante carga para evitar parpadeos
        root.withdraw()
        
        # Carga de la aplicación principal
        app = OMDownloaderApp(root)
        
        # Centrar y mostrar
        root.update_idletasks()
        w, h = 950, 650
        x = (root.winfo_screenwidth() // 2) - (w // 2)
        y = (root.winfo_screenheight() // 2) - (h // 2)
        root.geometry(f"{w}x{h}+{x}+{y}")
        
        root.deiconify()
        
        # FASE 1: Forzar icono nítido tras renderizado (Solución definitiva)
        if os.path.exists(settings.LOGO_ICO):
            def _force_icon():
                try:
                    root.iconbitmap(settings.LOGO_ICO)
                    root.wm_iconbitmap(settings.LOGO_ICO)
                except: pass
            root.after(200, _force_icon)

        logger.info(f"--- {settings.APP_NAME} Iniciado correctamente ---")
        
        # Loop principal
        root.mainloop()
            
    except Exception as e:
        logger.critical(f"Error fatal en el arranque: {str(e)}")
        # Asegurar shutdown si falla antes del loop
        services.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()
