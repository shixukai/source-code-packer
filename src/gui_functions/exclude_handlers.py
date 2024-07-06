# exclude_handling.py
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from di_container import DIContainer

def add_exclude_dir(gui, project_path_entry, exclude_dirs_entry):
    """
    添加排除的子目录。
    """
    gui_core = DIContainer().resolve("gui_core")
    project_path = project_path_entry.currentText().strip()
    if not project_path:
        QMessageBox.critical(gui_core, "错误", "请先选择项目路径")
        return

    selected_dir = QFileDialog.getExistingDirectory(gui, "选择排除的子目录", project_path)
    if selected_dir:
        relative_dir = os.path.relpath(selected_dir, project_path)
        current_excludes = exclude_dirs_entry.text().strip()
        exclude_dirs_entry.setText(f"{current_excludes};{relative_dir}".strip(";"))
        gui.update()  # 强制刷新界面
