
import os
from io import BytesIO

import pytesseract
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv

load_dotenv()

# Configure Tesseract on Windows
tesseract_cmd = os.getenv("TESSERACT_CMD")

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Default OCR languages
DEFAULT_LANGUAGES = os.getenv("OCR_LANGUAGES", "fra+eng")


def extract_image_text(
    image_content: bytes,
    languages: str = DEFAULT_LANGUAGES
) -> str:
    """
    Extract text from an image using Tesseract OCR.
    Supports French, English and Arabic.
    """

    if not image_content:
        raise ValueError("The image file is empty.")

    if not languages or not languages.strip():
        raise ValueError("At least one OCR language must be specified.")

    try:
        # Open image
        image = Image.open(BytesIO(image_content))

        # Normalize image format
        image = image.convert("RGB")

        # Perform OCR
        extracted_text = pytesseract.image_to_string(
            image,
            lang=languages
        )

        return extracted_text.strip()

    except UnidentifiedImageError as error:
        raise RuntimeError("Invalid or unsupported image format.") from error

    except pytesseract.TesseractNotFoundError as error:
        raise RuntimeError(
            "Tesseract is not installed or its path is incorrect."
        ) from error

    except pytesseract.TesseractError as error:
        raise RuntimeError(
            f"Tesseract OCR error: {str(error)}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"OCR extraction failed: {str(error)}"
        ) from error
