# 📦 OMDownloader v1.0.0 — Lanzamiento Oficial

![Version](https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge)
![Release](https://img.shields.io/badge/Release-Official-green?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Digitally%20Signed-blue?style=for-the-badge)

🎉 **¡Bienvenidos al lanzamiento oficial de OMDownloader v1.0.0!** Esta es la primera versión pública de nuestra estación de trabajo avanzada para la adquisición de medios. Hemos diseñado este sistema desde cero para garantizar una experiencia de descarga rápida, segura y de alto rendimiento.

---

## 🔧 Notas de esta Versión (v1.0.0)

Este lanzamiento marca el inicio de una herramienta de **Ingeniería del script** de primer nivel:

### 🚀 Ingeniería del script
*   **Widget Recycling & Object Pooling:** Navegación fluida (60 FPS) en la cola de descargas, permitiendo gestionar cientos de tareas sin retardos.
*   **Throttling de UI Inteligente:** Optimización de las actualizaciones de progreso (10-30 FPS) para maximizar la eficiencia del sistema.
*   **EventBus Desacoplado:** Arquitectura profesional que separa los motores de descarga de la interfaz de usuario.

### 🧼 Gestión de Datos y Privacidad
*   **Almacenamiento Centralizado:** Los datos críticos (Base de Datos SQLite, Logs, Sesiones) se gestionan de forma segura en `%LOCALAPPDATA%\OMDownloader`.
*   **Organización Automática:** Las descargas se dirigen por defecto a la carpeta `Downloads\OMDownloader` para un acceso inmediato.

### 🛡️ Seguridad y Autenticidad
*   **Firma Digital SHA256:** Todos los binarios están firmados digitalmente por **Walter Pablo Téllez Ayala**, garantizando la integridad del software.
*   **Entorno Seguro:** Aplicación diseñada para funcionar de forma aislada, sin telemetría ni archivos temporales dispersos.

### 📡 Motores de Descarga
*   **Motor de Telegram:** Soporte completo para URLs `t.me`, canales, grupos y chats privados con manejo de `FloodWait`.
*   **Motor yt-dlp:** Integración universal para extraer videos y audio de cientos de plataformas con la mejor calidad disponible.

---

## ✨ Características

*   📡 **Soporte de Telegram:** Captura de medios y avatares históricos con preservación de metadatos originales.
*   🎬 **Descarga Universal:** Fusión automática de audio y video a formato MP4 mediante yt-dlp.
*   ⚙️ **Gestión de Colas:** Sistema de persistencia en **SQLite (WAL Mode)** para evitar la pérdida de tareas.
*   🌍 **Internacionalización:** Soporte nativo para 9 idiomas con detección automática del sistema.

---

## 🚀 Opciones de Distribución (Assets)

1.  **OMDownloader_v1.0.0_Setup.zip (Instalador):** Instalación completa con creación de accesos directos y gestión profesional del sistema.
2.  **OMDownloader_Portable.zip (Versión Portable):** Todo el ecosistema comprimido en un archivo. Ideal para portabilidad inmediata.
3.  **OMDownloader_Folder.zip (Versión Carpeta):** Estructura abierta para máximo rendimiento de carga en entornos fijos.

---

## 🔑 Configuración de Telegram

Para habilitar las descargas de Telegram, configura tus credenciales en la pestaña **Ajustes**:
1. Obtén tu `api_id` y `api_hash` en [my.telegram.org](https://my.telegram.org).
2. Pégalos en la App y selecciona **"Aplicar Cambios"**.
3. Inicia sesión con tu número de teléfono de forma segura.

---

## 👨‍💻 Autor

**Walter Pablo Téllez Ayala**  
Software Developer  
📍 Bolivia 🇧🇴 <img src="https://flagcdn.com/w20/bo.png" width="20"/> <br>
📧 [pharmakoz@gmail.com](mailto:pharmakoz@gmail.com) 

© 2026 — Wordy Professional Tool

---
