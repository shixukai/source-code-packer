# layout_initializers.py

from tkinter import ttk

def apply_styles():
    """
    应用自定义样式。
    """
    style = ttk.Style()
    style.configure('Tag.TFrame', background='#e6f7ff', borderwidth=1, relief='solid')
    style.configure('Tag.TLabel', background='#e6f7ff', foreground='#005b96', font=('Arial', 11), padding=(5, 2))
    style.configure('Tag.TButton', background='#e6f7ff', foreground='#d9534f', font=('Arial', 9, 'bold'), padding=(1, 0), relief='flat')


def center_window(root):
    """将窗口居中"""
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def set_responsive_layout(root, bordered_frame, log_display_frame, bottom_buttons_frame, tags_frame, tags_canvas, tags_scroll):
    """设置窗口和组件的自适应布局"""
    # 主窗口列配置
    root.columnconfigure(0, weight=1)  # 使窗口主要列自适应
    root.rowconfigure(0, weight=1)  # 设置窗口首行自适应
    root.rowconfigure(5, weight=3)  # 日志显示区域的自适应高度权重
    root.rowconfigure(6, weight=0)  # 按钮行的自适应高度权重

    # 边框框架列配置
    bordered_frame.columnconfigure(0, weight=0)  # 靠左列
    bordered_frame.columnconfigure(1, weight=1)  # 中间列
    bordered_frame.columnconfigure(2, weight=0)  # 靠右列

    # 日志显示区域自适应配置
    log_display_frame.columnconfigure(0, weight=1)  # 日志显示区域的自适应宽度权重
    log_display_frame.rowconfigure(0, weight=1)  # 日志显示区域的自适应高度权重

    # 底部按钮区域的自适应配置
    bottom_buttons_frame.columnconfigure(0, weight=1)  # 底部按钮区域的自适应宽度权重

    # 标签框架自适应配置
    tags_frame.columnconfigure(0, weight=1)  # 标签框架的自适应宽度权重

    # 绑定窗口大小变化事件
    def on_resize(event):
        tags_frame.update_idletasks()
        tags_canvas.configure(scrollregion=tags_canvas.bbox("all"))

        # 控制滚动条的显示与隐藏
        if tags_canvas.bbox("all")[2] > tags_canvas.winfo_width():
            tags_scroll.pack(side='bottom', fill='x')
        else:
            tags_scroll.pack_forget()

    root.bind('<Configure>', on_resize)

