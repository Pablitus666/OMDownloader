# OMDownloader - Gestor de Fuentes Senior (Windows API)
import os
import ctypes
from utils.logger import logger

# Constantes de la API de Windows
FR_PRIVATE = 0x10
FR_NOT_ENUM = 0x20

def register_font(font_path):
    """Registra una fuente TTF en la sesión actual de Windows (Sin instalación permanente)."""
    if not os.path.exists(font_path):
        logger.error(f"Fonts: No se encontró el archivo {font_path}")
        return False

    path_buf = ctypes.create_unicode_buffer(font_path)
    
    # AddFontResourceExW es la función de nivel senior para registro privado
    res = ctypes.windll.gdi32.AddFontResourceExW(path_buf, FR_PRIVATE, 0)
    
    if res > 0:
        logger.info(f"Fonts: Registrada con éxito -> {os.path.basename(font_path)}")
        return True
    
    logger.error(f"Fonts: Fallo al registrar {os.path.basename(font_path)}")
    return False

def load_custom_fonts(fonts_dir):
    """Busca y registra todas las fuentes TTF en el directorio assets/fonts."""
    if not os.path.exists(fonts_dir):
        return
        
    for file in os.listdir(fonts_dir):
        if file.lower().endswith(".ttf"):
            register_font(os.path.join(fonts_dir, file))
