from PyQt5.QtWidgets import QApplication
from gui.gui_core import SourceCodePackerGUI


def create_gui():
    app = QApplication([])
    window = SourceCodePackerGUI()
    window.show()
    app.exec_()


if __name__ == "__main__":
    create_gui()
