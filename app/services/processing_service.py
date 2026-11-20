
import pymupdf
from app.services.pdf_service import (
    extract_pdf_text,
    is_scanned_pdf
)
from app.services.ocr_service import extract_image_text


def process_document(file_name, mime_type, content):

    result = {
        "file_name": file_name,
        "status": "pending",
        "method": None,
        "text": "",
        "error": None
    }

    try:
        result["status"] = "processing"

        if mime_type == "application/pdf":

            # Extract native PDF text first
            extracted_text = extract_pdf_text(content)

            if extracted_text.strip():
                result["method"] = "PDF Parser"
                result["text"] = extracted_text

            elif is_scanned_pdf(content):
                # Scanned PDF: apply OCR
                result["method"] = "OCR (Scanned PDF)"

                pdf_document = pymupdf.open(
                    stream=content,
                    filetype="pdf"
                )

                try:
                    pages_text = []

                    for page_number, page in enumerate(
                        pdf_document, start=1
                    ):
                        pixmap = page.get_pixmap(dpi=200)
                        image_content = pixmap.tobytes("png")

                        page_text = extract_image_text(
                            image_content
                        )

                        pages_text.append(
                            f"--- Page {page_number} ---\n{page_text}"
                        )

                    result["text"] = "\n\n".join(pages_text)

                finally:
                    pdf_document.close()

            else:
                result["method"] = "PDF Parser"
                result["text"] = ""

        elif mime_type in ["image/png", "image/jpeg"]:

            result["method"] = "OCR"
            result["text"] = extract_image_text(content)

        else:
            raise ValueError(
                f"Unsupported file type: {mime_type}"
            )

        result["status"] = "done"

    except Exception as error:
        result["status"] = "failed"
        result["error"] = str(error)

    return result
