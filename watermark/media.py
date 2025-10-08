import os
from typing import List


SUPPORTED_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}


def is_supported_image(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in SUPPORTED_EXTS


def scan_directory_for_images(folder_path: str) -> List[str]:
    files: List[str] = []
    for root, _, names in os.walk(folder_path):
        for name in names:
            if os.path.splitext(name)[1].lower() in SUPPORTED_EXTS:
                files.append(os.path.join(root, name))
    return files


def make_output_basename(orig_name: str, naming_rule: str, prefix: str, suffix: str) -> str:
    name, _ = os.path.splitext(orig_name)
    if naming_rule == "prefix":
        return f"{prefix}{name}"
    elif naming_rule == "suffix":
        return f"{name}{suffix}"
    return name