import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import queue
import platform
import subprocess
from config import read_config, DEFAULT_CONFIG_PATH
from packager import run_packaging
from logger import ConsoleLogger

def open_directory(path):
    """
    打开指定路径的目录。

    :param path: 要打开的目录路径
    """
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def validate_exclude_dir(exclude_dir, project_path):
    """
    验证排除目录是否是有效的子目录。
    
    :param exclude_dir: 排除的目录路径
    :param project_path: 项目目录的路径
    :return: 排除目录是否有效
    """
    full_path = os.path.join(project_path, exclude_dir)
    return os.path.isdir(full_path) and full_path.startswith(project_path)

def center_window(window):
    """
    将窗口居中显示在屏幕上。

    :param window: 要居中的窗口对象
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    
    window.geometry(f"+{position_right}+{position_down}")

def create_gui():
    """
    创建和运行图形用户界面。
    """
    root = tk.Tk()
    root.title("源码打包工具")
    root.geometry("600x600")

    # 读取默认配置
    if os.path.exists(DEFAULT_CONFIG_PATH):
        project_path, extensions, exclude_dirs = read_config(DEFAULT_CONFIG_PATH)
    else:
        project_path, extensions, exclude_dirs = "", [], []

    tk.Label(root, text="项目路径:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    project_path_entry = tk.Entry(root, width=50)
    project_path_entry.insert(0, project_path)
    project_path_entry.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="浏览", command=lambda: project_path_entry.delete(0, tk.END) or project_path_entry.insert(0, filedialog.askdirectory())).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="排除的子目录:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    exclude_dirs_entry = tk.Entry(root, width=50)
    exclude_dirs_entry.insert(0, ';'.join(exclude_dirs))
    exclude_dirs_entry.grid(row=1, column=1, padx=10, pady=5)

    def on_add_exclude_dir():
        """
        添加排除目录时的处理函数。
        """
        if project_path_entry.get():
            default_path = project_path_entry.get().strip()
        else:
            default_path = "/"
        
        new_exclude_dir = filedialog.askdirectory(initialdir=default_path)
        if new_exclude_dir:
            # 校验新添加的排除目录
            if validate_exclude_dir(new_exclude_dir, default_path):
                relative_dir = os.path.relpath(new_exclude_dir, default_path)
                current_dirs = exclude_dirs_entry.get().split(';')
                if relative_dir not in current_dirs:
                    if exclude_dirs_entry.get().strip() == "":
                        exclude_dirs_entry.insert(tk.END, relative_dir)
                    else:
                        exclude_dirs_entry.insert(tk.END, ';' + relative_dir)
            else:
                messagebox.showwarning("无效目录", f"目录 {new_exclude_dir} 无效或不在项目路径内。")

    tk.Button(root, text="添加", command=on_add_exclude_dir).grid(row=1, column=2, padx=10, pady=5)

    # 创建日志显示的整体框架
    log_display_frame = tk.Frame(root)
    log_display_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

    # 日志清除按钮在日志输出框的右上方
    clear_button = tk.Button(log_display_frame, text="清除日志", command=lambda: log_text.config(state=tk.NORMAL) or log_text.delete(1.0, tk.END) or log_text.config(state=tk.DISABLED))
    clear_button.grid(row=0, column=2, padx=5, pady=5, sticky="ne")

    log_text = scrolledtext.ScrolledText(log_display_frame, width=80, height=20, state=tk.DISABLED)
    log_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

    logger = ConsoleLogger(log_text)
    sys.stdout = logger
    sys.stderr = logger

    def on_package_button_click():
        updated_project_path = project_path_entry.get().strip()
        updated_exclude_dirs = [d.strip() for d in exclude_dirs_entry.get().split(';') if d.strip()]

        if not updated_project_path or not os.path.isdir(updated_project_path):
            messagebox.showwarning("警告", "请指定有效的项目路径。")
            return

        valid_exclude_dirs = [d for d in updated_exclude_dirs if validate_exclude_dir(d, updated_project_path)]
        if len(valid_exclude_dirs) != len(updated_exclude_dirs):
            messagebox.showwarning("警告", "某些排除目录无效或不在项目路径内。请检查输入。")
            return

        # 创建一个队列来从子线程中接收结果
        result_queue = queue.Queue()

        # 启动一个新线程来执行打包过程
        threading.Thread(target=run_packaging, args=(updated_project_path, extensions, valid_exclude_dirs, result_queue)).start()

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

    tk.Button(root, text="打包", command=on_package_button_click).grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky="w")

    # 使用系统默认样式的退出按钮
    exit_button = tk.Button(root, text="退出程序", command=root.quit)
    exit_button.grid(row=4, column=2, padx=10, pady=20, sticky="e")

    root.columnconfigure(1, weight=1)  # 使中间列（输入框列）可以调整宽度
    root.rowconfigure(2, weight=1)  # 使日志输出框可以调整高度

    log_display_frame.columnconfigure(0, weight=1)  # 使日志输出框可以调整宽度
    log_display_frame.rowconfigure(1, weight=1)  # 使日志输出框可以调整高度

    # 将窗口居中显示
    center_window(root)

    root.mainloop()
