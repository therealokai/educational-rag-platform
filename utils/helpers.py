from typing import Optional
import json
import base64
import io

try:
    # json_repair is helpful for recovering malformed JSON strings
    from json_repair import loads as _json_repair_loads
except Exception:
    _json_repair_loads = None


def safe_load_json(s: Optional[str]) -> Optional[dict]:
    """Attempt to load JSON safely.

    Tries json_repair first (if available) to recover malformed JSON, then falls
    back to the stdlib json.loads. Returns None if parsing fails or input is falsy.
    """
    if not s:
        return None
    if _json_repair_loads is not None:
        try:
            return _json_repair_loads(s)
        except Exception:
            pass
    try:
        return json.loads(s)
    except Exception:
        return None


def pil_image_to_base64(img, fmt: str = "PNG") -> str:
    """Convert a PIL Image to a base64-encoded string (PNG by default).

    Keeps the logic centralized so other modules can reuse it.
    """
    buffered = io.BytesIO()
    img.save(buffered, format=fmt)
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")
