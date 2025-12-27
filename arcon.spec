# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for ARCON
Builds a standalone .exe for Windows with all dependencies bundled
"""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['arcon.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/templates', 'src/templates'),
        ('src/static', 'src/static'),
    ],
    hiddenimports=['flask', 'werkzeug'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='arcon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
