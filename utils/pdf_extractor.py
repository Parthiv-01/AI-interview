import fitz  # PyMuPDF
import logging
from typing import Union

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    def extract_text(self, pdf_input: Union[str, bytes]) -> str:
        try:
            if isinstance(pdf_input, str):
                doc = fitz.open(pdf_input)
            else:
                doc = fitz.open(stream=pdf_input, filetype="pdf")

            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()

            if not text.strip():
                raise ValueError("No text found in PDF. It may be image-based.")

            return text.strip()

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""

