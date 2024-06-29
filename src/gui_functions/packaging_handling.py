import threading
import queue
import os
import tkinter as tk
from tkinter import messagebox, Toplevel
from .open_directory import open_directory
from .validate_exclude_dir import validate_exclude_dir, InvalidSubdirectoryException
from packager import run_packaging
import platform

def on_package_button_click(root, project_path_entry, selected_project, exclude_dirs_entry, logger):
    """
    处理打包按钮的点击事件。
    """
    updated_project_path = project_path_entry.get().strip()
    valid_extensions = [ext.strip() for ext in selected_project["file_extensions"]]
    exclude_dirs = [d.strip() for d in exclude_dirs_entry.get().split(";")]

    if not updated_project_path:
        messagebox.showerror("错误", "项目路径不能为空")
        return

    # 检查每个排除目录是否有效
    valid_exclude_dirs = []
    try:
        for sub_dir in exclude_dirs:
            validate_exclude_dir(sub_dir, updated_project_path)
            valid_exclude_dirs.append(sub_dir)
    except InvalidSubdirectoryException as e:
        messagebox.showerror("错误", str(e))
        return  # 如果有任何一个目录无效，停止打包操作

    logger.clear()
    logger.write("开始打包...\n")

    result_queue = queue.Queue()

    # 使用传递的 selected_project 来确保使用当前选择的项目配置
    current_extensions = selected_project["file_extensions"]

    # 启动一个新线程来执行打包过程
    threading.Thread(target=run_packaging, args=(updated_project_path, current_extensions, valid_exclude_dirs, result_queue)).start()

    def check_result():
        try:
            # 检查队列是否有消息
            result_message, output_path = result_queue.get_nowait()
            logger.write(result_message + "\n")
            if output_path:
                # 弹出确认对话框
                confirmation_dialog = Toplevel(root)
                confirmation_dialog.title("打包完成")
                tk.Label(confirmation_dialog, text=f"打包完成，压缩包创建在: {output_path}").pack(padx=20, pady=20)

                def on_open():
                    open_and_select_file(output_path)
                    confirmation_dialog.destroy()

                def on_cancel():
                    confirmation_dialog.destroy()

                button_frame = tk.Frame(confirmation_dialog)
                button_frame.pack(pady=10)

                tk.Button(button_frame, text="打开", command=on_open).pack(side='left', padx=10)
                tk.Button(button_frame, text="取消", command=on_cancel).pack(side='right', padx=10)

                # 设置模式对话框
                confirmation_dialog.grab_set()
                confirmation_dialog.transient(root)  # 将对话框设置为主窗口的子窗口

                # 将提示框居中显示
                root.update_idletasks()  # 强制更新主窗口，以确保获取最新的大小
                window_width = confirmation_dialog.winfo_reqwidth()
                window_height = confirmation_dialog.winfo_reqheight()
                position_right = int(root.winfo_screenwidth()/2 - window_width/2)
                position_down = int(root.winfo_screenheight()/2 - window_height/2)
                confirmation_dialog.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

                confirmation_dialog.wait_window(confirmation_dialog)  # 等待窗口关闭

        except queue.Empty:
            # 如果队列为空，100ms 后重试
            root.after(100, check_result)

    # 开始检查结果
    root.after(100, check_result)

def open_and_select_file(file_path):
    """
    打开文件所在的目录并选中该文件
    """
    if platform.system() == "Windows":
        os.startfile(file_path)
    elif platform.system() == "Darwin":
        os.system(f"open -R '{file_path}'")
    else:
        os.system(f"xdg-open '{os.path.dirname(file_path)}'")
