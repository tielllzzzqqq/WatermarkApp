import os
from typing import List, Tuple, Optional
from PIL import ImageFont


def load_font(font_size: int, font_path: Optional[str] = None) -> ImageFont.FreeTypeFont:
    """Load a font. Prefer provided `font_path`; otherwise choose a CJK-friendly fallback.

    Returns a Pillow Font object; falls back to default when unavailable.
    """
    # Try user selected font first
    if font_path:
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            pass

    # Prefer common CJK fonts available on macOS
    cjk_ttc_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
    ]
    for ttc in cjk_ttc_paths:
        if os.path.exists(ttc):
            for idx in range(0, 8):
                try:
                    return ImageFont.truetype(ttc, font_size, index=idx)
                except Exception:
                    continue

    # Other candidates if installed
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

    # Fallback to Arial or default
    try:
        return ImageFont.truetype("Arial", font_size)
    except Exception:
        return ImageFont.load_default()


def scan_system_font_files() -> List[Tuple[str, str]]:
    """Scan system font directories and collect available font files.

    Returns a list of tuples: (display_name, absolute_path).
    """
    fonts: List[Tuple[str, str]] = []
    search_dirs = [
        "/System/Library/Fonts",
        "/System/Library/Fonts/Supplemental",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]
    exts = {".ttf", ".otf", ".ttc"}
    seen = set()
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            path = os.path.join(d, name)
            if not os.path.isfile(path):
                continue
            _, ext = os.path.splitext(name)
            if ext.lower() in exts:
                disp = name
                if path not in seen:
                    fonts.append((disp, path))
                    seen.add(path)

    # Sort with priority for common Chinese fonts
    def score(item: Tuple[str, str]) -> int:
        n = item[0].lower()
        s = 0
        if "pingfang" in n or "songti" in n or "stheiti" in n or "hiragino" in n:
            s -= 10
        if "bold" in n:
            s += 1
        return s

    fonts.sort(key=score)
    return fonts