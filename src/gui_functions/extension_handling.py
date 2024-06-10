# extension_handling.py

import tkinter as tk
from tkinter import messagebox, ttk, Canvas

def create_rounded_rectangle(canvas, x1, y1, x2, y2, r=25, **kwargs):
    """
    在给定的坐标上创建一个带有圆角的矩形。
    """
    points = [x1 + r, y1,
              x1 + r, y1,
              x2 - r, y1,
              x2 - r, y1,
              x2, y1,
              x2, y1 + r,
              x2, y1 + r,
              x2, y2 - r,
              x2, y2 - r,
              x2, y2,
              x2 - r, y2,
              x2 - r, y2,
              x1 + r, y2,
              x1 + r, y2,
              x1, y2,
              x1, y2 - r,
              x1, y2 - r,
              x1, y1 + r,
              x1, y1 + r,
              x1, y1]
    
    return canvas.create_polygon(points, **kwargs, smooth=True)

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

    # 创建Canvas来绘制圆角背景和标签
    tag_canvas = Canvas(frame, width=80, height=30, bg=frame.cget('bg'), bd=0, highlightthickness=0)
    tag_canvas.pack(side='left', padx=5, pady=5)

    # 绘制带有圆角矩形的背景
    create_rounded_rectangle(tag_canvas, 5, 5, 75, 25, r=10, fill='#f0f8ff', outline='black')

    # 在Canvas上创建标签
    tag_canvas.create_text(20, 15, text=extension, anchor='w', fill='blue')

    # 在Canvas上创建删除按钮
    delete_btn = tag_canvas.create_text(60, 15, text='x', anchor='w', fill='red')
    
    # 绑定删除按钮的点击事件
    def delete_action(event, tag=tag_canvas, ext=extension):
        remove_extension(root, tag, ext, extensions, canvas, scrollbar)

    tag_canvas.tag_bind(delete_btn, "<Button-1>", delete_action)

    # 更新标签显示区域
    update_canvas(root, frame, canvas, scrollbar)
    root.update_idletasks()  # 强制刷新界面

    # 清空输入框内容
    if not init:
        entry_var.set("")

def remove_extension(root, tag_canvas, extension, extensions, canvas, scrollbar):
    """
    删除标签形式的文件扩展名。
    """
    if extension in extensions:
        extensions.remove(extension)
        tag_canvas.destroy()
        update_canvas(root, tag_canvas.master, canvas, scrollbar)
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
