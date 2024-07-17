import os
import platform

def open_and_select_file(file_path):
    """
    打开文件所在的目录并选中该文件
    """
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":
        os.system(f"open -R '{file_path}'")
    else:
        os.system(f"xdg-open '{os.path.dirname(file_path)}'")

def get_file_content(file_path, include_filename):
    """复制文件内容到剪贴板"""
    with open(file_path, 'r') as file:
        content = file.read()

        if include_filename:
            filename = f"# {os.path.basename(file_path)}"
            content = f"{filename}\n{content}"
        
        return content
