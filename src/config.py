import os
import json

DEFAULT_CONFIG_PATH = 'config.json'

def resource_path(relative_path):
    """获取打包后资源文件的路径"""
    base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def read_config():
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        # 生成默认配置
        default_config = {
            "projects": [
                {
                    "project_path": "请输入您的项目路径",
                    "file_extensions": [".py"],
                    "exclude_dirs": ["__pycache__"]
                }
            ]
        }
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, indent=4)
        return default_config["projects"]

    with open(config_path, 'r', encoding='utf-8') as file:
        config = json.load(file)
        return config.get("projects", [])

def save_config(project):
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        existing_config = {"projects": []}
    else:
        with open(config_path, 'r', encoding='utf-8') as file:
            existing_config = json.load(file)
    
    projects = existing_config.get("projects", [])
    
    # 检查是否已有相同路径的配置，若有则更新
    for i, proj in enumerate(projects):
        if proj["project_path"] == project["project_path"]:
            projects[i] = project
            break
    else:
        projects.append(project)
    
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump({"projects": projects}, file, indent=4)

def delete_config(project_path):
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        return

    with open(config_path, 'r', encoding='utf-8') as file:
        existing_config = json.load(file)
    
    projects = existing_config.get("projects", [])
    projects = [proj for proj in projects if proj["project_path"] != project_path]

    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump({"projects": projects}, file, indent=4)
