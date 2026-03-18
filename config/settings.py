# OMDownloader - Configuración Visual y Persistencia Robustas
import os
import json
from utils.resources import get_data_path

# Información del Proyecto
APP_NAME = "OMDownloader"
VERSION = "1.0.0"
AUTHOR = "Pablo Téllez A."
YEAR = "2026"

# Paleta de Colores Élite
COLOR_BG = "#023047"
COLOR_BG_DARK = "#011E23"
COLOR_PRIMARY = "#0B1F2A"
COLOR_ACCENT = "#fcbf49"
COLOR_TEXT = "white"
COLOR_TEXT_DARK = "#023047"
COLOR_BG_WHITE = "#FFFFFF"
COLOR_HOVER = "#15262D"

# Estados
COLOR_SUCCESS = "#28A745"
COLOR_ERROR = "#F44336"
COLOR_TEXT_DIM = "#8892B0"

# Fuentes (Segoe UI Historic - Nivel Élite)
FONT_FAMILY = "Segoe UI Historic"
FONT_BOLD = "Segoe UI Historic Bold"
FONT_SIZE_H1 = 22
FONT_SIZE_BODY = 14
FONT_SIZE_SMALL = 12

# Ventana
WINDOW_SIZE = "950x650"
MIN_WINDOW_SIZE = (850, 550)

# Rutas de Recursos (Nueva sección Élite para iconos HD)
from utils.resources import image_path, get_resource_path
from utils.logger import logger # Importación para logs senior

LOGO_ICO = get_resource_path("assets/images/icomulti.ico")
LOGO_PNG = get_resource_path("assets/images/logo.png")

# Rutas de Datos (Nivel Élite: Datos en AppData, Descargas en Downloads)
DATA_DIR = os.path.abspath(get_data_path("data"))
CONFIG_FILE = os.path.join(DATA_DIR, "settings_v1.json")

# Definir carpeta de descargas por defecto oficial de Windows
DEFAULT_DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads", "OMDownloader")
DOWNLOADS_DIR = DEFAULT_DOWNLOADS

# Límites de Rendimiento (Fase 4)
# --- CONFIGURACIÓN DE RENDIMIENTO ÉLITE ---
MAX_PARALLEL_DOWNLOADS = 3
MAX_PARALLEL_SCANS = 2
MAX_PARALLEL_THUMBS = 2

# --- TIMEOUTS DE SEGURIDAD ---
TIMEOUT_ANALYSIS = 45 # segundos
TIMEOUT_SCAN = 300    # 5 minutos
TIMEOUT_DOWNLOAD = 7200 # 2 horas


# Variables Globales de Estado
TELEGRAM_API_ID = 0
TELEGRAM_API_HASH = ""
TELEGRAM_SESSION_NAME = "omdownloader_session"

def load_config():
    """Carga la configuración de forma ultra-segura con autorreparación de tipos y rutas."""
    global TELEGRAM_API_ID, TELEGRAM_API_HASH, DOWNLOADS_DIR
    
    # 1. Asegurar que el directorio de datos base existe
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    # 2. Definir la ruta por defecto ideal (Carpeta Descargas del Usuario)
    if not os.path.exists(DEFAULT_DOWNLOADS):
        try: os.makedirs(DEFAULT_DOWNLOADS, exist_ok=True)
        except: pass

    needs_repair = False
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # REPARACIÓN DE TIPOS (Punto de fallo en PCs con config corrupta)
                raw_id = data.get("api_id", 0)
                try:
                    TELEGRAM_API_ID = int(raw_id) if raw_id else 0
                except (ValueError, TypeError):
                    TELEGRAM_API_ID = 0
                    needs_repair = True
                
                TELEGRAM_API_HASH = str(data.get("api_hash", ""))
                saved_path = data.get("downloads_dir", "")

                if saved_path:
                    DOWNLOADS_DIR = os.path.normpath(saved_path)
                else:
                    DOWNLOADS_DIR = DEFAULT_DOWNLOADS
                    needs_repair = True

            if needs_repair:
                save_config(TELEGRAM_API_ID, TELEGRAM_API_HASH, DOWNLOADS_DIR)

        except Exception as e:
            from utils.logger import logger
            logger.error(f"Settings: Error al leer configuración: {e}")
            DOWNLOADS_DIR = DEFAULT_DOWNLOADS
    else:
        DOWNLOADS_DIR = DEFAULT_DOWNLOADS
import time

def save_config(api_id, api_hash, downloads_dir):
    """Guarda la configuración de forma atómica y robusta contra bloqueos de Windows."""
    data = {
        "api_id": int(api_id),
        "api_hash": api_hash,
        "downloads_dir": downloads_dir
    }
    
    temp_file = CONFIG_FILE + ".tmp"
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # 1. Escribir en archivo temporal
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            
            # 2. Reemplazo atómico (os.replace maneja el borrado en Windows de forma más limpia)
            # Si el archivo está bloqueado, os.replace fallará, por eso el retry.
            if os.path.exists(temp_file):
                os.replace(temp_file, CONFIG_FILE)
            
            return True
            
        except OSError as e:
            if e.winerror == 32 and attempt < max_retries - 1:
                time.sleep(0.1 * (attempt + 1)) # Espera exponencial corta
                continue
            print(f"Error crítico al guardar configuración: {e}")
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass
            return False
        except Exception as e:
            print(f"Error inesperado al guardar configuración: {e}")
            return False
    return False

# Carga inicial
load_config()
