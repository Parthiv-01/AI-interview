import PyPDF3
from typing import Optional, Union
import logging

class PDFTextExtractor:
    def extract_text(self, pdf_input: Union[str, bytes]) -> str:
        pdf_bytes = self._get_pdf_bytes(pdf_input)
        text = self._extract_with_pypdf3(pdf_bytes)

        if not text:
            raise ValueError("Failed to extract text from PDF - document may be image-based")
        return text

    def _extract_with_pypdf3(self, pdf_bytes: bytes) -> Optional[str]:
        try:
            text = ""
            with open("/tmp/temp.pdf", "wb") as f:
                f.write(pdf_bytes)
            with open("/tmp/temp.pdf", "rb") as pdf_file:
                pdf_reader = PyPDF3.PdfFileReader(pdf_file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    page_text = page.extractText()
                    if page_text:
                        text += page_text + "\n"
            return text.strip() if text else None
        except Exception as e:
            logging.error(f"PyPDF3 extraction failed: {str(e)}")
            return None

    def _get_pdf_bytes(self, pdf_input: Union[str, bytes]) -> bytes:
        if isinstance(pdf_input, str):
            with open(pdf_input, "rb") as f:
                return f.read()
        return pdf_input
