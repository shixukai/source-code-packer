# layout_initializers.py

from PyQt5.QtWidgets import QStyleFactory, QPushButton
from PyQt5.QtGui import QFontMetrics

def apply_styles():
    """
    应用自定义样式。
    """
    # PyQt5中的样式可以通过QSS进行配置
    pass  # 根据需要添加样式

def center_window(window):
    """将窗口居中"""
    screen_geometry = window.screen().geometry()
    window_geometry = window.geometry()
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2
    window.move(x, y)

def set_responsive_layout(window):
    """设置窗口和组件的自适应布局"""
    window.setStyle(QStyleFactory.create('Fusion'))  # 根据需要设置样式

def create_styled_button(text, color="default"):
    button = QPushButton(text)
    if color == "green":
        button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 1px solid #004d40;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #004d40;
                border: 1px solid #00251a;
            }
        """)
    elif color == "red":
        button.setStyleSheet("""
            QPushButton {
                color: red;
                border: 1px solid #ccc;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                color: darkred;
            }
        """)
    elif color == "blue-bg":
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: 1px solid #004d40;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #004d40;
                border: 1px solid #00251a;
            }
        """)
    elif color == "blue":
        button.setStyleSheet("""
            QPushButton {
                color: blue;
                border: 1px solid #ccc;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                color: darkred;
            }
        """)
    elif color == "red-bg":
        button.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: 1px solid #b71c1c;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
                border: 1px solid #7f0000;
            }
        """)
    else:
        button.setStyleSheet("""
            QPushButton {
                color: black;
                border: 1px solid #ccc;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:pressed {
                color: darkgray;
            }
        """)

    # 计算按钮文字的宽度
    font_metrics = QFontMetrics(button.font())
    text_width = font_metrics.horizontalAdvance(text) + 40  # 加一些内边距
    button.setFixedWidth(text_width)

    return button