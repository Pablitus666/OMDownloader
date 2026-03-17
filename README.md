# 🚀 OMDownloader — Hybrid Media Downloader (Telegram + yt-dlp)

**OSINT & Media Acquisition Tool** | Herramienta Profesional de **Descarga de Medios Híbrida** con Gestión de Colas de Alto Rendimiento.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Architecture](https://img.shields.io/badge/Architecture-MVC%20%2B%20Service%20Locator-informational?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digitally%20Signed-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Elite%20Edition-gold?style=for-the-badge)

---

**OMDownloader** es una estación de trabajo avanzada diseñada para la adquisición masiva y quirúrgica de contenido multimedia. Fusiona la potencia de **Telegram (MTProto)** con la versatilidad de **yt-dlp**, todo bajo una arquitectura de ingeniería de software de alto nivel.

A diferencia de herramientas convencionales, **OMDownloader** implementa un sistema de colas asíncrono y desacoplado que garantiza estabilidad absoluta, incluso bajo cargas extremas de datos.

### 🎯 Público Objetivo
*   **Investigadores OSINT:** Extracción forense de medios y metadatos.
*   **Archivistas Digitales:** Preservación de contenido de canales y grupos.
*   **Creadores de Contenido:** Gestión centralizada de assets multimedia.
*   **Power Users:** Usuarios que exigen una herramienta limpia, rápida y sin telemetría intrusiva.

---

![OMDownloader Preview](https://raw.githubusercontent.com/Pablitus666/OMDownloader/main/images2/preview.png)

---

## ⚡ Ingeniería de Nivel Élite

| Dimensión | Excelencia Técnica |
| :--- | :--- |
| **Motor Híbrido** | Integración nativa de **Telethon** (Telegram) y **yt-dlp** para cobertura universal. |
| **Rendimiento 60 FPS** | **Widget Recycling** y **Object Pooling** para una UI fluida con miles de tareas. |
| **Throttling Inteligente** | EventBus optimizado (10-30 FPS) para minimizar el impacto en la CPU. |
| **Privacidad Total** | Almacenamiento aislado en `%LOCALAPPDATA%`. Cero archivos temporales en el escritorio. |
| **HiDPI Ready** | Escalado dinámico y assets multi-capa para nitidez perfecta en monitores 4K. |
| **Firma Digital** | Autenticidad garantizada mediante firma **SHA256** de Walter Pablo Téllez Ayala. |

---

## ✨ Características Destacadas

*   📡 **Motor de Telegram Blindado:** Soporte para canales, grupos y chats privados. Gestión automática de `FloodWait`, captura de avatares históricos y preservación de marcas de tiempo.
*   🎬 **Soporte Universal (yt-dlp):** Descarga inteligente de videos, audio y playlists desde cientos de plataformas (YouTube, Twitter, TikTok, etc.) con fusión automática a MP4 de alta calidad.
*   ⚙️ **Arquitectura de Microservicios Local:**
    *   **PriorityQueue:** Sistema de colas con reintentos inteligentes y persistencia en **SQLite (WAL Mode)**.
    *   **Shutdown Atómico:** Finalización limpia de hilos y procesos para evitar procesos zombis.
    *   **Caché de Doble Nivel:** ImageManager con caché LRU (Memoria/Disco) para una navegación instantánea.
*   🧼 **UX Industrial:** Interfaz moderna (Modo Light Forzado) diseñada para la claridad operativa, con soporte para 9 idiomas y detección dinámica del sistema.
*   🛡️ **Seguridad Corporativa:** Ejecutables e Instaladores firmados digitalmente. Integridad verificada desde el primer clic.

---

## 🏗️ Estructura del Ecosistema

```text
OMDownloader/
├── assets/             # Recursos: Fuentes TTF, Imágenes Master, I18n JSON.
├── config/             # Configuración centralizada y constantes estéticas.
├── core/               # El Corazón: EventBus, DB, QueueManager, I18n Engine.
├── engines/            # Motores: Telegram MTProto y Wrapper de yt-dlp.
├── gui/                # Vista: Pestañas modulares y componentes de Virtual List.
├── data/               # (Persistent) DB, Sesiones y Logs en %LOCALAPPDATA%.
├── utils/              # Utilidades: ImageManager, Logger Rotativo, Resources.
└── main.py             # Bootstrap de la aplicación y DI (Dependency Injection).
```

---

## 🔑 Configuración de Telegram (API ID & API Hash)

Para activar la potencia total del motor de Telegram, necesitas tus propias credenciales (proceso gratuito de 2 minutos):

1.  Inicia sesión en [**my.telegram.org**](https://my.telegram.org).
2.  Accede a **"API development tools"**.
3.  Crea una aplicación (ej: "OMDownloader") para obtener tu **api_id** y **api_hash**.
4.  **En la App:** Ve a la pestaña **Ajustes**, introduce los valores y pulsa **"Aplicar Cambios"**.
5.  Inicia sesión con tu número de teléfono de forma segura.

---

## 🚀 Distribución y Despliegue

### 1. Instalador Profesional (`OMDownloader_Setup.exe`) 💻
La experiencia definitiva. Instala la aplicación con accesos directos automáticos y gestión de desinstalación limpia.
> **Descarga desde [Releases](https://github.com/Pablitus666/OMDownloader/releases)**

### 2. Edición Portable (`OMDownloader_Portable.exe`) 🏃
Un único archivo ejecutable que contiene todo el ecosistema. Ideal para llevar en unidades externas.

### 3. Versión en Carpeta (`OMDownloader_Folder.zip`) 🖥️
Máximo rendimiento de arranque. Ideal para entornos de trabajo fijos donde la velocidad de carga es crítica.

---

## ⚠️ Compromiso de Uso Responsable

**OMDownloader** es una herramienta potente diseñada para la investigación, el archivo personal y la educación. El usuario es el único responsable del cumplimiento de los términos de servicio de las plataformas de origen y las leyes de propiedad intelectual vigentes.

---

## 👨‍💻 Autoría y Soporte

**Walter Pablo Téllez Ayala**  
*Senior Software Developer*  
📍 Bolivia 🇧🇴  
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — **OMDownloader Professional Edition**

---

⭐ Si OMDownloader aporta valor a tu flujo de trabajo, apoya el proyecto con una estrella: [**Repositorio Oficial**](https://github.com/Pablitus666/OMDownloader.git)
