from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent


from gui.layout_initializers import apply_styles, center_window, set_responsive_layout

from di_container import DIContainer
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

    def create_set_layout(self):
        di_container = DIContainer()

        layout = self.layout

        project_info_widget = di_container.resolve("project_info_widget")
        log_display = di_container.resolve("log_display")

        layout.addWidget(project_info_widget.project_info_frame, alignment=Qt.AlignBottom)
        layout.addWidget(project_info_widget.config_buttons_frame, alignment=Qt.AlignBottom)
        layout.addWidget(project_info_widget.extra_buttons_frame, alignment=Qt.AlignLeft)
        layout.addWidget(log_display.log_display_frame, alignment=Qt.AlignBottom)
        layout.addWidget(log_display.bottom_buttons_frame, alignment=Qt.AlignBottom)

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
            logger = DIContainer().resolve("logger")
            file_paths = [url.toLocalFile() for url in urls]
            logger.write("拖入的文件/文件夹:\n" + "\n".join(file_paths))
        event.acceptProposedAction()




