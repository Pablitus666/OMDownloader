# OMDownloader - Pestaña de Descarga Profesional (OSINT-Ready)
import customtkinter as ctk
import threading
import requests
import tkinter as tk
import time
import base64
import os
from io import BytesIO
from PIL import Image
from config import settings
from core.i18n import _
from core.services import services
from core.event_bus import event_bus
from utils.image_manager import create_image_button, get_real_bg
from gui.dialogs import show_message

class DownloaderTab(ctk.CTkFrame):
    def __init__(self, master, image_manager, **kwargs):
        super().__init__(master, **kwargs)
        self.image_manager = image_manager
        self.queue_manager = services.queue
        self.current_metadata = None
        self.scanned_cache = set()
        self.pending_results = [] # Acumulador Élite de hallazgos
        self.pending_counts = {"video": 0, "photo": 0, "document": 0} # Contador dinámico
        self._thumb_ref = None # Referencia de memoria sólida
        self._setup_ui()
        self._setup_dnd()
        self._subscribe_events()

    def _subscribe_events(self):
        """Suscribe la pestaña a eventos globales para actualizar la UI."""
        event_bus.subscribe("queue_finished_all", self._on_queue_finished_ui)

    def _on_queue_finished_ui(self, data=None):
        """Muestra un mensaje de éxito final en el panel central (Forzado)."""
        # Limpiar metadatos previos para evitar bloqueos visuales
        self.current_metadata = None
        self.pending_results = []
        self.pending_counts = {"video": 0, "photo": 0, "document": 0}
        
        # NOTIFICACIÓN PERSISTENTE EN BARRA DE ESTADO (Fase Élite)
        self._set_status_msg("¡DESCARGAS COMPLETADAS EXITOSAMENTE!", settings.COLOR_SUCCESS)
        
        # Dibujar la pantalla de éxito
        self.after(0, self._render_completion_screen)

    def _render_completion_screen(self):
        """Dibuja la pantalla de finalización minimalista en el centro."""
        for child in self.info_content.winfo_children(): child.destroy()
        
        container = ctk.CTkFrame(self.info_content, fg_color="transparent")
        container.pack(pady=40, fill="x", expand=True)
        
        ctk.CTkLabel(container, text="¡PROCESO FINALIZADO!", 
                     text_color=settings.COLOR_ACCENT, 
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)
        
        ctk.CTkLabel(container, text="TODAS LAS DESCARGAS SE HAN COMPLETADO.", 
                     text_color="white", 
                     font=ctk.CTkFont(size=16, weight="bold"), justify="center").pack(pady=10)

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, padx=(40, 20), pady=(20, 10), sticky="ew")
        
        titulo_img = self.image_manager.load_tk("titulo.png", size=(400, 80))
        if titulo_img:
            lbl = tk.Label(self.header, image=titulo_img, bg=get_real_bg(self.header), bd=0)
            lbl.image = titulo_img
            lbl.pack(pady=(0, 15))
        
        self.input_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        self.input_frame.pack(fill="x")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text=_("downloader.url_placeholder"), 
                                     height=45, font=ctk.CTkFont(size=14, weight="bold"),
                                     fg_color=settings.COLOR_BG_WHITE, text_color=settings.COLOR_TEXT_DARK,
                                     border_color=settings.COLOR_ACCENT)
        self.url_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.url_entry.bind("<Return>", lambda e: self._on_analyze_click())
        self.url_entry.bind("<Delete>", lambda e: self._clear_all_downloader())
        
        create_image_button(self.input_frame, _("downloader.analyze"), self._on_analyze_click,
                           self.image_manager, "boton_blue.png", (130, 45)).grid(row=0, column=1)

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Barra de Reporte
        self.report_header = ctk.CTkFrame(self.main_container, fg_color="transparent", height=45)
        self.report_header.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=(0, 5))
        self.report_header.grid_propagate(False)
        
        self.btn_report = create_image_button(
            self.report_header, "📋 REPORTE OSINT", self._copy_report_to_clipboard,
            self.image_manager, "boton_blue.png", (200, 40)
        )
        self.btn_report.pack(side="left")

        self.info_scroll = ctk.CTkScrollableFrame(self.main_container, fg_color=settings.COLOR_PRIMARY)
        self.info_scroll.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        self.info_content = ctk.CTkFrame(self.info_scroll, fg_color="transparent")
        self.info_content.pack(fill="both", expand=True)
        
        # CONTENEDOR DE MINIATURA (Fijo)
        self.thumb_container = ctk.CTkFrame(self.main_container, width=320, height=180, fg_color=settings.COLOR_PRIMARY,
                                          border_width=2, border_color=settings.COLOR_ACCENT)
        self.thumb_container.grid(row=1, column=1, sticky="n")
        self.thumb_container.grid_propagate(False)
        
        # Inicializar el label de miniatura
        self._create_fresh_thumb_label()

        # Footer
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.batch_panel = ctk.CTkFrame(self.footer, fg_color=settings.COLOR_PRIMARY, corner_radius=10)
        self.batch_panel.pack(fill="x", pady=(0, 10))
        self._setup_batch_panel()
        
        # Contenedor de Botones Principales
        self.actions_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        self.actions_frame.pack(pady=5)
        
        # Botón AGREGAR A COLA (Azul, Siempre visible)
        self.btn_add_queue = create_image_button(self.actions_frame, "AGREGAR A COLA", self._on_add_to_queue_click,
                                                self.image_manager, "boton_blue.png", (220, 50))
        self.btn_add_queue.pack(side="left", padx=10)
        
        # Botón DESCARGAR TODO (Verde, Siempre visible)
        self.btn_download_all = create_image_button(self.actions_frame, "DESCARGAR TODO", self._on_download_all_click,
                                                   self.image_manager, "button_green.png", (220, 50))
        self.btn_download_all.pack(side="left", padx=10)
        
        self._set_status_msg(_("downloader.status_ready"))

    def _create_fresh_thumb_label(self, image=None):
        """Regenera el widget de miniatura para evitar errores de pyimage en Tkinter."""
        # Destruir existente si existe
        if hasattr(self, "thumb_label"):
            try: self.thumb_label.destroy()
            except: pass
        
        # Crear uno nuevo (Siempre limpio)
        self.thumb_label = ctk.CTkLabel(self.thumb_container, text=_("downloader.no_thumbnail") if not image else "",
                                       image=image, text_color=settings.COLOR_TEXT, font=ctk.CTkFont(weight="bold"))
        self.thumb_label.place(relx=0.5, rely=0.5, anchor="center")
        if image: self._thumb_ref = image

    def _clear_all_downloader(self):
        """Limpia todo el contenido y sincroniza la cola (Reset Total)."""
        self.url_entry.delete(0, 'end')
        self.current_metadata = None
        self.scanned_cache.clear()
        self.pending_results = [] # LIMPIEZA CRÍTICA DE HALLAZGOS
        self.pending_counts = {"video": 0, "photo": 0, "document": 0}
        
        self._set_status_msg(_("downloader.status_ready"))
        
        # LIMPIEZA ABSOLUTA DE COLA (Waiting + Finished + Error)
        self.queue_manager.clear_all()
        
        self._thumb_ref = None
        self._create_fresh_thumb_label()
            
        for child in self.info_content.winfo_children(): child.destroy()

    def _setup_batch_panel(self):
        for child in self.batch_panel.winfo_children(): child.destroy()
        inner = ctk.CTkFrame(self.batch_panel, fg_color="transparent")
        inner.pack(pady=10, padx=10)
        ctk.CTkLabel(inner, text="EXTRACCIÓN MASIVA (TELEGRAM):", font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color=settings.COLOR_ACCENT).pack(side="left", padx=10)
        for mtype, label in [("video", "📥 VÍDEOS"), ("photo", "📸 FOTOS"), ("document", "📁 ARCHIVOS")]:
            create_image_button(inner, label, lambda t=mtype: self._on_batch_click(t), 
                               self.image_manager, "boton_blue.png", (120, 35)).pack(side="left", padx=5)

    def _set_status_msg(self, text, color=None):
        event_bus.emit("ui_notification", {"text": text, "color": color or settings.COLOR_TEXT_DIM})

    def _on_analyze_click(self):
        url = self.url_entry.get().strip()
        if not url:
            show_message(self, "ALERTA", "DEBES INTRODUCIR UNA URL VÁLIDA PARA ANALIZAR.", self.image_manager)
            return

        # SINCRONIZACIÓN Y LIMPIEZA DE MEMORIA (Nivel Senior)
        self.queue_manager.clear_waiting()
        self.scanned_cache.clear()
        self.pending_results = [] 
        self.pending_counts = {"video": 0, "photo": 0, "document": 0}
        
        # Liberar referencia de imagen previa para el recolector de basura
        self._thumb_ref = None 
        self._create_fresh_thumb_label()

        self._set_status_msg(_("downloader.status_analyzing"), settings.COLOR_ACCENT)
        services.submit_scan(self._analyze_task, url)

    def _analyze_task(self, url):
        """Tarea de análisis delegada al contenedor de servicios inteligente."""
        try:
            # FASE 5: Uso de caché y selección automática de motor
            metadata = services.get_metadata(url)
            
            if metadata:
                self.after(0, lambda: self._render_metadata(metadata))
            else:
                self.after(0, lambda: self._set_status_msg(_("downloader.error_osint"), settings.COLOR_ERROR))
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Error en análisis de UI: {e}")
            self.after(0, lambda: self._set_status_msg(_("downloader.error_osint"), settings.COLOR_ERROR))

    def _render_metadata(self, m):
        for child in self.info_content.winfo_children(): child.destroy()
        if not m:
            self._set_status_msg(_("downloader.error_osint"), settings.COLOR_ERROR)
            return
            
        self.current_metadata = m
        fields = [
            ("🆔 ID INTERNO", m.get('id')), ("👤 USUARIO / CANAL", m.get('uploader')),
            ("🔗 ALIAS", m.get('username')), ("🎬 TÍTULO", m.get('title')),
            ("👥 PARTICIPANTES", m.get('participants')), ("📅 FECHA", m.get('upload_date')),
            ("⏱️ DURACIÓN", m.get('duration')), ("👁️ VISTAS", m.get('view_count')),
            ("👍 LIKES", m.get('like_count')), ("🖥️ RESOLUCIÓN", m.get('resolution')),
            ("🎞️ FPS", m.get('fps')), ("📦 FORMATO", m.get('ext')),
            ("✨ VERIFICADO", m.get('verified')), ("⚠️ SCAM / FRAUDE", m.get('scam')),
            ("🎭 FAKE / FALSO", m.get('fake')), ("🚫 RESTRICCIÓN", m.get('restricted')),
            ("📡 MOTOR", m.get('extractor')), ("🏷️ ETIQUETAS", m.get('tags')),
            ("📝 DESCRIPCIÓN / BIO", m.get('description'))
        ]
        
        for label, val in fields:
            if val is None or val == "N/A" or val == "": continue
            row = ctk.CTkFrame(self.info_content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=label.upper(), width=140, anchor="w", text_color=settings.COLOR_ACCENT, font=ctk.CTkFont(size=10, weight="bold")).pack(side="left")
            ctk.CTkLabel(row, text=str(val), anchor="w", wraplength=400, justify="left", text_color=settings.COLOR_TEXT, font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", fill="x", expand=True)

        if m.get('thumbnail'):
            services.submit_thumb(self._load_thumb, m['thumbnail'])

    def _copy_report_to_clipboard(self):
        if not self.current_metadata:
            show_message(self, "ALERTA", "NO HAY DATOS PARA COPIAR. ANALIZA UNA URL PRIMERO.", self.image_manager)
            return
        report_text = f"--- REPORTE OSINT: {settings.APP_NAME} ---\n\n"
        m = self.current_metadata
        for k, v in m.items():
            if v and v != "N/A" and k != "thumbnail": report_text += f"{k.upper()}: {v}\n"
        self.master.clipboard_clear()
        self.master.clipboard_append(report_text)
        show_message(self, "ÉXITO", "REPORTE OSINT COPIADO AL PORTAPELES CORRECTAMENTE.", self.image_manager)

    def _load_thumb(self, url_or_b64):
        """Carga de miniatura con caché de nivel Élite (Fase 4)."""
        from utils.thumb_cache import thumb_cache
        
        # 1. Comprobación de caché instantánea
        cached_img = thumb_cache.get(url_or_b64)
        if cached_img:
            ctk_img = ctk.CTkImage(light_image=cached_img, dark_image=cached_img, 
                                  size=(cached_img.width, cached_img.height))
            self.after(0, lambda: self._create_fresh_thumb_label(ctk_img))
            return

        try:
            img = None
            if url_or_b64.startswith("data:image"):
                base64_data = url_or_b64.split(",")[1]
                img = Image.open(BytesIO(base64.b64decode(base64_data)))
            else:
                # FASE 8: Uso de la sesión global para evitar handshakes TLS repetidos
                resp = services.net.get(url_or_b64, timeout=10)
                img = Image.open(BytesIO(resp.content))
            
            if img:
                img.thumbnail((280, 150), Image.LANCZOS)
                # Guardar en caché para la próxima vez
                thumb_cache.set(url_or_b64, img)
                
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                self.after(0, lambda: self._create_fresh_thumb_label(ctk_img))
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"Error al cargar miniatura: {e}")

    def _on_batch_click(self, mtype):
        url = self.url_entry.get().strip()
        names = {"video": "VÍDEOS", "photo": "FOTOS", "document": "ARCHIVOS"}
        name = names.get(mtype, mtype.upper())
        if not url:
            show_message(self, "ALERTA", f"PRIMERO ANALIZA UNA URL PARA EXTRAER {name}.", self.image_manager)
            return
        cache_key = (url, mtype)
        if cache_key in self.scanned_cache:
            show_message(self, "HALLAZGOS", f"YA HAS ESCANEADO {name} PARA ESTA URL.", self.image_manager)
            return
        self._set_status_msg(f"ESCANEANDO {name}...", settings.COLOR_ACCENT)
        services.executor.submit(self._batch_task, url, mtype)

    def _batch_task(self, url, mtype):
        """Ejecuta el escaneo con timeout de seguridad (Fase 21)."""
        try:
            # Iniciamos el escaneo en el motor
            # Como es un hilo del executor, podemos esperar con un timeout relativo
            results = self.queue_manager.telegram_engine.scan_media(url, media_type=mtype)
            self.after(0, lambda: self._handle_batch(results, mtype, url))
        except Exception as e:
            from utils.logger import logger
            logger.error(f"Error en batch task: {e}")
            self.after(0, lambda: self._set_status_msg("FALLO EN ESCANEO MASIVO", settings.COLOR_ERROR))

    def _handle_batch(self, results, mtype, url):
        if not results:
            names = {"video": "VÍDEOS", "photo": "FOTOS", "document": "ARCHIVOS"}
            self._set_status_msg(f"NO SE ENCONTRARON {names.get(mtype)}.", settings.COLOR_ERROR)
            return
            
        # 1. ACUMULACIÓN INTELIGENTE
        self.pending_results.extend(results)
        self.pending_counts[mtype] += len(results)
        self.scanned_cache.add((url, mtype))
        
        self._set_status_msg(f"¡{len(results)} ELEMENTOS ENCONTRADOS!", settings.COLOR_SUCCESS)

        # 2. Renderizado de Resumen Dinámico
        for child in self.info_content.winfo_children(): child.destroy()
        
        container = ctk.CTkFrame(self.info_content, fg_color="transparent")
        container.pack(pady=(10, 30), fill="x") # Reducido pady superior de 30 a 10
        
        ctk.CTkLabel(container, text="🔍 RESUMEN DE HALLAZGOS ACUMULADOS", 
                     text_color=settings.COLOR_ACCENT, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))
        
        # Construcción de mensaje específico con saltos de línea para evitar desbordamiento
        parts = []
        if self.pending_counts["video"] > 0: parts.append(f"• {self.pending_counts['video']} VÍDEOS")
        if self.pending_counts["photo"] > 0: parts.append(f"• {self.pending_counts['photo']} FOTOS")
        if self.pending_counts["document"] > 0: parts.append(f"• {self.pending_counts['document']} ARCHIVOS")
        
        summary_block = "\n".join(parts)
        info_text = f"SE HAN LOCALIZADO:\n{summary_block}\n\nESTÁN LISTOS PARA SER AGREGADOS A LA COLA."
        ctk.CTkLabel(container, text=info_text, text_color=settings.COLOR_TEXT, 
                     font=ctk.CTkFont(size=14, weight="bold"), justify="center").pack(pady=10)

    def _on_add_to_queue_click(self):
        """Pasa los hallazgos acumulados a la cola de descargas real con inteligencia contextual."""
        if not self.pending_results:
            # Inteligencia OSINT: Verificar si ya se agregaron o si nunca hubo nada
            has_history_this_session = any(self.pending_counts.values())
            total_in_queue = len(self.queue_manager.get_all_tasks())
            
            if has_history_this_session:
                msg = "LOS HALLAZGOS DE ESTE ANÁLISIS YA HAN SIDO AGREGADOS.\n"
                if total_in_queue > 0:
                    msg += f"ACTUALMENTE TIENES {total_in_queue} TAREAS EN LA PESTAÑA 'COLA'."
                else:
                    msg += "ESCANEA OTRA CATEGORÍA O URL PARA CONTINUAR."
                show_message(self, "INFORMACIÓN", msg, self.image_manager)
            else:
                show_message(self, "ALERTA", "NO HAY HALLAZGOS PENDIENTES.\nREALIZA UN ESCANEO DE VÍDEOS O FOTOS PRIMERO.", self.image_manager)
            return
            
        count = len(self.pending_results)
        self._set_status_msg(f"ENCOLANDO {count} ELEMENTOS...", settings.COLOR_ACCENT)
        
        # Iniciar el proceso por lotes
        self._process_results_in_batches(list(self.pending_results), 0)
        
        # Limpiar SOLO la lista de resultados para evitar duplicados, 
        # pero MANTENEMOS pending_counts para la inteligencia del botón.
        self.pending_results = []
        
        # Actualizar vista a pantalla de éxito
        self._render_success_enqueue(count)

    def _render_success_enqueue(self, count):
        """Dibuja la pantalla de confirmación de encolado."""
        for child in self.info_content.winfo_children(): child.destroy()
        container = ctk.CTkFrame(self.info_content, fg_color="transparent")
        container.pack(pady=40)
        
        success_img = self.image_manager.load("button_green.png", size=(60, 60))
        if success_img: ctk.CTkLabel(container, text="", image=success_img).pack()
        
        msg = f"¡{count} ELEMENTOS AGREGADOS EXITOSAMENTE!\n\nYA PUEDES REVISARLOS EN LA PESTAÑA 'COLA'\nO PULSAR 'DESCARGAR TODO' AQUÍ DEBAJO."
        ctk.CTkLabel(container, text=msg, text_color="white", 
                     font=ctk.CTkFont(size=14, weight="bold"), justify="center").pack(pady=20)

    def _process_results_in_batches(self, results, start_idx, batch_size=50):
        """Añade tareas a la cola en lotes silenciosos para mantener la GUI fluida."""
        end_idx = min(start_idx + batch_size, len(results))
        for i in range(start_idx, end_idx):
            item = results[i]
            # USAR emit_event=False PARA NO SATURAR EL BUS
            self.queue_manager.add_task(item['url'], item['metadata'], auto_start=False, emit_event=False)
        
        if end_idx < len(results):
            # Siguiente lote en 10ms (Libera el hilo principal)
            self.after(10, lambda: self._process_results_in_batches(results, end_idx))
        else:
            # FIN TOTAL DEL ENCOLADO: Disparar una sola actualización visual
            event_bus.emit("tasks_cleared")

    def _on_download_all_click(self):
        started = self.queue_manager.start_all_waiting()
        if started > 0:
            self._set_status_msg(f"INICIANDO {started} DESCARGAS...", settings.COLOR_SUCCESS)
        elif self.current_metadata:
            # Solo intentar descarga individual si NO es un canal/perfil raíz (OSINT Safe)
            is_root = self.current_metadata.get('extractor') in ['Shielded MTProto', 'Telegram OSINT Core'] and not "/c/" in self.current_metadata.get('webpage_url', '')
            
            if not is_root:
                task = self.queue_manager.add_task(self.current_metadata.get('webpage_url', ''), self.current_metadata)
                if task:
                    self._set_status_msg("DESCARGA INDIVIDUAL INICIADA.", settings.COLOR_SUCCESS)
                else:
                    self._set_status_msg("EL ELEMENTO YA ESTÁ DESCARGADO O EN LA COLA.", settings.COLOR_ACCENT)
            else:
                self._set_status_msg("USA 'EXTRACCIÓN MASIVA' PARA DESCARGAR CANALES.", settings.COLOR_ACCENT)
        else:
            self._set_status_msg("NO HAY ELEMENTOS NUEVOS PARA DESCARGAR.", settings.COLOR_ACCENT)

    def _setup_dnd(self):
        """Configura el soporte de arrastrar y soltar (URLs y Archivos)."""
        try:
            # Registrar tanto texto (URLs) como archivos
            self.url_entry._entry.drop_target_register("DND_Text", "DND_Files")
            self.url_entry._entry.dnd_bind("<<Drop>>", self._handle_drop_event)
            
            # También permitir soltar en el contenedor principal para mayor comodidad
            self.main_container.drop_target_register("DND_Text", "DND_Files")
            self.main_container.dnd_bind("<<Drop>>", self._handle_drop_event)
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"DND no disponible en este entorno: {e}")

    def _handle_drop_event(self, event):
        """Manejador inteligente de eventos de soltado (Nivel Élite)."""
        data = event.data.strip()
        
        # 1. Limpieza de formato Windows (llaves en rutas con espacios o URLs)
        if data.startswith('{') and data.endswith('}'):
            data = data[1:-1]
            
        # 2. Detección de tipo: ¿Es un archivo o una URL?
        if os.path.isfile(data):
            ext = os.path.splitext(data)[1].lower()
            if ext == ".session":
                # Lógica especial para archivos de sesión de Telegram
                self._set_status_msg("ARCHIVO DE SESIÓN DETECTADO. IMPORTANDO...", settings.COLOR_ACCENT)
                # Aquí podrías llamar a una función de importación de sesión si fuera necesario
                # Por ahora, ponemos la ruta para que el usuario sepa que se detectó
                self.url_entry.delete(0, 'end')
                self.url_entry.insert(0, data)
                show_message(self, "SESIÓN TELEGRAM", "HAS ARRASTRADO UN ARCHIVO DE SESIÓN.\nESTA FUNCIONALIDAD SE GESTIONA EN 'AJUSTES'.", self.image_manager)
            else:
                show_message(self, "ERROR", "TIPO DE ARCHIVO NO SOPORTADO.\nARRASTRA UNA URL O UN ARCHIVO .SESSION", self.image_manager)
        else:
            # Es una URL o texto plano
            # Limpiar posibles prefijos de navegadores
            url = data.split('\n')[0].strip() # Tomar solo la primera línea si hay varias
            self.url_entry.delete(0, 'end')
            self.url_entry.insert(0, url)
            
            # Auto-análisis instantáneo (UX Premium)
            self._set_status_msg("URL DETECTADA POR DRAG & DROP.", settings.COLOR_SUCCESS)
            self.after(100, self._on_analyze_click)
