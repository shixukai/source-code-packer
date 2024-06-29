# logger.py

from PyQt5.QtGui import QFont

class ConsoleLogger:
    """
    自定义日志记录器，用于将日志输出到 GUI 中的文本框。
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.setReadOnly(True)
        self.log_queue = []

        # 设置字体，确保支持树形结构字符
        font = QFont()
        font.setStyleHint(QFont.Monospace)
        font.setFamily("Courier New, Courier, Monospace")
        self.text_widget.setFont(font)

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
