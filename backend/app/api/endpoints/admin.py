import os
import shutil
import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_current_admin
from app.database.session import get_db
from app.models.models import Document, DocumentChunk
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store, ChunkMetadata

router = APIRouter(tags=["Admin"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".csv", ".md"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


@router.post("/admin/login", response_model=AdminLoginResponse)
def admin_login(payload: AdminLoginRequest):
    if (
        payload.username != settings.ADMIN_USERNAME
        or payload.password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_access_token(data={"sub": payload.username, "role": "admin"})
    return AdminLoginResponse(
        access_token=token,
        token_type="bearer",
        username=payload.username
    )


@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            original_name=d.original_name,
            category=d.category,
            file_type=d.file_type,
            file_size=d.file_size,
            chunk_count=d.chunk_count,
            status=d.status,
            version=d.version,
            created_at=d.created_at,
            updated_at=d.updated_at
        )
        for d in docs
    ]


@router.post("/admin/documents/upload", response_model=DocumentUploadResponse)
def upload_document(
    file: UploadFile = File(...),
    category: str = Form("General"),
    version: str = Form("1.0"),
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # 1. Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension '{ext}' is not supported. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 2. Sanitize filename
    safe_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", file.filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    save_path = os.path.join(settings.DOCUMENTS_DIR, unique_filename)
    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)

    # 3. Save file and enforce max size
    file_size = 0
    with open(save_path, "wb") as f:
        while chunk := file.file.read(1024 * 1024):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.remove(save_path)
                raise HTTPException(status_code=400, detail="File size exceeds maximum 25 MB limit.")
            f.write(chunk)

    # 4. Process document into chunks
    processor = DocumentProcessor()
    try:
        chunks = processor.process_file(save_path)
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"Failed to extract document: {str(e)}")

    if not chunks:
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=400, detail="Document appears to be empty or contains no readable text.")

    # 5. Save Document record to DB
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        filename=unique_filename,
        original_name=file.filename,
        category=category,
        file_path=save_path,
        file_type=ext.lstrip("."),
        file_size=file_size,
        chunk_count=len(chunks),
        status="processed",
        version=version
    )
    db.add(doc)
    db.commit()

    # 6. Save chunks to DB
    chunk_records = []
    chunk_texts = []
    chunk_metas = []

    for c in chunks:
        chunk_id = str(uuid.uuid4())
        chunk_rec = DocumentChunk(
            id=chunk_id,
            document_id=doc_id,
            chunk_index=c.chunk_index,
            content=c.content,
            page_number=c.page_number
        )
        chunk_records.append(chunk_rec)
        chunk_texts.append(c.content)

        chunk_metas.append(
            ChunkMetadata(
                chunk_id=chunk_id,
                document_id=doc_id,
                document_name=file.filename,
                category=category,
                page_number=c.page_number,
                chunk_index=c.chunk_index,
                content=c.content
            )
        )

    db.add_all(chunk_records)
    db.commit()

    # 7. Generate embeddings and add to Vector Store
    # Fit or update TF-IDF corpus if needed
    embedding_service.fit_corpus(chunk_texts)
    embeddings = embedding_service.embed_documents(chunk_texts)
    vector_store.add_chunks(embeddings, chunk_metas)

    doc_response = DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        original_name=doc.original_name,
        category=doc.category,
        file_type=doc.file_type,
        file_size=doc.file_size,
        chunk_count=doc.chunk_count,
        status=doc.status,
        version=doc.version,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )

    return DocumentUploadResponse(
        message=f"Document '{file.filename}' successfully processed and indexed.",
        document=doc_response,
        chunks_created=len(chunks)
    )


@router.delete("/admin/documents/{document_id}")
def delete_document(
    document_id: str,
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # 1. Remove from vector store
    vector_store.delete_document(document_id)

    # 2. Delete physical file if present
    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except Exception as e:
            print(f"[Admin] Warning: failed to delete file {doc.file_path}: {e}")

    # 3. Delete from DB (cascades to chunks)
    db.delete(doc)
    db.commit()

    return {"message": f"Document '{doc.original_name}' and its vector index deleted successfully."}


@router.post("/admin/reindex")
def reindex_all_documents(
    admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Rebuilds the entire vector index from active documents in the database."""
    docs = db.query(Document).filter(Document.status == "processed").all()
    vector_store.clear()

    processor = DocumentProcessor()
    total_chunks = 0
    all_texts = []
    all_metas = []

    for doc in docs:
        fpath = doc.file_path if (doc.file_path and os.path.exists(doc.file_path)) else os.path.join(settings.DOCUMENTS_DIR, doc.filename)
        if not os.path.exists(fpath):
            continue
        try:
            chunks = processor.process_file(fpath)
            for c in chunks:
                all_texts.append(c.content)
                all_metas.append(
                    ChunkMetadata(
                        chunk_id=str(uuid.uuid4()),
                        document_id=doc.id,
                        document_name=doc.original_name,
                        category=doc.category,
                        page_number=c.page_number,
                        chunk_index=c.chunk_index,
                        content=c.content
                    )
                )
        except Exception as e:
            print(f"[Reindex] Error processing {doc.filename}: {e}")

    if all_texts:
        embedding_service.fit_corpus(all_texts)
        embeddings = embedding_service.embed_documents(all_texts)
        vector_store.add_chunks(embeddings, all_metas)
        total_chunks = len(all_texts)

    return {
        "message": f"Vector index successfully rebuilt across {len(docs)} documents.",
        "documents_reindexed": len(docs),
        "total_chunks_indexed": total_chunks
    }
