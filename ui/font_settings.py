try:
    from PyQt5.QtWidgets import (
        QWidget, QGridLayout, QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox
    )
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QGridLayout, QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox
    )


class FontSettingsUI:
    """字体设置子组件（字体选择、字号、粗体/斜体）。

    - 依赖宿主的属性与事件：
      host._available_fonts, host.font_size_user, host.font_bold, host.font_italic；
      host.on_font_selected, host.on_font_size_changed, host.on_font_bold_changed, host.on_font_italic_changed。
    - 构造后会将关键控件引用回填到宿主：
      host.font_combo, host.font_size_spin, host.font_bold_check, host.font_italic_check。
    """

    def __init__(self, host):
        self.group = QGroupBox("字体设置（可选）")
        layout = QGridLayout(self.group)

        # 字体选择
        layout.addWidget(QLabel("字体:"), 0, 0)
        font_combo = QComboBox()
        font_combo.addItem("自动选择（推荐）", userData=None)
        for name, path in getattr(host, "_available_fonts", []):
            font_combo.addItem(name, userData=path)
        font_combo.currentIndexChanged.connect(host.on_font_selected)
        layout.addWidget(font_combo, 0, 1)

        # 字号
        layout.addWidget(QLabel("字号:"), 1, 0)
        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 512)
        font_size_spin.setValue(int(getattr(host, "font_size_user", 36)))
        font_size_spin.valueChanged.connect(host.on_font_size_changed)
        layout.addWidget(font_size_spin, 1, 1)

        # 粗体 / 斜体
        font_bold_check = QCheckBox("粗体")
        font_bold_check.setChecked(bool(getattr(host, "font_bold", False)))
        font_bold_check.stateChanged.connect(host.on_font_bold_changed)
        layout.addWidget(font_bold_check, 2, 0)

        font_italic_check = QCheckBox("斜体")
        font_italic_check.setChecked(bool(getattr(host, "font_italic", False)))
        font_italic_check.stateChanged.connect(host.on_font_italic_changed)
        layout.addWidget(font_italic_check, 2, 1)

        # 引用回填
        host.font_combo = font_combo
        host.font_size_spin = font_size_spin
        host.font_bold_check = font_bold_check
        host.font_italic_check = font_italic_check