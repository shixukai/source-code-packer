# create_gui.py

import tkinter as tk
from .gui_core import SourceCodePackerGUI

def create_gui():
    root = tk.Tk()
    app = SourceCodePackerGUI(root)
    root.mainloop()
