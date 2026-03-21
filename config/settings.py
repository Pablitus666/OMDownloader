# OMDownloader - Configuración Centralizada (Objeto Único)
import os
import json
import time
from utils.resources import get_data_path, get_resource_path

class AppSettings:
    """Clase de configuración que centraliza el estado de la aplicación."""
    
    def __init__(self):
        # Información del Proyecto
        self.APP_NAME = "OMDownloader"
        self.VERSION = "1.0.0"
        self.AUTHOR = "Pablo Téllez A."
        self.YEAR = "2026"

        # Paleta de Colores
        self.COLOR_BG = "#023047"
        self.COLOR_BG_DARK = "#011E23"
        self.COLOR_PRIMARY = "#0B1F2A"
        self.COLOR_ACCENT = "#fcbf49"
        self.COLOR_TEXT = "white"
        self.COLOR_TEXT_DARK = "#023047"
        self.COLOR_BG_WHITE = "#FFFFFF"
        self.COLOR_HOVER = "#15262D"

        # Estados
        self.COLOR_SUCCESS = "#28A745"
        self.COLOR_ERROR = "#F44336"
        self.COLOR_TEXT_DIM = "#8892B0"

        # Fuentes
        self.FONT_FAMILY = "Segoe UI Historic"
        self.FONT_BOLD = "Segoe UI Historic Bold"
        self.FONT_SIZE_H1 = 22
        self.FONT_SIZE_BODY = 14
        self.FONT_SIZE_SMALL = 12

        # Ventana
        self.WINDOW_SIZE = "950x650"
        self.MIN_WINDOW_SIZE = (850, 550)

        # Rutas de Recursos
        self.LOGO_ICO = get_resource_path("assets/images/icomulti.ico")
        self.LOGO_PNG = get_resource_path("assets/images/logo.png")

        # Rutas de Datos
        self.DATA_DIR = os.path.abspath(get_data_path("data"))
        self.CONFIG_FILE = os.path.join(self.DATA_DIR, "settings_v1.json")

        # Carpeta de descargas por defecto
        self.DEFAULT_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads", "OMDownloader")
        self.DOWNLOADS_DIR = self.DEFAULT_DOWNLOADS

        # Límites de Rendimiento
        self.MAX_PARALLEL_DOWNLOADS = 3
        self.MAX_PARALLEL_SCANS = 2
        self.MAX_PARALLEL_THUMBS = 2

        # Timeouts de Seguridad
        self.TIMEOUT_ANALYSIS = 45
        self.TIMEOUT_SCAN = 300
        self.TIMEOUT_DOWNLOAD = 7200

        # Variables de Estado de Telegram
        self.TELEGRAM_API_ID = 0
        self.TELEGRAM_API_HASH = ""
        self.TELEGRAM_SESSION_NAME = "omdownloader_session"

        # Cargar configuración al inicializar
        self.load_config()

    def load_config(self):
        """Carga los valores desde el archivo JSON si existe."""
        if not os.path.exists(self.DATA_DIR):
            os.makedirs(self.DATA_DIR, exist_ok=True)

        if not os.path.exists(self.DEFAULT_DOWNLOADS):
            try: os.makedirs(self.DEFAULT_DOWNLOADS, exist_ok=True)
            except: pass

        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Carga segura de valores
                    raw_id = data.get("api_id", 0)
                    try:
                        self.TELEGRAM_API_ID = int(raw_id) if raw_id else 0
                    except:
                        self.TELEGRAM_API_ID = 0
                    
                    self.TELEGRAM_API_HASH = str(data.get("api_hash", ""))
                    saved_path = data.get("downloads_dir", "")
                    self.DOWNLOADS_DIR = os.path.normpath(saved_path) if saved_path else self.DEFAULT_DOWNLOADS

            except Exception as e:
                print(f"Error al cargar configuración: {e}")
                self.DOWNLOADS_DIR = self.DEFAULT_DOWNLOADS
        else:
            self.DOWNLOADS_DIR = self.DEFAULT_DOWNLOADS

    def save_config(self, api_id=None, api_hash=None, downloads_dir=None):
        """Guarda el estado actual o nuevos valores de forma atómica."""
        # Actualizar atributos internos si se pasan valores nuevos
        if api_id is not None: self.TELEGRAM_API_ID = int(api_id)
        if api_hash is not None: self.TELEGRAM_API_HASH = api_hash
        if downloads_dir is not None: self.DOWNLOADS_DIR = downloads_dir

        data = {
            "api_id": self.TELEGRAM_API_ID,
            "api_hash": self.TELEGRAM_API_HASH,
            "downloads_dir": self.DOWNLOADS_DIR
        }
        
        temp_file = self.CONFIG_FILE + ".tmp"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            # Reemplazo atómico seguro en Windows
            if os.path.exists(temp_file):
                if os.path.exists(self.CONFIG_FILE):
                    os.remove(self.CONFIG_FILE)
                os.rename(temp_file, self.CONFIG_FILE)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False

# Instancia exportable
app_settings = AppSettings()
