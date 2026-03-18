# OMDownloader - Motor de descarga yt-dlp (Élite Robustness)
import yt_dlp
import os
import time
from utils.logger import logger

class YTDLPEngine:
    """Motor avanzado de extracción y descarga con sanitización y fusión de formatos."""

    def __init__(self, download_path=None):
        self.download_path = download_path or os.getcwd()
        self.proxy = None
        self.cookies_file = None
        self.max_retries = 3
        self.retry_delay = 5

    def set_proxy(self, proxy_url):
        self.proxy = proxy_url

    def set_cookies(self, file_path):
        if file_path and os.path.exists(file_path):
            self.cookies_file = file_path

    def get_info(self, url):
        """Extrae metadatos con lógica de reintento."""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'skip_download': True,
            'proxy': self.proxy,
            'cookiefile': self.cookies_file,
            'extract_flat': 'in_playlist', 
            'noplaylist': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        for attempt in range(self.max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False, process=False)
                    return self._parse_metadata(info)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                logger.error(f"Error OSINT en {url}: {str(e)}")
                return None

    def download(self, url, options=None, progress_callback=None):
        """Descarga blindada con sanitización de nombres y detección de FFmpeg (Fase 12 - Senior)."""
        
        def _progress_hook(d):
            if progress_callback:
                progress_callback(self._parse_progress(d))

        # FASE 12: Detección inteligente de FFmpeg para portabilidad absoluta
        ffmpeg_location = None
        # Buscar ffmpeg.exe en el mismo directorio que el ejecutable (si existe)
        from utils.resources import get_base_path
        local_ffmpeg = os.path.join(get_base_path(), "ffmpeg.exe")
        if os.path.exists(local_ffmpeg):
            ffmpeg_location = get_base_path()

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(title).200B [%(id)s].%(ext)s'),
            'progress_hooks': [_progress_hook],
            'nocheckcertificate': True,
            'proxy': self.proxy,
            'cookiefile': self.cookies_file,
            'quiet': True,
            'no_color': True,
            'merge_output_format': 'mp4',
            'ffmpeg_location': ffmpeg_location, # Inyectar ruta si la encontramos localmente
            'retries': 10,
            'fragment_retries': 10,
            'retry_sleep_functions': {'http': lambda n: 5},
        }

        if options:
            ydl_opts.update(options)

        for attempt in range(self.max_retries):
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    return True
            except Exception as e:
                # Si el error es por falta de ffmpeg, intentamos descargar 'best' (sin fusión)
                if "ffmpeg" in str(e).lower() and ydl_opts.get('format') != 'best':
                    logger.warning("FFmpeg no detectado. Reintentando en modo compatibilidad (calidad reducida)...")
                    ydl_opts['format'] = 'best'
                    ydl_opts.pop('merge_output_format', None)
                    continue
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"Reintentando descarga ({attempt+1}/{self.max_retries}) por error: {e}")
                    time.sleep(self.retry_delay)
                    continue
                logger.error(f"Fallo persistente en descarga yt-dlp: {str(e)}")
                return False

    def _parse_metadata(self, info):
        if not info: return None
        desc = info.get('description', 'N/A')
        if desc and len(desc) > 300: desc = desc[:297] + "..."
        
        return {
            'id': info.get('id'),
            'title': info.get('title', 'N/A'),
            'uploader': info.get('uploader', 'N/A'),
            'upload_date': info.get('upload_date', 'N/A'),
            'description': desc,
            'duration': self._format_duration(info.get('duration', 0)),
            'thumbnail': info.get('thumbnail'),
            'ext': info.get('ext', 'N/A'),
            'extractor': info.get('extractor', 'N/A'),
            'webpage_url': info.get('webpage_url')
        }

    def _format_duration(self, seconds):
        if not seconds: return "00:00"
        import datetime
        return str(datetime.timedelta(seconds=int(seconds)))

    def _parse_progress(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%','').strip()
            try: percent = float(p)
            except: percent = 0.0
            return {
                'status': 'downloading',
                'percent': percent,
                'speed': d.get('_speed_str', 'N/A'),
                'eta': d.get('_eta_str', 'N/A'),
                'filename': d.get('filename', '')
            }
        elif d['status'] == 'finished':
            return {'status': 'finished', 'percent': 100.0, 'filename': d.get('filename', '')}
        return {'status': d['status'], 'percent': 0.0}
