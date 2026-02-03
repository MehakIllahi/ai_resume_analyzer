from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
import tempfile

def extract_pdf_text(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(uploaded_file.read())
            temp.flush()

            text = extract_text(temp.name)

            if not text or len(text.strip()) < 30:
                raise ValueError("PDF has no readable text")

            return text

    except PDFSyntaxError:
        raise ValueError(
            "❌ This file is not a valid text-based PDF. "
            "Please upload a proper PDF (not scanned or renamed)."
        )

    except Exception:
        raise ValueError(
            "❌ Unable to read this PDF. "
            "It may be scanned, corrupted, or image-based."
        )
