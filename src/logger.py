from PyQt5.QtGui import QFont, QTextCursor, QDesktopServices
from PyQt5.QtWidgets import QTextBrowser, QApplication
from PyQt5.QtCore import QUrl, QMimeData
import subprocess
from utility import open_and_select_file, get_file_content
import os

class ConsoleLogger:
    """
    自定义日志记录器，用于将日志输出到单例的 QTextBrowser 中。
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
        self.text_widget.setOpenExternalLinks(True)  # 确保打开外部链接
        self.text_widget.setOpenLinks(False)  # 使 anchorClicked 信号生效
        self.text_widget.anchorClicked.connect(self.handle_anchor_click)

    def write(self, message):
        if message != '\n':  # 排除多余的换行
            self.log_queue.append(message)
            self.text_widget.setReadOnly(False)
            self.text_widget.insertHtml(message + "<br>")
            self.text_widget.verticalScrollBar().setValue(self.text_widget.verticalScrollBar().maximum())
            self.text_widget.setReadOnly(True)

    def flush(self):
        pass

    def clear(self):
        """清空日志显示区域。"""
        self.text_widget.setReadOnly(False)
        self.text_widget.clear()
        self.text_widget.setReadOnly(True)

    def handle_anchor_click(self, url):
        """处理链接点击事件"""
        try:
            scheme = url.scheme()
            file_path = url.path()  # 使用 url.path() 代替 toLocalFile()
            content = ""

            if scheme == "file":
                open_and_select_file(file_path)
                return
            elif scheme == "copy":
                content = get_file_content(file_path, include_filename=False)
            elif scheme == "copywithname":
                content = get_file_content(file_path, include_filename=True)
            
            clipboard = QApplication.clipboard()
            mime_data = QMimeData()
            mime_data.setText(content)
            clipboard.setMimeData(mime_data)
            cursor = self.text_widget.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_widget.setTextCursor(cursor)
            self.write(f"文件内容已复制到剪贴板：{file_path}")
        except FileNotFoundError:
            self.write(f"文件未找到：{file_path}")
        except Exception as e:
            self.write(f"复制文件内容时发生错误：{str(e)}")