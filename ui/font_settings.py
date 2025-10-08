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

        # 描边宽度
        layout.addWidget(QLabel("描边宽度:"), 4, 0)
        stroke_width_spin = QSpinBox()
        stroke_width_spin.setRange(0, 10)
        stroke_width_spin.setValue(int(getattr(host, "font_stroke_width", 0)))
        stroke_width_spin.valueChanged.connect(host.on_font_stroke_width_changed)
        layout.addWidget(stroke_width_spin, 4, 1)

        # 描边颜色
        layout.addWidget(QLabel("描边颜色:"), 5, 0)
        stroke_color_row = QWidget()
        stroke_color_layout = QHBoxLayout(stroke_color_row)
        stroke_color_layout.setContentsMargins(0, 0, 0, 0)

        stroke_preview_btn = QPushButton()
        stroke_preview_btn.setFixedSize(32, 20)
        def _hex_to_css2(hex_str: str) -> str:
            h = (hex_str or "#000000").strip()
            if len(h) == 7 and h.startswith('#'):
                return h
            return "#000000"
        current_stroke_hex = str(getattr(host, "font_stroke_color", "#000000"))
        stroke_preview_btn.setStyleSheet(f"background:{_hex_to_css2(current_stroke_hex)}; border:1px solid #888;")

        def _choose_stroke_color():
            c = QColorDialog.getColor()
            if c and c.isValid():
                hex_val = c.name()
                stroke_preview_btn.setStyleSheet(f"background:{hex_val}; border:1px solid #888;")
                host.on_font_stroke_color_changed(hex_val)
        stroke_preview_btn.clicked.connect(_choose_stroke_color)
        stroke_color_layout.addWidget(stroke_preview_btn)

        stroke_preset_colors = [
            "#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF",
            "#FFFF00", "#00FFFF", "#FF00FF", "#808080"
        ]
        stroke_swatches = []
        for hx in stroke_preset_colors:
            b = QPushButton()
            b.setFixedSize(20, 20)
            b.setStyleSheet(f"background:{hx}; border:1px solid #666;")
            b.clicked.connect(lambda _, h=hx: (stroke_preview_btn.setStyleSheet(f"background:{h}; border:1px solid #888;"), host.on_font_stroke_color_changed(h)))
            stroke_color_layout.addWidget(b)
            stroke_swatches.append(b)

        layout.addWidget(stroke_color_row, 5, 1)

        # 阴影设置
        shadow_row = QWidget()
        shadow_layout = QHBoxLayout(shadow_row)
        shadow_layout.setContentsMargins(0, 0, 0, 0)
        shadow_check = QCheckBox("启用阴影")
        shadow_check.setChecked(bool(getattr(host, "font_shadow_enabled", False)))
        shadow_check.stateChanged.connect(host.on_font_shadow_enabled_changed)
        shadow_layout.addWidget(shadow_check)

        shadow_layout.addWidget(QLabel("偏移X:"))
        shadow_x_spin = QSpinBox()
        shadow_x_spin.setRange(-20, 20)
        shadow_x_spin.setValue(int(getattr(host, "font_shadow_offset_x", 2)))
        shadow_x_spin.valueChanged.connect(host.on_font_shadow_offset_x_changed)
        shadow_layout.addWidget(shadow_x_spin)

        shadow_layout.addWidget(QLabel("偏移Y:"))
        shadow_y_spin = QSpinBox()
        shadow_y_spin.setRange(-20, 20)
        shadow_y_spin.setValue(int(getattr(host, "font_shadow_offset_y", 2)))
        shadow_y_spin.valueChanged.connect(host.on_font_shadow_offset_y_changed)
        shadow_layout.addWidget(shadow_y_spin)

        # 阴影颜色
        shadow_preview_btn = QPushButton()
        shadow_preview_btn.setFixedSize(32, 20)
        current_shadow_hex = str(getattr(host, "font_shadow_color", "#000000"))
        shadow_preview_btn.setStyleSheet(f"background:{_hex_to_css2(current_shadow_hex)}; border:1px solid #888;")
        def _choose_shadow_color():
            c = QColorDialog.getColor()
            if c and c.isValid():
                hex_val = c.name()
                shadow_preview_btn.setStyleSheet(f"background:{hex_val}; border:1px solid #888;")
                host.on_font_shadow_color_changed(hex_val)
        shadow_preview_btn.clicked.connect(_choose_shadow_color)
        shadow_layout.addWidget(QLabel("阴影颜色:"))
        shadow_layout.addWidget(shadow_preview_btn)

        layout.addWidget(QLabel("阴影:"), 6, 0)
        layout.addWidget(shadow_row, 6, 1)

        # 高清渲染（超采样）
        layout.addWidget(QLabel("高清渲染倍数:"), 7, 0)
        render_scale_spin = QSpinBox()
        render_scale_spin.setRange(1, 4)
        render_scale_spin.setValue(int(getattr(host, "render_scale", 1)))
        render_scale_spin.valueChanged.connect(host.on_render_scale_changed)
        layout.addWidget(render_scale_spin, 7, 1)

        # 引用回填
        host.font_combo = font_combo
        host.font_size_spin = font_size_spin
        host.font_bold_check = font_bold_check
        host.font_italic_check = font_italic_check
        host.font_color_preview = preview_btn
        host.font_color_swatches = swatches

        host.font_stroke_width_spin = stroke_width_spin
        host.font_stroke_color_preview = stroke_preview_btn
        host.font_stroke_color_swatches = stroke_swatches
        host.font_shadow_check = shadow_check
        host.font_shadow_x_spin = shadow_x_spin
        host.font_shadow_y_spin = shadow_y_spin
        host.font_shadow_color_preview = shadow_preview_btn
        host.render_scale_spin = render_scale_spin