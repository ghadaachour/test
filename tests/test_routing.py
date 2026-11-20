
from unittest.mock import patch

from app.services.processing_service import process_document


def test_pdf_routing():

    with patch(
        "app.services.processing_service.extract_pdf_text",
        return_value="Invoice number 123"
    ) as parser:

        result = process_document(
            "invoice.pdf",
            "application/pdf",
            b"fake pdf content"
        )

        parser.assert_called_once()

        assert result["status"] == "done"
        assert result["method"] == "PDF Parser"
        assert result["text"] == "Invoice number 123"


def test_image_routing():

    with patch(
        "app.services.processing_service.extract_image_text",
        return_value="Hello World"
    ) as ocr:

        result = process_document(
            "document.png",
            "image/png",
            b"fake image content"
        )

        ocr.assert_called_once()

        assert result["status"] == "done"
        assert result["method"] == "OCR"
        assert result["text"] == "Hello World"


def test_unsupported_file():

    result = process_document(
        "document.docx",
        "application/docx",
        b"content"
    )

    assert result["status"] == "failed"
    assert result["error"] is not None
