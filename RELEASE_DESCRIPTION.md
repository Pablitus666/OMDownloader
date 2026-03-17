# 📦 OMDownloader v1.2.0 — Stable Elite Release

![Version](https://img.shields.io/badge/Version-1.2.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-Stable-green?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digitally%20Signed-blue?style=for-the-badge)

🎉 **¡OMDownloader v1.2.0 ya es una realidad!** Esta versión no es solo una actualización, es la consolidación de un sistema de adquisición de medios de nivel industrial. Hemos reconstruido el flujo de datos para garantizar que cada descarga sea rápida, segura y perfecta.

---

## 🔧 Notas de Lanzamiento (v1.2.0)

Esta edición marca la transición definitiva hacia una herramienta de **Ingeniería Senior**:

### 🚀 Rendimiento y Optimización
*   **Widget Recycling & Object Pooling:** Navegación ultra-fluida (60 FPS) en la cola de descargas, independientemente del número de tareas.
*   **Throttling de UI Inteligente:** Reducción dinámica de actualizaciones de progreso (10-30 FPS) para liberar recursos de CPU durante descargas masivas.
*   **EventBus de Alta Prioridad:** Comunicación desacoplada entre los motores de descarga y la interfaz.

### 🧼 Gestión de Datos y Privacidad
*   **Arquitectura de Escritorio Limpio:** Los archivos críticos (Base de Datos SQLite, Logs rotativos, Sesiones de Telegram) ahora se centralizan automáticamente en `%LOCALAPPDATA%\OMDownloader`.
*   **Ruta de Descargas Nativa:** Organización automática en la carpeta `Downloads\OMDownloader` de Windows para un acceso inmediato.

### 🛡️ Seguridad y Autenticidad
*   **Firma Digital SHA256:** Binarios firmados digitalmente por **Walter Pablo Téllez Ayala**. Se han eliminado las advertencias de "Editor Desconocido" de Windows.
*   **Integridad Verificada:** Cada ejecutable pasa por un proceso de auditoría antes de ser empaquetado.

### 📡 Evolución de Motores
*   **Telegram Engine v2:** Soporte robusto para URLs `t.me`, variantes K/Z y nombres de usuario. Manejo mejorado de `FloodWait` para sesiones prolongadas.
*   **yt-dlp Engine Pro:** Integración optimizada para la extracción rápida de metadatos y fusión transparente de audio/video.

---

## 🚀 Opciones de Distribución (Assets)

Elige el formato que mejor se adapte a tu flujo de trabajo:

1.  **OMDownloader_Setup.exe (Instalador):** Recomendado para una integración total con el sistema y accesos directos automáticos.
2.  **OMDownloader_Portable.exe (Único Archivo):** La máxima portabilidad. Ideal para herramientas en movimiento.
3.  **OMDownloader_Folder.zip (Versión Carpeta):** Optimizado para usuarios avanzados que buscan el arranque más rápido posible.

---

## 🔑 Configuración Rápida de Telegram

Recuerda configurar tus credenciales en la pestaña **Ajustes**:
1. Obtén tu `api_id` y `api_hash` en [my.telegram.org](https://my.telegram.org).
2. Pégalos en la aplicación y pulsa **"Aplicar Cambios"**.
3. Inicia sesión y comienza a descargar.

---

## 👨‍💻 Autoría

**Walter Pablo Téllez Ayala**  
*Senior Software Developer*  
📍 Bolivia 🇧🇴  

© 2026 — **OMDownloader Professional Edition**
