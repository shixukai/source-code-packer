# event_handlers.py

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from di_container import DIContainer
from .exclude_handlers import add_exclude_dir
from .packaging_handling import on_package_button_click
from config import save_config, delete_config, read_config, export_config, import_config, show_current_config

def load_project_config_handler(gui):
    """根据选择的项目加载配置"""
    gui.clear_current_config()  # 清空当前显示的配置
    selected_path = gui.project_path_combo.currentText()
    for project in gui.projects:
        if project["project_path"] == selected_path:
            gui.selected_project = project
            gui.load_project_details()  # 加载新的项目详情
            return  # 找到匹配的项目后立即返回

    # 如果未找到项目配置，则设置为临时状态
    gui.selected_project = {
        "project_path": selected_path,
        "file_extensions": gui.temp_extensions,
        "exclude_dirs": gui.temp_exclude_dirs
    }
    gui.temp_extensions = []
    gui.temp_exclude_dirs = []


def browse_project_path_handler(gui):
    """浏览选择项目路径"""
    current_path = gui.project_path_combo.currentText().strip()
    initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
    selected_dir = QFileDialog.getExistingDirectory(caption="选择项目路径", directory=initial_dir)
    if selected_dir:
        # 更新项目路径组合框并加载新路径的配置
        if selected_dir not in gui.project_paths:
            gui.project_paths.append(selected_dir)
            gui.project_path_combo.addItem(selected_dir)
        
        gui.project_path_combo.setCurrentText(selected_dir)
        
        # 确保 selected_project 被正确初始化
        gui.selected_project = {
            "project_path": selected_dir,
            "file_extensions": gui.temp_extensions,
            "exclude_dirs": gui.temp_exclude_dirs
        }
        
        gui.temp_extensions = []
        gui.temp_exclude_dirs = []
        
        gui.clear_current_config()
        gui.load_project_details()


def add_exclude_dir_handler(gui):
    """添加排除目录"""
    gui_core = DIContainer().resolve("gui_core")
    add_exclude_dir(gui_core, gui.project_path_combo, gui.exclude_dirs_entry)
    if not gui.selected_project:
        gui.temp_exclude_dirs = [d.strip() for d in gui.exclude_dirs_entry.text().split(";") if d.strip()]

def package_code_handler(gui):
    """处理打包按钮的点击事件"""
    gui_core = DIContainer().resolve("gui_core")

    project_path = gui.project_path_combo.currentText().strip()

    if not project_path:
        QMessageBox.critical(gui_core, "错误", "请先选择或配置一个项目路径")
        return
    
    project = {
        "project_path": project_path,
        "file_extensions": gui.temp_extensions,
        "exclude_dirs": [d.strip() for d in gui.exclude_dirs_entry.text().split(";") if d.strip()]
    }

    if gui.selected_project:
        project = gui.selected_project

    if not project["file_extensions"]:
        QMessageBox.critical(gui_core, "错误", "请先添加至少一个文件扩展名")
        return

    on_package_button_click(gui, project, gui.logger)


def save_current_config_handler(gui):
    """保存当前项目配置到config.json"""
    gui_core = DIContainer().resolve("gui_core")
    project_path = gui.project_path_combo.currentText().strip()

    # 检查项目路径是否为空
    if not project_path:
        QMessageBox.critical(gui_core, "错误", "项目路径不能为空")
        return

    if gui.selected_project:
        file_extensions = gui.selected_project["file_extensions"]
    else:
        file_extensions = gui.temp_extensions

    exclude_dirs = [d.strip() for d in gui.exclude_dirs_entry.text().split(";") if d.strip()]

    project = {
        "project_path": project_path,
        "file_extensions": file_extensions,
        "exclude_dirs": exclude_dirs
    }
    save_config(project)
    QMessageBox.information(gui_core, "提示", f"配置已保存到: {project_path}")

    # 更新配置列表
    gui.projects = read_config()
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo.clear()
    gui.project_path_combo.addItems(gui.project_paths)
    gui.project_path_combo.setCurrentText(project_path)  # 重新选择保存的项目
    gui.selected_project = project

def delete_current_config_handler(gui):
    """从config.json中删除当前项目配置"""
    gui_core = DIContainer().resolve("gui_core")
    project_path = gui.project_path_combo.currentText().strip()

    # 检查项目路径是否为空
    if not project_path:
        QMessageBox.critical(gui_core, "错误", "项目路径不能为空")
        return

    delete_config(project_path)
    QMessageBox.information(gui_core, "提示", f"配置已从 {project_path} 中删除")

    # 更新配置
    gui.projects = read_config()
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo.clear()
    gui.project_path_combo.addItems(gui.project_paths)
    if gui.project_paths:
        gui.project_path_combo.setCurrentIndex(0)  # 选择第一个项目路径
        load_project_config_handler(gui)
    else:
        gui.project_path_combo.clear()
        gui.clear_current_config()

def reload_current_config_handler(gui):
    """重新从config.json加载当前项目的配置"""
    gui_core = DIContainer().resolve("gui_core")
    project_path = gui.project_path_combo.currentText().strip()

    if not project_path:
        QMessageBox.critical(gui_core, "错误", "项目路径不能为空")
        return

    # 重新读取最新的配置
    projects = read_config()
    gui.projects = projects
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo.clear()
    gui.project_path_combo.addItems(gui.project_paths)

    # 检查该路径是否在最新的配置中
    for project in projects:
        if project["project_path"] == project_path:
            gui.clear_current_config()
            gui.selected_project = project
            gui.load_project_details()  # 加载新的项目详情
            break
    else:
        gui.selected_project = None
        QMessageBox.critical(gui_core, "错误", "项目路径未在配置中找到，请先保存配置")
        return

    if gui.selected_project:
        # 重新加载配置
        QMessageBox.information(gui_core, "提示", f"已重载配置：{project_path}")
    else:
        QMessageBox.critical(gui_core, "错误", "项目路径未在配置中找到，请先保存配置")

def export_current_config_handler(gui):
    # Open file save dialog to choose the export path
    gui_core = DIContainer().resolve("gui_core")
    export_path = QFileDialog.getSaveFileName(gui_core, "导出配置", "", "JSON files (*.json)")[0]
    if export_path:
        export_config(export_path)
        QMessageBox.information(gui_core, "成功", "配置已导出到: " + export_path)

def import_config_handler(gui):
    gui_core = DIContainer().resolve("gui_core")
    import_path = QFileDialog.getOpenFileName(gui_core, "选择配置文件", "", "JSON files (*.json)")[0]
    
    if not import_path:
        return  # 用户取消了文件选择

    try:
        projects = import_config(import_path)
        gui.projects = projects
        gui.project_paths = [project["project_path"] for project in projects]
        gui.project_path_combo.clear()
        gui.project_path_combo.addItems(gui.project_paths)

        if gui.project_paths:
            gui.project_path_combo.setCurrentIndex(0)  # 默认选择第一个项目路径
            load_project_config_handler(gui)
        else:
            gui.clear_current_config()

        QMessageBox.information(gui_core, "成功", "配置已成功导入")
    except Exception as e:
        QMessageBox.critical(gui_core, "错误", f"导入配置时出错: {e}")

def show_current_config_handler(gui):
    show_current_config(gui.logger)
