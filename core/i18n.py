# IntelFetch - Sistema de Internacionalización (i18n)
import json
import locale
import os
from utils.resources import locale_path
from utils.logger import logger

class I18nManager:
    """Gestiona las traducciones de la aplicación."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.current_lang = self._get_system_language()
        self.translations = {}
        self.load_language(self.current_lang)

    def _get_system_language(self):
        """Detecta el idioma del SO (ej. 'es', 'en')."""
        try:
            lang = locale.getdefaultlocale()[0]
            if lang:
                code = lang.split('_')[0].lower()
                # Verificar si el idioma existe en nuestros locales
                if os.path.exists(locale_path(f"{code}.json")):
                    return code
        except:
            pass
        return "es" # Fallback a español por defecto

    def load_language(self, lang_code):
        """Carga el archivo JSON de traducción."""
        file_name = f"{lang_code}.json"
        full_path = locale_path(file_name)
        
        if not os.path.exists(full_path):
            logger.warning(f"Idioma {lang_code} no encontrado. Cargando español (fallback).")
            full_path = locale_path("es.json")
            if not os.path.exists(full_path):
                self.translations = {}
                return

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
            logger.info(f"Idioma cargado: {lang_code}")
        except Exception as e:
            logger.error(f"Error al cargar idioma {lang_code}: {str(e)}")

    def get(self, key, default=None):
        """Obtiene una traducción por su clave exacta."""
        return self.translations.get(key, default or key)

# Función global de traducción
def _(key, default=None):
    return I18nManager().get(key, default)
