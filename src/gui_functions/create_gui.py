# create_gui.py

from PyQt5.QtWidgets import QApplication
from .gui_core import SourceCodePackerGUI

def create_gui():
    app = QApplication([])
    window = SourceCodePackerGUI()
    window.show()
    app.exec_()
