import os
import json
from typing import Any, Dict, Optional


def default_settings_path() -> str:
    return os.path.expanduser("~/.watermark_app/settings.json")


def ensure_parent_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def read_settings(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Read settings JSON from disk, return dict or None."""
    sp = path or default_settings_path()
    if os.path.exists(sp):
        try:
            with open(sp, "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def write_settings(data: Dict[str, Any], path: Optional[str] = None) -> None:
    """Write settings dict to JSON on disk."""
    sp = path or default_settings_path()
    ensure_parent_dir(sp)
    with open(sp, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)