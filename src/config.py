import os
import json

DEFAULT_CONFIG_PATH = 'config.json'

def resource_path(relative_path):
    """获取打包后资源文件的路径"""
    base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def get_default_config():
    default_config = {
        "projects": [
            {
                "project_path": "change_project_path_here",
                "file_extensions": [".py"],
                "exclude_dirs": ["__pycache__"]
            }
        ]
    }
    return default_config

def read_config():
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        # 生成默认配置
        default_config = get_default_config()
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

def export_config(export_path):
    # Load current configuration
    config_path = resource_path(DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        config_data = get_default_config()
    else:
        with open(config_path, 'r') as config_file:
            config_data = config_file.read()

    # Write to the specified export path
    with open(export_path, 'w') as export_file:
        export_file.write(config_data)
