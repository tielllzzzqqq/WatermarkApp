try:
    from PyQt5.QtWidgets import QGroupBox, QGridLayout, QPushButton
except Exception:
    from PySide6.QtWidgets import QGroupBox, QGridLayout, QPushButton


class PositionGridUI:
    """九宫格位置选择子组件。

    - 依赖宿主的事件：host.on_position_selected（读取 sender.property("position")）。
    - 构造后提供 group 以加入父布局，并可选回填按钮列表：host.position_buttons。
    """

    def __init__(self, host):
        self.group = QGroupBox("水印位置")
        layout = QGridLayout(self.group)

        positions = [
            ("左上", "top-left"), ("顶部", "top"), ("右上", "top-right"),
            ("左侧", "left"), ("中心", "center"), ("右侧", "right"),
            ("左下", "bottom-left"), ("底部", "bottom"), ("右下", "bottom-right"),
        ]

        btns = []
        for i, (label, pos) in enumerate(positions):
            btn = QPushButton(label)
            btn.setProperty("position", pos)
            btn.clicked.connect(host.on_position_selected)
            btn.setMinimumSize(84, 32)
            layout.addWidget(btn, i // 3, i % 3)
            btns.append(btn)

        # 可选：回填按钮列表，便于后续高亮或状态更新
        host.position_buttons = btns