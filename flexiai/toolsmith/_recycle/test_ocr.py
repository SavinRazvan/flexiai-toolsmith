# FILE: test_ocr.py

"""
test_ocr.py

Runs the tuned OCR pipeline on a sample screenshot and saves raw text to
*ocr_results.txt*.
"""

import logging
from pathlib import Path

from ocr_utils import extract_text_from_image, OCRError


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    img = Path(
        "flexiai/toolsmith/_recycle/test_image/Screenshot 2025-05-18 111345.png"
    )
    out = Path("ocr_results.txt")

    try:
        text = extract_text_from_image(
            str(img),
            lang="eng",
            dpi=600,
            adaptive_threshold=False,
            sharpen=True,
            psm=6,
            oem=3,
            whitelist=None,
            crop_top=0,
            crop_bottom=0,
        )

        print("===== Extracted Text =====\n")
        print(text)
        out.write_text(text, encoding="utf-8")
        logging.info("Wrote OCR result to %s", out.resolve())

    except (OCRError, Exception) as err:
        logging.error("OCR failure: %s", err)


if __name__ == "__main__":
    main()
