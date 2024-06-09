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
    root.geometry("800x700")  # 增加初始高度以容纳更多内容

    # 应用自定义样式
    apply_styles()

    # 读取所有项目配置
    projects = read_config()
    project_paths = [project["project_path"] for project in projects]

    # 默认选择第一个项目
    selected_project = projects[0] if projects else None

    # 项目选择
    tk.Label(root, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")

    project_path_combo = ttk.Combobox(root, values=project_paths, width=47)
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

    tk.Button(root, text="浏览", command=browse_project_path).grid(row=0, column=2, padx=10, pady=5)

    # 排除目录
    tk.Label(root, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    exclude_dirs_entry = tk.Entry(root, width=50)
    exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
    tk.Button(root, text="添加", command=lambda: add_exclude_dir(root, project_path_combo, exclude_dirs_entry)).grid(row=1, column=2, padx=10, pady=5)

    # 文件扩展名
    tk.Label(root, text="要打包的文件扩展名:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    extensions_frame = tk.Frame(root)
    extensions_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="we")

    # 标签输入框
    extensions_var = tk.StringVar()
    extensions_entry = tk.Entry(root, width=20, textvariable=extensions_var)
    extensions_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")
    tk.Button(root, text="添加扩展名", command=lambda: add_extension(root, tags_frame, extensions_entry.get(), selected_project["file_extensions"], tags_canvas, tags_scroll, extensions_var)).grid(row=3, column=2, padx=10, pady=5)

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

    # 日志显示区域
    log_display_frame = tk.Frame(root)
    log_display_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

    log_display = scrolledtext.ScrolledText(log_display_frame, wrap=tk.WORD)
    log_display.pack(fill="both", expand=True)

    logger = ConsoleLogger(log_display)

    # “清除日志”按钮放在“打包”按钮的上方，占一行
    tk.Button(root, text="清除日志", command=lambda: logger.clear()).grid(row=5, column=0, padx=10, pady=5, sticky="w")

    # 打包按钮放在左下角
    tk.Button(root, text="打包", command=lambda: on_package_button_click(root, project_path_combo, selected_project, exclude_dirs_entry, logger)).grid(row=6, column=0, padx=10, pady=20, sticky="w")

    # 退出按钮放在右下角
    tk.Button(root, text="退出程序", command=root.quit).grid(row=6, column=2, padx=10, pady=20, sticky="e")

    # 使输入框和日志框在窗口调整大小时扩展
    root.columnconfigure(1, weight=1)  # 使中间列（输入框列）可以调整宽度
    root.rowconfigure(4, weight=1)  # 使日志输出框可以调整高度

    log_display_frame.columnconfigure(0, weight=1)  # 使日志输出框可以调整宽度
    log_display_frame.rowconfigure(1, weight=1)  # 使日志输出框可以调整高度

    # 将窗口居中显示
    center_window(root)

    # 在程序启动时加载默认项目配置
    load_project_config()

    root.mainloop()
