import os
import sys
import json

DEFAULT_CONFIG_PATH = 'config.json'

def resource_path(relative_path):
    """获取打包后资源文件的路径"""
    try:
        # PyInstaller 创建临时文件夹时
        base_path = sys._MEIPASS
        print(f"base_path _MEIPASS: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        print(f"base_path: {base_path}")

    return os.path.join(base_path, relative_path)

def read_config(config_path=None):
    config_path = resource_path(DEFAULT_CONFIG_PATH)

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        project_path = config.get("project_path", "").strip()
        extensions = [ext.lower() for ext in config.get("file_extensions", [])]
        exclude_dirs = config.get("exclude_dirs", [])

    return project_path, extensions, exclude_dirs
