import tkinter as tk
import psutil
import winreg
import os
import sys

class MemoryWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("内存监控")
        self.root.geometry("160x100")
        self.root.configure(bg='#2d2d2d')
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.9)

        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

        btn_font = ("Segoe UI Symbol", 12)
        self.close_btn = tk.Button(self.root, text="✕", font=btn_font,
                                    fg='white', bg='#555555', activebackground='#777777',
                                    bd=0, width=2, height=1, command=self.root.quit)
        self.close_btn.place(x=5, y=5)

        self.settings_btn = tk.Button(self.root, text="⚙", font=btn_font,
                                      fg='white', bg='#555555', activebackground='#777777',
                                      bd=0, width=2, height=1, command=self.open_settings)
        self.settings_btn.place(x=130, y=5)

        self.percent_label = tk.Label(self.root, text="0%", font=("Microsoft YaHei", 26, "bold"),
                                       fg='#00ff88', bg='#2d2d2d')
        self.percent_label.place(x=0, y=35, relx=0.5, relwidth=1, anchor='center')

        self.info_label = tk.Label(self.root, text="已用 0.0GB / 共 0.0GB", font=("Microsoft YaHei", 9),
                                   fg='#666666', bg='#2d2d2d')
        self.info_label.place(x=0, y=75, relx=0.5, relwidth=1, anchor='center')

        for widget in [self.percent_label, self.info_label]:
            widget.bind("<Button-1>", self.on_drag_start)
            widget.bind("<B1-Motion>", self.on_drag_motion)

        self.root.bind("<Button-1>", self.on_drag_start)
        self.root.bind("<B1-Motion>", self.on_drag_motion)

        self.update_memory()
        self.root.mainloop()

    def on_drag_start(self, event):
        self.dragging = True
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag_motion(self, event):
        if self.dragging:
            x = self.root.winfo_x() + (event.x - self.offset_x)
            y = self.root.winfo_y() + (event.y - self.offset_y)
            self.root.geometry(f"+{x}+{y}")

    def update_memory(self):
        mem = psutil.virtual_memory()
        percent = mem.percent
        used = mem.used / (1024**3)
        total = mem.total / (1024**3)

        self.percent_label.config(text=f"{percent:.1f}%")

        if percent > 80:
            color = '#ff4444'
        elif percent > 60:
            color = '#ffaa00'
        else:
            color = '#00ff88'
        self.percent_label.config(fg=color)

        self.info_label.config(text=f"已用 {used:.1f}GB / 共 {total:.1f}GB")

        self.root.after(1000, self.update_memory)

    def open_settings(self):
        SettingsWindow(self.root)

    def get_exe_path(self):
        if getattr(sys, 'frozen', False):
            return sys.executable
        return os.path.abspath("memory_monitor.exe")

class SettingsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("设置")
        self.window.geometry("220x100")
        self.window.configure(bg='#2d2d2d')
        self.window.attributes('-topmost', True)

        tk.Label(self.window, text="设置", font=("Microsoft YaHei", 12, "bold"),
                 fg='white', bg='#2d2d2d').place(x=20, y=15)

        self.autostart_var = tk.BooleanVar(value=self.is_autostart_enabled())

        self.autostart_check = tk.Checkbutton(self.window, text="开机自启动",
                                              variable=self.autostart_var,
                                              fg='white', bg='#2d2d2d',
                                              selectcolor='#444444',
                                              command=self.toggle_autostart)
        self.autostart_check.place(x=20, y=45)

        tk.Button(self.window, text="关闭", font=("Microsoft YaHei", 10),
                  fg='#888888', bg='#2d2d2d', activebackground='#444444',
                  bd=0, command=self.window.destroy).place(x=85, y=70)

        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    def is_autostart_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "MemoryMonitor")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    def toggle_autostart(self):
        exe_path = MemoryWidget().get_exe_path()
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run",
                             0, winreg.KEY_WRITE)
        if self.autostart_var.get():
            winreg.SetValueEx(key, "MemoryMonitor", 0, winreg.REG_SZ, exe_path)
        else:
            try:
                winreg.DeleteValue(key, "MemoryMonitor")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)

if __name__ == "__main__":
    MemoryWidget()