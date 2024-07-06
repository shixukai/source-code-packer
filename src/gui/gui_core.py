from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox,
    QLineEdit, QTextEdit, QFrame, QScrollArea, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from logger import ConsoleLogger, SingletonQTextEditManager

from gui.layout_initializers import apply_styles, center_window, set_responsive_layout, create_styled_button
from gui.gui_pro_info import ProjectInfoWidget

class SourceCodePackerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("源码打包工具")

        default_width = 900
        default_height = 700
        self.resize(default_width, default_height)

        # 设置最小尺寸
        self.setMinimumSize(default_width, default_height)
        self.layout = QVBoxLayout()

        # 初始化样式
        apply_styles()

        # # 创建GUI
        # self.create_widgets()

        # 设置拖放功能
        self.setAcceptDrops(True)

    def create_widgets(self):
        layout = self.layout

        # 日志显示区域
        log_display_frame = QFrame()
        log_display_layout = QVBoxLayout()
        log_display_frame.setLayout(log_display_layout)

        log_display = SingletonQTextEditManager.get_instance()
        log_display.setReadOnly(True)
        log_display.setLineWrapMode(QTextEdit.WidgetWidth)
        log_display_layout.addWidget(log_display)

        self.logger = ConsoleLogger()

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

    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """处理文件放下事件"""
        urls = event.mimeData().urls()
        if urls:
            file_paths = [url.toLocalFile() for url in urls]
            self.logger.write("拖入的文件/文件夹:\n" + "\n".join(file_paths))
        event.acceptProposedAction()




