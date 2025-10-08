from PIL import Image
from typing import Tuple

try:
    from PyQt5.QtGui import QImage
except Exception:
    from PySide6.QtGui import QImage


def pil_to_qimage(img: Image.Image) -> QImage:
    img_rgba = img.convert("RGBA")
    data = img_rgba.tobytes("raw", "RGBA")
    return QImage(data, img_rgba.width, img_rgba.height, QImage.Format_RGBA8888)