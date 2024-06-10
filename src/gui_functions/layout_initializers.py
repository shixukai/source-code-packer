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

def set_responsive_layout(root, tags_frame, tags_canvas, tags_scroll):
    """设置窗口和组件的自适应布局"""
    root.columnconfigure(0, weight=1)  # 设置窗口主列的自适应
    root.columnconfigure(1, weight=1)  # 设置窗口主列的自适应
    root.columnconfigure(2, weight=1)  # 设置窗口主列的自适应

    root.rowconfigure(0, weight=1)  # 设置窗口首行的自适应
    root.rowconfigure(5, weight=3)  # 日志显示区域的自适应高度权重
    root.rowconfigure(6, weight=0)  # 按钮行的自适应高度权重
    root.rowconfigure(7, weight=0)  # 按钮行的自适应高度权重

    tags_frame.columnconfigure(0, weight=1)  # 标签框架的自适应宽度权重
    tags_frame.rowconfigure(0, weight=1)  # 标签框架的自适应高度权重

    tags_canvas.configure(scrollregion=tags_canvas.bbox("all"))  # 设置画布的滚动区域
