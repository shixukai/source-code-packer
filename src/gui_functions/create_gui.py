import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import platform
import subprocess
from config import read_config
from packager import run_packaging
from logger import ConsoleLogger
from .center_window import center_window
from .open_directory import open_directory
from .validate_exclude_dir import validate_exclude_dir, InvalidSubdirectoryException


from .center_window import center_window
from .open_directory import open_directory
from .validate_exclude_dir import validate_exclude_dir

def create_gui():
    """
    创建和运行图形用户界面。
    """
    root = tk.Tk()
    root.title("源码打包工具")
    root.geometry("800x700")  # 增加初始高度以容纳更多内容

    # 创建自定义样式
    style = ttk.Style()
    style.configure('Tag.TFrame', background='#e6f7ff', borderwidth=1, relief='solid')
    style.configure('Tag.TLabel', background='#e6f7ff', foreground='#005b96', font=('Arial', 11), padding=(5, 2))
    style.configure('Tag.TButton', background='#e6f7ff', foreground='#d9534f', font=('Arial', 9, 'bold'), padding=(1, 0), relief='flat')

    # 读取默认配置
    project_path, extensions, exclude_dirs = read_config()

    # 项目路径
    tk.Label(root, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    project_path_entry = tk.Entry(root, width=50)
    project_path_entry.insert(0, project_path)
    project_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="we")

    def browse_project_path():
        current_path = project_path_entry.get().strip()
        initial_dir = os.path.dirname(current_path) if current_path else os.path.expanduser("~")
        selected_dir = filedialog.askdirectory(initialdir=initial_dir)
        if selected_dir:  # 只有在用户选择了目录时才更新路径
            project_path_entry.delete(0, tk.END)
            project_path_entry.insert(0, selected_dir)
        root.update_idletasks()  # 强制刷新界面

    tk.Button(root, text="浏览", command=browse_project_path).grid(row=0, column=2, padx=10, pady=5)

    # 排除目录
    tk.Label(root, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    exclude_dirs_entry = tk.Entry(root, width=50)
    exclude_dirs_entry.insert(0, ";".join(exclude_dirs))
    exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5, sticky="we")
    tk.Button(root, text="添加", command=lambda: add_exclude_dir()).grid(row=1, column=2, padx=10, pady=5)

    # 文件扩展名
    tk.Label(root, text="要打包的文件扩展名:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    extensions_frame = tk.Frame(root)
    extensions_frame.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="we")

    # 标签输入框
    extensions_var = tk.StringVar()
    extensions_entry = tk.Entry(root, width=20, textvariable=extensions_var)
    extensions_entry.grid(row=3, column=1, padx=10, pady=5, sticky="we")
    tk.Button(root, text="添加", command=lambda: add_extension(tags_frame, extensions_entry.get())).grid(row=3, column=2, padx=10, pady=5)

    # 用于展示扩展名标签的Canvas和滚动条
    tags_canvas = tk.Canvas(extensions_frame, height=50, bg="#f0f8ff")
    tags_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

    tags_frame = tk.Frame(tags_canvas, bg="#f0f8ff")
    tags_canvas.create_window((0, 0), window=tags_frame, anchor='nw')

    tags_scroll = tk.Scrollbar(extensions_frame, orient=tk.HORIZONTAL, command=tags_canvas.xview)
    tags_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    tags_canvas.configure(xscrollcommand=tags_scroll.set)

    # 自动更新标签框的大小
    def update_canvas():
        tags_frame.update_idletasks()
        tags_canvas.config(scrollregion=tags_canvas.bbox("all"))

        # 控制滚动条的显示与隐藏
        if tags_canvas.bbox("all")[2] > tags_canvas.winfo_width():
            tags_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            tags_scroll.pack_forget()

    def add_exclude_dir():
        current_excludes = exclude_dirs_entry.get().strip()
        selected_dir = filedialog.askdirectory(initialdir=project_path_entry.get().strip())
        if selected_dir:  # 只有在用户选择了目录时才更新
            last_dir_name = os.path.basename(selected_dir)  # 提取最后一级目录名称
            exclude_dirs_list = [d.strip() for d in current_excludes.split(',') if d.strip()]  # 将现有目录拆分为列表
            exclude_dirs_list.append(last_dir_name)  # 追加新选择的目录名
            new_excludes = ", ".join(exclude_dirs_list)  # 重新组合为字符串
            exclude_dirs_entry.delete(0, tk.END)
            exclude_dirs_entry.insert(0, new_excludes)
            root.update_idletasks()  # 强制刷新界面
            """
            打开项目目录并选择子目录，然后将其添加到排除列表中。
            """
            project_path = project_path_entry.get().strip()
            if not project_path:
                messagebox.showerror("错误", "请先选择项目路径")
                return

            selected_dir = filedialog.askdirectory(initialdir=project_path)
            if selected_dir:
                relative_dir = os.path.relpath(selected_dir, project_path)
                exclude_dirs_entry.delete(0, tk.END)
                exclude_dirs_entry.insert(0, f"{exclude_dirs_entry.get()};{relative_dir}".strip(";"))
                logger.write(f"添加了排除的子目录: {relative_dir}\n")
            root.update_idletasks()  # 强制刷新界面

    def add_extension(frame, extension, init=False):
        """
        添加新的文件扩展名并以标签形式展示。
        """
        extension = extension.strip()  # 去除可能的空格

        if not extension.startswith('.'):
            extension = f'.{extension}'  # 自动补全扩展名前的点

        if not extension:
            return  # 如果扩展名为空，不执行任何操作

        if not init and extension in extensions:
            messagebox.showinfo("提示", f"扩展名 '{extension}' 已存在")
            return  # 避免重复添加相同的扩展名

        if not init:
            extensions.append(extension)
            extensions_var.set("")  # 清空输入框内容
            logger.write(f"添加了新的扩展名: {extension}\n")

        # 创建美观的标签显示
        tag_frame = ttk.Frame(frame, style='Tag.TFrame', padding=2)  # 调整padding使标签更紧凑
        tag_label = ttk.Label(tag_frame, text=extension, style='Tag.TLabel')
        tag_label.pack(side=tk.LEFT, padx=3, pady=3)
        remove_button = ttk.Button(tag_frame, text="x", style='Tag.TButton', width=1, command=lambda: remove_extension(tag_frame, extension))
        remove_button.pack(side=tk.RIGHT, padx=2, pady=2)  # 调整删除按钮的padding和位置
        tag_frame.pack(side=tk.LEFT, padx=5, pady=5)

        # 更新标签显示区域
        update_canvas()
        root.update_idletasks()  # 强制刷新界面

    def remove_extension(tag_frame, extension):
        """
        删除标签形式的文件扩展名。
        """
        if extension in extensions:
            extensions.remove(extension)
            tag_frame.destroy()
            logger.write(f"移除了扩展名: {extension}\n")
            update_canvas()
            root.update_idletasks()  # 强制刷新界面
        else:
            messagebox.showerror("错误", f"扩展名 '{extension}' 不存在")

    # 显示默认的文件扩展名
    for ext in extensions:
        add_extension(tags_frame, ext, init=True)

    # 日志显示区域
    log_display_frame = tk.Frame(root)
    log_display_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

    log_display = scrolledtext.ScrolledText(log_display_frame, wrap=tk.WORD)
    log_display.pack(fill="both", expand=True)

    logger = ConsoleLogger(log_display)  # 使用正确的小部件

    def on_package_button_click():
        updated_project_path = project_path_entry.get().strip()
        valid_extensions = [ext.strip() for ext in extensions]
        exclude_dirs = [d.strip() for d in exclude_dirs_entry.get().split(";")]

        if not updated_project_path:
            messagebox.showerror("错误", "项目路径不能为空")
            return

        # 检查每个排除目录是否有效
        valid_exclude_dirs = []
        try:
            for sub_dir in exclude_dirs:
                validate_exclude_dir(sub_dir, updated_project_path)
                valid_exclude_dirs += [sub_dir]
        except InvalidSubdirectoryException as e:
            messagebox.showerror("错误", str(e))
            return  # 如果有任何一个目录无效，停止打包操作

        logger.clear()
        logger.write("开始打包...\n")

        result_queue = queue.Queue()

        # 启动一个新线程来执行打包过程
        threading.Thread(target=run_packaging, args=(updated_project_path, valid_extensions, valid_exclude_dirs, result_queue)).start()

        def check_result():
            try:
                # 检查队列是否有消息
                result_message, output_path = result_queue.get_nowait()
                logger.write(result_message + "\n")
                if output_path:
                    # 弹出确认对话框
                    confirmation_dialog = tk.Toplevel(root)
                    confirmation_dialog.title("打包完成")
                    tk.Label(confirmation_dialog, text=f"打包完成，压缩包创建在: {output_path}").pack(padx=20, pady=20)

                    def on_open():
                        open_directory(os.path.dirname(output_path))
                        confirmation_dialog.destroy()

                    def on_cancel():
                        confirmation_dialog.destroy()

                    button_frame = tk.Frame(confirmation_dialog)
                    button_frame.pack(pady=10)

                    tk.Button(button_frame, text="打开", command=on_open).pack(side=tk.LEFT, padx=10)
                    tk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT, padx=10)

            except queue.Empty:
                # 如果队列为空，100ms 后重试
                root.after(100, check_result)

        # 开始检查结果
        root.after(100, check_result)

    # 打包按钮
    tk.Button(root, text="打包", command=on_package_button_click).grid(row=5, column=0, padx=10, pady=20, sticky="w")

    # 清除日志按钮
    tk.Button(root, text="清除日志", command=lambda: logger.clear()).grid(row=5, column=1, padx=10, pady=20, sticky="w")

    # 退出按钮
    tk.Button(root, text="退出程序", command=root.quit).grid(row=5, column=2, padx=10, pady=20, sticky="e")

    # 使输入框和日志框在窗口调整大小时扩展
    root.columnconfigure(1, weight=1)  # 使中间列（输入框列）可以调整宽度
    root.rowconfigure(4, weight=1)  # 使日志输出框可以调整高度

    log_display_frame.columnconfigure(0, weight=1)  # 使日志输出框可以调整宽度
    log_display_frame.rowconfigure(1, weight=1)  # 使日志输出框可以调整高度

    # 将窗口居中显示
    center_window(root)

    root.mainloop()

