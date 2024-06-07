# logger.py
import tkinter as tk

class ConsoleLogger:
    """
    自定义日志记录器，用于将日志输出到 GUI 中的文本框。
    """
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.text_widget.config(state=tk.DISABLED)
        self.log_queue = []

    def write(self, message):
        if message != '\n':  # 排除多余的换行
            self.log_queue.append(message)
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

    def clear(self):
        """清空日志显示区域。"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
