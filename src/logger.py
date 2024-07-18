# logger.py
import re
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtWidgets import QTextBrowser, QApplication
from PyQt5.QtCore import QUrl, QMimeData
import os
from utility import open_and_select_file, get_file_content

class ConsoleLogger:
    """
    自定义日志记录器，用于将日志输出到单例的 QTextBrowser 中。
    """

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.setReadOnly(True)
        self.log_queue = []
        self.last_copied_button = None
        self.last_copied_text = None  # 保存上次复制按钮的文本
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
            self.text_widget.moveCursor(QTextCursor.End)
            self.text_widget.insertHtml(message + "<br>")
            self.text_widget.moveCursor(QTextCursor.End)
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

            # 记录当前光标位置,在这期间不能打印其他日志，否则会滚动到最下面
            cursor = self.text_widget.textCursor()
            self.text_widget.setTextCursor(cursor)
            scroll_pos = self.text_widget.verticalScrollBar().value()

            # 更新最后复制的文件提示
            if self.last_copied_button:
                self.update_button_text(self.last_copied_button, self.last_copied_text)
                self.last_copied_text = None

            self.last_copied_text = url.fragment()  # 记录当前按钮的文字
            self.update_button_text(url, "已复制")
            self.last_copied_button = url

            # 恢复光标位置
            self.text_widget.verticalScrollBar().setValue(scroll_pos)

        except FileNotFoundError:
            self.write(f"文件未找到：{file_path}")
        except Exception as e:
            self.write(f"复制文件内容时发生错误：{str(e)}")

    def update_button_text(self, url, text):
        """更新按钮文字"""
        html_content = self.text_widget.toHtml()
        
        # 使用正则表达式匹配并替换 HTML 内容中的按钮文字，添加绿色样式
        pattern = re.compile(rf'(<a href="{re.escape(url.toString())}".*?>)(.*?)(</a>)', re.IGNORECASE)
        new_html = pattern.sub(rf'\1<span style="color:green;">{text}</span>\3', html_content)

        self.text_widget.setHtml(new_html)
