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
        tk.Button(bordered_frame, text="添加", command=lambda: self.add_exclude_dir()).grid(row=1, column=2, padx=10, pady=5, sticky="e")

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
        self.set_responsive_layout()

        # 将窗口居中显示
        center_window(self.root)

    def set_responsive_layout(self):
        # 设置自适应布局
        self.root.columnconfigure(0, weight=1)  # 设置窗口主列的自适应
        self.root.columnconfigure(1, weight=1)  # 设置窗口主列的自适应
        self.root.columnconfigure(2, weight=1)  # 设置窗口主列的自适应

        self.root.rowconfigure(0, weight=1)  # 设置窗口首行的自适应
        self.root.rowconfigure(5, weight=3)  # 日志显示区域的自适应高度权重
        self.root.rowconfigure(6, weight=0)  # 按钮行的自适应高度权重
        self.root.rowconfigure(7, weight=0)  # 按钮行的自适应高度权重

    def load_project_config(self, event=None):
        """根据选择的项目加载配置"""
        self.clear_current_config()  # 清空当前显示的配置
        selected_path = self.project_path_combo.get()
        for project in self.projects:
            if project["project_path"] == selected_path:
                self.selected_project = project
                self.load_project_details()  # 加载新的项目详情
                break

    def load_project_details(self):
        """加载当前选择的项目详情"""
        if self.selected_project:
            self.exclude_dirs_entry.insert(0, ";".join(self.selected_project["exclude_dirs"]))
            initialize_extensions(self.root, self.tags_frame, self.selected_project["file_extensions"], self.tags_canvas, self.tags_scroll, self.extensions_var)

    def clear_current_config(self):
        """清空当前项目的排除目录和扩展名标签"""
        self.exclude_dirs_entry.delete(0, tk.END)
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
        self.extensions_var.set("")
        self.temp_extensions = []
        self.temp_exclude_dirs = []

    def browse_project_path(self):
        current_path = self.project_path_combo.get().strip()
        initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(initialdir=initial_dir)
        if selected_dir:
            self.project_path_combo.set(selected_dir)
            # 清空显示的当前配置
            self.clear_current_config()
            # 检查该路径是否在现有配置中
            self.selected_project = None
            for project in self.projects:
                if project["project_path"] == selected_dir:
                    self.selected_project = project
                    self.load_project_details()
                    break

        self.root.update_idletasks()

    def add_exclude_dir(self):
        """添加排除目录"""
        add_exclude_dir(self.root, self.project_path_combo, self.exclude_dirs_entry)
        if not self.selected_project:
            self.temp_exclude_dirs = [d.strip() for d in self.exclude_dirs_entry.get().split(";") if d.strip()]

    def add_extension(self, extension):
        if self.selected_project:
            add_extension(self.root, self.tags_frame, extension, self.selected_project["file_extensions"], self.tags_canvas, self.tags_scroll, self.extensions_var)
        else:
            add_extension(self.root, self.tags_frame, extension, self.temp_extensions, self.tags_canvas, self.tags_scroll, self.extensions_var)

    def package_code(self):
        project_path = self.project_path_combo.get().strip()
        if not project_path:
            messagebox.showerror("错误", "请先选择或配置一个项目路径")
            return

        if self.selected_project:
            on_package_button_click(self.root, self.project_path_combo, self.selected_project, self.exclude_dirs_entry, self.logger)
        else:
            # 临时打包当前未保存的项目配置
            temp_project = {
                "project_path": project_path,
                "file_extensions": self.temp_extensions,
                "exclude_dirs": self.temp_exclude_dirs
            }
            on_package_button_click(self.root, self.project_path_combo, temp_project, self.exclude_dirs_entry, self.logger)

    def save_current_config(self):
        """保存当前项目配置到config.json"""
        project_path = self.project_path_combo.get().strip()

        # 检查项目路径是否为空
        if not project_path:
            messagebox.showerror("错误", "项目路径不能为空")
            return

        file_extensions = self.selected_project["file_extensions"] if self.selected_project else self.temp_extensions
        exclude_dirs = [d.strip() for d in self.exclude_dirs_entry.get().split(";") if d.strip()]

        project = {
            "project_path": project_path,
            "file_extensions": file_extensions,
            "exclude_dirs": exclude_dirs
        }
        save_config(project)
        messagebox.showinfo("提示", f"配置已保存到: {project_path}")

        # 更新配置列表
        self.projects = read_config()
        self.project_paths = [project["project_path"] for project in self.projects]
        self.project_path_combo['values'] = self.project_paths
        self.project_path_combo.set(project_path)  # 重新选择保存的项目
        self.selected_project = project

    def delete_current_config(self):
        """从config.json中删除当前项目配置"""
        project_path = self.project_path_combo.get().strip()

        # 检查项目路径是否为空
        if not project_path:
            messagebox.showerror("错误", "项目路径不能为空")
            return

        delete_config(project_path)
        messagebox.showinfo("提示", f"配置已从 {project_path} 中删除")

        # 更新配置
        self.projects = read_config()
        self.project_paths = [project["project_path"] for project in self.projects]
        self.project_path_combo['values'] = self.project_paths
        if self.project_paths:
            self.project_path_combo.current(0)  # 选择第一个项目路径
            self.load_project_config()
        else:
            self.project_path_combo.set('')
            self.clear_current_config()

# 导出类，以便其他模块可以导入
def create_gui():
    root = tk.Tk()
    app = SourceCodePackerGUI(root)
    root.mainloop()
