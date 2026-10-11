"""Tek dosyalık .exe üretir:  python build.py

Çıktı: dist/MasaustuDostlari.exe
"""
import os
import shutil
import sys

import PyInstaller.__main__

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
sys.path.insert(0, HERE)

from dostlar import APP_ID, __version__  # noqa: E402
from dostlar.gfx import make_logo       # noqa: E402

os.makedirs(BUILD, exist_ok=True)
ico = os.path.join(BUILD, "icon.ico")
make_logo(256).save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

PyInstaller.__main__.run([
    os.path.join(HERE, "main.pyw"),
    "--name", APP_ID,
    "--onefile",
    "--windowed",
    "--icon", ico,
    "--hidden-import", "pystray._win32",
    "--distpath", os.path.join(HERE, "dist"),
    "--workpath", os.path.join(BUILD, "work"),
    "--specpath", BUILD,
    "--noconfirm",
    "--clean",
])
shutil.rmtree(BUILD, ignore_errors=True)
print(f"\nHazır: dist/{APP_ID}.exe  (v{__version__})")
