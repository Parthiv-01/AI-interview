# Step 1: Install necessary libraries
# pip install transformers
# pip install --upgrade PyPDF3

# Step 2: Import required libraries
import PyPDF3
from typing import Optional, Union
import logging
from transformers import pipeline  # (Optional, for summarization/QA, etc.)

# Step 3: Class to handle PDF text extraction
class PDFTextExtractor:
    # Extract text from a file path or byte stream
    def extract_text(self, pdf_input: Union[str, bytes]) -> str:
        pdf_bytes = self._get_pdf_bytes(pdf_input)
        text = self._extract_with_pypdf3(pdf_bytes)

        if not text:
            raise ValueError("Failed to extract text from PDF - document may be image-based or blank.")
        return text

    # Internal method to extract text using PyPDF3
    def _extract_with_pypdf3(self, pdf_bytes: bytes) -> Optional[str]:
        try:
            text = ""
            # Write the bytes to a temporary file
            with open("/tmp/temp.pdf", "wb") as f:
                f.write(pdf_bytes)

            # Read from the temporary file
            with open("/tmp/temp.pdf", "rb") as pdf_file:
                pdf_reader = PyPDF3.PdfFileReader(pdf_file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    page_text = page.extractText()  # PyPDF3 uses extractText()
                    if page_text:
                        text += page_text + "\n"
            return text.strip() if text else None
        except Exception as e:
            logging.error(f"PyPDF3 extraction failed: {str(e)}")
            return None

    # Handle both string (path) and bytes input
    def _get_pdf_bytes(self, pdf_input: Union[str, bytes]) -> bytes:
        if isinstance(pdf_input, str):
            with open(pdf_input, "rb") as f:
                return f.read()
        return pdf_input

# Step 4: Example usage
if __name__ == "__main__":
    # Path to your PDF file
    pdf_path = "your_pdf_file.pdf"  # Replace with your actual file path

    # Create extractor instance
    extractor = PDFTextExtractor()
    
    # Extract text from the PDF
    try:
        extracted_text = extractor.extract_text(pdf_path)
        print("Extracted Text:\n", extracted_text)
    except Exception as e:
        print("Error:", e)

    # Optional: Use Transformers for summarization (uncomment if needed)
    # summarizer = pipeline("summarization")
    # summary = summarizer(extracted_text, max_length=100, min_length=30, do_sample=False)
    # print("\nSummary:\n", summary[0]['summary_text'])
