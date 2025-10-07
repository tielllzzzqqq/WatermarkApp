#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import importlib
from watermark_app import WatermarkApp

def _load_qt_modules():
    for base in ("PyQt5", "PySide6"):
        try:
            QtWidgets = importlib.import_module(f"{base}.QtWidgets")
            QtCore = importlib.import_module(f"{base}.QtCore")
            return QtWidgets, QtCore
        except Exception:
            continue
    raise ImportError("未找到 Qt 绑定，请安装 PyQt5 或 PySide6")
QtWidgets, QtCore = _load_qt_modules()
QApplication = QtWidgets.QApplication

if __name__ == "__main__":
    # 高DPI显示支持（必须在创建 QApplication 前设置）
    try:
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("WatermarkApp")
    window = WatermarkApp()
    window.show()
    # 兼容 PyQt5/PySide6 的事件循环方法，避免对 None 调用
    if hasattr(app, "exec"):
        exit_code = app.exec()
    elif hasattr(app, "exec_"):
        exit_code = app.exec_()
    else:
        raise RuntimeError("未找到 QApplication 的事件循环方法: exec/exec_")
    sys.exit(exit_code)