"""
CampusAI - Document Processing Module
=====================================
Handles document ingestion, text extraction across formats (PDF, DOCX, TXT, CSV, JSON),
overlapping recursive text chunking, and metadata preservation.
Written with simple, beginner-friendly Python functions suitable for viva presentation.
"""

import os
import json
import csv
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import pypdf
import docx
from config import CHUNK_SIZE, CHUNK_OVERLAP


def compute_file_hash(file_bytes: bytes) -> str:
    """
    Computes SHA-256 hash of file bytes.
    Used to prevent duplicate document indexing in ChromaDB.
    """
    return hashlib.sha256(file_bytes).hexdigest()


def detect_document_category(filename: str) -> str:
    """
    Infers document category from filename or returns 'General Policies'.
    Helps categorize institutional notices, syllabuses, and regulations.
    """
    fname_lower = filename.lower()
    if "attendance" in fname_lower:
        return "Attendance Policies"
    elif "exam" in fname_lower or "grading" in fname_lower:
        return "Examination Guidelines"
    elif "hostel" in fname_lower or "disciplinary" in fname_lower:
        return "Hostel & Campus Life"
    elif "scholarship" in fname_lower:
        return "Scholarship Information"
    elif "fee" in fname_lower or "refund" in fname_lower:
        return "Fee & Financial Policies"
    elif "syllabus" in fname_lower or "curriculum" in fname_lower or "course" in fname_lower:
        return "Course Syllabus & Academics"
    elif "calendar" in fname_lower or "schedule" in fname_lower:
        return "Academic Calendars"
    elif "faq" in fname_lower:
        return "Administrative FAQs"
    return "University Regulations"


def extract_pdf_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts text from a PDF file page-by-page using pypdf.
    Returns a list of dicts with 'page' number and extracted 'text'.
    Handles scanned or image-only PDFs with a helpful notice.
    """
    pages_data = []
    try:
        reader = pypdf.PdfReader(str(file_path))
        for page_idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            pages_data.append({
                "page": page_idx + 1,
                "text": page_text
            })

        total_extracted = sum(len(p["text"]) for p in pages_data)
        if total_extracted == 0 and len(reader.pages) > 0:
            pages_data.append({
                "page": 1,
                "text": "Note: This PDF appears to be a scanned image or contains no extractable text. "
                        "OCR text extraction is not enabled in this basic version."
            })
    except Exception as e:
        pages_data.append({
            "page": 1,
            "text": f"Error extracting PDF: {str(e)}"
        })
    return pages_data


def extract_docx_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts text from a Microsoft Word (.docx) document using python-docx.
    Aggregates paragraphs and tables into structured text.
    """
    try:
        doc = docx.Document(str(file_path))
        full_text = []

        # Read paragraphs
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)

        # Read tables if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_text.append(row_text)

        combined = "\n\n".join(full_text)
        return [{"page": 1, "text": combined}]
    except Exception as e:
        return [{"page": 1, "text": f"Error extracting DOCX: {str(e)}"}]


def extract_txt_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Reads plain text or markdown documents using utf-8 with fallback encodings.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()
    return [{"page": 1, "text": content.strip()}]


def extract_csv_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts rows from CSV files and formats each row as readable key-value sentences.
    """
    rows_text = []
    try:
        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                line = ", ".join(f"{k}: {v}" for k, v in row.items() if k and v)
                if line:
                    rows_text.append(f"Row {idx+1}: {line}")
        return [{"page": 1, "text": "\n".join(rows_text)}]
    except Exception as e:
        return [{"page": 1, "text": f"Error extracting CSV: {str(e)}"}]


def extract_json_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extracts structured content from JSON files and pretty-formats it.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        formatted = json.dumps(data, indent=2)
        return [{"page": 1, "text": formatted}]
    except Exception as e:
        return [{"page": 1, "text": f"Error extracting JSON: {str(e)}"}]


def extract_document_text(file_path: Path) -> List[Dict[str, Any]]:
    """
    Master extraction function that routes to appropriate extractor
    based on file extension (.pdf, .docx, .txt, .csv, .json).
    """
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf_text(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_docx_text(file_path)
    elif ext in [".txt", ".md"]:
        return extract_txt_text(file_path)
    elif ext == ".csv":
        return extract_csv_text(file_path)
    elif ext == ".json":
        return extract_json_text(file_path)
    else:
        # Fallback to plain text
        return extract_txt_text(file_path)


def split_text_into_chunks(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[str]:
    """
    Splits long text into overlapping chunks.
    Prefers splitting at natural paragraph and sentence boundaries.
    Ensures context continuity across chunk boundaries using chunk_overlap.
    """
    if not text or len(text.strip()) == 0:
        return []

    # If text is already shorter than chunk size, return as a single chunk
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size

        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Look for nearest sentence or paragraph break before chunk_size
        break_pos = -1
        for delim in ["\n\n", "\n", ". ", "? ", "! ", "; "]:
            pos = text.rfind(delim, start + (chunk_size // 2), end)
            if pos != -1:
                break_pos = pos + len(delim)
                break

        if break_pos != -1:
            chunk = text[start:break_pos].strip()
            if chunk:
                chunks.append(chunk)
            # Advance start with overlap
            start = max(start + 1, break_pos - chunk_overlap)
        else:
            # Hard split if no boundary delimiter found
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - chunk_overlap

    return chunks


def process_document(
    file_path: Path,
    category: Optional[str] = None,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Full document processing pipeline:
    1. Reads bytes to generate file hash.
    2. Extracts text page-by-page.
    3. Splits text into overlapping chunks.
    4. Attaches full provenance metadata to each chunk.
    """
    filename = file_path.name
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    file_hash = compute_file_hash(file_bytes)
    doc_category = category or detect_document_category(filename)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    extracted_pages = extract_document_text(file_path)
    all_chunks = []

    global_chunk_idx = 0
    for page_item in extracted_pages:
        page_num = page_item["page"]
        page_text = page_item["text"]

        text_chunks = split_text_into_chunks(page_text, chunk_size, chunk_overlap)
        for chunk in text_chunks:
            if not chunk or len(chunk.strip()) < 15:
                continue

            chunk_id = f"{filename}_p{page_num}_c{global_chunk_idx}"
            all_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk,
                "metadata": {
                    "source": filename,
                    "page": page_num,
                    "category": doc_category,
                    "upload_timestamp": timestamp,
                    "file_hash": file_hash,
                    "chunk_index": global_chunk_idx
                }
            })
            global_chunk_idx += 1

    return all_chunks
