# OMDownloader - Event Bus Profesional con Válvula de Seguridad (Élite)
import time
import threading
import queue
from utils.logger import logger

class EventBus:
    """Sistema de eventos Élite con Cola Thread-Safe y Throttling de 30 FPS."""
    
    def __init__(self):
        self.listeners = {}
        self.main_root = None 
        
        # Mapa de Prioridades
        self.priority_map = {
            "task_status_changed": 1, # ALTA
            "history_updated": 1,      # ALTA
            "ui_notification": 1,      # ALTA
            "task_added": 2,           # MEDIA
            "task_progress": 3         # BAJA (Buffered)
        }
        
        self._event_queue = queue.Queue() # Cola para thread-safety real
        self._progress_buffer = {} # task_id -> last_data (para throttling de progreso)
        self._lock = threading.Lock()
        self._is_processing = False

    def set_root(self, root):
        """Asocia el root de Tkinter e inicia el loop de procesamiento."""
        self.main_root = root
        if not self._is_processing:
            self._is_processing = True
            self._process_queue()

    def _process_queue(self):
        """Bucle centralizado de procesamiento (Válvula de Seguridad)."""
        if not self.main_root: return

        # Procesar lote de eventos de la cola
        batch_size = 0
        while not self._event_queue.empty() and batch_size < 50:
            try:
                event_type, data = self._event_queue.get_nowait()
                self._dispatch_now(event_type, data)
                self._event_queue.task_done()
                batch_size += 1
            except queue.Empty: break
        
        # Procesar buffer de progreso (Throttling a ~10 FPS para la UI)
        with self._lock:
            if self._progress_buffer:
                for data in list(self._progress_buffer.values()):
                    self._dispatch_now("task_progress", data)
                self._progress_buffer.clear()

        # Re-programar el siguiente ciclo (33ms = ~30 FPS para suavidad extrema)
        self.main_root.after(33, self._process_queue)

    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):
        """Inyecta eventos en la cola thread-safe."""
        priority = self.priority_map.get(event_type, 2)

        # Caso ESPECIAL: Throttling de progreso para no saturar la cola
        if priority == 3 and hasattr(data, 'id'):
            with self._lock:
                self._progress_buffer[data.id] = data
            return

        # Resto de eventos: a la cola para procesamiento en el hilo principal
        self._event_queue.put((event_type, data))

    def _dispatch_now(self, event_type, data):
        """Ejecuta los callbacks en el hilo principal de forma segura."""
        if event_type not in self.listeners: return
        
        for callback in self.listeners[event_type]:
            try:
                callback(data)
            except Exception:
                pass # Silenciar widgets destruidos

# Instancia única global
event_bus = EventBus()
