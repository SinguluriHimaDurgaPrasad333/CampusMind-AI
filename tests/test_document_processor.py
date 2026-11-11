"""
Tests for Document Processing and Chunking Module
"""

import pytest
from pathlib import Path
from document_processor import (
    split_text_into_chunks,
    compute_file_hash,
    detect_document_category,
    extract_document_text
)


def test_compute_file_hash():
    data1 = b"Sample university policy text"
    data2 = b"Sample university policy text"
    data3 = b"Different policy text"

    assert compute_file_hash(data1) == compute_file_hash(data2)
    assert compute_file_hash(data1) != compute_file_hash(data3)


def test_detect_document_category():
    assert detect_document_category("Attendance_Regulations_2025.txt") == "Attendance Policies"
    assert detect_document_category("Examination_Guidelines.pdf") == "Examination Guidelines"
    assert detect_document_category("Hostel_Rules.docx") == "Hostel & Campus Life"
    assert detect_document_category("Merit_Scholarship.txt") == "Scholarship Information"
    assert detect_document_category("CS_Syllabus.pdf") == "Course Syllabus & Academics"
    assert detect_document_category("Unknown_Notice.txt") == "University Regulations"


def test_split_text_into_chunks_short_text():
    short_text = "The minimum attendance requirement is 75% across all lectures."
    chunks = split_text_into_chunks(short_text, chunk_size=300, chunk_overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_split_text_into_chunks_long_text():
    # Long text with multiple sentences
    long_text = "Sentence one is about attendance. " * 30
    chunks = split_text_into_chunks(long_text, chunk_size=200, chunk_overlap=40)
    assert len(chunks) > 1
    # Check that each chunk is within bounds
    for c in chunks:
        assert len(c) <= 250
