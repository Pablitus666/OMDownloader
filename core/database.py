# IntelFetch - Gestor de Base de Datos (SQLite)
import sqlite3
import os
import threading
from utils.resources import get_data_path
from utils.logger import logger

class DatabaseManager:
    """Maneja la persistencia de datos de OMDownloader con bloqueo preventivo de hilos."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        self.db_path = os.path.join(get_data_path("data"), "history.db")
        # FASE 1: Lock preventivo para evitar colisiones entre hilos de descarga
        self.lock = threading.RLock()
        
        try:
            with self.lock:
                with self._get_connection() as conn:
                    # OPTIMIZACIÓN DE RENDIMIENTO ÉLITE
                    conn.execute("PRAGMA journal_mode=WAL;") 
                    conn.execute("PRAGMA synchronous=NORMAL;") 
                    
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS history (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            video_id TEXT,
                            title TEXT,
                            uploader TEXT,
                            url TEXT,
                            file_path TEXT,
                            file_size INTEGER,
                            status TEXT,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_video_id ON history(video_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON history(status)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp)")
                    
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS settings (
                            key TEXT PRIMARY KEY,
                            value TEXT
                        )
                    """)
                    conn.commit()
            logger.info("Base de datos inicializada correctamente.")
        except Exception as e:
            logger.error(f"Error al inicializar la base de datos: {str(e)}")

    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=30)

    def add_history(self, task_data):
        """Guarda un registro de descarga terminada con bloqueo de seguridad."""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    v_id = task_data.get('video_id', task_data.get('id', 'N/A'))
                    cursor.execute("""
                        INSERT INTO history (video_id, title, uploader, url, file_path, file_size, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        v_id,
                        task_data.get('title', 'Sin título'),
                        task_data.get('uploader', 'Desconocido'),
                        task_data.get('url', ''),
                        task_data.get('file_path', ''),
                        task_data.get('file_size', 0),
                        task_data.get('status', 'finished')
                    ))
                    conn.commit()
            logger.info(f"Historial guardado en BD: {task_data.get('title')}")
        except Exception as e:
            logger.error(f"Error al guardar historial: {str(e)}")

    def check_if_downloaded(self, item_id):
        """Verifica si un ítem ya fue descargado con éxito."""
        if not item_id: return False
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT video_id FROM history WHERE video_id = ? AND status = 'finished'", (str(item_id),))
                    return cursor.fetchone() is not None
        except:
            return False

    def get_history(self, limit=50, offset=0):
        """Obtiene descargas con soporte para paginación."""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT ? OFFSET ?", (limit, offset))
                    return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener historial: {str(e)}")
            return []

    def get_history_count(self):
        """Obtiene el número total de registros."""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM history")
                    return cursor.fetchone()[0]
        except:
            return 0

    def clear_history(self):
        """Borra todo el historial."""
        try:
            with self.lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM history")
                    conn.commit()
            logger.info("Historial de base de datos borrado.")
        except Exception as e:
            logger.error(f"Error al borrar historial: {str(e)}")

