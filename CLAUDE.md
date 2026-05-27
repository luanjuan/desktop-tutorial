# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 构建

```bash
# 编译为单文件 exe（无控制台窗口）
pyinstaller --onefile --noconsole memory_monitor.py
# 输出: dist/memory_monitor.exe
```

如果旧 exe 被占用导致编译失败，先手动删除 `dist/memory_monitor.exe`。

## 项目结构

- `memory_monitor.py` — 唯一源码文件，含 `MemoryWidget`（主窗口）和 `SettingsWindow`（设置弹窗）
- `dist/memory_monitor.exe` — 编译后的可执行文件
- `build/`、`memory_monitor.spec` — PyInstaller 产物

## 架构要点

**窗口系统**：`overrideredirect(True)` 无边框窗口，用 `transparentcolor` 实现全透明背景，文字和图标直接浮在桌面上。

**渲染**：所有 UI 元素（图标、文字）通过 tkinter Canvas 绘制，不依赖 tkinter 原生组件（Button/Label）。

**事件处理**：统一的事件分发机制——所有可见元素（`close`、`settings`、`drag` 三个 tag）绑定相同的 mousedown/mousemotion/mouseup 处理函数，通过 3px 移动阈值区分"点击"和"拖拽"。

**开机自启动**：通过 Windows 注册表 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 实现。

## 依赖

- `psutil` — 获取系统内存信息
- `pyinstaller` — 打包 exe（仅构建时需要）
