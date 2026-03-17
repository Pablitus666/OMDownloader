# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# -------------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------------

BLOCK_CIPHER = None

PROJECT_DIR = os.path.abspath(os.getcwd())

ASSETS_DIR = os.path.join(PROJECT_DIR, 'assets')
ICON_PATH = os.path.join(ASSETS_DIR, 'images', 'icon.ico')

# -------------------------------
# ANÁLISIS DE DEPENDENCIAS
# -------------------------------

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
    binaries=[],

    datas=[
        ('assets', 'assets'),
        ('core', 'core'),
        ('gui', 'gui'),
        ('utils', 'utils'),
        ('config', 'config'),
        ('locales', 'locales'),
        ('tkinterdnd2', 'tkinterdnd2'),
    ],

    hiddenimports=[

        # Tkinter DnD
        'tkinterdnd2',

        # PIL
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',

        # yt-dlp
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',

        # Telegram
        'telethon',
        'telethon.sync',
        'telethon.network',
        'telethon.crypto',

        # Async
        'asyncio',

        # Networking
        'requests',
        'urllib3',

        # XML parsing usado por yt-dlp
        'lxml',

    ],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PySide2',
        'torch',
        'tensorflow'
    ],

    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=BLOCK_CIPHER,
    noarchive=False,
)

# -------------------------------
# ARCHIVO PYZ
# -------------------------------

pyz = PYZ(a.pure, a.zipped_data, cipher=BLOCK_CIPHER)

# -------------------------------
# EJECUTABLE PORTABLE (ONEFILE)
# -------------------------------

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
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    icon=ICON_PATH,
)

# -------------------------------
# EJECUTABLE EN CARPETA (ONEDIR)
# -------------------------------

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

# -------------------------------
# BUILD DE CARPETA FINAL
# -------------------------------

coll = COLLECT(
    exe_folder,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='OMDownloader_Folder',
)