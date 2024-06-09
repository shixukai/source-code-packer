import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from config import read_config, save_config, delete_config
from packager import run_packaging
from logger import ConsoleLogger
from .center_window import center_window
from .open_directory import open_directory
from .validate_exclude_dir import validate_exclude_dir, InvalidSubdirectoryException
from .exclude_handling import add_exclude_dir
from .extension_handling import add_extension, remove_extension, update_canvas, initialize_extensions
from .packaging_handling import on_package_button_click
from .styles import apply_styles

def create_gui():
    """
    创建和运行图形用户界面。
    """
    root = tk.Tk()
    root.title("源码打包工具")
    root.geometry("1000x700")  # 初始大小适当调整

    # 应用自定义样式
    apply_styles()

    # 读取所有项目配置
    projects = read_config()
    project_paths = [project["project_path"] for project in projects]

    # 默认选择第一个项目
    selected_project = projects[0] if projects else None

    # 创建带边框的Frame用于包含项目配置的各个控件
    bordered_frame = tk.Frame(root, relief='solid', borderwidth=2, padx=10, pady=10)
    bordered_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    # 项目选择
    tk.Label(bordered_frame, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")

    project_path_combo = ttk.Combobox(bordered_frame, values=project_paths, width=60)
    project_path_combo.grid(row=0, column=1, padx=10, pady=5, sticky="we")
    project_path_combo.current(0)  # 默认选择第一个项目路径

    def load_project_config(event=None):
        """根据选择的项目加载配置"""
        selected_path = project_path_combo.get()
        for project in projects:
            if project["project_path"] == selected_path:
                # 清空现有的扩展名标签
                for widget in tags_frame.winfo_children():
                    widget.destroy()
                
                # 清空并重新设置排除目录
                exclude_dirs_entry.delete(0, tk.END)
                exclude_dirs_entry.insert(0, ";".join(project["exclude_dirs"]))
                
                # 清空并重新设置扩展名输入框
                extensions_var.set("")
                
                # 重新设置扩展名
                initialize_extensions(root, tags_frame, project["file_extensions"], tags_canvas, tags_scroll, extensions_var)
                
                # 更新 selected_project
                nonlocal selected_project  # 使用 nonlocal 更新外部作用域中的变量
                selected_project = project
                break

    project_path_combo.bind("<<ComboboxSelected>>", load_project_config)

    # 浏览按钮
    def browse_project_path():
        current_path = project_path_combo.get().strip()
        initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(initialdir=initial_dir)
        if selected_dir:
            project_path_combo.set(selected_dir)
        root.update_idletasks()

    tk.Button(bordered_frame, text="浏览", command=browse_project_path).grid(row=0, column=2, padx=10, pady=5, sticky="e")

    # 排除目录
    tk.Label(bordered_frame, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    exclude_dirs_entry = tk.Entry(bordered_frame, width=60)
    exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
    tk.Button(bordered_frame, text="添加", command=lambda: add_exclude_dir(root, project_path_combo, exclude_dirs_entry)).grid(row=1, column=2, padx=10, pady=5, sticky="e")

    # 文件扩展名
    tk.Label(bordered_frame, text="要打包的文件扩展名:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    extensions_frame = tk.Frame(bordered_frame)
    extensions_frame.grid(row=2, column=1, columnspan=1, padx=10, pady=5, sticky="we")

    # 标签输入框
    extensions_var = tk.StringVar()
    extensions_entry = tk.Entry(bordered_frame, width=40, textvariable=extensions_var)
    extensions_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")
    tk.Button(bordered_frame, text="添加扩展名", command=lambda: add_extension(root, tags_frame, extensions_entry.get(), selected_project["file_extensions"], tags_canvas, tags_scroll, extensions_var)).grid(row=3, column=2, padx=10, pady=5, sticky="e")

    # 用于展示扩展名标签的Canvas和滚动条
    tags_canvas = tk.Canvas(extensions_frame, height=50, bg="#f0f8ff")
    tags_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

    tags_frame = tk.Frame(tags_canvas, bg="#f0f8ff")
    tags_canvas.create_window((0, 0), window=tags_frame, anchor='nw')

    tags_scroll = tk.Scrollbar(extensions_frame, orient=tk.HORIZONTAL, command=tags_canvas.xview)
    tags_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    tags_canvas.configure(xscrollcommand=tags_scroll.set)

    # 初始化扩展名标签
    if selected_project:
        initialize_extensions(root, tags_frame, selected_project["file_extensions"], tags_canvas, tags_scroll, extensions_var)
        exclude_dirs_entry.insert(0, ";".join(selected_project["exclude_dirs"]))  # 初始时加载排除目录

    # 添加保存和删除配置按钮
    config_buttons_frame = tk.Frame(bordered_frame)
    config_buttons_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="we")

    tk.Button(config_buttons_frame, text="保存配置", command=lambda: save_current_config()).pack(side=tk.LEFT, padx=5)
    tk.Button(config_buttons_frame, text="删除配置", command=lambda: delete_current_config()).pack(side=tk.LEFT, padx=5)

    # 日志显示区域
    log_display_frame = tk.Frame(root)
    log_display_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

    log_display = scrolledtext.ScrolledText(log_display_frame, wrap=tk.WORD)
    log_display.pack(fill="both", expand=True)

    logger = ConsoleLogger(log_display)

    # “清除日志”按钮放在“打包”按钮的上方，占一行
    tk.Button(root, text="清除日志", command=lambda: logger.clear()).grid(row=6, column=0, padx=10, pady=5, sticky="w")

    # 打包按钮放在左下角
    tk.Button(root, text="打包", command=lambda: on_package_button_click(root, project_path_combo, selected_project, exclude_dirs_entry, logger)).grid(row=7, column=0, padx=10, pady=20, sticky="w")

    # 退出按钮放在右下角
    tk.Button(root, text="退出程序", command=root.quit).grid(row=7, column=2, padx=10, pady=20, sticky="e")

    def save_current_config():
        """保存当前项目配置到config.json"""
        project_path = project_path_combo.get().strip()
        
        # 检查项目路径是否为空
        if not project_path:
            messagebox.showerror("错误", "项目路径不能为空")
            return

        file_extensions = selected_project["file_extensions"]
        exclude_dirs = [d.strip() for d in exclude_dirs_entry.get().split(";") if d.strip()]

        project = {
            "project_path": project_path,
            "file_extensions": file_extensions,
            "exclude_dirs": exclude_dirs
        }
        save_config(project)
        messagebox.showinfo("提示", f"配置已保存到: {project_path}")

        # 更新配置列表
        nonlocal projects, project_paths
        projects = read_config()
        project_paths = [project["project_path"] for project in projects]
        project_path_combo['values'] = project_paths
        project_path_combo.set(project_path)  # 重新选择保存的项目

    def delete_current_config():
        """从config.json中删除当前项目配置"""
        project_path = project_path_combo.get().strip()
        
        # 检查项目路径是否为空
        if not project_path:
            messagebox.showerror("错误", "项目路径不能为空")
            return

        delete_config(project_path)
        messagebox.showinfo("提示", f"配置已从 {project_path} 中删除")

        # 更新配置
        nonlocal projects, project_paths
        projects = read_config()
        project_paths = [project["project_path"] for project in projects]
        project_path_combo['values'] = project_paths
        if project_paths:
            project_path_combo.current(0)  # 选择第一个项目路径
            load_project_config()
        else:
            project_path_combo.set('')
            exclude_dirs_entry.delete(0, tk.END)
            for widget in tags_frame.winfo_children():
                widget.destroy()

    # 设置自适应布局
    root.columnconfigure(0, weight=1)  # 设置窗口主列的自适应
    root.columnconfigure(1, weight=1)  # 设置窗口主列的自适应
    root.columnconfigure(2, weight=1)  # 设置窗口主列的自适应

    root.rowconfigure(0, weight=1)  # 设置窗口首行的自适应
    root.rowconfigure(5, weight=3)  # 日志显示区域的自适应高度权重
    root.rowconfigure(6, weight=0)  # 按钮行的自适应高度权重
    root.rowconfigure(7, weight=0)  # 按钮行的自适应高度权重

    bordered_frame.columnconfigure(0, weight=0)  # 靠左列
    bordered_frame.columnconfigure(1, weight=1)  # 中间列
    bordered_frame.columnconfigure(2, weight=0)  # 靠右列

    log_display_frame.columnconfigure(0, weight=1)  # 日志显示区域的自适应宽度权重
    log_display_frame.rowconfigure(0, weight=1)  # 日志显示区域的自适应高度权重

    # 将窗口居中显示
    center_window(root)

    # 在程序启动时加载默认项目配置
    load_project_config()

    root.mainloop()
