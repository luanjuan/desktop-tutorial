import tkinter as tk
import psutil
import winreg
import os
import sys


class MemoryWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("内存监控")
        self.W, self.H = 160, 100
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.configure(bg='#2d2d2d')
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        # #2d2d2d = transparent → background blends into desktop
        self.root.attributes('-transparentcolor', '#2d2d2d')

        self.offset_x = 0
        self.offset_y = 0
        self._drag_activated = False

        # Canvas bg matches transparent color → background fully invisible
        self.c = tk.Canvas(self.root, width=self.W, height=self.H,
                           bg='#2d2d2d', bd=0, highlightthickness=0)
        self.c.pack()

        self._draw_close_btn()
        self._draw_settings_btn()

        # Memory display
        self.percent_text = self.c.create_text(
            self.W // 2, 44, text="0%", font=("Microsoft YaHei", 26, "bold"),
            fill='#00ff88', anchor='center', tags="drag")
        self.info_text = self.c.create_text(
            self.W // 2, 78, text="已用 0.0GB / 共 0.0GB",
            font=("Microsoft YaHei", 9), fill='#666666', anchor='center', tags="drag")

        # Unified mouse handling: everything clickable is draggable
        for tag in ("drag", "close", "settings"):
            self.c.tag_bind(tag, "<Button-1>", self.on_btn_down)
            self.c.tag_bind(tag, "<B1-Motion>", self.on_drag_motion)
        self.c.tag_bind("drag", "<ButtonRelease-1>", self.on_release)
        self.c.tag_bind("close", "<ButtonRelease-1>", self.on_release)
        self.c.tag_bind("settings", "<ButtonRelease-1>", self.on_release)

        self.update_memory()
        self.root.mainloop()

    # ── button drawing ──────────────────────────────────────────────

    def _draw_close_btn(self):
        # Top-right: X icon
        x1, y1, x2, y2 = self.W - 18, 2, self.W - 2, 18
        pad = 4
        self.c.create_line(x1 + pad, y1 + pad, x2 - pad, y2 - pad,
                           fill='#888888', width=2, tags="close")
        self.c.create_line(x2 - pad, y1 + pad, x1 + pad, y2 - pad,
                           fill='#888888', width=2, tags="close")
        self.c.tag_bind("close", "<Enter>", lambda e:
            self.c.itemconfig("close", fill='white'))
        self.c.tag_bind("close", "<Leave>", lambda e:
            self.c.itemconfig("close", fill='#888888'))

    def _draw_settings_btn(self):
        # Top-left: gear icon
        self.c.create_text(10, 10, text="⚙", font=("Segoe UI Symbol", 12),
                           fill='#888888', anchor='center', tags="settings")
        self.c.tag_bind("settings", "<Enter>", lambda e:
            self.c.itemconfig("settings", fill='white'))
        self.c.tag_bind("settings", "<Leave>", lambda e:
            self.c.itemconfig("settings", fill='#888888'))

    # ── unified mouse: drag anywhere, click buttons ────────────────

    def on_btn_down(self, event):
        self._drag_activated = False
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag_motion(self, event):
        dx = event.x - self.offset_x
        dy = event.y - self.offset_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._drag_activated = True
        if self._drag_activated:
            x = self.root.winfo_x() + dx
            y = self.root.winfo_y() + dy
            self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        if self._drag_activated:
            return
        tags = self.c.gettags("current")
        if "close" in tags:
            self.root.quit()
        elif "settings" in tags:
            self.open_settings()

    # ── data ────────────────────────────────────────────────────────

    def update_memory(self):
        mem = psutil.virtual_memory()
        pct = mem.percent
        used = mem.used / (1024 ** 3)
        total = mem.total / (1024 ** 3)

        self.c.itemconfig(self.percent_text, text=f"{pct:.1f}%")
        color = '#ff4444' if pct > 80 else '#ffaa00' if pct > 60 else '#00ff88'
        self.c.itemconfig(self.percent_text, fill=color)
        self.c.itemconfig(self.info_text, text=f"已用 {used:.1f}GB / 共 {total:.1f}GB")
        self.root.after(1000, self.update_memory)

    # ── settings window ────────────────────────────────────────────

    def open_settings(self):
        SettingsWindow(self.root)

    @staticmethod
    def get_exe_path():
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
        tk.Checkbutton(self.window, text="开机自启动",
                       variable=self.autostart_var,
                       fg='white', bg='#2d2d2d',
                       selectcolor='#444444',
                       command=self.toggle_autostart).place(x=20, y=45)

        tk.Button(self.window, text="关闭", font=("Microsoft YaHei", 10),
                  fg='#888888', bg='#2d2d2d', activebackground='#444444',
                  bd=0, command=self.window.destroy).place(x=85, y=70)

        self.window.protocol("WM_DELETE_WINDOW", self.window.destroy)

    @staticmethod
    def is_autostart_enabled():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "MemoryMonitor")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    def toggle_autostart(self):
        exe_path = MemoryWidget.get_exe_path()
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
