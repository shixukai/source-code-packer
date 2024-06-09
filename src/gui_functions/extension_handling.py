import tkinter as tk
from tkinter import messagebox, ttk

def add_extension(root, frame, extension, extensions, canvas, scrollbar, entry_var, init=False):
    """
    添加新的文件扩展名并以标签形式展示。
    """
    extension = extension.strip()  # 去除可能的空格

    if not extension:
        messagebox.showerror("错误", "扩展名不能为空或仅包含空格")
        return

    if not extension.startswith('.'):
        extension = f'.{extension}'  # 自动补全扩展名前的点

    if not init and extension in extensions:
        messagebox.showinfo("提示", f"扩展名 '{extension}' 已存在")
        return  # 避免重复添加相同的扩展名

    if not init:
        extensions.append(extension)

    # 创建美观的标签显示
    tag_frame = ttk.Frame(frame, style='Tag.TFrame', padding=2)  # 调整padding使标签更紧凑
    tag_label = ttk.Label(tag_frame, text=extension, style='Tag.TLabel')
    tag_label.pack(side='left', padx=3, pady=3)
    remove_button = ttk.Button(tag_frame, text="x", style='Tag.TButton', width=1, command=lambda: remove_extension(root, tag_frame, extension, extensions, canvas, scrollbar))
    remove_button.pack(side='left', padx=2, pady=2)  # 调整删除按钮的padding和位置
    tag_frame.pack(side='left', padx=5, pady=5)  # 使用'left'确保标签在同一行按顺序显示

    # 更新标签显示区域
    update_canvas(root, frame, canvas, scrollbar)
    root.update_idletasks()  # 强制刷新界面

    # 清空输入框内容
    if not init:
        entry_var.set("")

def remove_extension(root, tag_frame, extension, extensions, canvas, scrollbar):
    """
    删除标签形式的文件扩展名。
    """
    if extension in extensions:
        extensions.remove(extension)
        tag_frame.destroy()
        update_canvas(root, tag_frame.master, canvas, scrollbar)
        root.update_idletasks()  # 强制刷新界面
    else:
        messagebox.showerror("错误", f"扩展名 '{extension}' 不存在")

def update_canvas(root, frame, canvas, scrollbar):
    """
    更新标签显示区域的大小。
    """
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # 控制滚动条的显示与隐藏
    if canvas.bbox("all")[2] > canvas.winfo_width():
        scrollbar.pack(side='bottom', fill='x')
    else:
        scrollbar.pack_forget()

    # 强制刷新界面，以更新显示区域
    root.update_idletasks()

def initialize_extensions(root, frame, extensions, canvas, scrollbar, entry_var):
    """
    初始化显示默认的文件扩展名。
    """
    for ext in extensions:
        add_extension(root, frame, ext, extensions, canvas, scrollbar, entry_var, init=True)
