"""
Document Parsers with Page & Metadata Tracking
Skill: agency-rag-pipeline-engineer, agency-application-security-engineer
"""

import io
import re
from typing import List
import pypdf
import docx
from app.rag.schemas import ParsedDocument, ParsedPage


def clean_text(text: str) -> str:
    """
    Cleans raw extracted text:
    - Normalizes non-breaking spaces and control characters
    - Strips NULL bytes
    - Normalizes excessive blank lines and spaces while preserving paragraph boundaries
    """
    if not text:
        return ""
    # Replace non-breaking spaces and null bytes
    text = text.replace("\xa0", " ").replace("\x00", "")
    # Remove surrogate characters
    text = re.sub(r"[\ud800-\udfff]", "", text)
    # Replace multiple spaces with a single space (except newlines)
    text = re.sub(r"[ \t]+", " ", text)
    # Normalize 3+ newlines to double newline
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_pdf(file_bytes: bytes, filename: str, doc_id: str) -> ParsedDocument:
    """
    Extracts text page-by-page from PDF bytes using pypdf.
    Maintains 1-indexed page numbering for accurate citation generation.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(f"Unable to read PDF file: Corrupted or invalid format ({str(exc)})")

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("PDF is encrypted or password-protected and cannot be processed.")

    pages: List[ParsedPage] = []
    for idx, page in enumerate(reader.pages):
        try:
            page_text = page.extract_text() or ""
            cleaned = clean_text(page_text)
            if cleaned:
                pages.append(ParsedPage(page_number=idx + 1, text=cleaned))
        except Exception:
            continue

    if not pages:
        raise ValueError("No extractable text found in PDF. The document may be scanned images without OCR.")

    return ParsedDocument(
        document_id=doc_id,
        original_filename=filename,
        file_type="pdf",
        total_pages=len(reader.pages),
        pages=pages,
    )


def parse_docx(file_bytes: bytes, filename: str, doc_id: str) -> ParsedDocument:
    """
    Extracts text from Word DOCX paragraphs and tables.
    """
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ValueError(f"Unable to read DOCX file: Corrupted or invalid format ({str(exc)})")

    extracted_parts: List[str] = []

    # Extract standard paragraphs
    for p in doc.paragraphs:
        cleaned_para = clean_text(p.text)
        if cleaned_para:
            extracted_parts.append(cleaned_para)

    # Extract tables
    for table in doc.tables:
        for row in table.rows:
            row_cells = [clean_text(cell.text) for cell in row.cells if clean_text(cell.text)]
            if row_cells:
                extracted_parts.append(" | ".join(row_cells))

    full_text = "\n\n".join(extracted_parts)
    if not full_text.strip():
        raise ValueError("No extractable text found in Word (.docx) document.")

    return ParsedDocument(
        document_id=doc_id,
        original_filename=filename,
        file_type="docx",
        total_pages=1,
        pages=[ParsedPage(page_number=1, text=full_text)],
    )


def parse_txt(file_bytes: bytes, filename: str, doc_id: str) -> ParsedDocument:
    """
    Extracts plain text with encoding fallbacks (UTF-8, Latin-1, CP1252).
    """
    text = ""
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("Text document (.txt) is empty or could not be decoded.")

    return ParsedDocument(
        document_id=doc_id,
        original_filename=filename,
        file_type="txt",
        total_pages=1,
        pages=[ParsedPage(page_number=1, text=cleaned)],
    )


def parse_document(file_bytes: bytes, filename: str, doc_id: str) -> ParsedDocument:
    """
    Master entrypoint: extracts text according to file extension with security checks.
    """
    filename_lower = filename.lower().strip()
    if filename_lower.endswith(".pdf"):
        return parse_pdf(file_bytes, filename, doc_id)
    elif filename_lower.endswith(".docx"):
        return parse_docx(file_bytes, filename, doc_id)
    elif filename_lower.endswith(".txt"):
        return parse_txt(file_bytes, filename, doc_id)
    else:
        raise ValueError(f"Unsupported file type for '{filename}'. Only .pdf, .docx, and .txt are permitted.")
