
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QFrame, QScrollArea, QGridLayout, QGroupBox
)

from gui.layout_initializers import create_styled_button
from config import read_config
from gui_functions.event_handlers import (
    save_current_config_handler,
    load_project_config_handler,
    browse_project_path_handler,
    package_code_handler,
    delete_current_config_handler,
    reload_current_config_handler,
    export_current_config_handler,
    import_config_handler,
    show_current_config_handler,
    add_exclude_dir_handler
)
from gui_functions.open_directory import open_directory
from gui_functions.extension_handlers import initialize_extensions, add_extension
from di_container import DIContainer

class ProjectInfoWidget:
    def __init__(self):
        self.gui_core = None

        # 读取配置
        self.projects = read_config()
        self.project_paths = [project["project_path"] for project in self.projects]

        # 默认选择第一个项目
        self.selected_project = self.projects[0] if self.projects else None

        # 临时存储新的项目路径的信息（扩展名和排除目录）
        self.temp_extensions = []
        self.temp_exclude_dirs = []

        self.project_path_combo = QComboBox()

        self.project_info_frame = QGroupBox()

        self.config_buttons_frame = QFrame()
        self.extra_buttons_frame = QFrame()

        self.exclude_dirs_entry = QLineEdit()
        self.extensions_var = QLineEdit()

        self.tags_frame = QScrollArea()
        self.tags_widget = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_widget)  # 使用 QHBoxLayout 以确保标签水平排列


        self.logger = DIContainer().resolve("logger")

    def create_widgets(self):
        self.gui_core = DIContainer().resolve("gui_core")

        self.project_path_combo.addItems(self.project_paths)
        self.project_path_combo.setCurrentIndex(0)
        self.project_path_combo.currentIndexChanged.connect(lambda: load_project_config_handler(self))

        # 创建带边框的Frame用于包含项目配置的各个控件
        project_info_layout = QGridLayout()
        self.project_info_frame.setLayout(project_info_layout)

        fixed_height = 260

        self.project_info_frame.setMinimumHeight(fixed_height)
        self.project_info_frame.setMaximumHeight(fixed_height)

        # 项目选择
        project_info_layout.addWidget(QLabel("项目路径:"), 0, 0)
        project_info_layout.addWidget(self.project_path_combo, 0, 1)

        browse_button = create_styled_button("修改")
        browse_button.clicked.connect(lambda: browse_project_path_handler(self))
        project_info_layout.addWidget(browse_button, 0, 2)

        # 排除目录
        project_info_layout.addWidget(QLabel("排除的子目录:"), 1, 0)
        project_info_layout.addWidget(self.exclude_dirs_entry, 1, 1)
        add_exclude_button = create_styled_button("添加")
        add_exclude_button.clicked.connect(lambda: add_exclude_dir_handler(self))
        project_info_layout.addWidget(add_exclude_button, 1, 2)

        # 文件扩展名
        project_info_layout.addWidget(QLabel("包含的扩展名:"), 2, 0)
        extensions_entry = self.extensions_var

         # 用于展示扩展名标签的QScrollArea和QWidget
        self.tags_layout.setAlignment(Qt.AlignLeft)  # 确保标签靠左对齐
        self.tags_widget.setLayout(self.tags_layout)
        self.tags_frame.setWidget(self.tags_widget)
        self.tags_frame.setWidgetResizable(True)
        self.tags_frame.setMinimumHeight(55)
        self.tags_frame.setMaximumHeight(55)
        self.tags_frame.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.tags_frame.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        project_info_layout.addWidget(self.tags_frame, 2, 1)  # 使其占据整行

        project_info_layout.addWidget(QLabel("新增扩展名:"), 3, 0)
        project_info_layout.addWidget(extensions_entry, 3, 1)
        add_extension_button = create_styled_button("添加")
        add_extension_button.clicked.connect(lambda: self.add_extension(extensions_entry.text()))
        project_info_layout.addWidget(add_extension_button, 3, 2)

        # 初始化扩展名标签
        if self.selected_project:
            self.load_project_details()

        # 添加保存、重载、删除配置按钮
        config_buttons_layout = QHBoxLayout(self.config_buttons_frame)
        config_buttons_layout.setSpacing(10)
        
        save_button = create_styled_button("保存配置")
        save_button.clicked.connect(lambda: save_current_config_handler(self))
        config_buttons_layout.addWidget(save_button)

        reload_button = create_styled_button("重载配置")
        reload_button.clicked.connect(lambda: reload_current_config_handler(self))
        config_buttons_layout.addWidget(reload_button)

        show_button = create_styled_button("查看配置")
        show_button.clicked.connect(lambda: show_current_config_handler(self))
        config_buttons_layout.addWidget(show_button)

        # 添加打开文件浏览器按钮
        open_folder_button = create_styled_button("浏览项目", "blue-bg")
        open_folder_button.clicked.connect(self.open_folder)
        config_buttons_layout.addWidget(open_folder_button, alignment=Qt.AlignRight)

        # 添加打包按钮
        package_button = create_styled_button("打包源码", "green")
        package_button.clicked.connect(lambda: package_code_handler(self))
        config_buttons_layout.addWidget(package_button)

        # 添加导出、导入和查看配置按钮
        extra_buttons_layout = QHBoxLayout(self.extra_buttons_frame)
        extra_buttons_layout.setSpacing(10)
        
        export_button = create_styled_button("导出配置")
        export_button.clicked.connect(lambda: export_current_config_handler(self))
        extra_buttons_layout.addWidget(export_button)

        import_button = create_styled_button("导入配置")
        import_button.clicked.connect(lambda: import_config_handler(self))
        extra_buttons_layout.addWidget(import_button)

        delete_button = create_styled_button("删除配置", "red-bg")
        delete_button.clicked.connect(lambda: delete_current_config_handler(self))
        extra_buttons_layout.addWidget(delete_button)

    def open_folder(self):
        """打开当前所选项目路径"""
        project_path = self.project_path_combo.currentText().strip()
        open_directory(project_path, self.logger)

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

    def add_extension(self, extension):
        """处理添加文件扩展名的逻辑"""
        # 检查并添加扩展名到临时或选定项目的扩展名列表
        if self.selected_project:
            add_extension(self, self.tags_layout, extension, self.selected_project["file_extensions"], self.tags_frame, self.extensions_var)
        else:
            add_extension(self, self.tags_layout, extension, self.temp_extensions, self.tags_frame, self.extensions_var)