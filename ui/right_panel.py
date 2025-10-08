try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QComboBox,
        QSpinBox, QCheckBox, QGroupBox, QFormLayout, QPushButton, QRadioButton
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QComboBox,
        QSpinBox, QCheckBox, QGroupBox, QFormLayout, QPushButton, QRadioButton
    )
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPixmap


class RightPanel(QWidget):
    def __init__(self, host):
        super().__init__()
        self._host = host
        layout = QVBoxLayout(self)

        # 预览
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(280)
        self.preview_label.setStyleSheet("border:1px solid #ccc;")
        # 连接鼠标事件到宿主
        self.preview_label.mousePressEvent = host.preview_mouse_press
        self.preview_label.mouseMoveEvent = host.preview_mouse_move
        self.preview_label.mouseReleaseEvent = host.preview_mouse_release
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # 水印文本与样式
        watermark_group = QGroupBox("水印设置")
        f = QFormLayout()
        self.text_input = QLineEdit(host.watermark_text)
        self.text_input.textChanged.connect(host.on_watermark_text_changed)
        f.addRow("文本", self.text_input)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(host.opacity * 100))
        self.opacity_slider.valueChanged.connect(host.on_opacity_changed)
        f.addRow("透明度", self.opacity_slider)

        self.font_combo = QComboBox()
        self.font_combo.addItems(host._available_fonts)
        self.font_combo.setCurrentText(host.font_family)
        self.font_combo.currentTextChanged.connect(host.on_font_family_changed)
        f.addRow("字体", self.font_combo)

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 512)
        self.font_size_spin.setValue(host.font_size)
        self.font_size_spin.valueChanged.connect(host.on_font_size_changed)
        f.addRow("字号", self.font_size_spin)

        self.bold_check = QCheckBox("加粗")
        self.bold_check.setChecked(host.bold)
        self.bold_check.toggled.connect(host.on_bold_toggled)
        f.addRow(self.bold_check)

        self.italic_check = QCheckBox("斜体")
        self.italic_check.setChecked(host.italic)
        self.italic_check.toggled.connect(host.on_italic_toggled)
        f.addRow(self.italic_check)

        watermark_group.setLayout(f)
        layout.addWidget(watermark_group)

        # 位置设置
        pos_group = QGroupBox("位置")
        pf = QFormLayout()
        self.x_offset_spin = QSpinBox()
        self.x_offset_spin.setRange(-10000, 10000)
        self.x_offset_spin.setValue(host.x_offset)
        self.x_offset_spin.valueChanged.connect(host.on_x_offset_changed)
        pf.addRow("X 偏移", self.x_offset_spin)

        self.y_offset_spin = QSpinBox()
        self.y_offset_spin.setRange(-10000, 10000)
        self.y_offset_spin.setValue(host.y_offset)
        self.y_offset_spin.valueChanged.connect(host.on_y_offset_changed)
        pf.addRow("Y 偏移", self.y_offset_spin)

        self.anchor_combo = QComboBox()
        self.anchor_combo.addItems(["center", "top-left", "top-right", "bottom-left", "bottom-right"])
        self.anchor_combo.setCurrentText(host.anchor)
        self.anchor_combo.currentTextChanged.connect(host.on_anchor_changed)
        pf.addRow("锚点", self.anchor_combo)

        pos_group.setLayout(pf)
        layout.addWidget(pos_group)

        # 输出设置
        out_group = QGroupBox("输出设置")
        of = QFormLayout()

        naming_layout = QHBoxLayout()
        self.radio_original = QRadioButton("保持原名")
        self.radio_prefix = QRadioButton("加前缀")
        self.radio_suffix = QRadioButton("加后缀")
        naming_layout.addWidget(self.radio_original)
        naming_layout.addWidget(self.radio_prefix)
        naming_layout.addWidget(self.radio_suffix)
        of.addRow("命名规则", naming_layout)

        # 初始化选项
        if host.naming_rule == "original":
            self.radio_original.setChecked(True)
        elif host.naming_rule == "prefix":
            self.radio_prefix.setChecked(True)
        else:
            self.radio_suffix.setChecked(True)

        self.prefix_input = QLineEdit(host.prefix)
        self.suffix_input = QLineEdit(host.suffix)
        self.prefix_input.textChanged.connect(host.on_prefix_changed)
        self.suffix_input.textChanged.connect(host.on_suffix_changed)
        of.addRow("前缀", self.prefix_input)
        of.addRow("后缀", self.suffix_input)

        self.output_dir_line = QLineEdit(host.output_dir or "")
        self.output_dir_line.textChanged.connect(host.on_output_dir_changed)
        of.addRow("输出目录", self.output_dir_line)

        # 命名规则变更连接
        self.radio_original.toggled.connect(lambda checked: checked and host.on_naming_rule_changed("original"))
        self.radio_prefix.toggled.connect(lambda checked: checked and host.on_naming_rule_changed("prefix"))
        self.radio_suffix.toggled.connect(lambda checked: checked and host.on_naming_rule_changed("suffix"))

        out_group.setLayout(of)
        layout.addWidget(out_group)

        # 模板操作
        tpl_group = QGroupBox("模板")
        tl = QHBoxLayout()
        self.save_template_button = QPushButton("保存模板")
        self.save_template_button.clicked.connect(host.save_template)
        self.load_template_button = QPushButton("加载模板")
        self.load_template_button.clicked.connect(host.load_template_dialog)
        tl.addWidget(self.save_template_button)
        tl.addWidget(self.load_template_button)
        tpl_group.setLayout(tl)
        layout.addWidget(tpl_group)

        # 暴露给宿主以便复用
        host.preview_label = self.preview_label
        host.text_input = self.text_input
        host.opacity_slider = self.opacity_slider
        host.font_combo = self.font_combo
        host.font_size_spin = self.font_size_spin
        host.bold_check = self.bold_check
        host.italic_check = self.italic_check
        host.x_offset_spin = self.x_offset_spin
        host.y_offset_spin = self.y_offset_spin
        host.anchor_combo = self.anchor_combo
        host.radio_original = self.radio_original
        host.radio_prefix = self.radio_prefix
        host.radio_suffix = self.radio_suffix
        host.prefix_input = self.prefix_input
        host.suffix_input = self.suffix_input
        host.output_dir_line = self.output_dir_line
        host.save_template_button = self.save_template_button
        host.load_template_button = self.load_template_button