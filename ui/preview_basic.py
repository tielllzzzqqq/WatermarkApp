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
    """预览区域 + 基础水印设置（文本与透明度）。

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

        # 基础设置（文本与透明度）
        self.basic_settings = QWidget()
        bs_layout = QVBoxLayout(self.basic_settings)

        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("水印文本:"))
        text_input = QLineEdit(host.watermark_text)
        text_input.textChanged.connect(host.on_watermark_text_changed)
        text_layout.addWidget(text_input)
        bs_layout.addLayout(text_layout)

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
        host.text_input = text_input
        host.opacity_slider = opacity_slider
        host.opacity_value_label = opacity_value_label