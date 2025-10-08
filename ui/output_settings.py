try:
    from PyQt5.QtWidgets import (
        QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
        QSlider, QSpinBox, QRadioButton, QLineEdit
    )
    from PyQt5.QtCore import Qt
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
        QSlider, QSpinBox, QRadioButton, QLineEdit
    )
    from PySide6.QtCore import Qt


class OutputSettingsUI:
    """输出与缩放设置子组件。

    - 复刻宿主的输出格式、JPEG质量与导出缩放（模式/宽/高/百分比）以及命名规则与前后缀输入。
    - 构造后将关键控件引用回填宿主以保持既有逻辑兼容：
      format_combo, jpeg_quality_container, jpeg_quality_slider, jpeg_quality_value_label,
      resize_container, resize_mode_combo, resize_width_row, resize_height_row, resize_percent_row,
      resize_width_spin, resize_height_spin, resize_percent_spin,
      naming_prefix_radio, naming_suffix_radio, naming_original_radio,
      prefix_input, suffix_input。
    """

    def __init__(self, host):
        self.group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(self.group)

        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        format_combo = QComboBox()
        format_combo.addItems(["PNG", "JPEG"])
        format_combo.currentTextChanged.connect(host.on_format_changed)
        format_layout.addWidget(format_combo)
        output_layout.addLayout(format_layout)

        # JPEG 质量设置（仅在选择 JPEG 时显示）
        jpeg_quality_container = QWidget()
        jq_layout = QHBoxLayout(jpeg_quality_container)
        jq_layout.addWidget(QLabel("JPEG质量:"))
        jpeg_quality_slider = QSlider(Qt.Horizontal)
        jpeg_quality_slider.setRange(0, 100)
        jpeg_quality_slider.setValue(int(getattr(host, "jpeg_quality", 85)))
        jpeg_quality_slider.valueChanged.connect(host.on_jpeg_quality_changed)
        jpeg_quality_value_label = QLabel(f"{int(getattr(host, 'jpeg_quality', 85))}")
        jq_layout.addWidget(jpeg_quality_slider)
        jq_layout.addWidget(jpeg_quality_value_label)
        output_layout.addWidget(jpeg_quality_container)
        # 初始显隐
        fmt = str(getattr(host, "output_format", "png")).lower()
        jpeg_quality_container.setVisible(fmt == "jpeg")

        # 导出缩放设置
        resize_container = QGroupBox("导出缩放")
        resize_v = QVBoxLayout(resize_container)
        # 模式选择
        resize_mode_layout = QHBoxLayout()
        resize_mode_layout.addWidget(QLabel("缩放模式:"))
        resize_mode_combo = QComboBox()
        resize_mode_combo.addItems(["不缩放", "按宽度", "按高度", "按百分比"])
        resize_mode_combo.currentTextChanged.connect(host.on_resize_mode_changed)
        resize_mode_layout.addWidget(resize_mode_combo)
        resize_v.addLayout(resize_mode_layout)
        # 宽度输入
        resize_width_row = QWidget()
        rw_layout = QHBoxLayout(resize_width_row)
        rw_layout.addWidget(QLabel("目标宽度:"))
        resize_width_spin = QSpinBox()
        resize_width_spin.setRange(1, 10000)
        resize_width_spin.setValue(int(getattr(host, "resize_width", 1920)))
        resize_width_spin.valueChanged.connect(host.on_resize_width_changed)
        rw_layout.addWidget(resize_width_spin)
        resize_v.addWidget(resize_width_row)
        # 高度输入
        resize_height_row = QWidget()
        rh_layout = QHBoxLayout(resize_height_row)
        rh_layout.addWidget(QLabel("目标高度:"))
        resize_height_spin = QSpinBox()
        resize_height_spin.setRange(1, 10000)
        resize_height_spin.setValue(int(getattr(host, "resize_height", 1080)))
        resize_height_spin.valueChanged.connect(host.on_resize_height_changed)
        rh_layout.addWidget(resize_height_spin)
        resize_v.addWidget(resize_height_row)
        # 百分比输入
        resize_percent_row = QWidget()
        rp_layout = QHBoxLayout(resize_percent_row)
        rp_layout.addWidget(QLabel("缩放百分比:"))
        resize_percent_spin = QSpinBox()
        resize_percent_spin.setRange(1, 500)
        resize_percent_spin.setSuffix(" %")
        resize_percent_spin.setValue(int(getattr(host, "resize_percent", 100)))
        resize_percent_spin.valueChanged.connect(host.on_resize_percent_changed)
        rp_layout.addWidget(resize_percent_spin)
        resize_v.addWidget(resize_percent_row)
        output_layout.addWidget(resize_container)
        # 初始显隐
        if hasattr(host, "_update_resize_rows_visibility"):
            host.resize_mode_combo = resize_mode_combo
            host.resize_width_row = resize_width_row
            host.resize_height_row = resize_height_row
            host.resize_percent_row = resize_percent_row
            host._update_resize_rows_visibility()

        # 命名规则
        naming_layout = QVBoxLayout()
        naming_layout.addWidget(QLabel("命名规则:"))
        naming_prefix_radio = QRadioButton("添加前缀")
        naming_prefix_radio.setChecked(getattr(host, "output_naming", "prefix") == "prefix")
        naming_prefix_radio.toggled.connect(lambda: host.on_naming_rule_changed("prefix"))

        naming_suffix_radio = QRadioButton("添加后缀")
        naming_suffix_radio.setChecked(getattr(host, "output_naming", "prefix") == "suffix")
        naming_suffix_radio.toggled.connect(lambda: host.on_naming_rule_changed("suffix"))

        naming_original_radio = QRadioButton("保留原文件名")
        naming_original_radio.setChecked(getattr(host, "output_naming", "prefix") == "original")
        naming_original_radio.toggled.connect(lambda: host.on_naming_rule_changed("original"))

        naming_layout.addWidget(naming_prefix_radio)
        naming_layout.addWidget(naming_suffix_radio)
        naming_layout.addWidget(naming_original_radio)
        # 前缀/后缀输入
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("前缀:"))
        prefix_input = QLineEdit(str(getattr(host, "output_prefix", "")))
        prefix_input.textChanged.connect(host.on_prefix_changed)
        prefix_layout.addWidget(prefix_input)

        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("后缀:"))
        suffix_input = QLineEdit(str(getattr(host, "output_suffix", "")))
        suffix_input.textChanged.connect(host.on_suffix_changed)
        suffix_layout.addWidget(suffix_input)
        naming_layout.addLayout(prefix_layout)
        naming_layout.addLayout(suffix_layout)
        output_layout.addLayout(naming_layout)

        # 回填控件引用到宿主
        host.format_combo = format_combo
        host.jpeg_quality_container = jpeg_quality_container
        host.jpeg_quality_slider = jpeg_quality_slider
        host.jpeg_quality_value_label = jpeg_quality_value_label
        host.resize_container = resize_container
        host.resize_mode_combo = resize_mode_combo
        host.resize_width_row = resize_width_row
        host.resize_height_row = resize_height_row
        host.resize_percent_row = resize_percent_row
        host.resize_width_spin = resize_width_spin
        host.resize_height_spin = resize_height_spin
        host.resize_percent_spin = resize_percent_spin
        host.naming_prefix_radio = naming_prefix_radio
        host.naming_suffix_radio = naming_suffix_radio
        host.naming_original_radio = naming_original_radio
        host.prefix_input = prefix_input
        host.suffix_input = suffix_input