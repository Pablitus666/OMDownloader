# OMDownloader - Caché Inteligente de Miniaturas
from PIL import Image
from io import BytesIO
import threading

class ThumbnailCache:
    """Caché LRU para miniaturas para evitar descargas repetidas."""
    def __init__(self, max_size=50):
        self.cache = {} # URL -> PIL Image
        self.order = []
        self.max_size = max_size
        self.lock = threading.Lock()

    def get(self, url):
        with self.lock:
            if url in self.cache:
                # Mover al final (más reciente)
                self.order.remove(url)
                self.order.append(url)
                return self.cache[url]
        return None

    def set(self, url, image):
        with self.lock:
            if url in self.cache:
                self.order.remove(url)
            elif len(self.cache) >= self.max_size:
                oldest = self.order.pop(0)
                del self.cache[oldest]
            
            self.cache[url] = image
            self.order.append(url)

    def clear(self):
        with self.lock:
            self.cache.clear()
            self.order.clear()

# Instancia global
thumb_cache = ThumbnailCache()
