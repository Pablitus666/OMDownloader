# -*- mode: python ; coding: utf-8 -*-
# OMDownloader - Configuración de Compilación Profesional (Versión Élite)

import sys
import os
import tkinterdnd2

# --- CONFIGURACIÓN DE RUTAS ---
PROJECT_DIR = os.path.abspath(os.getcwd())
ASSETS_DIR = os.path.join(PROJECT_DIR, 'assets')

# Usar el icono multi-capa para máxima nitidez
ICON_PATH = os.path.join(ASSETS_DIR, 'images', 'icomulti.ico')

# Localizar la ruta de tkinterdnd2 dinámicamente
tkdnd_path = os.path.dirname(tkinterdnd2.__file__)

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        (tkdnd_path, 'tkinterdnd2'), # Incluir binarios de DnD
    ],
    hiddenimports=[
        'tkinterdnd2',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'yt_dlp',
        'telethon',
        'telethon.sync',
        'telethon.network',
        'telethon.crypto',
        'cryptg',  # Aceleración de Telegram
        'hachoir', # Metadatos de Telegram
        'asyncio',
        'requests',
        'urllib3',
        'lxml',
        'sqlite3',
        'json'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'PySide2', 
        'torch', 'tensorflow', 'notebook', 'share'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# 1. EJECUTABLE PORTABLE (ONEFILE) - El favorito de los usuarios
exe_portable = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OMDownloader_Portable',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # UPX desactivado para evitar falsos positivos de antivirus
    runtime_tmpdir=None,
    console=False, # Sin consola negra
    disable_windowed_traceback=False,
    icon=ICON_PATH,
)

# 2. EJECUTABLE EN CARPETA (ONEDIR) - Más rápido en el arranque
exe_folder = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OMDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon=ICON_PATH,
)

coll = COLLECT(
    exe_folder,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='OMDownloader_Folder',
)
