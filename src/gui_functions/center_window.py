import tkinter as tk

def center_window(window):
    """
    将窗口居中显示在屏幕上。
    """
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()
    
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)
    
    window.geometry(f"+{position_right}+{position_down}")


