from tkinter import ttk

def apply_styles():
    """
    应用自定义样式。
    """
    style = ttk.Style()
    style.configure('Tag.TFrame', background='#e6f7ff', borderwidth=1, relief='solid')
    style.configure('Tag.TLabel', background='#e6f7ff', foreground='#005b96', font=('Arial', 11), padding=(5, 2))
    style.configure('Tag.TButton', background='#e6f7ff', foreground='#d9534f', font=('Arial', 9, 'bold'), padding=(1, 0), relief='flat')
