import os
import json
import tarfile
from pathlib import Path
import platform
import subprocess
import tempfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import queue
import sys

# 默认配置文件路径
DEFAULT_CONFIG_PATH = "config.json"

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

def read_config(config_path):
    """
    读取配置文件以获取要打包的文件后缀列表、项目路径和排除的子目录。

    :param config_path: 配置文件的路径
    :return: 文件后缀列表、项目路径和排除的子目录列表
    """
    try:
        with open(config_path, 'r') as file:
            config = json.load(file)
        project_path = config.get("project_path", "").strip()
        extensions = [ext.lower() for ext in config.get("file_extensions", [])]
        exclude_dirs = config.get("exclude_dirs", [])
        return project_path, extensions, exclude_dirs
    except Exception as e:
        messagebox.showerror("配置文件读取错误", f"读取配置文件出错: {e}")
        return "", [], []

def gather_files(project_path, extensions, exclude_dirs):
    """
    收集项目路径中符合给定后缀的所有文件，排除指定的子目录。

    :param project_path: 项目目录的路径
    :param extensions: 要包含的文件后缀列表
    :param exclude_dirs: 要排除的子目录列表
    :return: 要打包的文件路径列表
    """
    exclude_dirs_full = [os.path.join(project_path, exclude_dir) for exclude_dir in exclude_dirs]
    files_to_package = []
    for root, dirs, files in os.walk(project_path):
        # 检查并排除子目录
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs_full]
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                files_to_package.append(os.path.join(root, file))
    return files_to_package

def package_files(project_path, files, output_dir):
    """
    将收集到的文件打包成一个 .tar.gz 压缩包。

    :param project_path: 项目目录的路径
    :param files: 要包含在包中的文件路径列表
    :param output_dir: 保存输出包的目录
    :return: 创建的包的路径
    """
    project_name = os.path.basename(os.path.normpath(project_path))
    output_path = os.path.join(output_dir, f"{project_name}.tar.gz")
    with tarfile.open(output_path, "w:gz") as tar:
        for file in files:
            arcname = os.path.relpath(file, start=project_path)
            tar.add(file, arcname=arcname)
    return output_path

def print_tree(files, project_path):
    """
    以树形结构打印打包的文件结构。

    :param files: 被打包的文件路径列表
    :param project_path: 项目目录的路径
    :return: 打包文件的树形结构字符串
    """
    tree = {}
    for file in files:
        parts = Path(file).relative_to(project_path).parts
        d = tree
        for part in parts[:-1]:
            d = d.setdefault(part, {})
        d.setdefault(parts[-1], None)
    
    output = []
    def print_dict(d, prefix=''):
        """
        递归打印目录结构。

        :param d: 表示目录结构的字典
        :param prefix: 当前的前缀，用于打印竖线
        """
        pointers = ['├── '] * (len(d) - 1) + ['└── ']
        for pointer, (key, value) in zip(pointers, sorted(d.items())):
            output.append(prefix + pointer + key)
            if isinstance(value, dict):
                extension = '│   ' if pointer == '├── ' else '    '
                print_dict(value, prefix + extension)

    print_dict(tree)
    return '\n'.join(output)

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

def run_packaging(project_path, extensions, exclude_dirs, result_queue):
    """
    执行打包过程，并将结果放入队列。

    :param project_path: 项目路径
    :param extensions: 要打包的文件扩展名列表
    :param exclude_dirs: 要排除的目录列表
    :param result_queue: 用于传递打包结果的队列
    """
    try:
        files_to_package = gather_files(project_path, extensions, exclude_dirs)
        
        if not files_to_package:
            result_queue.put(("没有文件需要打包。", None))
            return
        
        output_dir = tempfile.gettempdir()  # 获取临时目录
        output_path = package_files(project_path, files_to_package, output_dir)
        
        file_tree = print_tree(files_to_package, project_path)
        result_message = f"压缩包创建在: {output_path}\n打包的文件列表:\n{file_tree}"
        
        result_queue.put((result_message, output_path))
    except Exception as e:
        result_queue.put((f"打包过程中出现错误: {e}", None))

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

    tk.Button(root, text="打包", command=on_package_button_click).grid(row=4, column=0, columnspan=3, padx=10, pady=20)

    root.columnconfigure(1, weight=1)  # 使中间列（输入框列）可以调整宽度
    root.rowconfigure(2, weight=1)  # 使日志输出框可以调整高度

    log_display_frame.columnconfigure(0, weight=1)  # 使日志输出框可以调整宽度
    log_display_frame.rowconfigure(1, weight=1)  # 使日志输出框可以调整高度

    root.mainloop()

if __name__ == "__main__":
    create_gui()
