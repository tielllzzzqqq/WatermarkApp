from typing import List, Dict, Optional


def add_or_update_template(templates: List[Dict], tpl: Dict) -> List[Dict]:
    name = tpl.get("name")
    if not name:
        return templates
    updated = False
    new_list: List[Dict] = []
    for t in templates:
        if t.get("name") == name:
            new_list.append(tpl)
            updated = True
        else:
            new_list.append(t)
    if not updated:
        new_list.append(tpl)
    return new_list


def list_template_names(templates: List[Dict]) -> List[str]:
    return [t.get("name", "") for t in templates if isinstance(t, dict)]


def find_template(templates: List[Dict], name: str) -> Optional[Dict]:
    for t in templates:
        if t.get("name") == name:
            return t
    return None


def normalize_template_fields(tpl: Dict) -> Dict:
    # Ensure essential fields exist; fallback to defaults if missing
    fields = {
        "name": tpl.get("name", ""),
        "text": tpl.get("text", ""),
        "opacity": tpl.get("opacity", 50),
        "position": tpl.get("position", "bottom-right"),
        "format": tpl.get("format", "png"),
        "naming": tpl.get("naming", "original"),
        "prefix": tpl.get("prefix", ""),
        "suffix": tpl.get("suffix", ""),
        "jpeg_quality": tpl.get("jpeg_quality", 90),
        "resize_mode": tpl.get("resize_mode", "none"),
        "resize_width": tpl.get("resize_width", 0),
        "resize_height": tpl.get("resize_height", 0),
        "resize_percent": tpl.get("resize_percent", 0),
        "font_path": tpl.get("font_path"),
        "font_size": tpl.get("font_size", 0),
        "font_bold": tpl.get("font_bold", False),
        "font_italic": tpl.get("font_italic", False),
        "font_color": tpl.get("font_color", "#000000"),
        # Advanced text style fields
        "font_stroke_width": tpl.get("font_stroke_width", 0),
        "font_stroke_color": tpl.get("font_stroke_color", "#000000"),
        "font_shadow_enabled": tpl.get("font_shadow_enabled", False),
        "font_shadow_offset_x": tpl.get("font_shadow_offset_x", 2),
        "font_shadow_offset_y": tpl.get("font_shadow_offset_y", 2),
        "font_shadow_color": tpl.get("font_shadow_color", "#000000"),
        "render_scale": tpl.get("render_scale", 1),
        # Image watermark fields
        "watermark_type": tpl.get("watermark_type", "text"),
        "image_watermark_path": tpl.get("image_watermark_path"),
        "image_scale_mode": tpl.get("image_scale_mode", "percent"),
        "image_scale_percent": tpl.get("image_scale_percent", 50),
        "image_scale_width": tpl.get("image_scale_width", 200),
        "image_scale_height": tpl.get("image_scale_height", 200),
        "image_keep_aspect": tpl.get("image_keep_aspect", True),
        # Rotation for both text and image watermarks
        "watermark_rotation": tpl.get("watermark_rotation", 0),
    }
    return fields