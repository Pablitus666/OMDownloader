# OMDownloader - Interfaz Principal Profesional
import customtkinter as ctk
from config import settings
from core.i18n import _
from core.services import services
from core.event_bus import event_bus
from utils.logger import logger
from utils.image_manager import ImageManager
from gui.about_window import AboutWindow
from gui.downloader_tab import DownloaderTab
from gui.queue_tab import QueueTab
from gui.history_tab import HistoryTab
from gui.settings_tab import SettingsTab

class OMDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{settings.APP_NAME} v{settings.VERSION}")
        self.root.geometry(settings.WINDOW_SIZE)
        self.root.minsize(*settings.MIN_WINDOW_SIZE)
        
        # PROTOCOLO DE CIERRE SEGURO (Punto 2)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Modo oscuro forzado
        ctk.set_appearance_mode("Light") 
        self.root.configure(bg=settings.COLOR_BG)
        
        # Núcleo y Servicios
        event_bus.set_root(self.root)
        self.image_manager = ImageManager(self.root)
        self.services = services
        self.services.set_image_manager(self.image_manager)
        
        self.frames = {}
        self.current_name = None
        
        self._setup_ui()
        self._setup_status_bar()
        self._preload_tabs()
        self._start_periodic_tasks()

    def _on_window_close(self):
        """Maneja el cierre de la ventana de forma profesional."""
        # Mostrar mensaje de 'Cerrando...' en la barra de estado si es posible
        self.status_label.configure(text="CERRANDO SERVICIOS Y SESIONES...", text_color=settings.COLOR_ACCENT)
        self.root.update()
        
        # Ejecutar shutdown atómico
        self.services.shutdown()
        
        # Destruir ventana
        self.root.destroy()

    def _start_periodic_tasks(self):
        """Lanza tareas de mantenimiento ligeras."""
        # Cada 10 minutos
        self.root.after(600000, self._periodic_cleanup)

    def _periodic_cleanup(self):
        """Punto 3: Watchdog de memoria."""
        self.image_manager.clear_cache()
        # Limpiar cachés de servicios
        self.services.run_memory_watchdog()
        self.root.after(600000, self._periodic_cleanup)

    def _setup_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)

        # Sidebar
        self.navigation_frame = ctk.CTkFrame(self.root, corner_radius=0, width=200, fg_color=settings.COLOR_BG_DARK)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        logo_img = self.image_manager.load("logo.png", size=(160, 160))
        self.logo_label = ctk.CTkLabel(self.navigation_frame, text="", image=logo_img, cursor="hand2")
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)
        self.logo_label.bind("<Button-1>", lambda e: AboutWindow(self.root, self.image_manager))

        self.btn_downloader = self._create_nav_btn(_("nav.downloader"), "downloader", 1)
        self.btn_queue = self._create_nav_btn(_("nav.queue"), "queue", 2)
        self.btn_history = self._create_nav_btn(_("nav.history"), "history", 3)
        self.btn_settings = self._create_nav_btn(_("nav.settings"), "settings", 4)

    def _preload_tabs(self):
        tab_map = {
            "downloader": DownloaderTab, 
            "queue": QueueTab, 
            "history": HistoryTab, 
            "settings": SettingsTab
        }
        
        for name, tab_class in tab_map.items():
            frame = tab_class(self.root, self.image_manager, fg_color=settings.COLOR_BG)
            frame.grid(row=0, column=1, sticky="nsew")
            frame.grid_remove()
            self.frames[name] = frame
            
        self.select_frame_by_name("downloader")

    def _create_nav_btn(self, text, name, row):
        btn = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=45, border_spacing=20, 
                           text=text, fg_color="transparent", text_color=settings.COLOR_TEXT,
                           hover_color=settings.COLOR_HOVER, anchor="w", 
                           font=ctk.CTkFont(family=settings.FONT_FAMILY, size=15, weight="bold"),
                           command=lambda: self.select_frame_by_name(name))
        btn.grid(row=row, column=0, sticky="ew")
        return btn

    def select_frame_by_name(self, name):
        if self.current_name == name: return
        if self.current_name and self.current_name in self.frames:
            self.frames[self.current_name].grid_remove()
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        self.current_name = name
        for n, btn in [("downloader", self.btn_downloader), ("queue", self.btn_queue), 
                       ("history", self.btn_history), ("settings", self.btn_settings)]:
            btn.configure(fg_color=settings.COLOR_HOVER if n == name else "transparent",
                          text_color=settings.COLOR_ACCENT if n == name else settings.COLOR_TEXT)
        if hasattr(self.frames[name], "on_tab_active"):
            self.frames[name].on_tab_active()

    def _setup_status_bar(self):
        """Crea una barra de estado dinámica (Nivel Élite)."""
        self.status_bar = ctk.CTkFrame(self.root, height=25, fg_color=settings.COLOR_BG_DARK, corner_radius=0)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text=_("downloader.status_ready").upper(), 
                                        font=ctk.CTkFont(size=10, weight="bold"),
                                        text_color=settings.COLOR_TEXT_DIM)
        self.status_label.grid(row=0, column=0, padx=20, pady=2, sticky="w")
        
        # Suscripciones críticas para el estado dinámico
        event_bus.subscribe("ui_notification", self._show_notification)
        event_bus.subscribe("task_status_changed", self._on_task_activity)
        event_bus.subscribe("queue_finished_all", self._on_queue_finished)

    def _on_task_activity(self, task=None):
        """Actualiza el estado dinámico cuando hay cambios en las tareas."""
        # Si no hay una notificación activa importante, refrescamos el estado base
        if not hasattr(self, "_notification_active") or not self._notification_active:
            self._refresh_default_status()

    def _refresh_default_status(self):
        """Calcula y muestra el estado base según la actividad de la cola."""
        count = self.services.queue.active_tasks_count
        if count > 0:
            msg = f"DESCARGANDO: {count} ARCHIVOS EN PROCESO..."
            color = settings.COLOR_ACCENT
        else:
            msg = _("downloader.status_ready")
            color = settings.COLOR_TEXT_DIM
            
        self.status_label.configure(text=msg.upper(), text_color=color)

    def _on_queue_finished(self, data=None):
        """Mensaje de éxito final."""
        self._show_notification({
            "text": "¡PROCESO FINALIZADO! TODOS LOS ARCHIVOS DESCARGADOS.",
            "color": settings.COLOR_SUCCESS
        })

    def _show_notification(self, data):
        """Muestra un mensaje temporal que sobrescribe el estado base."""
        if isinstance(data, dict):
            text = data.get("text", "")
            color = data.get("color", settings.COLOR_ACCENT)
            is_important = color in [settings.COLOR_SUCCESS, settings.COLOR_ERROR]
        else:
            text = str(data); color = settings.COLOR_ACCENT; is_important = False
            
        self.status_label.configure(text=text.upper(), text_color=color)
        self._notification_active = True
        
        if hasattr(self, "_status_timer"):
            self.root.after_cancel(self._status_timer)
        
        # Tras el tiempo de espera, volver al estado dinámico real (No a un texto fijo)
        delay = 15000 if is_important else 6000
        self._status_timer = self.root.after(delay, self._clear_notification)

    def _clear_notification(self):
        """Elimina la notificación temporal y vuelve al estado dinámico."""
        self._notification_active = False
        self._refresh_default_status()
