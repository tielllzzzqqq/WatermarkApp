try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
        QListWidgetItem, QAbstractItemView
    )
    from PyQt5.QtCore import QSize, Qt
    from PyQt5.QtGui import QPixmap, QIcon
except Exception:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget,
        QListWidgetItem, QAbstractItemView
    )
    from PySide6.QtCore import QSize, Qt
    from PySide6.QtGui import QPixmap, QIcon


class LeftPanel(QWidget):
    def __init__(self, host):
        super().__init__()
        self._host = host
        self.setAcceptDrops(True)
        self.dragEnterEvent = host._drag_enter_event
        self.dropEvent = host._drop_event

        layout = QVBoxLayout(self)

        class DropListWidget(QListWidget):
            def __init__(self, host):
                super().__init__()
                self._host = host
                self.setAcceptDrops(True)
                self.setDragDropMode(QAbstractItemView.NoDragDrop)

            def dragEnterEvent(self, event):
                self._host._drag_enter_event(event)

            def dragMoveEvent(self, event):
                self._host._drag_enter_event(event)

            def dropEvent(self, event):
                self._host._drop_event(event)

        self.image_list = DropListWidget(self._host)
        self.image_list.setIconSize(QSize(80, 80))
        self.image_list.itemClicked.connect(self._host.on_image_selected)
        layout.addWidget(QLabel("已导入图片:"))
        layout.addWidget(self.image_list)

        # 导入按钮
        import_layout = QHBoxLayout()
        self.import_button = QPushButton("导入图片")
        self.import_button.clicked.connect(self._host.import_images)
        self.import_folder_button = QPushButton("导入文件夹")
        self.import_folder_button.clicked.connect(self._host.import_folder)
        import_layout.addWidget(self.import_button)
        import_layout.addWidget(self.import_folder_button)
        layout.addLayout(import_layout)

        # 导出按钮
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("导出图片")
        self.export_button.clicked.connect(self._host.export_images)
        self.export_all_button = QPushButton("导出全部")
        self.export_all_button.clicked.connect(lambda: self._host.export_images(all_images=True))
        export_layout.addWidget(self.export_button)
        export_layout.addWidget(self.export_all_button)
        layout.addLayout(export_layout)

    def add_image_item(self, path: str):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item = QListWidgetItem()
            item.setIcon(QIcon(pixmap))
            item.setText(path.split('/')[-1])
            item.setData(Qt.UserRole, path)
            self.image_list.addItem(item)