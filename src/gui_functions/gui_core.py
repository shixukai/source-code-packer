# gui_core.py

import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from config import read_config
from logger import ConsoleLogger
from .extension_handling import initialize_extensions, add_extension
from .layout_initializers import apply_styles, center_window, set_responsive_layout
from .event_handlers import (
    save_current_config_handler,
    load_project_config_handler,
    browse_project_path_handler,
    add_exclude_dir_handler,
    package_code_handler,
    delete_current_config_handler,
    reload_current_config_handler,
    export_current_config_handler,
    import_config_handler,
    show_current_config_handler
)

class SourceCodePackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("源码打包工具")

        default_width = 900
        default_height = 700
        root.geometry(f"{default_width}x{default_height}")

    # 设置最小尺寸
        root.minsize(default_width, default_height)

        # 初始化样式
        apply_styles()

        # 读取配置
        self.projects = read_config()
        self.project_paths = [project["project_path"] for project in self.projects]

        # 默认选择第一个项目
        self.selected_project = self.projects[0] if self.projects else None

        # 临时存储新的项目路径的信息（扩展名和排除目录）
        self.temp_extensions = []
        self.temp_exclude_dirs = []

        # 创建GUI
        self.create_widgets()

    def create_widgets(self):
        # 创建带边框的Frame用于包含项目配置的各个控件
        self.bordered_frame = tk.Frame(self.root, relief='solid', borderwidth=2, padx=10, pady=10)
        self.bordered_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 项目选择
        tk.Label(self.bordered_frame, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        
        self.project_path_combo = ttk.Combobox(self.bordered_frame, values=self.project_paths, width=60)
        self.project_path_combo.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        if self.project_paths:
            self.project_path_combo.current(0)  # 默认选择第一个项目路径

        self.project_path_combo.bind("<<ComboboxSelected>>", self.load_project_config)

        tk.Button(self.bordered_frame, text="浏览", command=self.browse_project_path).grid(row=0, column=2, padx=10, pady=5, sticky="e")

        # 排除目录
        tk.Label(self.bordered_frame, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.exclude_dirs_entry = tk.Entry(self.bordered_frame, width=60)
        self.exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        tk.Button(self.bordered_frame, text="添加", command=self.add_exclude_dir).grid(row=1, column=2, padx=10, pady=5, sticky="e")

        # 文件扩展名
        tk.Label(self.bordered_frame, text="要打包的文件扩展名:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        extensions_frame = tk.Frame(self.bordered_frame)
        extensions_frame.grid(row=2, column=1, columnspan=1, padx=10, pady=5, sticky="we")

        self.extensions_var = tk.StringVar()
        extensions_entry = tk.Entry(self.bordered_frame, width=40, textvariable=self.extensions_var)
        extensions_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")
        tk.Button(self.bordered_frame, text="添加扩展名", command=lambda: self.add_extension(extensions_entry.get())).grid(row=3, column=2, padx=10, pady=5, sticky="e")

        # 用于展示扩展名标签的Canvas和滚动条
        self.tags_canvas = tk.Canvas(extensions_frame, height=50, bg="#f0f8ff")
        self.tags_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        self.tags_frame = tk.Frame(self.tags_canvas, bg="#f0f8ff")
        self.tags_canvas.create_window((0, 0), window=self.tags_frame, anchor='nw')

        self.tags_scroll = tk.Scrollbar(extensions_frame, orient=tk.HORIZONTAL, command=self.tags_canvas.xview)
        self.tags_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.tags_canvas.configure(xscrollcommand=self.tags_scroll.set)

        # 初始化扩展名标签
        if self.selected_project:
            self.load_project_details()

        # 添加保存、重载、删除配置和打包按钮
        config_buttons_frame = tk.Frame(self.bordered_frame)
        config_buttons_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        extra_buttons_frame = tk.Frame(self.bordered_frame)
        extra_buttons_frame.grid(row=5, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        tk.Button(config_buttons_frame, text="保存配置", command=self.save_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(config_buttons_frame, text="重载配置", command=self.reload_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(config_buttons_frame, text="删除配置", fg='red', command=self.delete_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(config_buttons_frame, text="打包源码", default='active', command=self.package_code).pack(side=tk.RIGHT, padx=5)

        tk.Button(extra_buttons_frame, text="导出配置", fg='blue', command=self.export_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(extra_buttons_frame, text="导入配置", fg='blue', command=self.import_config).pack(side=tk.LEFT, padx=5)
        tk.Button(extra_buttons_frame, text="查看配置", fg='green', command=self.show_current_config).pack(side=tk.LEFT, padx=5)

        # 日志显示区域
        self.log_display_frame = tk.Frame(self.root)
        self.log_display_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        log_display = scrolledtext.ScrolledText(self.log_display_frame, wrap=tk.WORD)
        log_display.pack(fill="both", expand=True)

        self.logger = ConsoleLogger(log_display)

        # 清除日志和退出程序按钮
        self.bottom_buttons_frame = tk.Frame(self.root)
        self.bottom_buttons_frame.grid(row=7, column=0, columnspan=3, pady=10, sticky="we")

        tk.Button(self.bottom_buttons_frame, text="清除日志", command=self.logger.clear).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(self.bottom_buttons_frame, text="退出程序", fg='red', command=self.root.quit).pack(side=tk.RIGHT, padx=10, pady=5)

        # 设置自适应布局
        set_responsive_layout(self.root, self.bordered_frame, self.log_display_frame, self.bottom_buttons_frame, self.tags_frame, self.tags_canvas, self.tags_scroll)

        # 将窗口居中显示
        center_window(self.root)

    def load_project_config(self, event=None):
        load_project_config_handler(self)

    def browse_project_path(self):
        browse_project_path_handler(self)

    def add_exclude_dir(self):
        add_exclude_dir_handler(self)

    def add_extension(self, extension):
        """处理添加文件扩展名的逻辑"""
        # 检查并添加扩展名到临时或选定项目的扩展名列表
        if self.selected_project:
            add_extension(self.root, self.tags_frame, extension, self.selected_project["file_extensions"], self.tags_canvas, self.tags_scroll, self.extensions_var)
        else:
            add_extension(self.root, self.tags_frame, extension, self.temp_extensions, self.tags_canvas, self.tags_scroll, self.extensions_var)

    def package_code(self):
        package_code_handler(self)

    def save_current_config(self):
        save_current_config_handler(self)

    def delete_current_config(self):
        delete_current_config_handler(self)

    def reload_current_config(self):
        reload_current_config_handler(self)

    def export_current_config(self):
        export_current_config_handler(self)
    
    def import_config(self):
        import_config_handler(self)
    
    def show_current_config(self):
        show_current_config_handler(self)

    def load_project_details(self):
        """加载当前项目的详细信息"""
        if self.selected_project:
            initialize_extensions(self.root, self.tags_frame, self.selected_project["file_extensions"], self.tags_canvas, self.tags_scroll, self.extensions_var)
            self.exclude_dirs_entry.delete(0, tk.END)
            self.exclude_dirs_entry.insert(0, ";".join(self.selected_project["exclude_dirs"]))
        else:
            self.clear_current_config()

    def clear_current_config(self):
        """清空当前显示的配置"""
        self.exclude_dirs_entry.delete(0, tk.END)
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        self.temp_extensions.clear()
        self.temp_exclude_dirs.clear()
        self.selected_project = None
