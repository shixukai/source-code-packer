# packager.py

import os
import tarfile
from pathlib import Path
import tempfile

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
            # 只收集指定扩展名的文件
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
    :return: 打包文件的树形结构字符串
    """
    tree = {}
    for file in files:
        parts = Path(file).relative_to(project_path).parts
        d = tree
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d.setdefault(parts[-1], None)
    
    output = []
    def print_dict(d, prefix=''):
        """
        递归打印目录结构。

        :param d: 表示目录结构的字典
        :param prefix: 当前的前缀，用于打印竖线
        """
        pointers = ['├── '] * (len(d) - 1) + ['└── ']
        for pointer, (key, value) in zip(pointers, sorted(d.items())):
            output.append(prefix + pointer + key)
            if isinstance(value, dict):
                extension = '│   ' if pointer == '├── ' else '    '
                print_dict(value, prefix + extension)

    print_dict(tree)
    return '\n'.join(output)

def run_packaging(project_path, extensions, exclude_dirs, result_queue):
    """
    执行打包过程，并将结果放入队列。

    :param project_path: 项目路径
    :param extensions: 要打包的文件扩展名列表
    :param exclude_dirs: 要排除的目录列表
    :param result_queue: 用于传递打包结果的队列
    """
    try:
        files_to_package = gather_files(project_path, extensions, exclude_dirs)
        
        if not files_to_package:
            result_queue.put(("没有文件需要打包。", None))
            return
        
        output_dir = tempfile.gettempdir()  # 获取临时目录
        output_path = package_files(project_path, files_to_package, output_dir)
        
        file_tree = print_tree(files_to_package, project_path)
        result_message = f"压缩包创建在: {output_path}\n打包的文件列表:\n{file_tree}"
        
        result_queue.put((result_message, output_path))
    except Exception as e:
        result_queue.put((f"打包过程中出现错误: {e}", None))
