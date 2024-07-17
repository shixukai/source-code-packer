from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout, 
    QTextBrowser, 
    QTextEdit, 
    QFrame,
    QSizePolicy
)
from di_container import DIContainer
from logger import ConsoleLogger
from gui.layout_initializers import create_styled_button

class LogDisplay:
    def __init__(self):
        self.gui_core = None
        self.log_display_main_frame = QFrame()

    def create_widgets(self):
        di_container = DIContainer()
        self.gui_core = DIContainer().resolve("gui_core")

        di_container.register("log_editor", QTextBrowser, singleton=True)
        di_container.register("logger", lambda di: ConsoleLogger(di.resolve("log_editor")), singleton=True)

        log_display_main_layout = QVBoxLayout(self.log_display_main_frame)

        # 日志显示区域
        log_editor = di_container.resolve("log_editor")

        log_editor.setReadOnly(True)
        log_editor.setLineWrapMode(QTextEdit.WidgetWidth)
        log_editor.setOpenExternalLinks(False)

        log_display_main_layout.addWidget(log_editor)

        # 清除日志和退出程序按钮
        clear_log_button = create_styled_button("清除日志")
        logger = di_container.resolve("logger")
        clear_log_button.clicked.connect(logger.clear)
        log_display_main_layout.addWidget(clear_log_button, alignment=Qt.AlignLeft)

        window = di_container.resolve("gui_core")
        exit_button = create_styled_button("退出程序", "red")
        exit_button.clicked.connect(window.close)
        log_display_main_layout.addWidget(exit_button, alignment=Qt.AlignRight)