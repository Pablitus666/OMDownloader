# OMDownloader - Entry Point (Blindaje Senior v1.3)
import os
import sys
import logging
import traceback

def show_fatal_error(message):
    """Muestra un mensaje de error nativo de Windows si la UI falla al cargar."""
    try:
        import ctypes
        full_msg = f"ERROR CRÍTICO AL ARRANCAR OMDownloader:\n\n{message}\n\nEl programa se cerrará."
        ctypes.windll.user32.MessageBoxW(0, full_msg, "OMDownloader - Error Fatal", 0x10)
    except:
        print(message)

def check_ffmpeg():
    """Verifica si ffmpeg está disponible en el sistema (Opcional pero recomendado)."""
    import shutil
    return shutil.which("ffmpeg") is not None

def main():
    """Arranque blindado con lazy loading de componentes pesados."""
    try:
        # 1. SILENCIAR RUIDO ANTES DE NADA
        logging.getLogger('telethon.crypto.libssl').setLevel(logging.CRITICAL)

        # 2. IMPORTACIONES DINÁMICAS (CAPTURA ERRORES DE LIBRERÍAS FALTANTES)
        try:
            import customtkinter as ctk
            from tkinterdnd2 import TkinterDnD
            from gui.app import OMDownloaderApp
            from utils.logger import logger
            from config import settings
            from core.services import services
            from core.fonts import load_custom_fonts
            from utils.resources import get_resource_path
        except ImportError as e:
            show_fatal_error(f"Falta una librería crítica: {str(e)}\nEjecuta 'pip install -r requirements.txt'")
            sys.exit(1)

        # 3. CONFIGURACIÓN DE IDENTIDAD (WINDOWS)
        if sys.platform == "win32":
            import ctypes
            try:
                myappid = f"pablotellez.{settings.APP_NAME}.{settings.VERSION}"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except: pass

        # 4. CARGA DE RECURSOS
        fonts_dir = get_resource_path("assets/fonts")
        load_custom_fonts(fonts_dir)
        
        # 5. INICIALIZAR ENTORNO DnD
        try:
            root = TkinterDnD.Tk()
        except Exception as e:
            show_fatal_error(f"Fallo al inicializar entorno Drag & Drop: {str(e)}")
            sys.exit(1)
        
        # 6. CHEQUEO FFmpeg (AVISO NO BLOQUEANTE)
        if not check_ffmpeg():
            logger.warning("FFmpeg no detectado. Las descargas de alta calidad de YT-DLP podrían fallar.")
        
        # 7. CARGA DE LA APP
        app = OMDownloaderApp(root)
        
        # 8. FORZAR ICONO (REDUNDANCIA SENIOR)
        if os.path.exists(settings.LOGO_ICO):
            def _force_icon():
                try:
                    root.iconbitmap(settings.LOGO_ICO)
                    root.wm_iconbitmap(settings.LOGO_ICO)
                except: pass
            root.after(300, _force_icon)

        logger.info(f"--- {settings.APP_NAME} Iniciado correctamente ---")
        root.mainloop()
            
    except Exception as e:
        error_detail = traceback.format_exc()
        try:
            from utils.logger import logger
            logger.critical(f"Error fatal en el arranque: {error_detail}")
        except: pass
        
        show_fatal_error(f"Error inesperado: {str(e)}\n\nDetalle técnico guardado en logs.")
        
        # Intento de shutdown seguro
        try:
            from core.services import services
            services.shutdown()
        except: pass
        sys.exit(1)

if __name__ == "__main__":
    main()
