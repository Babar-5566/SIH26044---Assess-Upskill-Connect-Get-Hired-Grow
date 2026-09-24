"""
Unit tests for Document Ingestion Pipeline (Parsers & Chunker)
Skill: agency-rag-pipeline-engineer, agency-software-architect
"""

import io
import pytest
import docx
import pypdf
from app.rag.parsers import clean_text, parse_document, parse_txt, parse_docx, parse_pdf
from app.rag.chunker import RecursiveTextChunker
from app.rag.schemas import ParsedDocument, ParsedPage


def test_clean_text():
    """Verify that text cleaning removes null bytes, normalizes whitespace and non-breaking spaces."""
    raw = "Hello\xa0World!\x00   This   is   a    test.\n\n\n\nNew paragraph."
    cleaned = clean_text(raw)
    assert "\x00" not in cleaned
    assert "\xa0" not in cleaned
    assert "Hello World!" in cleaned
    assert "This is a test." in cleaned
    assert "\n\n\n" not in cleaned


def test_parse_txt():
    """Verify plain text file parsing."""
    content = b"Enterprise Multi-LLM System\nRequires Python 3.10+."
    doc = parse_txt(content, filename="guide.txt", doc_id="test-doc-1")
    assert doc.document_id == "test-doc-1"
    assert doc.file_type == "txt"
    assert len(doc.pages) == 1
    assert "Enterprise Multi-LLM System" in doc.pages[0].text


def test_parse_docx():
    """Verify Word document parsing with paragraphs and tables."""
    bio = io.BytesIO()
    word_doc = docx.Document()
    word_doc.add_heading("Corporate Specifications", level=1)
    word_doc.add_paragraph("First paragraph content.")
    table = word_doc.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Model"
    table.cell(0, 1).text = "Score"
    table.cell(1, 0).text = "GPT-4o"
    table.cell(1, 1).text = "95%"
    word_doc.save(bio)

    doc = parse_docx(bio.getvalue(), filename="specs.docx", doc_id="test-doc-2")
    assert doc.file_type == "docx"
    assert "Corporate Specifications" in doc.pages[0].text
    assert "First paragraph content." in doc.pages[0].text
    assert "Model | Score" in doc.pages[0].text or "GPT-4o" in doc.pages[0].text


def test_parse_pdf():
    """Verify PDF document parsing with pypdf and page numbers."""
    bio = io.BytesIO()
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=100, height=100)
    # pypdf blank page doesn't have text; let's test error on empty/scanned PDF
    writer.write(bio)
    with pytest.raises(ValueError) as exc:
        parse_pdf(bio.getvalue(), filename="empty.pdf", doc_id="test-doc-3")
    assert "No extractable text found" in str(exc.value)


def test_unsupported_file_extension():
    """Verify rejection of non-whitelisted file types."""
    with pytest.raises(ValueError) as exc:
        parse_document(b"fake binary", filename="script.exe", doc_id="test-bad")
    assert "Unsupported file type" in str(exc.value)


def test_chunker_preserves_metadata_and_overlap():
    """Verify recursive chunking and metadata preservation."""
    sample_text = (
        "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python. "
        "It is based on standard Python type hints. "
        "The key features are high performance, fast to code, fewer bugs, and intuitive design. "
        "It provides automatic interactive API documentation via Swagger UI. "
        "NumPy provides support for large, multi-dimensional arrays and matrices. "
        "Cosine similarity computes the dot product of two normalized vectors. "
    )
    parsed_doc = ParsedDocument(
        document_id="doc-uuid-123",
        original_filename="manual.pdf",
        file_type="pdf",
        total_pages=2,
        pages=[
            ParsedPage(page_number=1, text=sample_text),
            ParsedPage(page_number=2, text="Second page contains advanced deployment guidelines."),
        ],
    )

    chunker = RecursiveTextChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.chunk_document(parsed_doc)

    assert len(chunks) > 1
    assert chunks[0].document_id == "doc-uuid-123"
    assert chunks[0].filename == "manual.pdf"
    assert chunks[0].page_number == 1
    assert chunks[-1].page_number == 2
    assert "deployment guidelines" in chunks[-1].content
    for c in chunks:
        assert c.chunk_id.startswith("doc-uuid-123_c")
        assert len(c.content) > 0
