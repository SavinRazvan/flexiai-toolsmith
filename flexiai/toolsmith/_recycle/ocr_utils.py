# FILE: ocr_utils.py

"""
ocr_utils.py

One-stop OCR helper optimised for IDE / code-editor screenshots.

Pipeline
~~~~~~~~
1. (optional) crop top / bottom margins
2. auto-scale → min 700 px width
3. grayscale
4. **2×2 dilation** — thickens all strokes (underscores, i-dots, etc.)
5. 1-px black halo
6. optional unsharp mask  (default ON, 300 %)
7. optional DPI resample  (default 600 dpi)
8. optional adaptive/simple threshold
9. Tesseract call with inter-word spaces preserved and DAWG dictionaries disabled
"""

from __future__ import annotations

import os
import logging
from typing import Optional, Sequence

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError, ImageFilter, ImageOps
import pytesseract

logger = logging.getLogger(__name__)


# ───────────────────────── Exceptions ──────────────────────────
class OCRError(Exception):
    """Tesseract failed after preprocessing."""


class ImageNotFoundError(OCRError):
    """Image path does not exist."""


class InvalidImageError(OCRError):
    """File could not be opened as an image."""


# ───────────────────────── Helpers ─────────────────────────────
def _auto_scale(
    img: Image.Image,
    *,
    min_width: int = 700,
    max_width: int = 2000,
) -> Image.Image:
    """Upscale if width < min_width, downscale if width > max_width."""
    w, _ = img.size
    if w < min_width:
        scale = min_width / w
    elif w > max_width:
        scale = max_width / w
    else:
        return img
    new_size = (int(w * scale), int(img.height * scale))
    logger.debug("Scale %dx%d → %dx%d", w, img.height, *new_size)
    return img.resize(new_size, Image.LANCZOS)


def _crop(img: Image.Image, *, top: int, bottom: int) -> Image.Image:
    w, h = img.size
    return img.crop((0, top, w, h - bottom))


def _preprocess(
    img: Image.Image,
    *,
    dpi: Optional[int],
    adaptive: bool,
    sharpen: bool,
    crop_top: int,
    crop_bottom: int,
) -> Image.Image:
    """Single-pass preprocessing."""
    img = _crop(img, top=crop_top, bottom=crop_bottom)
    img = _auto_scale(img)

    # 1) grayscale
    img = img.convert("L")

    # 2) dilate 2 × 2 to thicken thin strokes
    arr = cv2.dilate(np.array(img), np.ones((2, 2), np.uint8), iterations=1)
    img = Image.fromarray(arr)

    # 3) 1-px halo
    img = ImageOps.expand(img, border=1, fill=0)

    # 4) sharpen
    if sharpen:
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=300, threshold=1))

    # 5) virtual DPI up-sample
    if dpi:
        base_dpi = img.info.get("dpi", (72, 72))[0]
        scale = dpi / base_dpi
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

    # 6) optional threshold
    if adaptive:
        img = ImageOps.autocontrast(img)
        img = img.point(lambda p: 255 if p > 128 else 0)

    return img


# ───────────────────────── Public API ──────────────────────────
def extract_text_from_image(
    image_path: str,
    *,
    lang: Optional[str] = None,
    dpi: Optional[int] = None,
    adaptive_threshold: bool = False,
    sharpen: bool = True,
    psm: int = 6,
    oem: int = 3,
    whitelist: Optional[Sequence[str]] = None,
    crop_top: int = 0,
    crop_bottom: int = 0,
    tesseract_cmd: Optional[str] = None,
) -> str:
    """Return OCR text from *image_path* using the tuned pipeline."""
    if not isinstance(image_path, str):
        raise TypeError("image_path must be str")
    if not os.path.isfile(image_path):
        raise ImageNotFoundError(image_path)

    try:
        pil_img = Image.open(image_path)
    except (UnidentifiedImageError, OSError) as err:
        raise InvalidImageError(image_path) from err

    pil_img = _preprocess(
        pil_img,
        dpi=dpi,
        adaptive=adaptive_threshold,
        sharpen=sharpen,
        crop_top=crop_top,
        crop_bottom=crop_bottom,
    )

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    cfg = (
        f"--oem {oem} --psm {psm} "
        "-c preserve_interword_spaces=1 "
        "-c load_system_dawg=0 -c load_freq_dawg=0"
    )
    if lang:
        cfg = f"-l {lang} {cfg}"
    if whitelist:
        cfg += f" -c tessedit_char_whitelist={''.join(whitelist)}"

    try:
        return pytesseract.image_to_string(pil_img, config=cfg)
    except Exception as err:  # noqa: BLE001
        raise OCRError(image_path) from err
