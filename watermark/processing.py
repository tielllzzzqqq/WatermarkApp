from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter
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
    stroke_width: int = 0,
    stroke_color: Optional[str] = None,
    shadow_enabled: bool = False,
    shadow_offset: Tuple[int, int] = (2, 2),
    shadow_color: Optional[str] = None,
    render_scale: int = 1,
    rotation_deg: int = 0,
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
    scale = max(1, int(render_scale))
    font = load_font(font_size * scale, font_path)

    # Measure text size at high-res
    left, top, right, bottom = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), text, font=font)
    text_width_hr = max(0, right - left)
    text_height_hr = max(0, bottom - top)
    # Final low-res size after downscale
    text_width = max(1, text_width_hr // scale)
    text_height = max(1, text_height_hr // scale)

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
    sr, sg, sb = _parse_hex_color(stroke_color)
    stroke_fill = (sr, sg, sb, opacity)
    shr, shg, shb = _parse_hex_color(shadow_color)
    shadow_fill = (shr, shg, shb, max(0, min(255, int(opacity * 0.5))))

    # Draw text to its own layer to simulate bold/italic
    # Create high-res layer and draw with optional stroke/shadow
    text_layer_hr = Image.new('RGBA', (text_width_hr + 8 * scale, text_height_hr + 8 * scale), (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer_hr)
    base_pos = (4 * scale, 4 * scale)
    sw_scaled = max(0, int(stroke_width)) * scale
    off_x = int(shadow_offset[0]) * scale
    off_y = int(shadow_offset[1]) * scale

    # Shadow first
    if shadow_enabled:
        tdraw.text((base_pos[0] + off_x, base_pos[1] + off_y), text, font=font, fill=shadow_fill, stroke_width=sw_scaled, stroke_fill=shadow_fill)

    # Bold simulation at high-res
    if font_bold:
        tdraw.text(base_pos, text, font=font, fill=fill_color, stroke_width=sw_scaled, stroke_fill=stroke_fill)
        tdraw.text((base_pos[0] + 1 * scale, base_pos[1]), text, font=font, fill=fill_color, stroke_width=sw_scaled, stroke_fill=stroke_fill)
        tdraw.text((base_pos[0], base_pos[1] + 1 * scale), text, font=font, fill=fill_color, stroke_width=sw_scaled, stroke_fill=stroke_fill)
    else:
        tdraw.text(base_pos, text, font=font, fill=fill_color, stroke_width=sw_scaled, stroke_fill=stroke_fill)

    if font_italic:
        skew = 0.25
        w, h = text_layer_hr.size
        new_w = int(w + skew * h)
        text_layer_hr = text_layer_hr.transform((new_w, h), Image.AFFINE, (1, skew, 0, 0, 1, 0), resample=Image.BICUBIC)

    # Downscale for high-definition edges
    dest_w = max(1, text_layer_hr.size[0] // scale)
    dest_h = max(1, text_layer_hr.size[1] // scale)
    text_layer = text_layer_hr.resize((dest_w, dest_h), Image.LANCZOS)

    # Apply rotation if requested
    angle = int(rotation_deg) % 360
    if angle:
        text_layer = text_layer.rotate(angle, expand=True, resample=Image.BICUBIC)

    # Resolve position based on final layer size
    lw, lh = text_layer.size
    if position == "top-left":
        pos = (10, 10)
    elif position == "top":
        pos = ((width - lw) // 2, 10)
    elif position == "top-right":
        pos = (width - lw - 10, 10)
    elif position == "left":
        pos = (10, (height - lh) // 2)
    elif position == "center":
        pos = ((width - lw) // 2, (height - lh) // 2)
    elif position == "right":
        pos = (width - lw - 10, (height - lh) // 2)
    elif position == "bottom-left":
        pos = (10, height - lh - 10)
    elif position == "bottom":
        pos = ((width - lw) // 2, height - lh - 10)
    elif position == "bottom-right":
        pos = (width - lw - 10, height - lh - 10)
    else:
        # custom
        if custom_point is None:
            pos = (0, 0)
        else:
            pos = (max(0, min(width - lw, int(custom_point[0]))),
                   max(0, min(height - lh, int(custom_point[1]))))

    watermark.paste(text_layer, pos, text_layer)
    return Image.alpha_composite(img.convert("RGBA"), watermark)


def apply_image_watermark(
    img: Image.Image,
    watermark_path: str,
    position: str,
    custom_point: Optional[Tuple[int, int]],
    opacity_percent: int,
    scale_mode: str = "percent",  # "percent" | "free"
    scale_percent: int = 100,
    scale_width: int = 0,
    scale_height: int = 0,
    keep_aspect: bool = True,
    rotation_deg: int = 0,
) -> Image.Image:
    """Overlay an image watermark onto `img`.

    - Supports PNG with transparency (alpha channel preserved).
    - `opacity_percent`: 0-100 overall watermark transparency.
    - `scale_mode`: "percent" (relative) or "free" (explicit width/height).
    - `keep_aspect` applies when `scale_mode == "free"`.
    - `position`/`custom_point` follow the same rules as text watermark.
    """
    base = img.convert("RGBA")
    try:
        wm = Image.open(watermark_path).convert("RGBA")
    except Exception:
        # If opening watermark fails, just return original image
        return base

    # Compute target size
    ow, oh = wm.size
    if scale_mode == "percent":
        p = max(1, int(scale_percent))
        tw = max(1, int(ow * p / 100.0))
        th = max(1, int(oh * p / 100.0))
    else:
        # free mode
        w = int(scale_width)
        h = int(scale_height)
        if keep_aspect:
            if w > 0:
                ratio = w / float(ow)
                tw = max(1, w)
                th = max(1, int(oh * ratio))
            elif h > 0:
                ratio = h / float(oh)
                th = max(1, h)
                tw = max(1, int(ow * ratio))
            else:
                tw, th = ow, oh
        else:
            tw = max(1, w) if w > 0 else ow
            th = max(1, h) if h > 0 else oh

    wm_resized = wm.resize((tw, th), Image.LANCZOS)

    # Apply rotation if requested
    angle = int(rotation_deg) % 360
    if angle:
        wm_resized = wm_resized.rotate(angle, expand=True, resample=Image.BICUBIC)

    # Apply overall opacity by scaling existing alpha
    overall_alpha = int(255 * max(0, min(100, int(opacity_percent))) / 100.0)
    r, g, b, a = wm_resized.split()
    a = a.point(lambda x: int(x * overall_alpha / 255))
    wm_resized = Image.merge("RGBA", (r, g, b, a))

    bw, bh = base.size
    rw, rh = wm_resized.size
    # Resolve position
    if position == "top-left":
        pos = (10, 10)
    elif position == "top":
        pos = ((bw - rw) // 2, 10)
    elif position == "top-right":
        pos = (bw - rw - 10, 10)
    elif position == "left":
        pos = (10, (bh - rh) // 2)
    elif position == "center":
        pos = ((bw - rw) // 2, (bh - rh) // 2)
    elif position == "right":
        pos = (bw - rw - 10, (bh - rh) // 2)
    elif position == "bottom-left":
        pos = (10, bh - rh - 10)
    elif position == "bottom":
        pos = ((bw - rw) // 2, bh - rh - 10)
    elif position == "bottom-right":
        pos = (bw - rw - 10, bh - rh - 10)
    else:
        if custom_point is None:
            pos = (0, 0)
        else:
            pos = (max(0, min(bw - rw, int(custom_point[0]))),
                   max(0, min(bh - rh, int(custom_point[1]))))

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    layer.paste(wm_resized, pos, wm_resized)
    return Image.alpha_composite(base, layer)