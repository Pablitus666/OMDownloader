# 🚀 OMDownloader — Hybrid Media Downloader (Telegram + yt-dlp)

**OSINT & Media Acquisition Tool** | Herramienta de **Descarga de Medios Híbrida** con Gestión de Colas de Alto Rendimiento.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows)
![Architecture](https://img.shields.io/badge/Architecture-MVC%20%2B%20Service%20Locator-informational?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digitally%20Signed-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)

---

**OMDownloader** es una aplicación diseñada para la adquisición de contenido multimedia. Integra el motor de **Telegram (MTProto)** con la versatilidad de **yt-dlp** bajo una arquitectura modular.

Implementa un sistema de colas asíncrono que garantiza la estabilidad del sistema incluso durante el procesamiento de grandes volúmenes de datos.

### 🎯 Casos de Uso
*   **Investigación OSINT:** Extracción de medios y metadatos asociados.
*   **Preservación Digital:** Archivo de contenido desde canales y grupos.
*   **Gestión de Medios:** Descarga centralizada de activos multimedia desde múltiples plataformas.

---

![OMDownloader Preview](https://raw.githubusercontent.com/Pablitus666/OMDownloader/main/images2/preview.png)

---

## ⚡ Especificaciones Técnicas

| Componente | Implementación |
| :--- | :--- |
| **Motor Híbrido** | Uso de **Telethon** y **yt-dlp** para cobertura de más de 1000 sitios. |
| **Interfaz Fluida** | Sistema de reciclaje de widgets para mantener el rendimiento con listas extensas. |
| **Válvula de Eventos** | EventBus con control de ráfagas (30 FPS) para evitar saturación de la interfaz. |
| **Persistencia** | Base de datos **SQLite en modo WAL** para operaciones de escritura concurrentes. |
| **Alta Resolución** | Soporte nativo para pantallas de alta densidad (HiDPI) y assets vectorizados. |
| **Seguridad** | Firma digital **SHA256** para verificación de integridad. |

---

## ✨ Características 

*   📡 **Motor de Telegram:** Soporte para canales, grupos y chats privados. Gestión de `FloodWait`, descarga de avatares históricos y análisis de URLs complejas.
*   🎬 **Soporte Universal (yt-dlp):** Descarga de video y audio con fusión automática a MP4 mediante FFmpeg.
*   ⚙️ **Gestión de Recursos:**
    *   **PriorityQueue:** Cola de tareas con estados rastreables y reintentos automáticos.
    *   **Cierre Seguro:** Protocolo de apagado atómico para liberar sesiones y hilos activos.
    *   **Caché LRU:** Gestión eficiente de memoria para miniaturas e imágenes de interfaz.
*   🧼 **Experiencia de Usuario:** Interfaz optimizada con soporte para 9 idiomas y detección automática de configuración regional.

---

## 🏗️ Estructura del Proyecto

```text
OMDownloader/
├── assets/             # Recursos: Fuentes, Imágenes y Archivos de Idioma.
├── config/             # Configuración y constantes del sistema.
├── core/               # Lógica central: EventBus, Base de Datos y Gestión de Colas.
├── engines/            # Controladores de descarga (Telegram y yt-dlp).
├── gui/                # Componentes de interfaz y pestañas modulares.
├── data/               # Almacenamiento de sesiones, logs y base de datos.
├── utils/              # Herramientas de soporte: Gestión de imágenes y recursos.
└── main.py             # Punto de entrada y orquestación de servicios.
```

---

![OMDownloader Preview](https://raw.githubusercontent.com/Pablitus666/OMDownloader/main/images2/preview.png)

---


## 🔑 Configuración de Credenciales

Para utilizar el motor de Telegram es necesario configurar credenciales propias:

1.  Acceda a [**my.telegram.org**](https://my.telegram.org) e inicie sesión.
2.  Entre en **"API development tools"**.
3.  Cree una aplicación para obtener su **api_id** y **api_hash**.
4.  En la aplicación, vaya a la pestaña **Ajustes**, ingrese los datos y aplique los cambios.

---

## 🚀 Distribución

### 1. Instalador (`OMDownloader_Setup.zip`)
Configura la aplicación en el sistema con accesos directos y gestor de desinstalación.
> **Disponible en la sección de [Releases](https://github.com/Pablitus666/OMDownloader/releases)**

### 2. Versión Portable (`OMDownloader_Portable.zip`)
Ejecutable único que no requiere instalación previa.

### 3. Versión en Carpeta (`OMDownloader_Folder.zip`)
Estructura de archivos abierta para ejecución directa y carga rápida.

---

## ⚠️ Uso Responsable

Esta herramienta ha sido desarrollada para fines de investigación y archivo personal. El usuario es responsable de cumplir con los términos de servicio de las plataformas y las regulaciones locales sobre propiedad intelectual.

--- 

## 👨‍💻 Autor

**Walter Pablo Téllez Ayala**  
Software Developer  
📍 Bolivia 🇧🇴 <img src="https://flagcdn.com/w20/bo.png" width="20"/> <br>
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — Wordy Tool

---

⭐ Repositorio Oficial: [**GitHub**](https://github.com/Pablitus666/OMDownloader.git)
