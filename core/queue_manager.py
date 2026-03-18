# OMDownloader - Gestor de Colas de Descarga (Plan Maestro v1 - Fixed)
import threading
import queue
import time
import os
import uuid
from engines.ytdlp_engine import YTDLPEngine
from engines.telegram_engine import TelegramEngine
from config import settings
from core.database import DatabaseManager
from core.i18n import _
from core.event_bus import event_bus
from utils.logger import dl_logger as logger
from utils.resources import get_data_path

class DownloadTask:
    """Representa una tarea individual de descarga con control de estado Élite."""
    def __init__(self, url, metadata, options=None):
        self.url = url
        self.metadata = metadata or {}
        self.options = options or {}
        self.id = str(uuid.uuid4())
        self.status = "waiting" # waiting, scanning, downloading, finished, error, cancelled, paused
        self.progress = 0.0
        self.speed = "0 KB/s"
        self.eta = "00:00"
        self.error_msg = ""
        self.file_path = ""
        self._is_cancelled = False
        self._is_paused = False
        self.is_telegram = any(x in url for x in ["t.me/", "web.telegram.org", "telegram.me/"]) or url.strip().startswith("@")

    def cancel(self):
        self._is_cancelled = True
        self.status = "cancelled"

    def pause(self):
        self._is_paused = True
        self.status = "paused"

    def resume(self):
        self._is_paused = False
        self.status = "downloading"

class QueueManager:
    """Gestiona la cola de descargas con hilos rastreados y PriorityQueue (Tie-break fixed)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QueueManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        self.tasks = []
        self.task_ids_set = set() 
        self.download_queue = queue.PriorityQueue()
        self.active_tasks_count = 0 
        self.active_workers_threads = {} 
        
        # FASE 4: Contador de secuencia para desempate en PriorityQueue (FIX TypeError)
        self._sequence_counter = 0
        self._sequence_lock = threading.Lock()
        
        # Inicialización de motores (la ruta se actualizará dinámicamente en cada descarga)
        self.ytdlp_engine = YTDLPEngine(download_path=settings.DOWNLOADS_DIR)
        
        try:
            self.telegram_engine = TelegramEngine(
                api_id=settings.TELEGRAM_API_ID,
                api_hash=settings.TELEGRAM_API_HASH,
                session_name=os.path.join(get_data_path("data"), settings.TELEGRAM_SESSION_NAME)
            )
        except Exception as e:
            logger.error(f"No se pudo iniciar TelegramEngine: {e}")
            self.telegram_engine = None

        self.db_manager = DatabaseManager()
        
        # FASE 10: Limitación real a 3 descargas paralelas para optimizar red
        self.max_workers = 3 
        self.lock = threading.Lock()
        
        for i in range(self.max_workers):
            threading.Thread(target=self._worker, name=f"DL-Worker-{i}", daemon=True).start()


    def _get_next_sequence(self):
        """Genera un ID de secuencia atómico para el desempatado de la cola."""
        with self._sequence_lock:
            self._sequence_counter += 1
            return self._sequence_counter

    def add_task(self, url, metadata, options=None, auto_start=True, emit_event=True, priority=10):
        """Añade una nueva tarea con soporte de prioridad y secuencia."""
        existing_id = metadata.get('id')
        
        with self.lock:
            if existing_id and str(existing_id) in self.task_ids_set:
                return None

        task = DownloadTask(url, metadata, options)
        if existing_id:
            task.id = str(existing_id)

        with self.lock:
            self.tasks.append(task)
            self.task_ids_set.add(task.id)
            if auto_start:
                self.active_tasks_count += 1
        
        if emit_event:
            event_bus.emit("task_added", task)
            
        if auto_start: 
            # Tupla: (Prioridad, Secuencia, Tarea) -> Secuencia evita el TypeError
            self.download_queue.put((priority, self._get_next_sequence(), task))
        return task

    def start_all_waiting(self):
        """Inicia todas las tareas en espera con desempate de secuencia."""
        started_count = 0
        with self.lock:
            for task in self.tasks:
                if task.status == "waiting":
                    task.status = "downloading"
                    self.download_queue.put((10, self._get_next_sequence(), task))
                    self.active_tasks_count += 1
                    started_count += 1
        return started_count

    def cancel_task(self, task_id):
        """Cancela una tarea de forma segura."""
        with self.lock:
            for task in self.tasks:
                if task.id == task_id:
                    task.cancel()
                    event_bus.emit("task_status_changed", task)
                    return True
        return False

    def _worker(self):
        """Hilo trabajador Élite compatible con tuplas de 3 elementos."""
        while True:
            try:
                item = self.download_queue.get()
                if item is None: break
                # Desempaquetar los 3 valores (Priority, Seq, Task)
                priority, seq, task = item
            except: break
            
            if task._is_cancelled:
                self.download_queue.task_done()
                continue

            task_id = task.id
            current_thread = threading.current_thread()
            
            with self.lock:
                self.active_workers_threads[task_id] = current_thread

            try:
                # DINAMISMO MAESTRO: Obtener y normalizar la ruta actual de settings
                from config import settings
                current_download_dir = os.path.normpath(os.path.abspath(settings.DOWNLOADS_DIR))
                
                # Log de depuración Senior (Invisible para el usuario, visible en logs)
                logger.debug(f"QueueManager: Iniciando descarga en carpeta: {current_download_dir}")
                
                # Asegurar que la carpeta existe antes de descargar
                if not os.path.exists(current_download_dir):
                    try: os.makedirs(current_download_dir, exist_ok=True)
                    except Exception as e:
                        logger.error(f"QueueManager: No se pudo crear la carpeta {current_download_dir}: {e}")
                        # Fallback seguro solo si falla la creación
                        current_download_dir = get_data_path("data/downloads")

                # Sincronizar motor YT-DLP con la ruta normalizada
                self.ytdlp_engine.download_path = current_download_dir

                if self.db_manager.check_if_downloaded(task_id):
                    task.status = "finished"
                    event_bus.emit("task_status_changed", task)
                    continue

                task.status = "downloading"
                event_bus.emit("task_status_changed", task)
                
                success = False
                
                if task.is_telegram:
                    task.status = "scanning"
                    event_bus.emit("task_status_changed", task)
                    success = self._process_telegram_download(task)
                else:
                    success = self.ytdlp_engine.download(
                        task.url, 
                        options=task.options,
                        progress_callback=lambda p: self._update_task_progress(task, p)
                    )
                
                if task._is_cancelled:
                    task.status = "cancelled"
                    success = False
                else:
                    task.status = "finished" if success else "error"
                    if success: task.progress = 100.0 # FIX: Forzar barra llena al terminar
                
                if not success and not task.error_msg and task.status != "cancelled":
                    task.error_msg = _("queue.unknown_error")
                
                event_bus.emit("task_status_changed", task)
                
                if success and self.download_queue.qsize() < 5:
                    event_bus.emit("ui_notification", {
                        "text": f"{_('queue.status_finished')}: {task.metadata.get('title', '')[:30]}...", 
                        "color": settings.COLOR_SUCCESS
                    })
                
                if success:
                    self._persist_result(task)
                    
            except Exception as e:
                if "DOWNLOAD_CANCELLED" in str(e) or task._is_cancelled:
                    task.status = "cancelled"
                else:
                    task.status = "error"
                    task.error_msg = str(e)
                    logger.error(f"Error en worker al descargar {task.url}: {str(e)}")
                event_bus.emit("task_status_changed", task)
            
            finally:
                with self.lock:
                    if task_id in self.active_workers_threads:
                        del self.active_workers_threads[task_id]
                    self.active_tasks_count = max(0, self.active_tasks_count - 1)
                    
                    # FASE 12: Finalización inteligente
                    if self.active_tasks_count == 0 and self.download_queue.empty():
                        # Contar cuántas terminaron bien vs mal
                        success_count = sum(1 for t in self.tasks if t.status == "finished")
                        error_count = sum(1 for t in self.tasks if t.status == "error")
                        
                        if error_count > 0 and success_count == 0:
                            event_bus.emit("ui_notification", {
                                "text": f"PROCESO TERMINADO CON {error_count} ERRORES.",
                                "color": settings.COLOR_ERROR
                            })
                        else:
                            event_bus.emit("queue_finished_all")
                
                self.download_queue.task_done()

    def _process_telegram_download(self, task):
        """Maneja la lógica específica de descarga de Telegram con task_ref."""
        if not self.telegram_engine:
            task.error_msg = "Telegram Engine no inicializado"
            return False

        if not self.telegram_engine.is_authorized():
            task.error_msg = "Telegram: Se requiere inicio de sesión"
            return False

        message = None
        if task.metadata.get('is_raw_media') or 'media_obj' in task.metadata:
            message = task.metadata.get('media_obj')
        
        if not message:
            entity_id, msg_id = None, None
            if 'entity_id' in task.metadata:
                entity_id = task.metadata['entity_id']
                msg_id = int(task.metadata['id'])
            else:
                entity_id, msg_id = self.telegram_engine.get_entity_from_url(task.url)

            if not entity_id or not msg_id:
                task.error_msg = "Contenido inaccesible"
                return False

            message = self.telegram_engine.get_message_media(entity_id, msg_id)

        if not message:
            task.error_msg = "Contenido inaccesible"
            return False

        filename = task.metadata.get('title', f"telegram_file_{task.id}")
        if hasattr(message, 'file') and hasattr(message.file, 'name') and message.file.name:
            filename = message.file.name
        else:
            is_video = False
            if hasattr(message, 'video') and message.video: is_video = True
            elif hasattr(message, 'document') and message.document:
                mime = message.document.mime_type
                if mime and (mime.startswith('video/') or mime == 'application/x-tgvideo'):
                    is_video = True
            
            if not os.path.splitext(filename)[1]:
                filename += ".mp4" if is_video else ".jpg"
        
        # DINAMISMO EXTREMO: Usar la ruta actual de settings para Telegram también
        output_path = os.path.join(settings.DOWNLOADS_DIR, filename)

        result_path = self.telegram_engine.download_media(
            message, 
            output_path,
            progress_callback=lambda p: self._update_task_progress(task, p),
            task_ref=task
        )

        if result_path:
            task.file_path = result_path
            return True
        return False

    def _persist_result(self, task):
        """Guarda el resultado en la base de datos usando el ID único de la tarea."""
        self.db_manager.add_history({
            'video_id': task.id, # USAR UUID REAL DE LA TAREA
            'title': task.metadata.get('title', 'Desconocido'),
            'uploader': task.metadata.get('uploader', 'N/A'),
            'url': task.url,
            'file_path': task.file_path,
            'status': task.status
        })
        event_bus.emit("history_updated")

    def _update_task_progress(self, task, p):
        """Callback para actualizar los datos de la tarea con protección."""
        if task._is_cancelled: return

        status = p.get('status', 'downloading')
        if status == 'waiting':
            task.speed = "FloodWait"
            task.eta = p.get('msg', 'Espera...')
            event_bus.emit("task_progress", task)
            return

        percent = p.get('percent', 0.0)
        if 'current' in p and 'total' in p:
            task.info_extra = f"{p['current']}/{p['total']} bytes"
            
        task.progress = percent
        task.speed = p.get('speed', 'N/A')
        task.eta = p.get('eta', 'N/A')
        
        if 'filename' in p:
            task.file_path = p['filename']
        
        event_bus.emit("task_progress", task)

    def get_all_tasks(self):
        """Retorna la lista de todas las tareas."""
        with self.lock:
            return list(self.tasks)
            
    def clear_finished(self):
        """Limpia las tareas terminadas."""
        with self.lock:
            self.tasks = [t for t in self.tasks if t.status not in ["finished", "error", "cancelled"]]
        event_bus.emit("tasks_cleared")

    def clear_all(self):
        """Limpieza absoluta."""
        with self.lock:
            self.tasks = []
            self.task_ids_set = set()
            self.active_tasks_count = 0
            try:
                while not self.download_queue.empty():
                    self.download_queue.get_nowait()
                    self.download_queue.task_done()
            except: pass
        event_bus.emit("tasks_cleared")

    def clear_waiting(self):
        """Limpia tareas en espera."""
        with self.lock:
            initial_count = len(self.tasks)
            self.tasks = [t for t in self.tasks if t.status != "waiting"]
            self.task_ids_set = {str(t.id) for t in self.tasks if t.id}
            removed = initial_count - len(self.tasks)
            self.active_tasks_count = max(0, self.active_tasks_count - removed)
            try:
                while not self.download_queue.empty():
                    self.download_queue.get_nowait()
                    self.download_queue.task_done()
            except: pass
        event_bus.emit("tasks_cleared")

    def restart_telegram_engine(self, api_id, api_hash):
        """Reinicia el motor de Telegram con nuevas credenciales (Punto 1)."""
        logger.info(f"QueueManager: Reiniciando TelegramEngine con API_ID: {api_id}")
        if self.telegram_engine:
            try: self.telegram_engine.disconnect()
            except: pass
        
        self.telegram_engine = TelegramEngine(
            api_id=api_id,
            api_hash=api_hash,
            session_name=os.path.join(get_data_path("data"), settings.TELEGRAM_SESSION_NAME)
        )
        return True
