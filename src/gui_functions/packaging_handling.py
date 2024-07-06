# packaging_handling.py
import threading
import queue
import os
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFontMetrics
from .open_directory import open_directory
from .validate_exclude_dir import validate_exclude_dir, InvalidSubdirectoryException
from packager import run_packaging
import platform
from di_container import DIContainer

def on_package_button_click(root, project, logger):
    """
    处理打包按钮的点击事件。
    """
    gui_core = DIContainer().resolve("gui_core")
    if not project["project_path"]:
        QMessageBox.critical(gui_core, "错误", "未选择有效的项目路径。")
        return

    updated_project_path = project.get("project_path").strip()
    valid_extensions = [ext.strip() for ext in project.get("file_extensions", [])]

    if not updated_project_path:
        QMessageBox.critical(gui_core, "错误", "项目路径不能为空")
        return

    # 检查每个排除目录是否有效
    valid_exclude_dirs = []
    try:
        for sub_dir in project.get("exclude_dirs", []):
            validate_exclude_dir(sub_dir, updated_project_path)
            valid_exclude_dirs.append(sub_dir)
    except InvalidSubdirectoryException as e:
        QMessageBox.critical(gui_core, "错误", str(e))
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
                confirmation_dialog = QDialog(gui_core)
                confirmation_dialog.setWindowTitle("打包完成")
                layout = QVBoxLayout()

                layout.addWidget(QLabel(f"打包完成，压缩包创建在: {output_path}"))

                button_frame = QFrame()
                button_layout = QHBoxLayout()
                button_frame.setLayout(button_layout)

                open_button = QPushButton("打开")
                open_button.clicked.connect(lambda: open_and_select_file(output_path))
                open_button.clicked.connect(confirmation_dialog.accept)

                cancel_button = QPushButton("取消")
                cancel_button.clicked.connect(confirmation_dialog.reject)

                # 计算按钮宽度
                font_metrics = QFontMetrics(open_button.font())
                open_button_width = font_metrics.horizontalAdvance(open_button.text()) + 50  # 添加一些内边距
                cancel_button_width = font_metrics.horizontalAdvance(cancel_button.text()) + 50  # 添加一些内边距
                open_button.setFixedWidth(open_button_width)
                cancel_button.setFixedWidth(cancel_button_width)

                button_layout.addWidget(open_button)
                button_layout.addWidget(cancel_button)

                layout.addWidget(button_frame)
                confirmation_dialog.setLayout(layout)

                # 设置对话框为模态对话框
                confirmation_dialog.setWindowModality(Qt.ApplicationModal)

                # 将提示框居中显示
                confirmation_dialog.adjustSize()
                screen_geometry = QApplication.desktop().screenGeometry()
                dialog_geometry = confirmation_dialog.geometry()
                x = (screen_geometry.width() - dialog_geometry.width()) // 2
                y = (screen_geometry.height() - dialog_geometry.height()) // 2
                confirmation_dialog.move(x, y)

                confirmation_dialog.exec_()

        except queue.Empty:
            # 如果队列为空，100ms 后重试
            QTimer.singleShot(100, check_result)

    # 开始检查结果
    QTimer.singleShot(100, check_result)


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
