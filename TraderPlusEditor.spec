# -*- mode: python ; coding: utf-8 -*-
import os

# Получаем путь к папке со скриптом
script_dir = os.path.dirname(os.path.abspath('trader_editor.py'))
icon_path = os.path.join(script_dir, 'icon.ico')

a = Analysis(
    ['trader_editor.py'],
    pathex=[],
    binaries=[],
    datas=[(icon_path, '.')] if os.path.exists(icon_path) else [],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TraderPlusEditor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
