from PyQt5.QtWidgets import QWidget, QMessageBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics

def add_extension(root, layout, extension, extensions, canvas, entry_var, init=False):
    """
    添加新的文件扩展名并以标签形式展示。
    """
    extension = extension.strip()  # 去除可能的空格

    if not extension:
        QMessageBox.critical(root, "错误", "扩展名不能为空或仅包含空格")
        return

    if not extension.startswith('.'):
        extension = f'.{extension}'  # 自动补全扩展名前的点

    if not init and extension in extensions:
        QMessageBox.information(root, "提示", f"扩展名 '{extension}' 已存在")
        return  # 避免重复添加相同的扩展名

    if not init:
        extensions.append(extension)

    # 创建用于标签和删除按钮的容器
    tag_widget = QFrame()
    tag_layout = QHBoxLayout(tag_widget)
    tag_layout.setContentsMargins(0, 0, 0, 0)
    tag_layout.setSpacing(0)

    # 创建标签
    label = QLabel(extension)
    label.setFixedHeight(25)
    label.setStyleSheet("""
        QLabel {
            background-color: #e0f7fa;
            color: #00796b;
            padding: 3px;
            border: 1px solid #004d40;
            border-top-left-radius: 3px;
            border-bottom-left-radius: 3px;
            font-size: 12px;
        }
    """)
    label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    # 动态计算标签宽度
    font_metrics = QFontMetrics(label.font())
    text_width = font_metrics.horizontalAdvance(extension)
    label.setFixedWidth(text_width + 15)  # 添加一些 padding

    tag_layout.addWidget(label)

    # 创建删除按钮
    delete_btn = QPushButton('✕')
    delete_btn.setFixedHeight(25)
    delete_btn.setFixedWidth(25)
    delete_btn.setStyleSheet("""
        QPushButton {
            background-color: #ffccbc;
            color: #d32f2f;
            border-top: 1px solid #b71c1c;
            border-right: 1px solid #b71c1c;
            border-bottom: 1px solid #b71c1c;
            border-top-right-radius: 3px;
            border-bottom-right-radius: 3px;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #ef9a9a;
        }
    """)
    delete_btn.clicked.connect(lambda: remove_extension(root, tag_widget, extension, extensions, canvas))
    tag_layout.addWidget(delete_btn)

    tag_widget.setLayout(tag_layout)
    tag_widget.setFixedHeight(25)
    layout.addWidget(tag_widget, 0, Qt.AlignLeft)

    # 设置固定的标签间距
    layout.setSpacing(10)

    # 更新标签显示区域
    update_canvas(root, layout, canvas)

    # 清空输入框内容
    if not init:
        entry_var.setText("")

def remove_extension(root, tag_widget, extension, extensions, canvas):
    """
    删除标签形式的文件扩展名。
    """
    if extension in extensions:
        extensions.remove(extension)
        tag_widget.deleteLater()
        update_canvas(root, tag_widget.parentWidget().layout(), canvas)
    else:
        QMessageBox.critical(root, "错误", f"扩展名 '{extension}' 不存在")

def update_canvas(root, layout, canvas):
    """
    更新标签显示区域的大小。
    """
    canvas_widget = canvas.widget()
    if canvas_widget:
        canvas_widget.updateGeometry()
    canvas.setWidgetResizable(True)
    canvas.setWidget(layout.parentWidget())
    layout.parentWidget().updateGeometry()

def initialize_extensions(root, layout, extensions, canvas, entry_var):
    """
    初始化显示默认的文件扩展名。
    """
    for ext in extensions:
        add_extension(root, layout, ext, extensions, canvas, entry_var, init=True)
