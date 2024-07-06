# main.py
from PyQt5.QtWidgets import QApplication
from gui.gui_core import SourceCodePackerGUI
from gui.gui_proj_info import ProjectInfoWidget
from di_container import DIContainer
from gui.log_display import LogDisplay

def create_gui():
    di_container = DIContainer()
    app = QApplication([])

    di_container.register("log_display", LogDisplay, singleton=True)
    di_container.register("gui_core", SourceCodePackerGUI, singleton=True)
    di_container.register("project_info_widget", ProjectInfoWidget, singleton=True)

    window = di_container.resolve("gui_core")

    log_display = di_container.resolve("log_display")
    log_display.create_widgets()

    project_info_widget = di_container.resolve("project_info_widget")
    project_info_widget.create_widgets()


    window.create_set_layout()
    window.show()
    app.exec_()


if __name__ == "__main__":
    create_gui()
