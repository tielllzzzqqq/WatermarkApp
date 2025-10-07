#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

# 直接尝试导入 PyQt5（优先）或 PySide6 的具体类，便于编辑器类型解析
try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QFileDialog, QListWidget, QListWidgetItem, QSlider, QComboBox, QLineEdit,
        QGroupBox, QRadioButton, QCheckBox, QMessageBox, QSplitter, QFrame,
        QGridLayout, QInputDialog, QScrollArea, QSizePolicy
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
            QFileDialog, QListWidget, QListWidgetItem, QSlider, QComboBox, QLineEdit,
            QGroupBox, QRadioButton, QCheckBox, QMessageBox, QSplitter, QFrame,
            QGridLayout, QInputDialog, QScrollArea, QSizePolicy
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
        
        # 设置中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # 创建左侧面板
        self.create_left_panel()
        
        # 创建右侧面板
        self.create_right_panel()
        
        # 加载上次的设置
        self.load_settings()
        
    def create_left_panel(self):
        """创建左侧面板，包含图片列表和导入/导出按钮"""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMinimumWidth(260)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.itemClicked.connect(self.on_image_selected)
        left_layout.addWidget(QLabel("已导入图片:"))
        left_layout.addWidget(self.image_list)
        
        # 导入按钮
        import_layout = QHBoxLayout()
        self.import_button = QPushButton("导入图片")
        self.import_button.clicked.connect(self.import_images)
        self.import_folder_button = QPushButton("导入文件夹")
        self.import_folder_button.clicked.connect(self.import_folder)
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.import_folder_button)
        left_layout.addLayout(import_layout)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("导出图片")
        self.export_button.clicked.connect(self.export_images)
        self.export_all_button = QPushButton("导出全部")
        self.export_all_button.clicked.connect(lambda: self.export_images(all_images=True))
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.export_all_button)
        left_layout.addLayout(export_layout)
        
        # 添加到主布局
        self.main_layout.addWidget(left_panel, 1)
        
    def create_right_panel(self):
        """创建右侧面板，包含预览和水印设置"""
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 预览区支持鼠标事件以手动拖拽水印（默认开启）
        self.preview_label.setMouseTracking(True)
        self.preview_label.mousePressEvent = self._preview_mouse_press_event
        self.preview_label.mouseMoveEvent = self._preview_mouse_move_event
        preview_layout.addWidget(self.preview_label)
        
        # 水印设置
        settings_group = QGroupBox("水印设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 文本水印设置
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("水印文本:"))
        self.text_input = QLineEdit(self.watermark_text)
        self.text_input.textChanged.connect(self.on_watermark_text_changed)
        text_layout.addWidget(self.text_input)
        settings_layout.addLayout(text_layout)
        
        # 透明度设置
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("透明度:"))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.watermark_opacity)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        self.opacity_value_label = QLabel(f"{self.watermark_opacity}%")
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value_label)
        settings_layout.addLayout(opacity_layout)
        
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
                watermarked_img = watermarked_img.convert("RGBA")
                data = watermarked_img.tobytes("raw", "RGBA")
                qimg = QImage(data, watermarked_img.width, watermarked_img.height, QImage.Format_RGBA8888)
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
        """应用水印到图片"""
        # 创建一个透明图层
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        # 计算水印位置
        width, height = img.size
        
        # 使用更健壮的字体加载，支持中文/Unicode 字符
        font_size = int(min(width, height) / 15)  # 根据图片大小调整字体大小
        font = self._load_font(font_size)
        
        # 获取文本大小
        left, top, right, bottom = draw.textbbox((0, 0), self.watermark_text, font=font)
        text_width = right - left
        text_height = bottom - top
        
        # 根据选择的位置确定坐标
        if self.watermark_position == "top-left":
            position = (10, 10)
        elif self.watermark_position == "top":
            position = ((width - text_width) // 2, 10)
        elif self.watermark_position == "top-right":
            position = (width - text_width - 10, 10)
        elif self.watermark_position == "left":
            position = (10, (height - text_height) // 2)
        elif self.watermark_position == "center":
            position = ((width - text_width) // 2, (height - text_height) // 2)
        elif self.watermark_position == "right":
            position = (width - text_width - 10, (height - text_height) // 2)
        elif self.watermark_position == "bottom-left":
            position = (10, height - text_height - 10)
        elif self.watermark_position == "bottom":
            position = ((width - text_width) // 2, height - text_height - 10)
        elif self.watermark_position == "bottom-right":
            position = (width - text_width - 10, height - text_height - 10)
        else:
            # 自定义位置
            position = (self.watermark_position_custom.x(), self.watermark_position_custom.y())
        
        # 绘制文本水印
        opacity = int(255 * (self.watermark_opacity / 100))
        draw.text(position, self.watermark_text, fill=(0, 0, 0, opacity), font=font)
        
        # 将水印合并到原图
        return Image.alpha_composite(img.convert("RGBA"), watermark)

    def _load_font(self, font_size):
        """尽可能选择支持中文/Unicode 的字体，避免字符显示为方框。
        在 macOS 上优先尝试系统字体；如果不可用则回退到默认字体。
        """
        # 优先尝试常见的 CJK 字体（按存在概率排序）
        cjk_ttc_paths = [
            "/System/Library/Fonts/PingFang.ttc",  # 苹果系统中文字体集合
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # 冬青黑体简体中文
            "/System/Library/Fonts/STHeiti Medium.ttc",  # 华文黑体（中）
            "/System/Library/Fonts/STHeiti Light.ttc",   # 华文黑体（细）
            "/System/Library/Fonts/Supplemental/Songti.ttc",  # 宋体
        ]
        for ttc in cjk_ttc_paths:
            if os.path.exists(ttc):
                # 尝试多个集合索引
                for idx in range(0, 8):
                    try:
                        return ImageFont.truetype(ttc, font_size, index=idx)
                    except Exception:
                        continue
        # 其他可选字体（若安装了）
        other_candidates = [
            "/Library/Fonts/NotoSansCJKsc-Regular.otf",
            "/Library/Fonts/NotoSansCJK-Regular.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
        for path in other_candidates:
            try:
                if os.path.exists(path):
                    return ImageFont.truetype(path, font_size)
            except Exception:
                continue
        # 最后回退到 Arial 或默认字体
        try:
            return ImageFont.truetype("Arial", font_size)
        except Exception:
            return ImageFont.load_default()
    
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
                name, _ = os.path.splitext(filename)
                
                if self.output_naming == "prefix":
                    output_name = f"{self.output_prefix}{name}"
                elif self.output_naming == "suffix":
                    output_name = f"{name}{self.output_suffix}"
                else:  # original
                    output_name = name
                
                # 添加扩展名
                if self.output_format.lower() == "jpeg":
                    output_path = os.path.join(output_dir, f"{output_name}.jpg")
                else:
                    output_path = os.path.join(output_dir, f"{output_name}.png")
                
                # 打开原图并添加水印
                img = Image.open(input_path)
                watermarked_img = self.apply_watermark(img)
                
                # 保存图片
                if self.output_format.lower() == "jpeg":
                    watermarked_img = watermarked_img.convert("RGB")
                    watermarked_img.save(output_path, "JPEG", quality=95)
                else:
                    watermarked_img.save(output_path, "PNG")
        
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
        font_size = int(min(img_w, img_h) / 15) if min(img_w, img_h) > 0 else 20
        font = self._load_font(font_size)
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
                "suffix": self.output_suffix
            }
            
            self.templates.append(template)
            self.save_settings()
            QMessageBox.information(self, "成功", f"模板 '{template_name}' 已保存")
    
    def show_templates(self):
        """显示模板列表"""
        if not self.templates:
            QMessageBox.information(self, "提示", "没有保存的模板")
            return
        
        template_names = [t["name"] for t in self.templates]
        template_name, ok = QInputDialog.getItem(self, "加载模板", "选择模板:", template_names, 0, False)
        
        if ok and template_name:
            for template in self.templates:
                if template["name"] == template_name:
                    self.load_template(template)
                    break
    
    def load_template(self, template):
        """加载模板"""
        self.watermark_text = template["text"]
        self.watermark_opacity = template["opacity"]
        self.watermark_position = template["position"]
        self.output_format = template["format"]
        self.output_naming = template["naming"]
        self.output_prefix = template["prefix"]
        self.output_suffix = template["suffix"]
        
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
            "templates": self.templates
        }
        
        try:
            os.makedirs(os.path.expanduser("~/.watermark_app"), exist_ok=True)
            with open(os.path.expanduser("~/.watermark_app/settings.json"), "w") as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def load_settings(self):
        """加载设置"""
        try:
            settings_path = os.path.expanduser("~/.watermark_app/settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                
                self.watermark_text = settings.get("watermark_text", self.watermark_text)
                self.watermark_opacity = settings.get("watermark_opacity", self.watermark_opacity)
                self.watermark_position = settings.get("watermark_position", self.watermark_position)
                self.output_format = settings.get("output_format", self.output_format)
                self.output_naming = settings.get("output_naming", self.output_naming)
                self.output_prefix = settings.get("output_prefix", self.output_prefix)
                self.output_suffix = settings.get("output_suffix", self.output_suffix)
                self.templates = settings.get("templates", [])
                
                # 更新UI
                self.text_input.setText(self.watermark_text)
                self.opacity_slider.setValue(self.watermark_opacity)
                
                if self.output_format.lower() == "jpeg":
                    self.format_combo.setCurrentIndex(1)
                
                if self.output_naming == "prefix":
                    self.naming_prefix_radio.setChecked(True)
                elif self.output_naming == "suffix":
                    self.naming_suffix_radio.setChecked(True)
                else:
                    self.naming_original_radio.setChecked(True)
                
                self.prefix_input.setText(self.output_prefix)
                self.suffix_input.setText(self.output_suffix)
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def closeEvent(self, event):
        """关闭窗口时保存设置"""
        self.save_settings()
        event.accept()