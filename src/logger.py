from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTextEdit

class SingletonQTextEditManager:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = QTextEdit()
            cls._instance.setReadOnly(True)
            # 设置字体，确保支持树形结构字符
            font = QFont()
            font.setStyleHint(QFont.Monospace)
            font.setFamily("Courier New, Courier, Monospace")
            cls._instance.setFont(font)
        return cls._instance


class ConsoleLogger:
    """
    自定义日志记录器，用于将日志输出到单例的 QTextEdit 中。
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConsoleLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # 避免多次初始化
            self.text_widget = SingletonQTextEditManager.get_instance()
            self.log_queue = []
            self.initialized = True

    def write(self, message):
        if message != '\n':  # 排除多余的换行
            self.log_queue.append(message)
            self.text_widget.setReadOnly(False)
            self.text_widget.append(message)
            self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
            self.text_widget.setReadOnly(True)

    def flush(self):
        pass

    def clear(self):
        """清空日志显示区域。"""
        self.text_widget.setReadOnly(False)
        self.text_widget.clear()
        self.text_widget.setReadOnly(True)
