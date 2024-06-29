# open_directory.py

import os
import platform
import subprocess

def open_directory(path):
    """
    打开指定路径的目录。
    """
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

