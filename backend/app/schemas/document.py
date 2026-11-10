from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class DocumentChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    page_number: int


class DocumentResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    category: str
    file_type: str
    file_size: int
    chunk_count: int
    status: str
    version: str
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse
    chunks_created: int
