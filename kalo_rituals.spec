# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Kalo Rituals
# Build with: pyinstaller kalo_rituals.spec
#
# IMPORTANT: Run this from the project root directory where game.py lives.
# Requires Python 3.11 or 3.12 — NOT Python 3.14 (PyInstaller compatibility).
#
# DO NOT edit game.py. All packaging config lives here.

import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# ── Collect every submodule in the locally-vendored OpenGL package ──────────
# PyOpenGL uses lazy loading and string-based plugin registration.
# PyInstaller static analysis misses most of it. collect_submodules catches all.
opengl_hidden = collect_submodules('OpenGL')

# ── Collect data files from the local OpenGL package (non-.py files) ────────
# This captures OpenGL/DLLS/*.dll, *.txt, and any other data files.
opengl_datas = collect_data_files('OpenGL', include_py_files=False)

a = Analysis(
    ['game.py'],

    # pathex ensures PyInstaller finds the local OpenGL/ package in the project root.
    pathex=['.'],

    binaries=[],

    datas=opengl_datas + [
        # Explicitly bundle the freeglut DLLs.
        # ctypesloader.py line 15 computes:
        #   DLL_DIRECTORY = os.path.join(os.path.dirname(OpenGL.__file__), 'DLLS')
        # It then checks os.path.isfile(os.path.join(DLL_DIRECTORY, name + '.dll'))
        # The DLL must land at: <bundle>/OpenGL/DLLS/freeglut64.vc14.dll
        ('OpenGL/DLLS/freeglut64.vc14.dll', 'OpenGL/DLLS'),
        ('OpenGL/DLLS/freeglut32.vc14.dll', 'OpenGL/DLLS'),
        ('OpenGL/DLLS/gle64.vc14.dll',      'OpenGL/DLLS'),
        ('OpenGL/DLLS/gle32.vc14.dll',      'OpenGL/DLLS'),
    ],

    hiddenimports=opengl_hidden + [
        # ── Platform backend ─────────────────────────────────────────────────
        # PyInstaller cannot detect which platform module OpenGL/__init__.py
        # will select at runtime (it checks sys.platform dynamically).
        'OpenGL.platform.win32',
        'OpenGL.platform.ctypesloader',
        'OpenGL.platform.baseplatform',

        # ── Array format handlers ─────────────────────────────────────────────
        # OpenGL.arrays uses a plugin registry (formathandler.py).
        # Each handler registers itself by class name string — static analysis blind.
        'OpenGL.arrays.numpymodule',
        'OpenGL.arrays.numbers',
        'OpenGL.arrays.strings',
        'OpenGL.arrays.lists',
        'OpenGL.arrays.nones',
        'OpenGL.arrays.ctypesarrays',
        'OpenGL.arrays.ctypesparameters',
        'OpenGL.arrays.ctypespointers',

        # ── GLUT sub-modules ──────────────────────────────────────────────────
        # game.py calls glutBitmapCharacter, glutMainLoop etc. These pull in
        # freeglut and special callback machinery.
        'OpenGL.GLUT.freeglut',
        'OpenGL.GLUT.special',
        'OpenGL.GLUT.fonts',

        # ── GL exceptional/extension handling ─────────────────────────────────
        'OpenGL.GL.exceptional',

        # ── Lazy extension loader ─────────────────────────────────────────────
        'OpenGL.extensions',
        'OpenGL.wrapper',
        'OpenGL.converters',
        'OpenGL.contextdata',
    ],

    hookspath=['.'],       # Look for hook-*.py files in project root
    hooksconfig={},
    runtime_hooks=[],

    # Exclude packages definitely not used — speeds up build, shrinks bundle.
    excludes=[
        'numpy',
        'PIL',
        'Pillow',
        'pygame',
        'tkinter',
        '_tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'IPython',
        'jupyter',
        'wx',
        'PyQt5',
        'PySide2',
    ],

    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,   # --onedir mode: binaries live in the COLLECT output dir

    name='KaloRituals',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,

    # UPX disabled: antivirus tools frequently flag UPX-compressed PyInstaller
    # executables as false-positive malware. Avoid for itch.io / GitHub distribution.
    upx=False,

    # console=False removes the black CMD window on launch.
    # CHANGE TO True when debugging to see Python tracebacks.
    console=False,

    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,

    # icon='assets/icon.ico',  # Uncomment and add a 256x256 .ico file for a custom icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='KaloRituals',   # Output folder: dist/KaloRituals/
)
