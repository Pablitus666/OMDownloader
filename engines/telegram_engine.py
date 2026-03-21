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
        """Versión asíncrona interna para máxima eficiencia."""
        if not self.client:
            from config import settings
            api_id = settings.TELEGRAM_API_ID
            api_hash = settings.TELEGRAM_API_HASH
            if not api_id or not api_hash or api_id == 0: return False
            try:
                self.client = TelegramClient(self.session_name, api_id, api_hash, loop=self.loop)
            except: return False

        if self.client.is_connected(): return True
        try:
            await asyncio.wait_for(self.client.connect(), timeout=15)
            return True
        except: return False

    def get_info(self, url):
        """Punto de entrada síncrono para análisis."""
        async def _analyze():
            if not await self._async_ensure_connected(): return None
            try:
                entity_id, msg_id = self.get_entity_from_url(url)
                if not entity_id: return None
                
                entity = await self.client.get_entity(entity_id)
                full_entity = None
                try:
                    if isinstance(entity, (types.Channel, types.Chat)):
                        full_entity = await self.client(functions.channels.GetFullChannelRequest(channel=entity))
                    elif isinstance(entity, types.User):
                        full_entity = await self.client(functions.users.GetFullUserRequest(id=entity))
                except: pass

                uploader = getattr(entity, 'title', getattr(entity, 'username', 'Telegram User'))
                username = getattr(entity, 'username', 'N/A')
                is_restricted = getattr(entity, 'noforwards', False)
                
                verified = "SÍ ✅" if getattr(entity, 'verified', False) else "NO"
                scam = "SÍ ⚠️" if getattr(entity, 'scam', False) else "NO"
                fake = "SÍ 🎭" if getattr(entity, 'fake', False) else "NO"
                restricted = "SÍ 🚫" if is_restricted else "NO"
                
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
        try: return future.result(timeout=7200)
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
                    await asyncio.sleep(0.05)
                return results
            except Exception as e:
                logger.error(f"Error en escaneo asíncrono: {e}")
                return results

        future = asyncio.run_coroutine_threadsafe(_scan(), self.loop)
        try: return future.result(timeout=300)
        except: return []

    def get_entity_from_url(self, url):
        """Analizador universal de URLs."""
        if not url: return None, None
        if '?' in url: url = url.split('?')[0]
        url = url.strip().replace(" ", "")
        
        if url.startswith('@'): return url[1:], None
        
        if 'web.telegram.org' in url:
            fragment = url.split('#')[-1] if '#' in url else ''
            if not fragment: return None, None
            clean_frag = fragment.replace('tgaddr?parts=', '').lstrip('@')
            if '_' in clean_frag:
                parts = clean_frag.split('_')
                try:
                    # Convertir a int si es un ID numérico
                    entity = int(parts[0]) if parts[0].replace('-', '').isdigit() else parts[0]
                    return entity, int(parts[1])
                except: pass
            # Caso ID simple sin mensaje
            if clean_frag.replace('-', '').isdigit(): return int(clean_frag), None
            return clean_frag, None
            
        if '/c/' in url:
            try:
                parts = url.rstrip('/').split('/')
                idx = parts.index('c')
                channel_id = parts[idx+1]
                msg_id = int(parts[idx+2]) if len(parts) > idx+2 else None
                if channel_id.replace('-', '').isdigit():
                    full_id = int(channel_id)
                    # Forzar prefijo -100 si parece un ID corto de canal privado
                    if not str(full_id).startswith('-100'):
                        full_id = int('-100' + str(full_id))
                    return full_id, msg_id
                return channel_id, msg_id
            except: pass
            
        parts = url.rstrip('/').split('/')
        if len(parts) >= 2:
            entity = parts[-2] if len(parts) >= 3 and parts[-1].isdigit() else parts[-1]
            if entity.replace('-', '').isdigit(): entity = int(entity)
            msg_id = int(parts[-1]) if parts[-1].isdigit() else None
            return entity.lstrip('@') if isinstance(entity, str) else entity, msg_id
            
        return url.lstrip('@'), None

    def get_message_media(self, entity_id, msg_id):
        """Obtiene el objeto de mensaje media."""
        async def _get():
            if not await self._async_ensure_connected(): return None
            try:
                entity = await self.client.get_entity(entity_id)
                return await self.client.get_messages(entity, ids=msg_id)
            except: return None
        try: return asyncio.run_coroutine_threadsafe(_get(), self.loop).result(timeout=30)
        except: return None

    def is_connected_status(self):
        return self.client and self.client.is_connected()

    def send_code_request(self, phone):
        """Solicita el código de inicio de sesión."""
        async def _request():
            for attempt in range(2):
                if not await self._async_ensure_connected(): return False
                try:
                    phone_clean = phone.strip().replace(" ", "")
                    if not phone_clean.startswith("+"): phone_clean = f"+591{phone_clean}"
                    self._phone = phone_clean
                    res = await self.client.send_code_request(phone_clean)
                    self._phone_code_hash = res.phone_code_hash
                    return True
                except errors.AuthRestartError:
                    await self.client.disconnect()
                    await asyncio.sleep(1)
                    continue
                except: return False
            return False
        try: return asyncio.run_coroutine_threadsafe(_request(), self.loop).result(timeout=60)
        except: return False

    def sign_in(self, code, password=None):
        """Completa el inicio de sesión."""
        async def _login():
            if not await self._async_ensure_connected(): return False
            try:
                try:
                    await self.client.sign_in(self._phone, code, phone_code_hash=self._phone_code_hash)
                    return True
                except errors.SessionPasswordNeededError:
                    if password:
                        await self.client.sign_in(password=password)
                        return True
                    return "2FA_REQUIRED"
                except: return False
            except: return False
        try: return asyncio.run_coroutine_threadsafe(_login(), self.loop).result(timeout=30)
        except: return False

    def disconnect(self):
        """Cierre atómico limpio."""
        if not self.loop or not self.loop.is_running(): return
        async def _disc():
            if self.client: 
                try: await self.client.disconnect()
                except: pass
            tasks = [t for t in asyncio.all_tasks(self.loop) if t is not asyncio.current_task()]
            for task in tasks: task.cancel()
            try: await asyncio.gather(*tasks, return_exceptions=True)
            except: pass
            self.loop.stop()
        asyncio.run_coroutine_threadsafe(_disc(), self.loop)
