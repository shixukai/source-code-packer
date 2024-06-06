import os
import json
import tarfile
from pathlib import Path

def read_config(script_path):
    """
    读取配置文件以获取要打包的文件后缀列表和排除的子目录。

    :param script_path: 脚本文件的路径
    :return: 文件后缀列表和排除的子目录列表
    """
    config_path = os.path.join(script_path, "config.json")
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        extensions = [ext.lower() for ext in config.get("file_extensions", [])]
        exclude_dirs = config.get("exclude_dirs", [])
        return extensions, exclude_dirs
    except Exception as e:
        print(f"读取配置文件出错: {e}")
        return [], []

def gather_files(project_path, extensions, exclude_dirs):
    """
    收集项目路径中符合给定后缀的所有文件，排除指定的子目录。

    :param project_path: 项目目录的路径
    :param extensions: 要包含的文件后缀列表
    :param exclude_dirs: 要排除的子目录列表
    :return: 要打包的文件路径列表
    """
    exclude_dirs_full = [os.path.join(project_path, exclude_dir) for exclude_dir in exclude_dirs]
    files_to_package = []
    for root, dirs, files in os.walk(project_path):
        # 检查并排除子目录
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs_full]
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                files_to_package.append(os.path.join(root, file))
    return files_to_package

def package_files(project_path, files, output_dir):
    """
    将收集到的文件打包成一个 .tar.gz 压缩包。

    :param project_path: 项目目录的路径
    :param files: 要包含在包中的文件路径列表
    :param output_dir: 保存输出包的目录
    :return: 创建的包的路径
    """
    project_name = os.path.basename(os.path.normpath(project_path))
    output_path = os.path.join(output_dir, f"{project_name}.tar.gz")
    
    with tarfile.open(output_path, "w:gz") as tar:
        for file in files:
            arcname = os.path.relpath(file, start=project_path)
            tar.add(file, arcname=arcname)
    
    return output_path

def print_tree(files, project_path):
    """
    以树形结构打印打包的文件结构。

    :param files: 被打包的文件路径列表
    :param project_path: 项目目录的路径
    """
    tree = {}
    for file in files:
        parts = Path(file).relative_to(project_path).parts
        d = tree
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d.setdefault(parts[-1], None)
    
    def print_dict(d, prefix=''):
        """
        递归打印目录结构。

        :param d: 表示目录结构的字典
        :param prefix: 当前的前缀，用于打印竖线
        """
        pointers = ['├── '] * (len(d) - 1) + ['└── ']
        for pointer, (key, value) in zip(pointers, sorted(d.items())):
            print(prefix + pointer + key)
            if isinstance(value, dict):
                extension = '│   ' if pointer == '├── ' else '    '
                print_dict(value, prefix + extension)

    print_dict(tree)

def main():
    """
    执行打包过程的主函数。
    """
    script_path = os.path.dirname(os.path.abspath(__file__))  # 获取脚本文件的目录
    extensions, config_exclude_dirs = read_config(script_path)
    
    if not extensions:
        print("配置文件中未找到文件后缀列表或配置文件为空。")
        return
    
    project_path = input("输入项目路径: ").strip()
    exclude_dirs = config_exclude_dirs.copy()

    while True:
        exclude_dir = input("输入需要排除的子目录 (相对路径), 完成输入 'done': ").strip()
        if exclude_dir.lower() == 'done':
            break
        exclude_dirs.append(exclude_dir)
    
    exclude_dirs = list(set(exclude_dirs))  # 去重

    files_to_package = gather_files(project_path, extensions, exclude_dirs)
    
    if not files_to_package:
        print("没有文件需要打包。")
        return
    
    output_dir = "/tmp"
    output_path = package_files(project_path, files_to_package, output_dir)
    
    print(f"压缩包创建在: {output_path}")
    print("打包的文件列表:")
    print_tree(files_to_package, project_path)

if __name__ == "__main__":
    main()