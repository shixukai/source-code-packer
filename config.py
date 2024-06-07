import json
from tkinter import messagebox

DEFAULT_CONFIG_PATH = "config.json"

def read_config(config_path=DEFAULT_CONFIG_PATH):
    """
    读取配置文件以获取要打包的文件后缀列表、项目路径和排除的子目录。

    :param config_path: 配置文件的路径
    :return: 文件后缀列表、项目路径和排除的子目录列表
    """
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        project_path = config.get("project_path", "").strip()
        extensions = [ext.lower() for ext in config.get("file_extensions", [])]
        exclude_dirs = config.get("exclude_dirs", [])
        return project_path, extensions, exclude_dirs
    except Exception as e:
        messagebox.showerror("配置文件读取错误", f"读取配置文件出错: {e}")
        return "", [], []
