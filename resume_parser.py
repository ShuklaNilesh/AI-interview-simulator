import io
import PyPDF2
import docx

class ResumeParser:
    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        filename_lower = filename.lower()
        try:
            if filename_lower.endswith(".pdf"):
                return ResumeParser._extract_pdf(file_bytes)
            elif filename_lower.endswith(".docx"):
                return ResumeParser._extract_docx(file_bytes)
            else:
                # Default text decoding
                return file_bytes.decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Error extracting text from file: {str(e)}"

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        text = ""
        pdf_file = io.BytesIO(file_bytes)
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
        return text

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> str:
        text = ""
        docx_file = io.BytesIO(file_bytes)
        try:
            doc = docx.Document(docx_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"DOCX extraction failed: {str(e)}")
        return text
