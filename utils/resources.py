# IntelFetch - Gestión de Rutas y Recursos
import os
import sys
from pathlib import Path

def get_base_path():
    """Retorna la ruta base del proyecto, compatible con PyInstaller."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

def get_data_path(subfolder=""):
    """Retorna la ruta de datos del usuario en una ubicación oculta del sistema."""
    if sys.platform == "win32":
        # Usar LOCALAPPDATA para que no ensucie el escritorio (Nivel Profesional)
        base = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~"))) / "OMDownloader"
    else:
        base = Path.home() / ".omdownloader"
        
    path = base / subfolder
    path.mkdir(parents=True, exist_ok=True)
    return str(path)

def get_resource_path(relative_path):
    """Retorna la ruta absoluta a un recurso (dentro del proyecto/ejecutable)."""
    return str(get_base_path() / relative_path)

def image_path(filename):
    """Helper para obtener la ruta de una imagen, priorizando png_master."""
    # Intentar primero en png_master para máxima calidad
    master_path = get_resource_path(f"assets/images/png_master/{filename}")
    if os.path.exists(master_path):
        return master_path
    # Fallback a la carpeta images normal
    return get_resource_path(f"assets/images/{filename}")

def font_path(filename):
    """Helper para obtener la ruta de una fuente."""
    return get_resource_path(f"assets/fonts/{filename}")

def locale_path(filename):
    """Helper para obtener la ruta de un archivo de traducción."""
    return get_resource_path(f"assets/locales/{filename}")
