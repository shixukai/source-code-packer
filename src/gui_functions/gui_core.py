# gui_core.py

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QFontMetrics

from config import read_config
from logger import ConsoleLogger
from .extension_handling import initialize_extensions, add_extension
from .layout_initializers import apply_styles, center_window, set_responsive_layout, create_styled_button
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

class SourceCodePackerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("源码打包工具")

        default_width = 900
        default_height = 700
        self.resize(default_width, default_height)

        # 设置最小尺寸
        self.setMinimumSize(default_width, default_height)

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
        layout = QVBoxLayout()

        # 创建带边框的Frame用于包含项目配置的各个控件
        bordered_frame = QGroupBox()
        bordered_layout = QGridLayout()
        bordered_frame.setLayout(bordered_layout)

        fixed_height = 260
        bordered_frame.setMinimumHeight(fixed_height)
        bordered_frame.setMaximumHeight(fixed_height)

        # 项目选择
        bordered_layout.addWidget(QLabel("项目路径:"), 0, 0)
        
        self.project_path_combo = QComboBox()
        self.project_path_combo.addItems(self.project_paths)
        self.project_path_combo.setCurrentIndex(0)
        self.project_path_combo.currentIndexChanged.connect(lambda: load_project_config_handler(self))
        bordered_layout.addWidget(self.project_path_combo, 0, 1)
        
        browse_button = create_styled_button("浏览")
        browse_button.clicked.connect(lambda: browse_project_path_handler(self))
        bordered_layout.addWidget(browse_button, 0, 2)

        # 排除目录
        bordered_layout.addWidget(QLabel("排除的子目录:"), 1, 0)
        self.exclude_dirs_entry = QLineEdit()
        bordered_layout.addWidget(self.exclude_dirs_entry, 1, 1)
        add_exclude_button = create_styled_button("添加")
        add_exclude_button.clicked.connect(lambda: add_exclude_dir_handler(self))
        bordered_layout.addWidget(add_exclude_button, 1, 2)

        # 文件扩展名
        bordered_layout.addWidget(QLabel("已包含的扩展名:"), 2, 0)
        self.extensions_var = QLineEdit()
        extensions_entry = self.extensions_var

        # 用于展示扩展名标签的QScrollArea和QWidget
        self.tags_frame = QScrollArea()
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_widget)  # 使用 QHBoxLayout 以确保标签水平排列
        self.tags_layout.setAlignment(Qt.AlignLeft)  # 确保标签靠左对齐
        self.tags_widget.setLayout(self.tags_layout)
        self.tags_frame.setWidget(self.tags_widget)
        self.tags_frame.setWidgetResizable(True)
        self.tags_frame.setMinimumHeight(60)
        self.tags_frame.setMaximumHeight(60)
        self.tags_frame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tags_frame.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        bordered_layout.addWidget(self.tags_frame, 2, 1)  # 使其占据整行

        bordered_layout.addWidget(QLabel("新增扩展名:"), 3, 0)
        bordered_layout.addWidget(extensions_entry, 3, 1)
        add_extension_button = create_styled_button("添加")
        add_extension_button.clicked.connect(lambda: self.add_extension(extensions_entry.text()))
        bordered_layout.addWidget(add_extension_button, 3, 2)


        # 初始化扩展名标签
        if self.selected_project:
            self.load_project_details()

        layout.addWidget(bordered_frame)

        # 添加保存、重载、删除配置按钮
        config_buttons_frame = QFrame()
        config_buttons_layout = QHBoxLayout(config_buttons_frame)
        config_buttons_layout.setSpacing(10)
        
        save_button = create_styled_button("保存配置")
        save_button.clicked.connect(lambda: save_current_config_handler(self))
        config_buttons_layout.addWidget(save_button)

        reload_button = create_styled_button("重载配置")
        reload_button.clicked.connect(lambda: reload_current_config_handler(self))
        config_buttons_layout.addWidget(reload_button)

        delete_button = create_styled_button("删除配置", "red")
        delete_button.clicked.connect(lambda: delete_current_config_handler(self))
        config_buttons_layout.addWidget(delete_button)

        # 添加打包按钮
        package_button = create_styled_button("打包源码", "green")
        package_button.clicked.connect(lambda: package_code_handler(self))
        config_buttons_layout.addWidget(package_button, alignment=Qt.AlignRight)

        layout.addWidget(config_buttons_frame)

        # 添加导出、导入和查看配置按钮
        extra_buttons_frame = QFrame()
        extra_buttons_layout = QHBoxLayout(extra_buttons_frame)
        extra_buttons_layout.setSpacing(10)
        
        export_button = create_styled_button("导出配置")
        export_button.clicked.connect(lambda: export_current_config_handler(self))
        extra_buttons_layout.addWidget(export_button)

        import_button = create_styled_button("导入配置")
        import_button.clicked.connect(lambda: import_config_handler(self))
        extra_buttons_layout.addWidget(import_button)

        show_button = create_styled_button("查看配置")
        show_button.clicked.connect(lambda: show_current_config_handler(self))
        extra_buttons_layout.addWidget(show_button)

        layout.addWidget(extra_buttons_frame, alignment=Qt.AlignLeft)

        # 日志显示区域
        log_display_frame = QFrame()
        log_display_layout = QVBoxLayout()
        log_display_frame.setLayout(log_display_layout)

        log_display = QTextEdit()
        log_display.setReadOnly(True)
        log_display.setLineWrapMode(QTextEdit.WidgetWidth)
        log_display_layout.addWidget(log_display)

        self.logger = ConsoleLogger(log_display)

        layout.addWidget(log_display_frame)

        # 清除日志和退出程序按钮
        bottom_buttons_frame = QFrame()
        bottom_buttons_layout = QHBoxLayout(bottom_buttons_frame)
        
        clear_log_button = create_styled_button("清除日志")
        clear_log_button.clicked.connect(self.logger.clear)
        bottom_buttons_layout.addWidget(clear_log_button, alignment=Qt.AlignLeft)

        exit_button = create_styled_button("退出程序", "red")
        exit_button.clicked.connect(self.close)
        bottom_buttons_layout.addWidget(exit_button, alignment=Qt.AlignRight)

        layout.addWidget(bottom_buttons_frame)

        self.setLayout(layout)

        # 设置自适应布局
        set_responsive_layout(self)

        # 将窗口居中显示
        center_window(self)



    def add_extension(self, extension):
        """处理添加文件扩展名的逻辑"""
        # 检查并添加扩展名到临时或选定项目的扩展名列表
        if self.selected_project:
            add_extension(self, self.tags_layout, extension, self.selected_project["file_extensions"], self.tags_frame, self.extensions_var)
        else:
            add_extension(self, self.tags_layout, extension, self.temp_extensions, self.tags_frame, self.extensions_var)

    def load_project_details(self):
        """加载当前项目的详细信息"""
        if self.selected_project:
            initialize_extensions(self, self.tags_layout, self.selected_project["file_extensions"], self.tags_frame, self.extensions_var)
            self.exclude_dirs_entry.setText(";".join(self.selected_project["exclude_dirs"]))
        else:
            self.clear_current_config()

    def clear_current_config(self):
        """清空当前显示的配置"""
        self.exclude_dirs_entry.clear()
        for i in reversed(range(self.tags_layout.count())):
            widget = self.tags_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        self.temp_extensions.clear()
        self.temp_exclude_dirs.clear()
        self.selected_project = None
