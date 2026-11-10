import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.models.models import Document, DocumentChunk
from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import embedding_service
from app.rag.vector_store import vector_store, ChunkMetadata
from app.api.router import api_router


def seed_initial_knowledge_base():
    """Seed and index initial university documents on first launch."""
    db = SessionLocal()
    try:
        existing_count = db.query(Document).count()
        if existing_count > 0 and len(vector_store.metadata_store) > 0:
            print(f"[CampusMind AI] Knowledge base already initialized ({existing_count} documents).")
            return

        docs_dir = settings.DOCUMENTS_DIR
        if not os.path.exists(docs_dir):
            return

        files = [f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f))]
        if not files:
            return

        print(f"[CampusMind AI] Auto-indexing {len(files)} initial university documents...")
        processor = DocumentProcessor()
        all_texts = []
        all_metas = []

        # Category mapping heuristics
        category_map = {
            "attendance": "Attendance Policies",
            "calendar": "Academic Calendars",
            "exam": "Examination Guidelines",
            "hostel": "Hostel Rules and Regulations",
            "scholarship": "Scholarship Information",
            "fee": "Fee-related Policies",
            "syllabus": "University Syllabus and Course Details",
            "faq": "Frequently Asked Questions (FAQs) & Administrative Policies"
        }

        for fname in sorted(files):
            file_path = os.path.join(docs_dir, fname)
            file_size = os.path.getsize(file_path)
            ext = os.path.splitext(fname)[1].lower().lstrip(".")

            category = "General Academic Policy"
            for k, cat in category_map.items():
                if k in fname.lower():
                    category = cat
                    break

            try:
                chunks = processor.process_file(file_path)
                if not chunks:
                    continue

                doc_id = str(uuid.uuid4())
                existing_doc = db.query(Document).filter(Document.filename == fname).first()
                if not existing_doc:
                    doc = Document(
                        id=doc_id,
                        filename=fname,
                        original_name=fname,
                        category=category,
                        file_path=file_path,
                        file_type=ext,
                        file_size=file_size,
                        chunk_count=len(chunks),
                        status="processed",
                        version="1.0"
                    )
                    db.add(doc)
                    db.commit()
                else:
                    doc_id = existing_doc.id

                for c in chunks:
                    chunk_id = str(uuid.uuid4())
                    all_texts.append(c.content)
                    meta = ChunkMetadata(
                        chunk_id=chunk_id,
                        document_id=doc_id,
                        document_name=fname,
                        category=category,
                        page_number=c.page_number,
                        chunk_index=c.chunk_index,
                        content=c.content
                    )
                    all_metas.append(meta)

                    # Also store in DocumentChunk DB table if not present
                    if not existing_doc:
                        chunk_rec = DocumentChunk(
                            id=chunk_id,
                            document_id=doc_id,
                            chunk_index=c.chunk_index,
                            content=c.content,
                            page_number=c.page_number
                        )
                        db.add(chunk_rec)

                if not existing_doc:
                    db.commit()

            except Exception as e:
                print(f"[CampusMind AI] Error indexing {fname}: {e}")

        if all_texts:
            embedding_service.fit_corpus(all_texts)
            embeddings = embedding_service.embed_documents(all_texts)
            vector_store.clear()
            vector_store.add_chunks(embeddings, all_metas)
            print(f"[CampusMind AI] Successfully indexed {len(all_metas)} chunks into vector store.")

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup:
    print(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode...")
    init_db()
    seed_initial_knowledge_base()
    yield
    # Shutdown
    print(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent University Student Assistant Using Retrieval-Augmented Generation (RAG)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development and Vite frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Mount Frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    from starlette.responses import FileResponse

    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": "1.0.0",
            "status": "online",
            "description": "Production-style RAG-powered University Student Assistant",
            "documentation": "/docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
