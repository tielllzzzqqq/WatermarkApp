try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QGroupBox, QSizePolicy
    )
    from PyQt5.QtCore import Qt
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSlider, QGroupBox, QSizePolicy
    )
    from PySide6.QtCore import Qt


class PreviewBasicUI:
    """预览区域 + 基础水印设置（文本/图片水印与透明度）。

    - 仅依赖宿主的事件与属性：
      host._preview_mouse_press_event, host._preview_mouse_move_event,
      host._drag_enter_event, host._drop_event,
      host.on_watermark_text_changed, host.on_opacity_changed,
      host.watermark_text, host.watermark_opacity。
    - 构造后会将关键控件引用回填到宿主：
      host.preview_label, host.text_input, host.opacity_slider, host.opacity_value_label。
    """

    def __init__(self, host):
        # 预览区域
        self.preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(self.preview_group)
        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignCenter)
        preview_label.setMinimumSize(400, 300)
        preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        preview_label.setMouseTracking(True)
        preview_label.mousePressEvent = host._preview_mouse_press_event
        preview_label.mouseMoveEvent = host._preview_mouse_move_event
        preview_label.setAcceptDrops(True)
        preview_label.dragEnterEvent = host._drag_enter_event
        preview_label.dropEvent = host._drop_event
        preview_layout.addWidget(preview_label)
        host.preview_label = preview_label

        # 基础设置（文本/图片水印与透明度）
        self.basic_settings = QWidget()
        bs_layout = QVBoxLayout(self.basic_settings)

        # 水印类型选择
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("水印类型:"))
        try:
            from PyQt5.QtWidgets import QComboBox, QPushButton, QSpinBox, QCheckBox
        except Exception:
            from PySide6.QtWidgets import QComboBox, QPushButton, QSpinBox, QCheckBox
        type_combo = QComboBox()
        type_combo.addItem("文本水印", userData="text")
        type_combo.addItem("图片水印", userData="image")
        # 初始化当前类型
        current_type = getattr(host, "watermark_type", "text")
        type_combo.setCurrentIndex(0 if current_type == "text" else 1)
        type_combo.currentIndexChanged.connect(host.on_watermark_type_changed)
        type_row.addWidget(type_combo)
        bs_layout.addLayout(type_row)

        text_row = QWidget()
        text_layout = QHBoxLayout(text_row)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.addWidget(QLabel("水印文本:"))
        text_input = QLineEdit(host.watermark_text)
        text_input.textChanged.connect(host.on_watermark_text_changed)
        text_layout.addWidget(text_input)
        bs_layout.addWidget(text_row)

        # 图片水印选择
        image_row = QWidget()
        image_row_layout = QHBoxLayout(image_row)
        image_row_layout.setContentsMargins(0, 0, 0, 0)
        image_row_layout.addWidget(QLabel("图片水印:"))
        image_path_edit = QLineEdit(str(getattr(host, "image_watermark_path", "") or ""))
        image_path_edit.setPlaceholderText("选择本地图片（支持 PNG 透明）")
        image_path_edit.textChanged.connect(host.on_image_watermark_path_changed)
        image_row_layout.addWidget(image_path_edit)
        pick_btn = QPushButton("选择图片...")
        pick_btn.clicked.connect(host.on_select_image_watermark)
        image_row_layout.addWidget(pick_btn)
        bs_layout.addWidget(image_row)

        # 图片缩放设置
        scale_row = QWidget()
        scale_layout = QHBoxLayout(scale_row)
        scale_layout.setContentsMargins(0, 0, 0, 0)
        scale_layout.addWidget(QLabel("缩放方式:"))
        scale_mode_combo = QComboBox()
        scale_mode_combo.addItem("按比例", userData="percent")
        scale_mode_combo.addItem("自由调整", userData="free")
        init_mode = getattr(host, "image_scale_mode", "percent")
        scale_mode_combo.setCurrentIndex(0 if init_mode == "percent" else 1)
        scale_mode_combo.currentIndexChanged.connect(host.on_image_scale_mode_changed)
        scale_layout.addWidget(scale_mode_combo)

        # 按比例：百分比
        percent_row = QWidget()
        pr_layout = QHBoxLayout(percent_row)
        pr_layout.setContentsMargins(0, 0, 0, 0)
        pr_layout.addWidget(QLabel("比例%:"))
        percent_spin = QSpinBox()
        percent_spin.setRange(1, 400)
        percent_spin.setValue(int(getattr(host, "image_scale_percent", 50)))
        percent_spin.valueChanged.connect(host.on_image_scale_percent_changed)
        pr_layout.addWidget(percent_spin)
        scale_layout.addWidget(percent_row)

        # 自由调整：宽/高与保持比例
        free_row = QWidget()
        fr_layout = QHBoxLayout(free_row)
        fr_layout.setContentsMargins(0, 0, 0, 0)
        fr_layout.addWidget(QLabel("宽:"))
        width_spin = QSpinBox()
        width_spin.setRange(1, 4096)
        width_spin.setValue(int(getattr(host, "image_scale_width", 200)))
        width_spin.valueChanged.connect(host.on_image_scale_width_changed)
        fr_layout.addWidget(width_spin)
        fr_layout.addWidget(QLabel("高:"))
        height_spin = QSpinBox()
        height_spin.setRange(1, 4096)
        height_spin.setValue(int(getattr(host, "image_scale_height", 200)))
        height_spin.valueChanged.connect(host.on_image_scale_height_changed)
        fr_layout.addWidget(height_spin)
        keep_check = QCheckBox("保持比例")
        keep_check.setChecked(bool(getattr(host, "image_keep_aspect", True)))
        keep_check.stateChanged.connect(host.on_image_keep_aspect_changed)
        fr_layout.addWidget(keep_check)
        scale_layout.addWidget(free_row)
        bs_layout.addWidget(scale_row)

        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        opacity_slider = QSlider(Qt.Horizontal)
        opacity_slider.setRange(0, 100)
        opacity_slider.setValue(host.watermark_opacity)
        opacity_slider.valueChanged.connect(host.on_opacity_changed)
        opacity_value_label = QLabel(f"{host.watermark_opacity}%")
        opacity_layout.addWidget(opacity_slider)
        opacity_layout.addWidget(opacity_value_label)
        bs_layout.addLayout(opacity_layout)

        # 引用回填
        host.watermark_type_combo = type_combo
        host.text_row = text_row
        host.text_input = text_input
        host.image_row = image_row
        host.image_path_edit = image_path_edit
        host.image_pick_btn = pick_btn
        host.scale_row = scale_row
        host.scale_mode_combo = scale_mode_combo
        host.percent_row = percent_row
        host.percent_spin = percent_spin
        host.free_row = free_row
        host.width_spin = width_spin
        host.height_spin = height_spin
        host.keep_aspect_check = keep_check
        host.opacity_slider = opacity_slider
        host.opacity_value_label = opacity_value_label

        # 初始行可见性
        _is_image = (current_type == "image")
        host.text_row.setVisible(not _is_image)
        image_row.setVisible(_is_image)
        scale_row.setVisible(_is_image)
        percent_row.setVisible(init_mode == "percent")
        free_row.setVisible(init_mode == "free")