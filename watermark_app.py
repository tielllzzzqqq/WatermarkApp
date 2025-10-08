#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

# 直接尝试导入 PyQt5（优先）或 PySide6 的具体类，便于编辑器类型解析
try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFileDialog, QListWidget, QListWidgetItem, QSlider, QComboBox, QLineEdit, QSpinBox,
        QGroupBox, QRadioButton, QCheckBox, QMessageBox, QSplitter, QFrame,
        QGridLayout, QInputDialog, QScrollArea, QSizePolicy, QAbstractItemView
    )
    from PyQt5.QtGui import (
        QPixmap, QImage, QFont, QColor, QPainter, QDrag, QIcon
    )
    from PyQt5.QtCore import (
        Qt, QSize, QPoint, QRect, QMimeData, QByteArray
    )
    QT_LIB = "PyQt5"
except Exception:
    try:
        from PySide6.QtWidgets import (
            QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
            QFileDialog, QListWidget, QListWidgetItem, QSlider, QComboBox, QLineEdit, QSpinBox,
            QGroupBox, QRadioButton, QCheckBox, QMessageBox, QSplitter, QFrame,
            QGridLayout, QInputDialog, QScrollArea, QSizePolicy, QAbstractItemView
        )
        from PySide6.QtGui import (
            QPixmap, QImage, QFont, QColor, QPainter, QDrag, QIcon
        )
        from PySide6.QtCore import (
            Qt, QSize, QPoint, QRect, QMimeData, QByteArray
        )
        QT_LIB = "PySide6"
    except Exception as e:
        raise ImportError("未找到 Qt 绑定，请先安装依赖：pip install PyQt5 或 pip install PySide6") from e

# 直接导入 Pillow 的常用类，便于编辑器类型解析
try:
    from PIL import Image, ImageDraw, ImageFont
except Exception as e:
    raise ImportError("未找到 Pillow，请先安装：pip install Pillow") from e

# 抽离模块：字体、处理、导出、设置
from watermark.fonts import scan_system_font_files, load_font
from watermark.processing import apply_text_watermark
from watermark.exporting import resize_image_proportionally, save_image
from watermark.settings_io import read_settings, write_settings
from watermark.templates_io import add_or_update_template, list_template_names, find_template, normalize_template_fields
from watermark.media import is_supported_image, scan_directory_for_images, make_output_basename
from watermark.preview import pil_to_qimage
from ui.preview_basic import PreviewBasicUI
from ui.font_settings import FontSettingsUI

class WatermarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("水印应用")
        self.setMinimumSize(1000, 700)
        
        # 初始化变量
        self.images = []  # 存储导入的图片路径
        self.current_image_index = -1  # 当前显示的图片索引
        self.watermark_text = "水印文本"  # 默认水印文本
        self.watermark_opacity = 50  # 默认透明度 (0-100)
        self.watermark_position = "center"  # 默认位置
        self.watermark_position_custom = QPoint(0, 0)  # 自定义位置
        self.output_format = "png"  # 默认输出格式
        self.output_naming = "prefix"  # 默认命名规则
        self.output_prefix = "wm_"  # 默认前缀
        self.output_suffix = "_watermarked"  # 默认后缀
        self.templates = []  # 存储水印模板
        self._last_image_size = None  # 最近一次预览的原图尺寸 (w, h)
        self.jpeg_quality = 85  # JPEG 质量默认值 (0-100)
        # 导出缩放设置
        self.resize_mode = "none"  # none|width|height|percent
        self.resize_width = 1920
        self.resize_height = 1080
        self.resize_percent = 100
        # 文本水印字体设置（高级）
        self.font_path = None  # 选中的字体文件路径（ttf/otf/ttc）
        self.font_size_user = 36  # 用户指定字号（像素），0 表示自动
        self.font_bold = False
        self.font_italic = False
        self._available_fonts = scan_system_font_files()
        
        # 设置中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        # 启用整窗体拖放导入
        self.setAcceptDrops(True)
        
        # 创建主布局
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # 创建左侧面板
        self.create_left_panel()
        
        # 创建右侧面板
        self.create_right_panel()
        
        # 加载上次的设置
        self.load_settings()

    # ==== 拖拽导入支持 ====
    def dragEnterEvent(self, event):
        """主窗口拖入事件"""
        self._drag_enter_event(event)

    def dropEvent(self, event):
        """主窗口放下事件"""
        self._drop_event(event)
        
    def create_left_panel(self):
        """创建左侧面板（使用子组件）"""
        from ui.left_panel import LeftPanel
        self.left_panel = LeftPanel(self)
        self.left_panel.setMinimumWidth(260)
        # 引用控件到主类，保持后续逻辑可用
        self.image_list = self.left_panel.image_list
        self.import_button = self.left_panel.import_button
        self.import_folder_button = self.left_panel.import_folder_button
        self.export_button = self.left_panel.export_button
        self.export_all_button = self.left_panel.export_all_button
        self.main_layout.addWidget(self.left_panel, 1)
        
    def create_right_panel(self):
        """创建右侧面板，包含预览和水印设置"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 预览与基础设置（子组件）
        _pb = PreviewBasicUI(self)
        preview_group = _pb.preview_group
        
        # 水印设置
        settings_group = QGroupBox("水印设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 基础设置（文本与透明度）
        settings_layout.addWidget(_pb.basic_settings)
        
        # 字体设置（子组件）
        _fs = FontSettingsUI(self)
        settings_layout.addWidget(_fs.group)
        
        # 位置设置
        position_group = QGroupBox("水印位置")
        position_layout = QGridLayout(position_group)
        
        # 九宫格位置选择
        positions = [
            ("左上", "top-left"), ("顶部", "top"), ("右上", "top-right"),
            ("左侧", "left"), ("中心", "center"), ("右侧", "right"),
            ("左下", "bottom-left"), ("底部", "bottom"), ("右下", "bottom-right")
        ]
        
        for i, (label, pos) in enumerate(positions):
            btn = QPushButton(label)
            btn.setProperty("position", pos)
            btn.clicked.connect(self.on_position_selected)
            btn.setMinimumSize(84, 32)
            position_layout.addWidget(btn, i // 3, i % 3)
            
        settings_layout.addWidget(position_group)

        # 无需手动拖拽开关，拖拽默认可用
        
        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QVBoxLayout(output_group)
        
        # 输出格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("输出格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        output_layout.addLayout(format_layout)

        # JPEG 质量设置（仅在选择 JPEG 时显示）
        self.jpeg_quality_container = QWidget()
        jq_layout = QHBoxLayout(self.jpeg_quality_container)
        jq_layout.addWidget(QLabel("JPEG质量:"))
        self.jpeg_quality_slider = QSlider(Qt.Horizontal)
        self.jpeg_quality_slider.setRange(0, 100)
        self.jpeg_quality_slider.setValue(self.jpeg_quality)
        self.jpeg_quality_slider.valueChanged.connect(self.on_jpeg_quality_changed)
        self.jpeg_quality_value_label = QLabel(f"{self.jpeg_quality}")
        jq_layout.addWidget(self.jpeg_quality_slider)
        jq_layout.addWidget(self.jpeg_quality_value_label)
        output_layout.addWidget(self.jpeg_quality_container)
        # 初始显隐
        self.jpeg_quality_container.setVisible(self.output_format.lower() == "jpeg")

        # 导出缩放设置
        self.resize_container = QGroupBox("导出缩放")
        resize_v = QVBoxLayout(self.resize_container)
        # 模式选择
        resize_mode_layout = QHBoxLayout()
        resize_mode_layout.addWidget(QLabel("缩放模式:"))
        self.resize_mode_combo = QComboBox()
        self.resize_mode_combo.addItems(["不缩放", "按宽度", "按高度", "按百分比"])
        self.resize_mode_combo.currentTextChanged.connect(self.on_resize_mode_changed)
        resize_mode_layout.addWidget(self.resize_mode_combo)
        resize_v.addLayout(resize_mode_layout)
        # 宽度输入
        self.resize_width_row = QWidget()
        rw_layout = QHBoxLayout(self.resize_width_row)
        rw_layout.addWidget(QLabel("目标宽度:"))
        self.resize_width_spin = QSpinBox()
        self.resize_width_spin.setRange(1, 10000)
        self.resize_width_spin.setValue(self.resize_width)
        self.resize_width_spin.valueChanged.connect(self.on_resize_width_changed)
        rw_layout.addWidget(self.resize_width_spin)
        resize_v.addWidget(self.resize_width_row)
        # 高度输入
        self.resize_height_row = QWidget()
        rh_layout = QHBoxLayout(self.resize_height_row)
        rh_layout.addWidget(QLabel("目标高度:"))
        self.resize_height_spin = QSpinBox()
        self.resize_height_spin.setRange(1, 10000)
        self.resize_height_spin.setValue(self.resize_height)
        self.resize_height_spin.valueChanged.connect(self.on_resize_height_changed)
        rh_layout.addWidget(self.resize_height_spin)
        resize_v.addWidget(self.resize_height_row)
        # 百分比输入
        self.resize_percent_row = QWidget()
        rp_layout = QHBoxLayout(self.resize_percent_row)
        rp_layout.addWidget(QLabel("缩放百分比:"))
        self.resize_percent_spin = QSpinBox()
        self.resize_percent_spin.setRange(1, 500)
        self.resize_percent_spin.setSuffix(" %")
        self.resize_percent_spin.setValue(self.resize_percent)
        self.resize_percent_spin.valueChanged.connect(self.on_resize_percent_changed)
        rp_layout.addWidget(self.resize_percent_spin)
        resize_v.addWidget(self.resize_percent_row)
        output_layout.addWidget(self.resize_container)
        # 初始显隐
        self._update_resize_rows_visibility()
        
        # 命名规则
        naming_layout = QVBoxLayout()
        naming_layout.addWidget(QLabel("命名规则:"))
        
        self.naming_prefix_radio = QRadioButton("添加前缀")
        self.naming_prefix_radio.setChecked(self.output_naming == "prefix")
        self.naming_prefix_radio.toggled.connect(lambda: self.on_naming_rule_changed("prefix"))
        
        self.naming_suffix_radio = QRadioButton("添加后缀")
        self.naming_suffix_radio.setChecked(self.output_naming == "suffix")
        self.naming_suffix_radio.toggled.connect(lambda: self.on_naming_rule_changed("suffix"))
        
        self.naming_original_radio = QRadioButton("保留原文件名")
        self.naming_original_radio.setChecked(self.output_naming == "original")
        self.naming_original_radio.toggled.connect(lambda: self.on_naming_rule_changed("original"))
        
        naming_layout.addWidget(self.naming_prefix_radio)
        naming_layout.addWidget(self.naming_suffix_radio)
        naming_layout.addWidget(self.naming_original_radio)
        
        # 前缀/后缀输入
        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(QLabel("前缀:"))
        self.prefix_input = QLineEdit(self.output_prefix)
        self.prefix_input.textChanged.connect(self.on_prefix_changed)
        prefix_layout.addWidget(self.prefix_input)
        
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("后缀:"))
        self.suffix_input = QLineEdit(self.output_suffix)
        self.suffix_input.textChanged.connect(self.on_suffix_changed)
        suffix_layout.addWidget(self.suffix_input)
        
        naming_layout.addLayout(prefix_layout)
        naming_layout.addLayout(suffix_layout)
        output_layout.addLayout(naming_layout)
        
        settings_layout.addWidget(output_group)

        # 模板管理
        template_layout = QHBoxLayout()
        self.save_template_button = QPushButton("保存当前设置为模板")
        self.save_template_button.clicked.connect(self.save_template)
        self.load_template_button = QPushButton("加载模板")
        self.load_template_button.clicked.connect(self.show_templates)
        template_layout.addWidget(self.save_template_button)
        template_layout.addWidget(self.load_template_button)
        settings_layout.addLayout(template_layout)

        # 用滚动区域包裹预览与设置，避免窗口缩小时挤压
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.addWidget(preview_group)
        inner_layout.addWidget(settings_group)
        inner_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(inner)
        right_layout.addWidget(scroll)

        # 添加到主布局
        self.main_layout.addWidget(right_panel, 2)
        
    def import_images(self):
        """导入图片"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff)")
        
        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()
            self.add_images(file_paths)
    
    def import_folder(self):
        """导入文件夹中的所有图片"""
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        
        if folder_dialog.exec_():
            folder_path = folder_dialog.selectedFiles()[0]
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            
            file_paths = []
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        file_paths.append(os.path.join(root, file))
            
            self.add_images(file_paths)

    # 拖放事件处理（复用于主窗体/列表/预览）
    def _drag_enter_event(self, event):
        mime = event.mimeData()
        if mime.hasUrls():
            # 如果包含至少一个支持的文件/目录则接受
            urls = mime.urls()
            for url in urls:
                path = url.toLocalFile()
                if not path:
                    continue
                if os.path.isdir(path) or self._is_supported_image(path):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def _drop_event(self, event):
        mime = event.mimeData()
        paths = []
        if mime.hasUrls():
            for url in mime.urls():
                path = url.toLocalFile()
                if not path:
                    continue
                if os.path.isdir(path):
                    paths.extend(self._scan_directory_for_images(path))
                elif self._is_supported_image(path):
                    paths.append(path)
        if paths:
            self.add_images(paths)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _is_supported_image(self, path):
        return is_supported_image(path)

    def _scan_directory_for_images(self, folder_path):
        return scan_directory_for_images(folder_path)
    
    def add_images(self, file_paths):
        """添加图片到列表"""
        for path in file_paths:
            if path not in self.images:
                self.images.append(path)
                
                # 创建缩略图
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                    # 创建列表项
                    item = QListWidgetItem()
                    item.setIcon(QIcon(pixmap))
                    item.setText(os.path.basename(path))
                    item.setData(Qt.UserRole, path)
                    
                    self.image_list.addItem(item)
        
        # 如果这是第一次添加图片，选择第一张有效的图片
        if self.current_image_index == -1 and self.images:
            # 尝试找到第一张有效的图片
            for i, image_path in enumerate(self.images):
                try:
                    # 尝试打开图片验证是否有效
                    with Image.open(image_path) as test_img:
                        pass  # 如果能打开就是有效的
                    self.current_image_index = i
                    self.image_list.setCurrentRow(i)
                    self.update_preview()
                    break
                except Exception as e:
                    print(f"Skipping invalid image {image_path}: {e}")
                    continue
    
    def on_image_selected(self, item):
        """当从列表中选择图片时"""
        path = item.data(Qt.UserRole)
        try:
            self.current_image_index = self.images.index(path)
            self.update_preview()
        except ValueError:
            # 如果路径不在列表中，重置索引
            self.current_image_index = -1
            print(f"Warning: Image path not found in list: {path}")
    
    def update_preview(self):
        """更新预览图"""
        if self.current_image_index >= 0 and self.current_image_index < len(self.images):
            # 获取当前图片
            image_path = self.images[self.current_image_index]
            
            try:
                # 使用PIL添加水印
                img = Image.open(image_path)
                
                # 添加水印
                watermarked_img = self.apply_watermark(img)
                # 记录原图尺寸用于坐标映射
                self._last_image_size = (watermarked_img.width, watermarked_img.height)
                
                # 转换为QPixmap并显示
                qimg = pil_to_qimage(watermarked_img)
                pixmap = QPixmap.fromImage(qimg)
                
                # 缩放以适应预览区域
                preview_size = self.preview_label.size()
                pixmap = pixmap.scaled(preview_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.preview_label.setPixmap(pixmap)
            except Exception as e:
                # 如果图片无法打开，显示错误信息
                print(f"Error opening image {image_path}: {e}")
                self.preview_label.setText(f"无法打开图片:\n{os.path.basename(image_path)}\n错误: {str(e)}")
                self.preview_label.setAlignment(Qt.AlignCenter)
    
    def apply_watermark(self, img):
        """应用水印到图片（委托处理模块）"""
        custom_point = (self.watermark_position_custom.x(), self.watermark_position_custom.y())
        return apply_text_watermark(
            img,
            text=self.watermark_text,
            position=self.watermark_position,
            custom_point=custom_point,
            opacity_percent=int(self.watermark_opacity),
            font_path=self.font_path,
            font_size_user=int(self.font_size_user),
            font_bold=bool(self.font_bold),
            font_italic=bool(self.font_italic),
        )

    def _load_font(self, font_size):
        """包装为外部统一的字体加载器（保留兼容调用）。"""
        return load_font(font_size, self.font_path)

    def _scan_system_font_files(self):
        """包装为外部统一的字体扫描器（保留兼容调用）。"""
        return scan_system_font_files()

    # ==== 字体设置事件处理 ====
    def on_font_selected(self, idx):
        self.font_path = self.font_combo.itemData(idx)
        self.update_preview()

    def on_font_size_changed(self, val):
        self.font_size_user = int(val)
        self.update_preview()

    def on_font_bold_changed(self, state):
        self.font_bold = (state == Qt.Checked)
        self.update_preview()

    def on_font_italic_changed(self, state):
        self.font_italic = (state == Qt.Checked)
        self.update_preview()
    
    def export_images(self, all_images=False):
        """导出图片"""
        if not self.images:
            QMessageBox.warning(self, "警告", "没有图片可导出")
            return
        
        # 选择输出文件夹
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if not output_dir:
            return
        
        # 确定要导出的图片
        if all_images:
            indices = range(len(self.images))
        else:
            indices = [self.current_image_index]
        
        # 导出每张图片
        for idx in indices:
            if idx >= 0 and idx < len(self.images):
                input_path = self.images[idx]
                
                # 生成输出文件名
                filename = os.path.basename(input_path)
                output_name = make_output_basename(filename, self.output_naming, self.output_prefix, self.output_suffix)
                
                # 添加扩展名
                if self.output_format.lower() == "jpeg":
                    output_path = os.path.join(output_dir, f"{output_name}.jpg")
                else:
                    output_path = os.path.join(output_dir, f"{output_name}.png")
                
                # 打开原图并添加水印
                img = Image.open(input_path)
                watermarked_img = self.apply_watermark(img)
                # 按导出缩放设置处理
                watermarked_img = resize_image_proportionally(
                    watermarked_img,
                    mode=self.resize_mode,
                    resize_width=int(self.resize_width),
                    resize_height=int(self.resize_height),
                    resize_percent=int(self.resize_percent),
                )
                # 保存图片
                save_image(
                    watermarked_img,
                    output_format=self.output_format,
                    jpeg_quality=int(self.jpeg_quality),
                    output_path=output_path,
                )
        
        QMessageBox.information(self, "成功", "图片导出完成")
    
    def on_watermark_text_changed(self, text):
        """水印文本变更"""
        self.watermark_text = text
        self.update_preview()
    
    def on_opacity_changed(self, value):
        """透明度变更"""
        self.watermark_opacity = value
        self.opacity_value_label.setText(f"{value}%")
        self.update_preview()
    
    def on_position_selected(self):
        """位置选择"""
        sender = self.sender()
        pos = sender.property("position")
        # 九宫格选择直接覆盖当前位置
        self.watermark_position = pos
        self.update_preview()
    
    def on_format_changed(self, format_text):
        """输出格式变更"""
        self.output_format = format_text.lower()
        # 切换 JPEG 时显示质量控制
        if hasattr(self, "jpeg_quality_container"):
            self.jpeg_quality_container.setVisible(self.output_format == "jpeg")
        # 缩放行显隐保持与模式一致
        self._update_resize_rows_visibility()

    def on_jpeg_quality_changed(self, value):
        """JPEG 质量变更"""
        self.jpeg_quality = int(value)
        if hasattr(self, "jpeg_quality_value_label"):
            self.jpeg_quality_value_label.setText(f"{self.jpeg_quality}")

    def on_resize_mode_changed(self, text):
        mapping = {
            "不缩放": "none",
            "按宽度": "width",
            "按高度": "height",
            "按百分比": "percent",
        }
        self.resize_mode = mapping.get(text, "none")
        self._update_resize_rows_visibility()

    def on_resize_width_changed(self, value):
        self.resize_width = int(value)

    def on_resize_height_changed(self, value):
        self.resize_height = int(value)

    def on_resize_percent_changed(self, value):
        self.resize_percent = int(value)

    def _update_resize_rows_visibility(self):
        mode = getattr(self, "resize_mode", "none")
        if hasattr(self, "resize_width_row"):
            self.resize_width_row.setVisible(mode == "width")
        if hasattr(self, "resize_height_row"):
            self.resize_height_row.setVisible(mode == "height")
        if hasattr(self, "resize_percent_row"):
            self.resize_percent_row.setVisible(mode == "percent")
    
    def on_naming_rule_changed(self, rule):
        """命名规则变更"""
        self.output_naming = rule
    
    def on_prefix_changed(self, prefix):
        """前缀变更"""
        self.output_prefix = prefix
    
    def on_suffix_changed(self, suffix):
        """后缀变更"""
        self.output_suffix = suffix

    def _preview_mouse_press_event(self, event):
        """在预览图中按下鼠标以设置水印位置"""
        self._update_custom_position_by_event(event)

    def _preview_mouse_move_event(self, event):
        """拖拽过程中更新水印位置"""
        if event.buttons() & Qt.LeftButton:
            self._update_custom_position_by_event(event)

    def _update_custom_position_by_event(self, event):
        """根据预览坐标映射到原图坐标，设置自定义水印位置"""
        pixmap = self.preview_label.pixmap()
        if pixmap is None or self._last_image_size is None:
            return
        pm_w = pixmap.width()
        pm_h = pixmap.height()
        lab_size = self.preview_label.size()
        lab_w = lab_size.width()
        lab_h = lab_size.height()
        # 预览中的居中偏移（保持纵横比时会留边）
        offset_x = (lab_w - pm_w) // 2
        offset_y = (lab_h - pm_h) // 2
        x_in_pm = event.x() - offset_x
        y_in_pm = event.y() - offset_y
        if x_in_pm < 0 or y_in_pm < 0 or x_in_pm > pm_w or y_in_pm > pm_h:
            return
        img_w, img_h = self._last_image_size
        # 等比缩放（与预览缩放一致），统一比例
        scale_x = pm_w / float(img_w) if img_w else 1.0
        scale_y = pm_h / float(img_h) if img_h else 1.0
        # 正常情况下两者相等；取 scale_x 使用
        scale = scale_x
        img_x = int(x_in_pm / scale)
        img_y = int(y_in_pm / scale)

        # 以文本中心对齐更自然：需要计算文本尺寸
        auto_size = int(min(img_w, img_h) / 15) if min(img_w, img_h) > 0 else 20
        font_size = int(self.font_size_user) if int(self.font_size_user) > 0 else auto_size
        font = load_font(font_size, self.font_path)
        # 创建一个临时画布以计算文本边界
        temp_img = Image.new('RGBA', (img_w, img_h), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        left, top, right, bottom = temp_draw.textbbox((0, 0), self.watermark_text, font=font)
        text_w = max(0, right - left)
        text_h = max(0, bottom - top)
        pos_x = img_x - (text_w // 2)
        pos_y = img_y - (text_h // 2)
        # 边界约束，避免跑出图外
        pos_x = max(0, min(img_w - text_w, pos_x))
        pos_y = max(0, min(img_h - text_h, pos_y))
        # 设置自定义位置（文本左上角）
        self.watermark_position_custom = QPoint(pos_x, pos_y)
        self.watermark_position = "custom"
        self.update_preview()
    def save_template(self):
        """保存当前设置为模板"""
        template_name, ok = QInputDialog.getText(self, "保存模板", "输入模板名称:")
        if ok and template_name:
            template = {
                "name": template_name,
                "text": self.watermark_text,
                "opacity": self.watermark_opacity,
                "position": self.watermark_position,
                "format": self.output_format,
                "naming": self.output_naming,
                "prefix": self.output_prefix,
                "suffix": self.output_suffix,
                "jpeg_quality": self.jpeg_quality
                ,"resize_mode": self.resize_mode,
                "resize_width": self.resize_width,
                "resize_height": self.resize_height,
                "resize_percent": self.resize_percent,
                "font_path": self.font_path,
                "font_size": self.font_size_user,
                "font_bold": self.font_bold,
                "font_italic": self.font_italic
            }
            
            self.templates = add_or_update_template(self.templates, template)
            self.save_settings()
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已保存")
    
    def show_templates(self):
        """显示模板列表"""
        if not self.templates:
            QMessageBox.information(self, "提示", "没有保存的模板")
            return
        
        template_names = list_template_names(self.templates)
        template_name, ok = QInputDialog.getItem(self, "加载模板", "选择模板:", template_names, 0, False)
        
        if ok and template_name:
            tpl = find_template(self.templates, template_name)
            if tpl:
                self.load_template(tpl)
    
    def load_template(self, template):
        """加载模板"""
        tpl = normalize_template_fields(template)
        self.watermark_text = tpl["text"]
        self.watermark_opacity = tpl["opacity"]
        self.watermark_position = tpl["position"]
        self.output_format = tpl["format"]
        self.output_naming = tpl["naming"]
        self.output_prefix = tpl["prefix"]
        self.output_suffix = tpl["suffix"]
        self.jpeg_quality = tpl.get("jpeg_quality", self.jpeg_quality)
        self.resize_mode = tpl.get("resize_mode", self.resize_mode)
        self.resize_width = tpl.get("resize_width", self.resize_width)
        self.resize_height = tpl.get("resize_height", self.resize_height)
        self.resize_percent = tpl.get("resize_percent", self.resize_percent)
        self.font_path = tpl.get("font_path", self.font_path)
        self.font_size_user = int(tpl.get("font_size", self.font_size_user))
        self.font_bold = bool(tpl.get("font_bold", self.font_bold))
        self.font_italic = bool(tpl.get("font_italic", self.font_italic))
        
        # 更新UI
        self.text_input.setText(self.watermark_text)
        self.opacity_slider.setValue(self.watermark_opacity)
        
        if self.output_format.lower() == "jpeg":
            self.format_combo.setCurrentIndex(1)
        else:
            self.format_combo.setCurrentIndex(0)
        # 更新 JPEG 质量 UI
        if hasattr(self, "jpeg_quality_slider"):
            self.jpeg_quality_slider.setValue(int(self.jpeg_quality))
            self.jpeg_quality_value_label.setText(f"{int(self.jpeg_quality)}")
        # 更新字体 UI
        if hasattr(self, "font_combo"):
            if self.font_path:
                idx = self.font_combo.findData(self.font_path)
                if idx >= 0:
                    self.font_combo.setCurrentIndex(idx)
            else:
                self.font_combo.setCurrentIndex(0)
        if hasattr(self, "font_size_spin"):
            self.font_size_spin.setValue(int(self.font_size_user))
        if hasattr(self, "font_bold_check"):
            self.font_bold_check.setChecked(bool(self.font_bold))
        if hasattr(self, "font_italic_check"):
            self.font_italic_check.setChecked(bool(self.font_italic))
        # 更新缩放 UI
        if hasattr(self, "resize_mode_combo"):
            reverse_map = {
                "none": "不缩放",
                "width": "按宽度",
                "height": "按高度",
                "percent": "按百分比",
            }
            text = reverse_map.get(self.resize_mode, "不缩放")
            idx = self.resize_mode_combo.findText(text)
            if idx >= 0:
                self.resize_mode_combo.setCurrentIndex(idx)
        if hasattr(self, "resize_width_spin"):
            self.resize_width_spin.setValue(int(self.resize_width))
        if hasattr(self, "resize_height_spin"):
            self.resize_height_spin.setValue(int(self.resize_height))
        if hasattr(self, "resize_percent_spin"):
            self.resize_percent_spin.setValue(int(self.resize_percent))
        self._update_resize_rows_visibility()
        
        if self.output_naming == "prefix":
            self.naming_prefix_radio.setChecked(True)
        elif self.output_naming == "suffix":
            self.naming_suffix_radio.setChecked(True)
        else:
            self.naming_original_radio.setChecked(True)
        
        self.prefix_input.setText(self.output_prefix)
        self.suffix_input.setText(self.output_suffix)
        
        self.update_preview()
    
    def save_settings(self):
        """保存设置到文件"""
        settings = {
            "watermark_text": self.watermark_text,
            "watermark_opacity": self.watermark_opacity,
            "watermark_position": self.watermark_position,
            "output_format": self.output_format,
            "output_naming": self.output_naming,
            "output_prefix": self.output_prefix,
            "output_suffix": self.output_suffix,
            "jpeg_quality": self.jpeg_quality,
            "resize_mode": self.resize_mode,
            "resize_width": self.resize_width,
            "resize_height": self.resize_height,
            "resize_percent": self.resize_percent,
            "font_path": self.font_path,
            "font_size": self.font_size_user,
            "font_bold": self.font_bold,
            "font_italic": self.font_italic,
            "templates": self.templates
        }
        
        try:
            write_settings(settings)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def load_settings(self):
        """加载设置"""
        try:
            settings = read_settings()
            if settings:
                self.watermark_text = settings.get("watermark_text", self.watermark_text)
                self.watermark_opacity = settings.get("watermark_opacity", self.watermark_opacity)
                self.watermark_position = settings.get("watermark_position", self.watermark_position)
                self.output_format = settings.get("output_format", self.output_format)
                self.output_naming = settings.get("output_naming", self.output_naming)
                self.output_prefix = settings.get("output_prefix", self.output_prefix)
                self.output_suffix = settings.get("output_suffix", self.output_suffix)
                self.templates = settings.get("templates", [])
                self.jpeg_quality = settings.get("jpeg_quality", self.jpeg_quality)
                self.resize_mode = settings.get("resize_mode", self.resize_mode)
                self.resize_width = settings.get("resize_width", self.resize_width)
                self.resize_height = settings.get("resize_height", self.resize_height)
                self.resize_percent = settings.get("resize_percent", self.resize_percent)
                self.font_path = settings.get("font_path", self.font_path)
                self.font_size_user = int(settings.get("font_size", self.font_size_user))
                self.font_bold = bool(settings.get("font_bold", self.font_bold))
                self.font_italic = bool(settings.get("font_italic", self.font_italic))
                
                # 更新UI
                self.text_input.setText(self.watermark_text)
                self.opacity_slider.setValue(self.watermark_opacity)
                
                if self.output_format.lower() == "jpeg":
                    self.format_combo.setCurrentIndex(1)
                else:
                    self.format_combo.setCurrentIndex(0)
                
                if self.output_naming == "prefix":
                    self.naming_prefix_radio.setChecked(True)
                elif self.output_naming == "suffix":
                    self.naming_suffix_radio.setChecked(True)
                else:
                    self.naming_original_radio.setChecked(True)
                
                self.prefix_input.setText(self.output_prefix)
                self.suffix_input.setText(self.output_suffix)
                # 更新 JPEG 质量 UI 显示与数值
                if hasattr(self, "jpeg_quality_container"):
                    self.jpeg_quality_container.setVisible(self.output_format.lower() == "jpeg")
                if hasattr(self, "jpeg_quality_slider"):
                    self.jpeg_quality_slider.setValue(int(self.jpeg_quality))
                if hasattr(self, "jpeg_quality_value_label"):
                    self.jpeg_quality_value_label.setText(f"{int(self.jpeg_quality)}")
                # 更新字体 UI
                if hasattr(self, "font_combo"):
                    if self.font_path:
                        idx = self.font_combo.findData(self.font_path)
                        if idx >= 0:
                            self.font_combo.setCurrentIndex(idx)
                    else:
                        self.font_combo.setCurrentIndex(0)
                if hasattr(self, "font_size_spin"):
                    self.font_size_spin.setValue(int(self.font_size_user))
                if hasattr(self, "font_bold_check"):
                    self.font_bold_check.setChecked(bool(self.font_bold))
                if hasattr(self, "font_italic_check"):
                    self.font_italic_check.setChecked(bool(self.font_italic))
                # 更新缩放 UI
                if hasattr(self, "resize_mode_combo"):
                    reverse_map = {
                        "none": "不缩放",
                        "width": "按宽度",
                        "height": "按高度",
                        "percent": "按百分比",
                    }
                    text = reverse_map.get(self.resize_mode, "不缩放")
                    idx = self.resize_mode_combo.findText(text)
                    if idx >= 0:
                        self.resize_mode_combo.setCurrentIndex(idx)
                if hasattr(self, "resize_width_spin"):
                    self.resize_width_spin.setValue(int(self.resize_width))
                if hasattr(self, "resize_height_spin"):
                    self.resize_height_spin.setValue(int(self.resize_height))
                if hasattr(self, "resize_percent_spin"):
                    self.resize_percent_spin.setValue(int(self.resize_percent))
                self._update_resize_rows_visibility()
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def closeEvent(self, event):
        """关闭窗口时保存设置"""
        self.save_settings()
        event.accept()