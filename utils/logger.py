# OMDownloader - Logger Estructurado Senior
import logging
import os
from logging.handlers import RotatingFileHandler
from utils.resources import get_data_path

class StructuredLogger:
    """Sistema de logging con rotación y etiquetas estructuradas."""
    
    def __init__(self):
        log_dir = get_data_path("data/logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        self.log_file = os.path.join(log_dir, "omdownloader.log")
        
        # Formato: [TIEMPO] [NIVEL] [MODULO] Mensaje
        format_str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        
        # Handler de archivo con rotación (5MB por archivo, max 3 backups)
        file_handler = RotatingFileHandler(
            self.log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(format_str, date_format))
        
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(format_str, date_format))
        
        # Configuración raíz
        logging.basicConfig(
            level=logging.INFO,
            handlers=[file_handler, console_handler]
        )

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

# Inicializar sistema
StructuredLogger()

# Loggers específicos para cada módulo
logger = logging.getLogger("OMDownloader")
dl_logger = logging.getLogger("Downloader")
tg_logger = logging.getLogger("TelegramEngine")
db_logger = logging.getLogger("Database")
