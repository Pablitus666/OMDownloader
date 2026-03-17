# OMDownloader - Pestaña de Historial con Lazy Loading Senior
import customtkinter as ctk
import os
import time
from config import settings
from core.i18n import _
from core.services import services
from core.event_bus import event_bus
from utils.image_manager import create_image_button
from gui.dialogs import show_message

class HistoryTab(ctk.CTkFrame):
    """Pestaña de Historial Élite con carga incremental (Lazy Loading)."""
    
    def __init__(self, master, image_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.image_manager = image_manager
        self.db_manager = services.database
        self._display_limit = 50 # FASE 11: Límite óptimo
        self._current_offset = 0
        self._is_rendering = False
        self._last_refresh_time = 0
        
        self._setup_ui()
        self._subscribe_events()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=(40, 20), pady=20, sticky="ew")
        
        ctk.CTkLabel(self.header_frame, text=_("nav.history"), 
                     font=ctk.CTkFont(family=settings.FONT_BOLD, size=settings.FONT_SIZE_H1, weight="bold"),
                     text_color=settings.COLOR_ACCENT).pack(side="left")
        
        create_image_button(self.header_frame, _("history.clear"), self._on_clear_click,
                           self.image_manager, "boton_blue.png", (150, 35)).pack(side="right", padx=(10, 0))

        create_image_button(self.header_frame, _("history.refresh"), self._on_refresh_click,
                           self.image_manager, "boton_blue.png", (120, 35)).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color=settings.COLOR_BG_DARK)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def _subscribe_events(self):
        event_bus.subscribe("history_updated", self._on_history_updated_event)

    def _on_history_updated_event(self, data=None):
        """Refresco inteligente: solo si la pestaña es visible y han pasado 5s."""
        now = time.time()
        if (now - self._last_refresh_time) > 5:
            try:
                if self.winfo_exists() and self.winfo_viewable():
                    self._on_refresh_click()
            except: pass

    def on_tab_active(self):
        """Carga automática al entrar."""
        if self._current_offset == 0:
            self._on_refresh_click()

    def _on_refresh_click(self):
        """Limpia y reinicia la carga desde el principio."""
        self._current_offset = 0
        self._last_refresh_time = time.time()
        for child in self.scroll_frame.winfo_children(): child.destroy()
        self._load_next_batch()

    def _load_next_batch(self):
        """Carga el siguiente bloque de datos sin borrar los anteriores (Infinite Scroll)."""
        if self._is_rendering: return
        self._is_rendering = True
        
        # 1. Obtener datos
        total_count = self.db_manager.get_history_count()
        items = self.db_manager.get_history(limit=self._display_limit, offset=self._current_offset)
        
        # 2. Si es el primer lote y está vacío
        if total_count == 0 and self._current_offset == 0:
            self._is_rendering = False
            ctk.CTkLabel(self.scroll_frame, text=_("history.empty"), text_color=settings.COLOR_TEXT,
                         font=ctk.CTkFont(size=15, weight="bold")).pack(pady=50)
            return

        # 3. Eliminar footer previo si existe
        for child in self.scroll_frame.winfo_children():
            if hasattr(child, "is_footer"): child.destroy()

        # 4. Renderizar batch de forma atómica
        self._render_batch(items, 0, total_count)

    def _render_batch(self, items, start_idx, total_count):
        if start_idx >= len(items):
            self._current_offset += len(items)
            if self._current_offset < total_count:
                self._add_pagination_footer(total_count)
            self._is_rendering = False
            return

        # Procesar de 10 en 10 para mantener la GUI receptiva
        end_idx = min(start_idx + 10, len(items))
        for i in range(start_idx, end_idx):
            self._create_history_row(items[i])
        
        self.after(5, lambda: self._render_batch(items, end_idx, total_count))

    def _add_pagination_footer(self, total):
        footer = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        footer.pack(fill="x", pady=20)
        footer.is_footer = True
        
        msg = f"🔍 MOSTRANDO {self._current_offset} DE {total} REGISTROS"
        ctk.CTkLabel(footer, text=msg, font=ctk.CTkFont(size=11, weight="bold"), 
                     text_color=settings.COLOR_TEXT_DIM).pack()
        
        create_image_button(footer, "CARGAR MÁS", self._load_next_batch,
                           self.image_manager, "boton_blue.png", (180, 35)).pack(pady=10)

    def _create_history_row(self, item):
        row = ctk.CTkFrame(self.scroll_frame, fg_color=settings.COLOR_PRIMARY, height=75)
        row.pack(fill="x", padx=10, pady=5)
        row.pack_propagate(False)
        
        color = settings.COLOR_SUCCESS if item.get('status') == 'finished' else settings.COLOR_ERROR
        ctk.CTkFrame(row, width=4, fg_color=color).pack(side="left", fill="y")
        
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        title = item.get('title', 'N/A')
        title = title[:75] + ("..." if len(title) > 75 else "")
        ctk.CTkLabel(info_frame, text=title, font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color=settings.COLOR_TEXT, anchor="w").pack(fill="x")
        
        uploader = item.get('uploader', 'N/A')
        ts = item.get('timestamp', 'N/A')
        ctk.CTkLabel(info_frame, text=f"{uploader} | {ts}", font=ctk.CTkFont(size=10, weight="bold"), 
                     text_color=settings.COLOR_TEXT_DIM, anchor="w").pack(fill="x")
        
        create_image_button(row, _("history.open_folder"), lambda p=item.get('file_path'): self._open_folder(p),
                           self.image_manager, "boton_blue.png", (110, 30)).pack(side="right", padx=10)

    def _open_folder(self, path):
        if not path or not os.path.exists(path):
            show_message(self, "warning.title", "warning.folder_not_found", self.image_manager)
            return
        try:
            folder = os.path.dirname(path) if os.path.isfile(path) else path
            if os.path.exists(folder): os.startfile(folder)
        except: pass

    def _on_clear_click(self):
        if self.db_manager.get_history_count() == 0:
            show_message(self, "ALERTA", "EL HISTORIAL YA ESTÁ VACÍO.", self.image_manager)
            return
        self.db_manager.clear_history()
        self._on_refresh_click()
        show_message(self, "ÉXITO", "HISTORIAL ELIMINADO.", self.image_manager)
