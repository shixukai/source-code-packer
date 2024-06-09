import os
from tkinter import filedialog

def read_config():
    """
    读取默认配置。
    """
    # 模拟读取配置，可以替换为实际的配置读取逻辑
    project_path = "默认路径"
    extensions = [".py", ".md"]
    exclude_dirs = ["test", "build"]
    return project_path, extensions, exclude_dirs

def browse_project_path(root, project_path_entry):
    """
    浏览项目路径。
    """
    current_path = project_path_entry.get().strip()
    initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
    selected_dir = filedialog.askdirectory(initialdir=initial_dir)
    if selected_dir:  # 只有在用户选择了目录时才更新路径
        project_path_entry.delete(0, 'end')
        project_path_entry.insert(0, selected_dir)
    root.update_idletasks()  # 强制刷新界面
