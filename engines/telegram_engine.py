# OMDownloader - Motor de Telegram OSINT Profesional (Fase 12 - Senior)
import os
import asyncio
import threading
import time
import base64
from io import BytesIO
from telethon import TelegramClient, errors, functions, types
from config import settings
from utils.logger import tg_logger as logger

class TelegramEngine:
    """Motor MTProto de Nivel Senior: Gestión asíncrona total sin bloqueos de hilo."""

    def __init__(self, api_id, api_hash, session_name='anon'):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.loop = asyncio.new_event_loop()
        self.is_connected = False
        self.client = None
        self.loop_ready = threading.Event()
        
        # SIEMPRE iniciamos el loop, independientemente de las credenciales
        # Esto evita el timeout infinito al intentar interactuar con el motor
        threading.Thread(target=self._start_loop, daemon=True).start()
        if not self.loop_ready.wait(timeout=10):
            logger.error("TelegramEngine: Fallo al iniciar loop asyncio.")
            return

        if not self.api_id or not self.api_hash or self.api_id == 0:
            logger.warning("TelegramEngine: Credenciales no configuradas. Motor en espera...")
            return

        # Inicialización no bloqueante del cliente si hay credenciales
        self.loop.call_soon_threadsafe(self._init_client)

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop_ready.set()
        self.loop.run_forever()

    def _init_client(self):
        """Inicializa el cliente dentro del loop de asyncio."""
        try:
            self.client = TelegramClient(
                self.session_name, self.api_id, self.api_hash, 
                loop=self.loop,
                connection_retries=10,
                retry_delay=5,
                auto_reconnect=True
            )
            # El cliente Telethon necesita ser iniciado/conectado dentro del loop
            # pero lo haremos a demanda o vía connect() explicito.
        except Exception as e:
            logger.error(f"Fallo al crear cliente Telethon: {e}")

    def connect(self):
        """Conexión síncrona (espera controlada) para el arranque."""
        if not self.client: return False
        async def _conn():
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                return True
            except Exception as e:
                logger.error(f"TelegramEngine: Error en connect: {e}")
                return False
        
        try:
            return asyncio.run_coroutine_threadsafe(_conn(), self.loop).result(timeout=30)
        except: return False

    def is_authorized(self):
        async def _check():
            try:
                if not self.client.is_connected(): await self.client.connect()
                return await self.client.is_user_authorized()
            except: return False
        try:
            return asyncio.run_coroutine_threadsafe(_check(), self.loop).result(timeout=15)
        except: return False

    async def _async_ensure_connected(self):
        """Versión asíncrona interna para máxima eficiencia con auto-inicialización y reparación."""
        if not self.client:
            from config import settings
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            
            if not api_id or not api_hash or api_id == 0:
                logger.error("TelegramEngine: No se puede conectar sin API_ID/API_HASH configurados.")
                return False
                
            try:
                logger.info(f"TelegramEngine: Inicializando cliente bajo demanda con API_ID: {api_id}")
                self.api_id = api_id
                self.api_hash = api_hash
                self.client = TelegramClient(
                    self.session_name, self.api_id, self.api_hash, 
                    loop=self.loop,
                    connection_retries=5,
                    retry_delay=2,
                    auto_reconnect=True
                )
            except Exception as e:
                logger.error(f"TelegramEngine: Error al crear cliente bajo demanda: {e}")
                return False

        if self.client.is_connected():
            return True
            
        try:
            # Intento de conexión con timeout agresivo
            await asyncio.wait_for(self.client.connect(), timeout=15)
            return True
        except Exception as e:
            logger.warning(f"TelegramEngine: Fallo al conectar ({e}). Intentando limpieza de sesión...")
            try:
                # Si el error persiste, la sesión podría estar corrupta. 
                # Desconectamos y dejamos que el siguiente intento re-inicialice.
                await self.client.disconnect()
            except: pass
            return False

    def get_info(self, url):
        """Punto de entrada síncrono para análisis (usado por Services)."""
        async def _analyze():
            if not await self._async_ensure_connected(): return None
            try:
                entity_id, msg_id = self.get_entity_from_url(url)
                if not entity_id: return None
                
                # FASE 12: Extracción de Entidad Completa (OSINT Senior)
                entity = await self.client.get_entity(entity_id)
                full_entity = None
                try:
                    # Intentar obtener información extendida (Bio, Participantes)
                    if isinstance(entity, (types.Channel, types.Chat)):
                        full_entity = await self.client(functions.channels.GetFullChannelRequest(channel=entity))
                    elif isinstance(entity, types.User):
                        full_entity = await self.client(functions.users.GetFullUserRequest(id=entity))
                except: pass

                uploader = getattr(entity, 'title', getattr(entity, 'username', 'Telegram User'))
                username = getattr(entity, 'username', 'N/A')
                is_restricted = getattr(entity, 'noforwards', False)
                
                # Metadatos de Seguridad y Verificación
                verified = "SÍ ✅" if getattr(entity, 'verified', False) else "NO"
                scam = "SÍ ⚠️" if getattr(entity, 'scam', False) else "NO"
                fake = "SÍ 🎭" if getattr(entity, 'fake', False) else "NO"
                restricted = "SÍ 🚫" if is_restricted else "NO"
                
                # Información de Participantes y Bio
                participants = "N/A"
                description = "Sin descripción"
                if full_entity:
                    if hasattr(full_entity, 'full_chat'):
                        participants = getattr(full_entity.full_chat, 'participants_count', "N/A")
                        description = getattr(full_entity.full_chat, 'about', "Sin descripción")
                    elif hasattr(full_entity, 'about'):
                        description = full_entity.about or "Sin descripción"

                avatar_b64 = None
                try:
                    photo_bytes = await self.client.download_profile_photo(entity, file=BytesIO())
                    if photo_bytes:
                        photo_bytes.seek(0)
                        avatar_b64 = f"data:image/jpeg;base64,{base64.b64encode(photo_bytes.read()).decode()}"
                except: pass

                if msg_id:
                    message = await self.client.get_messages(entity, ids=msg_id)
                    if not message or not message.media: return None
                    title = message.file.name if hasattr(message, 'file') and message.file and message.file.name else "Video/Archivo"
                    
                    msg_thumb = None
                    try:
                        if message.photo or message.video:
                            m_bytes = await self.client.download_media(message, file=BytesIO(), thumb=-1)
                            if m_bytes:
                                m_bytes.seek(0)
                                msg_thumb = f"data:image/jpeg;base64,{base64.b64encode(m_bytes.read()).decode()}"
                    except: pass

                    return {
                        'id': str(message.id),
                        'title': f"{'[PROTEGIDO] ' if is_restricted else ''}{title}",
                        'uploader': uploader,
                        'username': f"@{username}" if username != "N/A" else "N/A",
                        'upload_date': message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else "N/A",
                        'extractor': 'Shielded MTProto',
                        'webpage_url': url,
                        'is_message': True,
                        'thumbnail': msg_thumb or avatar_b64,
                        'verified': verified, 'scam': scam, 'fake': fake,
                        'restricted': restricted, 'participants': participants,
                        'description': description
                    }
                else:
                    return {
                        'id': str(entity.id),
                        'title': f"CANAL: {uploader}",
                        'uploader': uploader,
                        'username': f"@{username}" if username != "N/A" else "N/A",
                        'extractor': 'Telegram Channel OSINT',
                        'webpage_url': url,
                        'is_message': False,
                        'thumbnail': avatar_b64,
                        'verified': verified, 'scam': scam, 'fake': fake,
                        'restricted': restricted, 'participants': participants,
                        'description': description
                    }
            except Exception as e:
                logger.error(f"Error asíncrono en get_info: {e}")
                return None

        # Usamos timeout para no bloquear el hilo del Services permanentemente
        future = asyncio.run_coroutine_threadsafe(_analyze(), self.loop)
        try: return future.result(timeout=60)
        except: return None

    def download_media(self, message_or_url, output_path, progress_callback=None, task_ref=None):
        """Descarga asíncrona real."""
        async def _down():
            last_update = 0
            if not await self._async_ensure_connected(): return None
            
            try:
                msg = message_or_url
                if isinstance(message_or_url, str):
                    entity_id, msg_id = self.get_entity_from_url(message_or_url)
                    entity = await self.client.get_entity(entity_id)
                    msg = await self.client.get_messages(entity, ids=msg_id)

                if not msg: return None

                def _prog(cur, tot):
                    nonlocal last_update
                    if task_ref and task_ref._is_cancelled: raise Exception("DOWNLOAD_CANCELLED")
                    while task_ref and task_ref._is_paused and not task_ref._is_cancelled: time.sleep(0.5)
                    
                    now = time.time()
                    if now - last_update < 0.2: return
                    last_update = now
                    if progress_callback:
                        p = (cur/tot)*100 if tot > 0 else 0
                        progress_callback({'status': 'downloading', 'percent': p, 'current': cur, 'total': tot})
                
                return await self.client.download_media(msg, file=output_path, progress_callback=_prog)
            except errors.FloodWaitError as e:
                logger.warning(f"Telegram FloodWait: {e.seconds}s")
                await asyncio.sleep(e.seconds)
                return await _down()
            except Exception as e:
                if "DOWNLOAD_CANCELLED" not in str(e): logger.error(f"Error en descarga asíncrona: {e}")
                return None

        future = asyncio.run_coroutine_threadsafe(_down(), self.loop)
        try: return future.result(timeout=7200) # 2 horas para archivos masivos
        except: return None

    def scan_media(self, url, media_type="video", limit=2000):
        """Escaneo asíncrono ultra-rápido."""
        async def _scan():
            if not await self._async_ensure_connected(): return []
            results = []
            try:
                entity_id, _ = self.get_entity_from_url(url)
                if not entity_id: return []
                entity = await self.client.get_entity(entity_id)
                max_items = min(limit, 2000)

                # Avatares primero
                if media_type == "photo":
                    try:
                        photos = await self.client.get_profile_photos(entity)
                        for i, photo in enumerate(photos):
                            results.append({
                                'url': url,
                                'metadata': {
                                    'id': f"avatar_{photo.id}",
                                    'title': f"Avatar_Historico_{len(photos)-i}",
                                    'uploader': getattr(entity, 'title', 'Telegram'),
                                    'upload_date': "N/A", 'extractor': 'Avatar History OSINT',
                                    'is_raw_media': True, 'media_obj': photo, 'entity_id': entity.id
                                }
                            })
                            if len(results) >= max_items: break
                    except: pass

                # Mensajes después
                offset_id = 0
                while len(results) < max_items:
                    messages = await self.client.get_messages(entity, limit=100, offset_id=offset_id)
                    if not messages: break
                    
                    for message in messages:
                        offset_id = message.id
                        if not message.media: continue
                        
                        mime = ""
                        if hasattr(message, 'document') and message.document:
                            mime = message.document.mime_type or ""
                        
                        is_video = message.video or mime.startswith('video/') or mime == 'application/x-tgvideo'
                        is_gif = False
                        if hasattr(message, 'document') and message.document:
                            is_gif = any(isinstance(a, types.DocumentAttributeAnimated) for a in message.document.attributes) or mime == "image/gif"
                        
                        is_voice = message.voice or mime.startswith('audio/ogg')
                        
                        add = False
                        # FASE 12: Inclusión inteligente de medios en categoría VIDEO
                        if media_type == "video" and (is_video or is_gif or is_voice): add = True
                        elif media_type == "photo" and message.photo: add = True
                        elif media_type == "document" and hasattr(message, 'document') and message.document and not is_video and not is_voice and not is_gif: add = True
                        
                        if add:
                            title = message.file.name if hasattr(message, 'file') and message.file and message.file.name else f"{media_type}_{message.id}"
                            if is_voice and media_type == "video": title = f"Nota_de_Voz_{message.id}.ogg"
                            if is_gif and media_type == "video": title = f"GIF_{message.id}.mp4"
                            cid = str(entity.id)
                            display_cid = cid[4:] if cid.startswith('-100') else cid
                            results.append({
                                'url': f"https://t.me/c/{display_cid}/{message.id}",
                                'metadata': {
                                    'id': str(message.id), 'title': title,
                                    'uploader': getattr(entity, 'title', 'Telegram'),
                                    'upload_date': message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else "N/A",
                                    'extractor': 'Shielded MTProto', 'entity_id': entity.id
                                }
                            })
                            if len(results) >= max_items: break
                    await asyncio.sleep(0.05) # Delay mínimo para no saturar pero ser rápido
                return results
            except Exception as e:
                logger.error(f"Error en escaneo asíncrono: {e}")
                return results

        future = asyncio.run_coroutine_threadsafe(_scan(), self.loop)
        try: return future.result(timeout=300) # 5 minutos para escaneos masivos
        except: return []

    def get_entity_from_url(self, url):
        """Analizador universal de URLs Élite (Fase 12 - Senior)."""
        if not url: return None, None
        url = url.strip().replace(" ", "")
        
        # Caso 1: Nombre de usuario directo (@user o user)
        if url.startswith('@'): return url[1:], None
        
        # Caso 2: URLs de la Web oficial (web.telegram.org)
        if 'web.telegram.org' in url:
            fragment = url.split('#')[-1] if '#' in url else ''
            if not fragment: return None, None
            clean_frag = fragment.replace('q=', '').lstrip('@')
            if '_' in clean_frag:
                parts = clean_frag.split('_')
                try:
                    entity = parts[0]
                    # Manejar IDs de canales negativos
                    if entity.replace('-', '').isdigit(): return int(entity), int(parts[1])
                    return entity, int(parts[1])
                except: pass
            if clean_frag.replace('-', '').isdigit(): return int(clean_frag), None
            return clean_frag, None
            
        # Caso 3: Enlaces cortos (t.me/c/ o telegram.me/c/) - Canales Privados/Específicos
        if '/c/' in url:
            try:
                parts = url.rstrip('/').split('/')
                # El ID del canal está antes del ID del mensaje
                idx = parts.index('c')
                channel_id = parts[idx+1]
                msg_id = int(parts[idx+2]) if len(parts) > idx+2 else None
                
                if channel_id.isdigit():
                    # Los canales privados en MTProto requieren el prefijo -100
                    full_id = int('-100' + channel_id) if not channel_id.startswith('-100') else int(channel_id)
                    return full_id, msg_id
                return channel_id, msg_id
            except: pass
            
        # Caso 4: Enlaces públicos estándar (t.me/nombre o t.me/nombre/123)
        parts = url.rstrip('/').split('/')
        if len(parts) >= 3: # https://t.me/user/123
            entity = parts[-2]
            try:
                msg_id = int(parts[-1])
                return entity.lstrip('@'), msg_id
            except:
                # Si el último no es número, el último es la entidad
                return parts[-1].lstrip('@'), None
        elif len(parts) == 2: # t.me/user o user
            return parts[-1].lstrip('@'), None
            
        # Fallback: Intentar usar el string completo como entidad si no tiene barras
        if '/' not in url:
            return url.lstrip('@'), None
            
        return None, None

    def get_message_media(self, entity_id, msg_id):
        async def _get():
            if not await self._async_ensure_connected(): return None
            try:
                entity = await self.client.get_entity(entity_id)
                return await self.client.get_messages(entity, ids=msg_id)
            except: return None
        try: return asyncio.run_coroutine_threadsafe(_get(), self.loop).result(timeout=30)
        except: return None

    def is_connected_status(self):
        """Devuelve si el cliente está conectado físicamente."""
        return self.client and self.client.is_connected()

    def send_code_request(self, phone):
        """Solicita el código de inicio de sesión a Telegram (Síncrono para la UI)."""
        async def _request():
            # Intentar hasta 2 veces si hay errores de reinicio de sesión
            for attempt in range(2):
                if not await self._async_ensure_connected(): 
                    logger.error("TelegramEngine: No se pudo asegurar la conexión antes de enviar código.")
                    return False
                try:
                    # Normalizar número (Bolivia +591 por defecto si no tiene +)
                    phone_clean = phone.strip().replace(" ", "")
                    if not phone_clean.startswith("+"):
                        phone_clean = f"+591{phone_clean}"
                    
                    # Almacenar el hash para el siguiente paso del login
                    self._phone = phone_clean
                    logger.info(f"TelegramEngine: Solicitando código para {phone_clean} (Intento {attempt+1})...")
                    res = await self.client.send_code_request(phone_clean)
                    self._phone_code_hash = res.phone_code_hash
                    logger.info(f"TelegramEngine: Código enviado con éxito. Hash: {self._phone_code_hash}")
                    return True
                except errors.AuthRestartError:
                    logger.warning("TelegramEngine: AuthRestartError detectado. Reiniciando cliente...")
                    await self.client.disconnect()
                    await asyncio.sleep(1)
                    continue # Reintentar tras desconectar
                except errors.FloodWaitError as e:
                    logger.error(f"TelegramEngine: Demasiados intentos. Espera {e.seconds} segundos.")
                    return f"FLOOD_WAIT_{e.seconds}"
                except Exception as e:
                    import traceback
                    logger.error(f"TelegramEngine: Error al solicitar código: {str(e)}")
                    # Si estamos desconectados, intentar reconectar en el próximo intento del bucle
                    if "disconnected" in str(e).lower():
                        await asyncio.sleep(1)
                        continue
                    return False
            return False
        
        try:
            # Aumentamos el timeout global para permitir los reintentos
            return asyncio.run_coroutine_threadsafe(_request(), self.loop).result(timeout=60)
        except Exception as e:
            logger.error(f"TelegramEngine: Timeout o fallo crítico en send_code_request: {e}")
            return False

    def sign_in(self, code, password=None):
        """Completa el inicio de sesión con el código (y password si tiene 2FA)."""
        async def _login():
            if not await self._async_ensure_connected(): return False
            try:
                try:
                    await self.client.sign_in(self._phone, code, phone_code_hash=self._phone_code_hash)
                    logger.info("Inicio de sesión completado con éxito.")
                    return True
                except errors.SessionPasswordNeededError:
                    if password:
                        await self.client.sign_in(password=password)
                        logger.info("Inicio de sesión con 2FA completado con éxito.")
                        return True
                    else:
                        logger.warning("Se requiere contraseña 2FA.")
                        return "2FA_REQUIRED"
                except Exception as e:
                    logger.error(f"Error en sign_in de Telethon: {e}")
                    return False
            except Exception as e:
                logger.error(f"Fallo crítico en sign_in: {e}")
                return False

        try:
            return asyncio.run_coroutine_threadsafe(_login(), self.loop).result(timeout=30)
        except Exception as e:
            logger.error(f"Timeout en sign_in: {e}")
            return False

    def disconnect(self):
        """Cierre atómico del cliente y detención del bucle de eventos."""
        async def _disc():
            if self.client: 
                await self.client.disconnect()
            self.loop.stop() # DETENER FÍSICAMENTE EL LOOP
            
        if self.client and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(_disc(), self.loop)
