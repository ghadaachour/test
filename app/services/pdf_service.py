
from io import BytesIO
from pypdf import PdfReader


def extract_pdf_text(file_content: bytes) -> str:
    """
    Extract text from a native PDF using pypdf.
    Returns extracted text page by page.
    """

    if not file_content:
        raise ValueError("The PDF file is empty.")

    try:
        reader = PdfReader(BytesIO(file_content))

        if reader.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported.")

        if len(reader.pages) == 0:
            raise ValueError("The PDF contains no pages.")

        extracted_pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            extracted_pages.append(
                f"--- Page {page_number} ---\n{text.strip()}"
            )

        return "\n\n".join(extracted_pages).strip()

    except Exception as error:
        raise RuntimeError(
            f"PDF extraction failed: {str(error)}"
        ) from error


def is_scanned_pdf(file_content: bytes) -> bool:
    """
    Detect whether a PDF has no extractable text.
    Such PDFs may require OCR.
    """

    try:
        text = extract_pdf_text(file_content)
        return len(text.strip()) == 0

    except Exception:
        raise
