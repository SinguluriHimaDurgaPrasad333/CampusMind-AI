import os
import re
import csv
from typing import List, Dict, Any, Tuple
import pypdf
from docx import Document as DocxDocument
from app.core.config import settings


class ProcessedChunk:
    def __init__(self, content: str, page_number: int, chunk_index: int, metadata: Dict[str, Any] = None):
        self.content = content
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.metadata = metadata or {}


class DocumentProcessor:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        # Remove null bytes and non-printable control characters
        text = text.replace("\x00", "")
        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Replace 3 or more newlines with two
        text = re.sub(r"\n{3,}", "\n\n", text)
        # Normalize multiple spaces and tabs to single spaces
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def extract_text(self, file_path: str) -> List[Tuple[str, int]]:
        """
        Extract text from file.
        Returns a list of tuples: (text_content, page_number).
        """
        ext = os.path.splitext(file_path)[1].lower()
        pages: List[Tuple[str, int]] = []

        if ext == ".pdf":
            try:
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    cleaned = self.clean_text(page_text)
                    if cleaned:
                        pages.append((cleaned, i + 1))
            except Exception as e:
                raise ValueError(f"Failed to extract PDF text from {file_path}: {e}")

        elif ext in [".docx", ".doc"]:
            try:
                doc = DocxDocument(file_path)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                # Also extract table text
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                        if row_text:
                            paragraphs.append(row_text)
                full_text = "\n\n".join(paragraphs)
                cleaned = self.clean_text(full_text)
                if cleaned:
                    pages.append((cleaned, 1))
            except Exception as e:
                raise ValueError(f"Failed to extract DOCX text from {file_path}: {e}")

        elif ext == ".csv":
            try:
                with open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.DictReader(f)
                    row_texts = []
                    for i, row in enumerate(reader):
                        row_str = ", ".join([f"{k}: {v}" for k, v in row.items() if v])
                        if row_str:
                            row_texts.append(f"[Record {i+1}] {row_str}")
                    full_text = "\n\n".join(row_texts)
                    cleaned = self.clean_text(full_text)
                    if cleaned:
                        pages.append((cleaned, 1))
            except Exception as e:
                raise ValueError(f"Failed to extract CSV text from {file_path}: {e}")

        elif ext in [".txt", ".md", ".json"]:
            try:
                with open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                cleaned = self.clean_text(content)
                if cleaned:
                    pages.append((cleaned, 1))
            except Exception as e:
                raise ValueError(f"Failed to extract text from {file_path}: {e}")

        else:
            # Fallback text reading
            try:
                with open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                cleaned = self.clean_text(content)
                if cleaned:
                    pages.append((cleaned, 1))
            except Exception as e:
                raise ValueError(f"Unsupported file format: {ext}")

        return pages

    def chunk_text(self, pages: List[Tuple[str, int]]) -> List[ProcessedChunk]:
        """
        Split extracted pages into overlapping, semantically coherent chunks.
        """
        all_chunks: List[ProcessedChunk] = []
        global_index = 0

        for text, page_num in pages:
            if not text:
                continue

            # Split recursively by paragraphs first
            paragraphs = text.split("\n\n")
            current_chunk = ""

            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                # If paragraph fits in current chunk
                if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                else:
                    # Flush current chunk if it has substantial content
                    if current_chunk:
                        all_chunks.append(
                            ProcessedChunk(
                                content=current_chunk,
                                page_number=page_num,
                                chunk_index=global_index
                            )
                        )
                        global_index += 1
                        # Retain overlap from end of current_chunk (snapping to word boundary)
                        overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                        if overlap_start > 0:
                            cand = [p for p in (current_chunk.find(" ", overlap_start), current_chunk.find("\n", overlap_start)) if p != -1 and p < len(current_chunk)]
                            if cand:
                                overlap_start = min(cand) + 1
                        overlap_text = current_chunk[overlap_start:].strip()
                        current_chunk = overlap_text + ("\n\n" if overlap_text else "") + para
                    else:
                        current_chunk = para

                    # If a single paragraph is larger than chunk_size, split by sentences
                    while len(current_chunk) > self.chunk_size:
                        split_point = self.chunk_size
                        # Try to find sentence boundary
                        sentence_break = current_chunk.rfind(". ", 0, self.chunk_size)
                        if sentence_break != -1 and sentence_break > self.chunk_size // 2:
                            split_point = sentence_break + 1
                        else:
                            # Try to find space
                            space_break = current_chunk.rfind(" ", 0, self.chunk_size)
                            if space_break != -1 and space_break > self.chunk_size // 3:
                                split_point = space_break

                        chunk_to_add = current_chunk[:split_point].strip()
                        if chunk_to_add:
                            all_chunks.append(
                                ProcessedChunk(
                                    content=chunk_to_add,
                                    page_number=page_num,
                                    chunk_index=global_index
                                )
                            )
                            global_index += 1

                        remainder = current_chunk[split_point:].strip()
                        overlap_start = max(0, len(chunk_to_add) - self.chunk_overlap)
                        if overlap_start > 0:
                            cand = [p for p in (chunk_to_add.find(" ", overlap_start), chunk_to_add.find("\n", overlap_start)) if p != -1 and p < len(chunk_to_add)]
                            if cand:
                                overlap_start = min(cand) + 1
                        overlap_text = chunk_to_add[overlap_start:].strip()
                        current_chunk = (overlap_text + " " if overlap_text else "") + remainder

            if current_chunk and current_chunk.strip():
                all_chunks.append(
                    ProcessedChunk(
                        content=current_chunk.strip(),
                        page_number=page_num,
                        chunk_index=global_index
                    )
                )
                global_index += 1

        return all_chunks

    def process_file(self, file_path: str) -> List[ProcessedChunk]:
        """Complete ingestion pipeline for a single file."""
        pages = self.extract_text(file_path)
        return self.chunk_text(pages)
