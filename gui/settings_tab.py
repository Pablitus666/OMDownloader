# OMDownloader - Pestaña de Ajustes Profesional (Ultra-Fluidez)
import customtkinter as ctk
from tkinter import filedialog
import os
import threading
from config import settings
from core.i18n import _
from utils.resources import get_data_path
from core.queue_manager import QueueManager
from utils.logger import logger
from utils.image_manager import create_image_button
from gui.dialogs import show_message

class SettingsTab(ctk.CTkFrame):
    """Componente de configuración con renderizado ultra-fluido y persistencia."""
    
    def __init__(self, master, image_manager, **kwargs):
        kwargs.setdefault("fg_color", settings.COLOR_BG)
        super().__init__(master, **kwargs)
        self.image_manager = image_manager
        self.queue_manager = QueueManager()
        
        # 1. Contenedor Maestro
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10) # Reducido pady superior
        self.main_container.grid_columnconfigure(0, weight=1)

        # 2. Renderizado Progresivo (Carga en cascada para fluidez total)
        # Saltamos _render_header para ganar espacio
        self.after(60, self._render_downloads_section)
        self.after(110, self._render_connection_section)
        self.after(160, self._render_telegram_section)
        self.after(210, self._render_footer)
        
        # 3. Procesos de red retardados
        self.after(1000, self._check_tg_status)

    def _render_downloads_section(self):
        """Bloque 2: Descargas"""
        self._create_section_title(_("settings.downloads"), 1)
        folder_frame = self._create_setting_row(2)
        ctk.CTkLabel(folder_frame, text=_("settings.download_folder"), 
                     font=ctk.CTkFont(family=settings.FONT_FAMILY, size=14, weight="bold"),
                     text_color=settings.COLOR_TEXT).pack(side="left")
        
        self.path_entry = ctk.CTkEntry(folder_frame, width=350, fg_color=settings.COLOR_BG_WHITE, 
                                     text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.path_entry.pack(side="left", padx=10)
        self.path_entry.insert(0, os.path.abspath(settings.DOWNLOADS_DIR))
        self.path_entry.configure(state="readonly")
        
        create_image_button(folder_frame, _("settings.browse"), self._on_browse_click,
                           self.image_manager, "boton_blue.png", (100, 35)).pack(side="left", padx=5)

    def _render_connection_section(self):
        """Bloque 3: Conexión"""
        self._create_section_title(_("settings.connection"), 3)
        proxy_frame = self._create_setting_row(4)
        ctk.CTkLabel(proxy_frame, text=_("settings.proxy"), font=ctk.CTkFont(weight="bold"), 
                     text_color=settings.COLOR_TEXT).pack(side="left")
        self.proxy_entry = ctk.CTkEntry(proxy_frame, placeholder_text="http://user:pass@host:port", 
                                      width=350, fg_color=settings.COLOR_BG_WHITE, 
                                      text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.proxy_entry.pack(side="left", padx=10)

        cookies_frame = self._create_setting_row(5)
        ctk.CTkLabel(cookies_frame, text=_("settings.cookies"), font=ctk.CTkFont(weight="bold"), 
                     text_color=settings.COLOR_TEXT).pack(side="left")
        self.cookies_path_label = ctk.CTkLabel(cookies_frame, text=_("settings.none_selected"), 
                                              text_color=settings.COLOR_TEXT,
                                              font=ctk.CTkFont(family=settings.FONT_FAMILY, size=13, weight="bold"))
        self.cookies_path_label.pack(side="left", padx=10)
        create_image_button(cookies_frame, _("settings.cookies_btn"), self._on_select_cookies_click,
                           self.image_manager, "boton_blue.png", (140, 35)).pack(side="left")

    def _render_telegram_section(self):
        """Bloque 4: Telegram"""
        self._create_section_title(_("settings.telegram_auth"), 6)
        tg_status_frame = self._create_setting_row(7)
        self.tg_status_label = ctk.CTkLabel(tg_status_frame, text=_("settings.tg_checking"), 
                                            text_color=settings.COLOR_TEXT_DIM,
                                            font=ctk.CTkFont(family=settings.FONT_FAMILY, size=13, weight="bold"))
        self.tg_status_label.pack(side="left")
        
        api_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        api_row.grid(row=8, column=0, sticky="ew", pady=2)
        ctk.CTkLabel(api_row, text="API ID:", width=60, text_color=settings.COLOR_ACCENT, font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.api_id_entry = ctk.CTkEntry(api_row, width=120, fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.api_id_entry.pack(side="left", padx=5)
        self.api_id_entry.insert(0, str(settings.TELEGRAM_API_ID) if settings.TELEGRAM_API_ID != 0 else "")
        
        ctk.CTkLabel(api_row, text="API Hash:", width=70, text_color=settings.COLOR_ACCENT, font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.api_hash_entry = ctk.CTkEntry(api_row, width=280, fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.api_hash_entry.pack(side="left", padx=5)
        self.api_hash_entry.insert(0, settings.TELEGRAM_API_HASH)

        self.tg_login_frame = ctk.CTkFrame(self.main_container, fg_color=settings.COLOR_PRIMARY)
        self.tg_login_frame.grid(row=9, column=0, sticky="ew", pady=2, padx=5) # Reducido pady
        
        phone_row = ctk.CTkFrame(self.tg_login_frame, fg_color="transparent")
        phone_row.pack(fill="x", padx=15, pady=5) # Reducido pady
        ctk.CTkLabel(phone_row, text=_("settings.phone"), width=100, anchor="w").pack(side="left")
        self.phone_entry = ctk.CTkEntry(phone_row, placeholder_text="+59160000000", width=200, fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.phone_entry.pack(side="left", padx=10)
        create_image_button(phone_row, _("settings.send_code"), self._on_tg_send_code, self.image_manager, "boton_blue.png", (120, 30)).pack(side="left")

        auth_row = ctk.CTkFrame(self.tg_login_frame, fg_color="transparent")
        auth_row.pack(fill="x", padx=15, pady=(0, 5)) # Reducido pady
        ctk.CTkLabel(auth_row, text=_("settings.tg_code"), width=100, anchor="w").pack(side="left")
        self.code_entry = ctk.CTkEntry(auth_row, placeholder_text="12345", width=80, fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.code_entry.pack(side="left", padx=10)
        ctk.CTkLabel(auth_row, text=_("settings.tg_2fa"), width=60, anchor="w").pack(side="left")
        self.pass_entry = ctk.CTkEntry(auth_row, placeholder_text="*****", width=120, show="*", fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK, border_color=settings.COLOR_ACCENT)
        self.pass_entry.pack(side="left", padx=10)
        create_image_button(auth_row, "VALIDAR", self._on_tg_login_finish, self.image_manager, "button_green.png", (140, 30)).pack(side="right")

    def _render_footer(self):
        """Bloque 5: Botón Guardar"""
        self.btn_save = create_image_button(self.main_container, _("settings.apply"), self._on_save_advanced, self.image_manager, "button_green.png", (180, 45))
        self.btn_save.grid(row=11, column=0, pady=(10, 0)) # Reducido pady superior y quitado inferior

    def _create_section_title(self, title, row):
        ctk.CTkLabel(self.main_container, text=title.upper(), font=ctk.CTkFont(size=12, weight="bold"), text_color=settings.COLOR_ACCENT).grid(row=row, column=0, sticky="w", pady=(5, 2)) # Reducido pady


    def _create_setting_row(self, row):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid(row=row, column=0, sticky="ew", pady=5)
        return frame

    def _check_tg_status(self):
        if not self.queue_manager.telegram_engine:
            self.tg_status_label.configure(text=_("settings.tg_error_init"), text_color=settings.COLOR_ERROR)
            return
        def _task():
            try:
                is_auth = self.queue_manager.telegram_engine.is_authorized()
                self.after(0, lambda: self._update_tg_ui(is_auth))
            except: pass
        threading.Thread(target=_task, daemon=True).start()

    def _update_tg_ui(self, is_authorized):
        if is_authorized:
            self.tg_status_label.configure(text=_("settings.tg_authorized"), text_color=settings.COLOR_SUCCESS)
            self.tg_login_frame.grid_remove()
        else:
            self.tg_status_label.configure(text=_("settings.tg_unauthorized"), text_color=settings.COLOR_ACCENT)
            self.tg_login_frame.grid()

    def _on_tg_send_code(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            show_message(self, "warning.title", "warning.no_phone", self.image_manager)
            return
        def _task():
            success = self.queue_manager.telegram_engine.send_code_request(phone)
            self.after(0, lambda: show_message(self, "info.title" if success else "warning.title", "info.code_sent" if success else "warning.error_sending_code", self.image_manager))
        threading.Thread(target=_task, daemon=True).start()

    def _on_tg_login_finish(self):
        code = self.code_entry.get().strip()
        password = self.pass_entry.get().strip()
        if not code:
            show_message(self, "warning.title", "warning.missing_fields", self.image_manager)
            return
        def _task():
            result = self.queue_manager.telegram_engine.sign_in(code, password if password else None)
            self.after(0, lambda: self._handle_login_result(result))
        threading.Thread(target=_task, daemon=True).start()

    def _handle_login_result(self, result):
        if result == True:
            show_message(self, "info.title", "info.tg_login_success", self.image_manager)
            self._check_tg_status()
        elif result == "2FA_REQUIRED":
            show_message(self, "info.title", "info.tg_2fa_needed", self.image_manager)
        else:
            show_message(self, "warning.title", "warning.tg_login_error", self.image_manager)

    def _on_browse_click(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.configure(state="normal")
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, directory)
            self.path_entry.configure(state="readonly")
            self.queue_manager.ytdlp_engine.download_path = directory

    def _on_select_cookies_click(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if file_path:
            self.cookies_path_label.configure(text=os.path.basename(file_path))
            self.temp_cookies_path = file_path

    def _on_save_advanced(self):
        downloads_dir = self.path_entry.get().strip()
        proxy = self.proxy_entry.get().strip()
        cookies = getattr(self, 'temp_cookies_path', None)
        new_api_id = self.api_id_entry.get().strip()
        new_api_hash = self.api_hash_entry.get().strip()
        if not new_api_id or not new_api_hash:
            show_message(self, "warning.title", "warning.missing_fields", self.image_manager)
            return
        if str(settings.TELEGRAM_API_ID) != new_api_id or settings.TELEGRAM_API_HASH != new_api_hash:
            settings.TELEGRAM_API_ID = int(new_api_id)
            settings.TELEGRAM_API_HASH = new_api_hash
            self.queue_manager.restart_telegram_engine(new_api_id, new_api_hash)
            self.after(500, self._check_tg_status)
        
        self.queue_manager.ytdlp_engine.download_path = downloads_dir
        self.queue_manager.ytdlp_engine.set_proxy(proxy if proxy else None)
        if cookies: self.queue_manager.ytdlp_engine.set_cookies(cookies)
        
        # Guardar en persistencia (JSON) usando el nuevo método del objeto
        settings.save_config(api_id=new_api_id, api_hash=new_api_hash, downloads_dir=downloads_dir)
        show_message(self, "warning.title", "warning.apply_success", self.image_manager)
