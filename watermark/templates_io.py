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
    }
    return fields