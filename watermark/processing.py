from typing import Tuple, Optional
from PIL import Image, ImageDraw
from .fonts import load_font


def apply_text_watermark(
    img: Image.Image,
    text: str,
    position: str,
    custom_point: Optional[Tuple[int, int]],
    opacity_percent: int,
    font_path: Optional[str],
    font_size_user: int,
    font_bold: bool,
    font_italic: bool,
    font_color: Optional[str] = None,
) -> Image.Image:
    """Apply a text watermark to `img` and return a new image.

    - `position`: one of predefined anchors or "custom".
    - `custom_point`: (x, y) for text top-left when position == "custom".
    - `opacity_percent`: 0-100.
    - `font_size_user`: 0 means auto size based on image dimensions.
    """
    width, height = img.size

    # Determine font size and load font
    auto_size = int(min(width, height) / 15) if min(width, height) > 0 else 20
    font_size = int(font_size_user) if int(font_size_user) > 0 else auto_size
    font = load_font(font_size, font_path)

    # Measure text size
    left, top, right, bottom = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), text, font=font)
    text_width = max(0, right - left)
    text_height = max(0, bottom - top)

    # Resolve position
    if position == "top-left":
        pos = (10, 10)
    elif position == "top":
        pos = ((width - text_width) // 2, 10)
    elif position == "top-right":
        pos = (width - text_width - 10, 10)
    elif position == "left":
        pos = (10, (height - text_height) // 2)
    elif position == "center":
        pos = ((width - text_width) // 2, (height - text_height) // 2)
    elif position == "right":
        pos = (width - text_width - 10, (height - text_height) // 2)
    elif position == "bottom-left":
        pos = (10, height - text_height - 10)
    elif position == "bottom":
        pos = ((width - text_width) // 2, height - text_height - 10)
    elif position == "bottom-right":
        pos = (width - text_width - 10, height - text_height - 10)
    else:
        # custom
        if custom_point is None:
            pos = (0, 0)
        else:
            pos = (max(0, min(width - text_width, int(custom_point[0]))),
                   max(0, min(height - text_height, int(custom_point[1]))))

    # Prepare layers
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    opacity = int(255 * max(0, min(100, opacity_percent)) / 100.0)

    def _parse_hex_color(hex_str: Optional[str]) -> Tuple[int, int, int]:
        h = (hex_str or "#000000").strip()
        if h.startswith('#') and len(h) == 7:
            try:
                r = int(h[1:3], 16)
                g = int(h[3:5], 16)
                b = int(h[5:7], 16)
                return r, g, b
            except Exception:
                pass
        return 0, 0, 0

    r, g, b = _parse_hex_color(font_color)
    fill_color = (r, g, b, opacity)

    # Draw text to its own layer to simulate bold/italic
    text_layer = Image.new('RGBA', (text_width + 8, text_height + 8), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer)
    base_pos = (4, 4)

    if font_bold:
        tdraw.text(base_pos, text, font=font, fill=fill_color)
        tdraw.text((base_pos[0] + 1, base_pos[1]), text, font=font, fill=fill_color)
        tdraw.text((base_pos[0], base_pos[1] + 1), text, font=font, fill=fill_color)
    else:
        tdraw.text(base_pos, text, font=font, fill=fill_color)

    if font_italic:
        skew = 0.25
        w, h = text_layer.size
        new_w = int(w + skew * h)
        text_layer = text_layer.transform((new_w, h), Image.AFFINE, (1, skew, 0, 0, 1, 0), resample=Image.BICUBIC)

    watermark.paste(text_layer, pos, text_layer)
    return Image.alpha_composite(img.convert("RGBA"), watermark)