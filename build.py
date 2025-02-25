# ---
# KazLabs Media Group
# Made with ♥ by Liam Sorensen - AI Assisted by Cursor.AI.
# Version 0.1.0 - 2024-03-19
# ---

import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'app.py',
    '--onefile',
    '--windowed',
    '--name=KazLabs-AutoClicker',
    '--icon=icon.ico',
    '--version-file=version_info.txt',
    '--add-data=config.json;.',
    '--add-data=icon.ico;.',
    '--clean',
    '--uac-admin'
]) 