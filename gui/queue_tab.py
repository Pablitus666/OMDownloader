# OMDownloader - Pestaña de Cola de Ultra-Alto Rendimiento
import customtkinter as ctk
import time
from config import settings
from core.i18n import _
from core.services import services
from core.event_bus import event_bus
from utils.image_manager import create_image_button
from gui.dialogs import show_message

class QueueTab(ctk.CTkFrame):
    """Componente Élite: Usa Widget Recycling (Object Pooling) para fluidez absoluta."""
    
    def __init__(self, master, image_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.image_manager = image_manager
        self.queue_manager = services.queue
        
        # Estructuras de Datos de Rendimiento
        self.pool_size = 50 # FASE 6: Optimización de pool
        self.widget_pool = [] # Lista fija de widgets reutilizables
        self.active_task_map = {} # ID -> index_in_pool
        self.last_update_times = {} # ID -> timestamp (Throttling)
        
        self._current_offset = 0
        self._is_rendering = False
        
        self._setup_ui()
        self._init_widget_pool() # Pre-creación de widgets
        self._subscribe_events()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=(40, 20), pady=20, sticky="ew")
        
        ctk.CTkLabel(self.header_frame, text=_("nav.queue"), 
                     font=ctk.CTkFont(family=settings.FONT_BOLD, size=settings.FONT_SIZE_H1, weight="bold"),
                     text_color=settings.COLOR_ACCENT).pack(side="left")
        
        self.btn_clear = create_image_button(
            self.header_frame, _("queue.clear_finished"), self._on_clear_click,
            self.image_manager, "boton_blue.png", (110, 35)
        )
        self.btn_clear.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=settings.COLOR_BG_DARK)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def _init_widget_pool(self):
        """Pre-crea los slots de la cola para reciclarlos después."""
        for _ in range(self.pool_size):
            slot = self._create_empty_row()
            slot["container"].pack_forget() # Ocultar el contenedor real
            self.widget_pool.append(slot)

    def _create_empty_row(self):
        """Crea la estructura visual de una fila sin datos."""
        container = ctk.CTkFrame(self.scroll_frame, fg_color=settings.COLOR_PRIMARY, height=80)
        container.pack_propagate(False)
        
        lbl_title = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=12, weight="bold"), 
                                text_color=settings.COLOR_TEXT, anchor="w")
        lbl_title.pack(side="top", fill="x", padx=15, pady=(10, 0))
        
        progress = ctk.CTkProgressBar(container, height=8, progress_color=settings.COLOR_ACCENT)
        progress.pack(side="top", fill="x", padx=15, pady=5)
        
        status_frame = ctk.CTkFrame(container, fg_color="transparent")
        status_frame.pack(side="top", fill="x", padx=15)
        
        lbl_status = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=10, weight="bold"))
        lbl_status.pack(side="left")
        
        lbl_info = ctk.CTkLabel(status_frame, text="", font=ctk.CTkFont(size=10), 
                               text_color=settings.COLOR_TEXT_DIM)
        lbl_info.pack(side="right")
        
        return {
            "container": container,
            "title": lbl_title,
            "progress": progress,
            "status": lbl_status,
            "info": lbl_info,
            "task_id": None
        }

    def _subscribe_events(self):
        # Usar un pequeño retardo para no refrescar 1000 veces al añadir masivamente
        event_bus.subscribe("task_added", self._on_task_added_debounced)
        event_bus.subscribe("task_progress", self._on_task_update)
        event_bus.subscribe("task_status_changed", self._on_task_update)
        event_bus.subscribe("tasks_cleared", self._on_tasks_cleared_event)

    def _on_task_added_debounced(self, task):
        """Añade un retardo inteligente al refresco tras añadir tareas."""
        if hasattr(self, "_debounce_timer"):
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(100, self._refresh_tasks)

    def _on_tasks_cleared_event(self, data=None):
        self._current_offset = 0
        self._refresh_tasks()

    def _on_task_update(self, task):
        """Actualización quirúrgica ultra-veloz."""
        if self._is_rendering: return
        if task.id not in self.active_task_map: return
        
        now = time.time()
        if task.status != "downloading" or (now - self.last_update_times.get(task.id, 0)) > 0.3:
            idx = self.active_task_map[task.id]
            self._update_widget_data(self.widget_pool[idx], task)
            self.last_update_times[task.id] = now

    def _refresh_tasks(self, data=None):
        """Reciclaje instantáneo de widgets con reset de scroll."""
        if self._is_rendering: return
        self._is_rendering = True
        
        # RESET DE SCROLL (Solución al "Scroll Fantasma")
        self.scroll_frame._parent_canvas.yview_moveto(0.0)
        
        all_tasks = self.queue_manager.get_all_tasks()
        self.active_task_map.clear()
        self.last_update_times.clear()
        
        if hasattr(self, "limit_footer"):
            try: self.limit_footer.destroy()
            except: pass

        # 1. Definir ventana
        start = self._current_offset
        visible_tasks = all_tasks[start : start + self.pool_size]
        
        # 2. Actualizar Slots
        for i in range(self.pool_size):
            slot = self.widget_pool[i]
            if i < len(visible_tasks):
                task = visible_tasks[i]
                slot["task_id"] = task.id
                self.active_task_map[task.id] = i
                self._update_widget_data(slot, task)
                slot["container"].pack(fill="x", padx=10, pady=5)
            else:
                slot["task_id"] = None
                slot["container"].pack_forget()

        # 3. Footer y Empty Msg
        self._check_empty_message(len(all_tasks))
        if len(all_tasks) > self.pool_size:
            self._add_pagination_footer(len(all_tasks))
            
        self._is_rendering = False

    def _update_widget_data(self, slot, task):
        """Rellena un slot existente con nuevos datos."""
        title = task.metadata.get('title', 'N/A')
        slot["title"].configure(text=title[:65] + "..." if len(title) > 65 else title)
        
        # CORRECCIÓN: Si está terminado, forzar 1.0 (100%)
        p_val = 1.0 if task.status == "finished" else (task.progress / 100)
        slot["progress"].set(p_val)
        
        try:
            if task.status == "downloading":
                slot["status"].configure(text=_("queue.status_downloading"), text_color=settings.COLOR_ACCENT)
                slot["info"].configure(text=f"{task.speed} | {task.eta}")
            elif task.status == "scanning":
                slot["status"].configure(text="ESCANEO...", text_color=settings.COLOR_ACCENT)
                slot["info"].configure(text="Analizando...")
            elif task.status == "finished":
                slot["status"].configure(text=_("queue.status_finished"), text_color=settings.COLOR_SUCCESS)
                slot["info"].configure(text=_("queue.info_finished"))
            elif task.status == "error":
                slot["status"].configure(text=_("queue.status_error"), text_color=settings.COLOR_ERROR)
                error_msg = task.error_msg or "Error"
                slot["info"].configure(text=error_msg[:35] + "..." if len(error_msg) > 35 else error_msg)
            else:
                slot["status"].configure(text=_("queue.status_waiting"), text_color=settings.COLOR_TEXT_DIM)
                slot["info"].configure(text=_("queue.info_waiting_turn"))
        except: pass

    def _add_pagination_footer(self, total):
        self.limit_footer = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.limit_footer.pack(fill="x", pady=20)
        current_shown = min(self._current_offset + self.pool_size, total)
        msg = f"🔍 MOSTRANDO {self._current_offset + 1}-{current_shown} DE {total} TAREAS"
        ctk.CTkLabel(self.limit_footer, text=msg, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=settings.COLOR_ACCENT).pack()
        
        btn_frame = ctk.CTkFrame(self.limit_footer, fg_color="transparent")
        btn_frame.pack(pady=10)
        if self._current_offset > 0:
            create_image_button(btn_frame, "ANTERIOR", self._prev_page, self.image_manager, "boton_blue.png", (120, 30)).pack(side="left", padx=5)
        if current_shown < total:
            create_image_button(btn_frame, "SIGUIENTE", self._next_page, self.image_manager, "boton_blue.png", (120, 30)).pack(side="left", padx=5)

    def _next_page(self):
        self._current_offset += self.pool_size
        self._refresh_tasks()

    def _prev_page(self):
        self._current_offset = max(0, self._current_offset - self.pool_size)
        self._refresh_tasks()

    def _check_empty_message(self, count):
        for child in self.scroll_frame.winfo_children():
            if isinstance(child, ctk.CTkLabel) and "VACÍA" in child.cget("text").upper():
                child.destroy()
        if count == 0:
            ctk.CTkLabel(self.scroll_frame, text="LA COLA ESTÁ VACÍA.", text_color=settings.COLOR_TEXT,
                         font=ctk.CTkFont(size=15, weight="bold")).pack(pady=50)

    def _on_clear_click(self):
        if not self.queue_manager.get_all_tasks():
            show_message(self, "warning.title", "warning.queue_empty_clear", self.image_manager)
            return
        self.queue_manager.clear_finished()

    def on_tab_active(self):
        self._refresh_tasks()
