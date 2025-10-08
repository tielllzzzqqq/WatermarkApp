try:
    from PyQt5.QtWidgets import (
        QWidget, QGridLayout, QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox,
        QHBoxLayout, QPushButton, QColorDialog
    )
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QGridLayout, QGroupBox, QLabel, QComboBox, QSpinBox, QCheckBox,
        QHBoxLayout, QPushButton, QColorDialog
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

        # 颜色选择（调色板 + 自定义）
        layout.addWidget(QLabel("颜色:"), 3, 0)
        color_row = QWidget()
        color_row_layout = QHBoxLayout(color_row)
        color_row_layout.setContentsMargins(0, 0, 0, 0)

        # 当前颜色预览与拾色
        preview_btn = QPushButton()
        preview_btn.setFixedSize(32, 20)
        def _hex_to_css(hex_str: str) -> str:
            h = (hex_str or "#000000").strip()
            if len(h) == 7 and h.startswith('#'):
                return h
            return "#000000"
        current_hex = str(getattr(host, "font_color", "#000000"))
        preview_btn.setStyleSheet(f"background:{_hex_to_css(current_hex)}; border:1px solid #888;")

        def _choose_color():
            c = QColorDialog.getColor()
            if c and c.isValid():
                hex_val = c.name()  # #RRGGBB
                preview_btn.setStyleSheet(f"background:{hex_val}; border:1px solid #888;")
                host.on_font_color_changed(hex_val)
        preview_btn.clicked.connect(_choose_color)
        color_row_layout.addWidget(preview_btn)

        # 预设色块
        preset_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#00FFFF", "#FF00FF", "#808080"
        ]
        swatches = []
        for hx in preset_colors:
            b = QPushButton()
            b.setFixedSize(20, 20)
            b.setStyleSheet(f"background:{hx}; border:1px solid #666;")
            b.clicked.connect(lambda _, h=hx: (preview_btn.setStyleSheet(f"background:{h}; border:1px solid #888;"), host.on_font_color_changed(h)))
            color_row_layout.addWidget(b)
            swatches.append(b)

        layout.addWidget(color_row, 3, 1)

        # 引用回填
        host.font_combo = font_combo
        host.font_size_spin = font_size_spin
        host.font_bold_check = font_bold_check
        host.font_italic_check = font_italic_check
        host.font_color_preview = preview_btn
        host.font_color_swatches = swatches