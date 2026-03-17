# OMDownloader - Service Locator con Shutdown Atómico (Plan Maestro v1)
from concurrent.futures import ThreadPoolExecutor
from core.queue_manager import QueueManager
from core.database import DatabaseManager
from core.net import net_session
from utils.logger import logger
from utils.thumb_cache import thumb_cache
import os
import time
import threading

class Services:
    """Contenedor central de servicios con Gestión de Ciclo de Vida Élite."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Services, cls).__new__(cls)
            cls._instance._init_services()
        return cls._instance

    def _init_services(self):
        """Inicializa los servicios con control de recursos."""
        logger.info("Services: Iniciando ciclo de vida Senior...")
        
        from config import settings
        from core.event_bus import event_bus # Importación local para evitar circularidad
        
        # Semáforos de Concurrencia (Punto 1)
        self._scan_semaphore = threading.Semaphore(settings.MAX_PARALLEL_SCANS)
        self._thumb_semaphore = threading.Semaphore(settings.MAX_PARALLEL_THUMBS)
        
        # FASE 2: Concurrencia Limitada (Global)
        max_workers = min(10, (os.cpu_count() or 2) * 2)
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="OMTask")
        
        self.database = DatabaseManager()
        self.queue = QueueManager()
        self.image_manager = None
        self.net = net_session 
        
        self._metadata_cache = {}
        self._cache_lock = threading.Lock()
        self._is_shutting_down = False
        
        # ACTIVACIÓN DEL WATCHDOG (Fase de Mantenimiento Élite)
        event_bus.subscribe("history_updated", lambda _: self.run_memory_watchdog())
        event_bus.subscribe("tasks_cleared", lambda _: self.run_memory_watchdog())
        
        logger.info(f"Services: Sistema activo (Workers: {max_workers}).")

    def submit_scan(self, func, *args, **kwargs):
        """Envía un escaneo con limitación por semáforo."""
        def _wrapped():
            with self._scan_semaphore:
                return func(*args, **kwargs)
        return self.submit(_wrapped)

    def submit_thumb(self, func, *args, **kwargs):
        """Envía carga de miniatura con limitación por semáforo."""
        def _wrapped():
            with self._thumb_semaphore:
                return func(*args, **kwargs)
        return self.submit(_wrapped)

    def submit(self, func, *args, **kwargs):
        """Envía tareas al pool central con protección de shutdown."""
        if self._is_shutting_down: return None
        return self.executor.submit(func, *args, **kwargs)

    def set_image_manager(self, manager):
        """Asigna el gestor de imágenes global."""
        self.image_manager = manager

    def get_metadata(self, url):
        """Obtiene metadatos con caché y protección de timeout (Punto 4)."""
        if not url: return None
        
        now = time.time()
        with self._cache_lock:
            if url in self._metadata_cache:
                ts, data = self._metadata_cache[url]
                if (now - ts) < 600: # 10 min cache
                    return data

        is_tg = any(x in url for x in ["t.me/", "web.telegram.org", "telegram.me/"]) or url.strip().startswith("@")
        
        try:
            # FASE 4: Protección contra URLs maliciosas mediante timeouts en motores
            if is_tg:
                metadata = self.queue.telegram_engine.get_info(url)
            else:
                metadata = self.queue.ytdlp_engine.get_info(url)
            
            if metadata:
                with self._cache_lock:
                    self._metadata_cache[url] = (now, metadata)
            return metadata
        except Exception as e:
            logger.error(f"Watchdog: Error analizando URL {url[:30]}... : {e}")
            return None

    def run_memory_watchdog(self):
        """Punto 3: Limpieza periódica de cachés para sesiones largas."""
        with self._cache_lock:
            now = time.time()
            # Limpiar entradas de más de 30 min
            self._metadata_cache = {k: v for k, v in self._metadata_cache.items() if (now - v[0]) < 1800}
        
        thumb_cache.clear() # Limpiar miniaturas para liberar RAM de PIL
        logger.debug("Watchdog: Limpieza de memoria completada.")

    def shutdown(self):
        """Punto 2: Shutdown Atómico. Sin hilos zombies."""
        if self._is_shutting_down: return
        self._is_shutting_down = True
        
        logger.info("Services: Iniciando secuencia de apagado atómico...")
        
        # 1. Detener Cola de descargas inmediatamente
        try:
            self.queue.clear_all()
            logger.info("Services: Cola de descargas detenida.")
        except: pass

        # 2. Desconectar Telegram (Síncrono para asegurar cierre de sesión)
        if self.queue.telegram_engine:
            try:
                self.queue.telegram_engine.disconnect()
                logger.info("Services: Telegram desconectado.")
            except: pass

        # 3. Apagar Executor Pool (Forzado)
        try:
            self.executor.shutdown(wait=False, cancel_futures=True)
            logger.info("Services: Executor pool cerrado.")
        except: pass

        # 4. Limpiar cachés finales
        if self.image_manager:
            self.image_manager.clear_cache()
        thumb_cache.clear()
        
        logger.info("Services: ¡APAGADO COMPLETADO EXITOSAMENTE!")

# Instancia global
services = Services()
