from typing import Tuple
from PIL import Image


def resize_image_proportionally(img: Image.Image, mode: str, resize_width: int, resize_height: int, resize_percent: int) -> Image.Image:
    """Resize image proportionally according to mode.

    - mode: 'none'|'width'|'height'|'percent'
    """
    try:
        ow, oh = img.size
        tw, th = ow, oh
        if mode == "width" and resize_width > 0 and ow > 0:
            tw = int(resize_width)
            scale = tw / float(ow)
            th = max(1, int(oh * scale))
        elif mode == "height" and resize_height > 0 and oh > 0:
            th = int(resize_height)
            scale = th / float(oh)
            tw = max(1, int(ow * scale))
        elif mode == "percent" and resize_percent > 0:
            scale = float(resize_percent) / 100.0
            tw = max(1, int(ow * scale))
            th = max(1, int(oh * scale))
        if (tw, th) != (ow, oh):
            return img.resize((tw, th), Image.LANCZOS)
        return img
    except Exception:
        # On failure, return original image
        return img


def save_image(img: Image.Image, output_format: str, jpeg_quality: int, output_path: str) -> None:
    """Save image in given format, handling color conversion for JPEG."""
    fmt = (output_format or "png").lower()
    if fmt == "jpeg":
        img_rgb = img.convert("RGB")
        img_rgb.save(output_path, "JPEG", quality=int(jpeg_quality))
    else:
        img.save(output_path, "PNG")