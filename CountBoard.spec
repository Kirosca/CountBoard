# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [
    ('favicon.ico', '.'),
    ('del.ico', '.'),
    ('edit.ico', '.'),
    ('exit.ico', '.'),
    ('github.ico', '.'),
    ('help.ico', '.'),
    ('home.ico', '.'),
    ('recovery.ico', '.'),
    ('update.ico', '.'),
    ('introduction.md', '.')
]
datas += copy_metadata('apscheduler')

block_cipher = None

a = Analysis(
    ['CountBoard.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'sqlitedict',
        'apscheduler',
        'pywin10',
        'ttkbootstrap',
        'markdown2',
        'tkhtmlview'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'pydoc', 'pdb'],
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
    name='CountBoard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico',
)
