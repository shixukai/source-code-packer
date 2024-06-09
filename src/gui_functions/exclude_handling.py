import os
from tkinter import filedialog, messagebox

def add_exclude_dir(root, project_path_entry, exclude_dirs_entry):
    """
    添加排除的子目录。
    """
    project_path = project_path_entry.get().strip()
    if not project_path:
        messagebox.showerror("错误", "请先选择项目路径")
        return

    selected_dir = filedialog.askdirectory(initialdir=project_path)
    if selected_dir:
        relative_dir = os.path.relpath(selected_dir, project_path)
        current_excludes = exclude_dirs_entry.get().strip()
        exclude_dirs_entry.delete(0, 'end')
        exclude_dirs_entry.insert(0, f"{current_excludes};{relative_dir}".strip(";"))
        root.update_idletasks()  # 强制刷新界面
