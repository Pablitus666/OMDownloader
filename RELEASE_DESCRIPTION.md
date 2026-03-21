# 📦 OMDownloader v1.0.0 — Versión Estable

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-Official-green?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digitally%20Signed-blue?style=for-the-badge)

**Lanzamiento oficial de OMDownloader v1.0.0.** Esta versión consolida una arquitectura robusta para la descarga de medios desde Telegram y plataformas web, optimizando el uso de recursos del sistema y garantizando una experiencia de usuario fluida.

---

## 🔧 Notas de la Versión

Esta actualización introduce mejoras estructurales significativas centradas en la estabilidad y el rendimiento:

### 🚀 Rendimiento y Estabilidad
*   **Válvula de Eventos (30 FPS):** Implementación de un sistema de colas para eventos de interfaz que evita bloqueos del sistema durante descargas masivas.
*   **Gestión de Base de Datos:** Optimización de SQLite mediante el modo WAL (Write-Ahead Logging) y manejo seguro de conexiones para prevenir bloqueos de archivos.
*   **Refresco Seguro de UI:** Reestructuración de los métodos de actualización de la interfaz para evitar errores de recursión y mejorar la respuesta visual.

### 🧼 Gestión de Datos
*   **Persistencia Atómica:** Sistema de guardado de configuración que protege la integridad de los archivos ante interrupciones inesperadas.
*   **Almacenamiento Estructurado:** Organización centralizada de sesiones, logs y descargas en carpetas de sistema estándar.

### 🛡️ Seguridad
*   **Firma Digital:** Binarios firmados con certificado SHA256 para verificar la autenticidad del software.
*   **Protocolo de Cierre:** Secuencia de apagado que asegura la desconexión limpia de motores y la liberación de memoria.

### 📡 Mejoras en Motores
*   **Telegram Engine:** Analizador de URLs mejorado para soportar formatos complejos y parámetros adicionales.
*   **yt-dlp Wrapper:** Sistema de reintentos optimizado y gestión de dependencias externas (FFmpeg).

---

## ✨ Características Principales

*   📡 **Soporte Telegram:** Descarga de canales, grupos y chats con gestión de marcas de tiempo originales.
*   🎬 **Compatibilidad Web:** Soporte para YouTube, Twitter, TikTok y más de 1000 sitios mediante yt-dlp.
*   ⚙️ **Cola de Tareas:** Gestión de descargas paralelas con prioridades y seguimiento en tiempo real.
*   🌍 **Internacionalización:** Disponible en 9 idiomas con detección automática de idioma del sistema.

---

## 🚀 Distribución

1.  **OMDownloader_Setup.zip (Instalador):** Configuración asistida con accesos directos.
2.  **OMDownloader_Portable.zip (Portable):** Ejecución inmediata desde un solo archivo comprimido.
3.  **OMDownloader_Folder.zip (Carpeta):** Estructura de archivos abierta para máximo rendimiento.

---

## 👨‍💻 Autor

**Software Developer**  
📍 Bolivia 🇧🇴 <img src="https://flagcdn.com/w20/bo.png" width="20"/> <br>
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — Wordy Tool
