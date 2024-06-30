# open_directory.py

import os, sys
import subprocess

def open_directory(project_path, logger):
    if project_path and os.path.exists(project_path):
        if os.name == 'nt':  # Windows
            os.startfile(project_path)
        elif os.name == 'posix':  # macOS, Linux
            subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', project_path])
    else:
        logger.write(f"项目路径不存在: {project_path}")
