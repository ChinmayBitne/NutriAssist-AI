"""
gemini_handler.py
Gemini is used only for food image detection.
"""

from __future__ import annotations

import io
import os
from typing import List

from PIL import Image

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    if not GEMINI_API_KEY:
        return None
    from google import genai
    _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def detect_food_from_image(image: Image.Image) -> List[str]:
    client = _get_client()
    if client is None:
        return ["Gemini API key missing"]

    from google.genai import types

    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    prompt = (
        "Look at this image and list only the food items that are clearly visible. "
        "Return a comma-separated list of food names only. "
        "No quantities, no descriptions, no extra text."
    )
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=[types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"), prompt],
        )
        raw = (resp.text or "").strip()
        items = [x.strip() for x in raw.split(",") if x.strip()]
        return items if items else ["unknown food"]
    except Exception as exc:
        print(f"[Gemini Vision error] {exc}")
        return ["unknown food"]
