# event_handlers.py

import os
from tkinter import messagebox, filedialog
from .extension_handling import add_extension, initialize_extensions
from .exclude_handling import add_exclude_dir as add_exclude_dir_to_gui
from .packaging_handling import on_package_button_click
from config import save_config, delete_config, read_config

def load_project_config(gui):
    """根据选择的项目加载配置"""
    gui.clear_current_config()  # 清空当前显示的配置
    selected_path = gui.project_path_combo.get()
    for project in gui.projects:
        if project["project_path"] == selected_path:
            gui.selected_project = project
            gui.load_project_details()  # 加载新的项目详情
            return  # 找到匹配的项目后立即返回

    # 如果未找到项目配置，则设置为临时状态
    gui.selected_project = None
    gui.temp_extensions = []
    gui.temp_exclude_dirs = []

def browse_project_path(gui):
    """浏览选择项目路径"""
    current_path = gui.project_path_combo.get().strip()
    initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
    selected_dir = filedialog.askdirectory(initialdir=initial_dir)
    if selected_dir:
        gui.project_path_combo.set(selected_dir)
        # 清空显示的当前配置
        gui.clear_current_config()
        # 检查该路径是否在现有配置中
        gui.selected_project = None
        for project in gui.projects:
            if project["project_path"] == selected_dir:
                gui.selected_project = project
                gui.load_project_details()
                break
        if gui.selected_project is None:
            gui.temp_extensions = []
            gui.temp_exclude_dirs = []
    gui.root.update_idletasks()

def add_exclude_dir(gui):
    """添加排除目录"""
    add_exclude_dir_to_gui(gui.root, gui.project_path_combo, gui.exclude_dirs_entry)
    if not gui.selected_project:
        gui.temp_exclude_dirs = [d.strip() for d in gui.exclude_dirs_entry.get().split(";") if d.strip()]

def add_extension(gui, extension):
    """添加文件扩展名"""
    if gui.selected_project:
        add_extension(gui.root, gui.tags_frame, extension, gui.selected_project["file_extensions"], gui.tags_canvas, gui.tags_scroll, gui.extensions_var)
    else:
        add_extension(gui.root, gui.tags_frame, extension, gui.temp_extensions, gui.tags_canvas, gui.tags_scroll, gui.extensions_var)

def package_code(gui):
    """处理打包按钮的点击事件"""
    project_path = gui.project_path_combo.get().strip()
    if not project_path:
        messagebox.showerror("错误", "请先选择或配置一个项目路径")
        return

    if gui.selected_project:
        on_package_button_click(gui.root, gui.project_path_combo, gui.selected_project, gui.exclude_dirs_entry, gui.logger)
    else:
        # 临时打包当前未保存的项目配置
        temp_project = {
            "project_path": project_path,
            "file_extensions": gui.temp_extensions,
            "exclude_dirs": gui.temp_exclude_dirs
        }
        on_package_button_click(gui.root, gui.project_path_combo, temp_project, gui.exclude_dirs_entry, gui.logger)

def save_current_config(gui):
    """保存当前项目配置到config.json"""
    project_path = gui.project_path_combo.get().strip()

    # 检查项目路径是否为空
    if not project_path:
        messagebox.showerror("错误", "项目路径不能为空")
        return

    file_extensions = gui.selected_project["file_extensions"] if gui.selected_project else gui.temp_extensions
    exclude_dirs = [d.strip() for d in gui.exclude_dirs_entry.get().split(";") if d.strip()]

    project = {
        "project_path": project_path,
        "file_extensions": file_extensions,
        "exclude_dirs": exclude_dirs
    }
    save_config(project)
    messagebox.showinfo("提示", f"配置已保存到: {project_path}")

    # 更新配置列表
    gui.projects = read_config()
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo['values'] = gui.project_paths
    gui.project_path_combo.set(project_path)  # 重新选择保存的项目
    gui.selected_project = project

def delete_current_config(gui):
    """从config.json中删除当前项目配置"""
    project_path = gui.project_path_combo.get().strip()

    # 检查项目路径是否为空
    if not project_path:
        messagebox.showerror("错误", "项目路径不能为空")
        return

    delete_config(project_path)
    messagebox.showinfo("提示", f"配置已从 {project_path} 中删除")

    # 更新配置
    gui.projects = read_config()
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo['values'] = gui.project_paths
    if gui.project_paths:
        gui.project_path_combo.current(0)  # 选择第一个项目路径
        gui.load_project_config()
    else:
        gui.project_path_combo.set('')
        gui.clear_current_config()

def reload_current_config(gui):
    """重新从config.json加载当前项目的配置"""
    project_path = gui.project_path_combo.get().strip()

    if not project_path:
        messagebox.showerror("错误", "项目路径不能为空")
        return

    # 重新读取最新的配置
    projects = read_config()
    gui.projects = projects
    gui.project_paths = [project["project_path"] for project in gui.projects]
    gui.project_path_combo['values'] = gui.project_paths

    # 检查该路径是否在最新的配置中
    for project in projects:
        if project["project_path"] == project_path:
            gui.clear_current_config()
            gui.selected_project = project
            gui.load_project_details()  # 加载新的项目详情
            break
    else:
        gui.selected_project = None
        messagebox.showerror("错误", "项目路径未在配置中找到，请先保存配置")
        return


    if gui.selected_project:
        # 重新加载配置
        messagebox.showinfo("提示", f"已重载配置：{project_path}")
    else:
        messagebox.showerror("错误", "项目路径未在配置中找到，请先保存配置")
