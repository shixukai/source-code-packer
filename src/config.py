import os
import sys
import json

DEFAULT_CONFIG_PATH = 'config.json'

def resource_path(relative_path):
    """获取打包后资源文件的路径"""
    try:
        # PyInstaller 创建临时文件夹时
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./src")
    return os.path.join(base_path, relative_path)

def read_config(config_path=None):
    """
    读取配置文件，返回项目列表。
    """
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        projects = config.get("projects", [])

    return projects
