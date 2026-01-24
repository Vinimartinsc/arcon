# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

c2pa_binaries = collect_dynamic_libs("c2pa")
c2pa_hiddenimports = collect_submodules("c2pa")

a = Analysis(
    ['src/app.py'],
    pathex=[],
    binaries=c2pa_binaries,
    datas=[
        ('src/templates', 'templates'),
        ('src/static', 'static'),
        ('bundle/windows', 'bundle/windows'),
        ('bundle/unix', 'bundle/unix'),
    ],
    hiddenimports=[
        'flask',
        'flask.cli',
        *c2pa_hiddenimports,
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

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
