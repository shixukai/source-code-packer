import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from config import read_config
from logger import ConsoleLogger
from .extension_handling import initialize_extensions, add_extension, update_canvas, remove_extension
from .layout_initializers import apply_styles, center_window, set_responsive_layout
from .event_handlers import save_current_config, load_project_config, browse_project_path, add_exclude_dir, package_code, delete_current_config

class SourceCodePackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("源码打包工具")
        self.root.geometry("1000x700")  # 初始大小适当调整

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
        bordered_frame = tk.Frame(self.root, relief='solid', borderwidth=2, padx=10, pady=10)
        bordered_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        # 项目选择
        tk.Label(bordered_frame, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        
        self.project_path_combo = ttk.Combobox(bordered_frame, values=self.project_paths, width=60)
        self.project_path_combo.grid(row=0, column=1, padx=10, pady=5, sticky="we")
        if self.project_paths:
            self.project_path_combo.current(0)  # 默认选择第一个项目路径

        self.project_path_combo.bind("<<ComboboxSelected>>", self.load_project_config)

        tk.Button(bordered_frame, text="浏览", command=self.browse_project_path).grid(row=0, column=2, padx=10, pady=5, sticky="e")

        # 排除目录
        tk.Label(bordered_frame, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.exclude_dirs_entry = tk.Entry(bordered_frame, width=60)
        self.exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
        tk.Button(bordered_frame, text="添加", command=self.add_exclude_dir).grid(row=1, column=2, padx=10, pady=5, sticky="e")

        # 文件扩展名
        tk.Label(bordered_frame, text="要打包的文件扩展名:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        extensions_frame = tk.Frame(bordered_frame)
        extensions_frame.grid(row=2, column=1, columnspan=1, padx=10, pady=5, sticky="we")

        self.extensions_var = tk.StringVar()
        extensions_entry = tk.Entry(bordered_frame, width=40, textvariable=self.extensions_var)
        extensions_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")
        tk.Button(bordered_frame, text="添加扩展名", command=lambda: self.add_extension(extensions_entry.get())).grid(row=3, column=2, padx=10, pady=5, sticky="e")

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

        # 添加保存、删除配置和打包按钮
        config_buttons_frame = tk.Frame(bordered_frame)
        config_buttons_frame.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="we")

        tk.Button(config_buttons_frame, text="保存配置", command=self.save_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(config_buttons_frame, text="删除配置", fg='red', command=self.delete_current_config).pack(side=tk.LEFT, padx=5)
        tk.Button(config_buttons_frame, text="打包源码", default='active', command=self.package_code).pack(side=tk.RIGHT, padx=5)

        # 日志显示区域
        log_display_frame = tk.Frame(self.root)
        log_display_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        log_display = scrolledtext.ScrolledText(log_display_frame, wrap=tk.WORD)
        log_display.pack(fill="both", expand=True)

        self.logger = ConsoleLogger(log_display)

        # 清除日志和退出程序按钮
        bottom_buttons_frame = tk.Frame(self.root)
        bottom_buttons_frame.grid(row=6, column=0, columnspan=3, pady=10, sticky="we")

        tk.Button(bottom_buttons_frame, text="清除日志", command=self.logger.clear).pack(side=tk.LEFT, padx=10, pady=5)
        tk.Button(bottom_buttons_frame, text="退出程序", fg='red', command=self.root.quit).pack(side=tk.RIGHT, padx=10, pady=5)

        # 设置自适应布局
        set_responsive_layout(self.root, self.tags_frame, self.tags_canvas, self.tags_scroll)

        # 将窗口居中显示
        center_window(self.root)

    def load_project_config(self, event=None):
        load_project_config(self)

    def browse_project_path(self):
        browse_project_path(self)

    def add_exclude_dir(self):
        add_exclude_dir(self)

    def add_extension(self, extension):
        add_extension(self.root, self.tags_frame, extension, self.temp_extensions, self.tags_canvas, self.tags_scroll, self.extensions_var)

    def package_code(self):
        package_code(self)

    def save_current_config(self):
        save_current_config(self)

    def delete_current_config(self):
        delete_current_config(self)

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
