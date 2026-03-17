# OMDownloader - Event Bus Profesional con Prioridades (Plan Maestro v1)
import time
import threading
from utils.logger import logger

class EventBus:
    """Sistema de eventos Élite con Buffer de Agrupación y Jerarquía de Prioridades."""
    
    def __init__(self):
        self.listeners = {}
        self.main_root = None 
        
        # FASE 3: Prioridades
        self.priority_map = {
            "task_status_changed": 1, # ALTA
            "history_updated": 1,      # ALTA
            "ui_notification": 1,      # ALTA
            "task_added": 2,           # MEDIA
            "task_progress": 3         # BAJA (Buffered)
        }
        
        self._event_buffer = {} # task_id -> last_data
        self._lock = threading.Lock()
        self._buffer_delay = 100 # ms por defecto

    def set_root(self, root):
        self.main_root = root
        self._start_buffer_processor()

    def _start_buffer_processor(self):
        """Procesa el buffer de eventos agrupados. FASE 7: Throttling dinámico."""
        if not self.main_root: return
        
        def _process():
            # Ajustar velocidad según carga
            with self._lock:
                # Si hay muchas tareas, bajamos la frecuencia a 150ms para no saturar
                if len(self._event_buffer) > 10:
                    self._buffer_delay = 150
                else:
                    self._buffer_delay = 100

                if self._event_buffer:
                    for task_id, data in list(self._event_buffer.items()):
                        self._emit_to_listeners("task_progress", data)
                    self._event_buffer.clear()
            
            self.main_root.after(self._buffer_delay, _process)
        
        self.main_root.after(self._buffer_delay, _process)

    def subscribe(self, event_type, callback):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)

    def emit(self, event_type, data=None):
        """Emite eventos con jerarquía de prioridad."""
        priority = self.priority_map.get(event_type, 2)

        # Caso BAJA PRIORIDAD: Buffer
        if priority == 3 and hasattr(data, 'id'):
            with self._lock:
                self._event_buffer[data.id] = data
            return

        # Casos ALTA/MEDIA PRIORIDAD: Emisión inmediata (vía .after para thread-safety)
        self._emit_to_listeners(event_type, data)

    def _emit_to_listeners(self, event_type, data):
        if event_type not in self.listeners: return
        
        for callback in self.listeners[event_type]:
            if self.main_root:
                try:
                    # Usamos after(0) para inyectar en el loop de Tkinter lo antes posible
                    self.main_root.after(0, lambda c=callback, d=data: self._safe_call(c, d))
                except: pass
            else:
                self._safe_call(callback, data)

    def _safe_call(self, callback, data):
        try:
            callback(data)
        except Exception:
            pass # Silenciar widgets destruidos

# Instancia única global
event_bus = EventBus()
