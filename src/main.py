# main.py
from PyQt5.QtWidgets import QApplication
from gui.gui_core import SourceCodePackerGUI
from gui.gui_pro_info import ProjectInfoWidget
from di_container import DIContainer

def create_gui():
    di_container = DIContainer()
    di_container.register("gui_core", SourceCodePackerGUI, singleton=True)
    di_container.register("project_info_widget", ProjectInfoWidget, singleton=True)


    app = QApplication([])
    window = di_container.resolve("gui_core")

    project_info_widget = di_container.resolve("project_info_widget")
    project_info_widget.create_widgets()

    window.create_widgets()
    window.show()
    app.exec_()


if __name__ == "__main__":
    create_gui()
