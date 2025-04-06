from PyPDF2 import PdfReader
from io import BytesIO
from typing import Optional, Union
import logging

class PDFTextExtractor:
    def extract_text(self, pdf_input: Union[str, bytes]) -> str:
        pdf_bytes = self._get_pdf_bytes(pdf_input)
        text = self._extract_with_pypdf2(pdf_bytes)
        
        if not text:
            raise ValueError("Failed to extract text from PDF - document may be image-based")
        return text

    def _extract_with_pypdf2(self, pdf_bytes: bytes) -> Optional[str]:
        try:
            text = []
            with BytesIO(pdf_bytes) as file:
                reader = PdfReader(file)
                text = [page.extract_text() 
                       for page in reader.pages 
                       if page.extract_text()]
            return "\n".join(text) if text else None
        except Exception as e:
            logging.error(f"PyPDF2 extraction failed: {str(e)}")
            return None

    def _get_pdf_bytes(self, pdf_input: Union[str, bytes]) -> bytes:
        if isinstance(pdf_input, str):
            with open(pdf_input, "rb") as f:
                return f.read()
        return pdf_input