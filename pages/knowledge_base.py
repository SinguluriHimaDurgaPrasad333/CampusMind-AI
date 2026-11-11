"""
CampusAI - Knowledge Base Management Page
=========================================
Admin-secured interface for uploading, chunking, indexing, and deleting
institutional documents (PDF, DOCX, TXT, CSV, JSON) in ChromaDB.
Includes educational RAG processing graphic for viva demonstrations.
"""

import os
import re
from pathlib import Path
import streamlit as st
import pandas as pd
from config import DOCUMENTS_DIR, UNVERIFIED_FALLBACK_MESSAGE
from auth import is_admin_authenticated, login_admin, logout_admin
from document_processor import process_document
from vector_database import (
    index_document_chunks,
    delete_document_by_filename,
    get_indexed_documents_stats,
    get_or_create_collection,
    reset_collection
)
from rag_pipeline import ensure_knowledge_base_initialized


def sanitize_filename(filename: str) -> str:
    """Sanitizes uploaded filename to prevent directory traversal attacks."""
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", Path(filename).name)
    return clean.strip("._") or "uploaded_document.txt"


def render_knowledge_base_page():
    """Renders the Knowledge Base management and RAG pipeline inspector."""
    ensure_knowledge_base_initialized()

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #1E293B;">🗂️ University Knowledge Base</h2>
            <p style="color: #64748B; margin-top: 4px; font-size: 0.95rem;">
                Explore indexed academic documents, inspect vector database status, and manage knowledge corpus.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Educational RAG Processing Graphic (Crucial for Viva!)
    st.markdown("<h4>Educational RAG Ingestion Pipeline</h4>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 18px; padding: 20px; box-shadow: 0 4px 15px rgba(37,99,235,0.05); margin-bottom: 24px;">
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 130px; text-align: center; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 12px 8px;">
                    <div style="font-size: 1.5rem;">📄</div>
                    <strong style="color: #1E40AF; font-size: 0.85rem;">DOCUMENT UPLOAD</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">PDF, DOCX, TXT, CSV</div>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="flex: 1; min-width: 130px; text-align: center; background: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 12px 8px;">
                    <div style="font-size: 1.5rem;">🔍</div>
                    <strong style="color: #6D28D9; font-size: 0.85rem;">TEXT EXTRACTION</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">pypdf &amp; python-docx</div>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="flex: 1; min-width: 130px; text-align: center; background: #ECFDF5; border: 1px solid #A7F3D0; border-radius: 12px; padding: 12px 8px;">
                    <div style="font-size: 1.5rem;">✂️</div>
                    <strong style="color: #065F46; font-size: 0.85rem;">TEXT CHUNKING</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">800c size, 120c overlap</div>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="flex: 1; min-width: 130px; text-align: center; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 12px; padding: 12px 8px;">
                    <div style="font-size: 1.5rem;">🧠</div>
                    <strong style="color: #92400E; font-size: 0.85rem;">EMBEDDINGS</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">all-MiniLM-L6-v2</div>
                </div>
                <div style="color: #94A3B8; font-weight: bold;">➔</div>
                <div style="flex: 1; min-width: 130px; text-align: center; background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 12px; padding: 12px 8px;">
                    <div style="font-size: 1.5rem;">🗄️</div>
                    <strong style="color: #166534; font-size: 0.85rem;">CHROMADB</strong>
                    <div style="font-size: 0.72rem; color: #64748B;">Cosine Vector Index</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # High-level Knowledge Base Metrics
    docs_stats = get_indexed_documents_stats()
    total_docs = len(docs_stats)
    total_chunks = sum(d["chunks_count"] for d in docs_stats)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Indexed Documents</div>
                <div class="metric-value">{total_docs}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Total Text Chunks</div>
                <div class="metric-value">{total_chunks}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Vector Dimension</div>
                <div class="metric-value">384</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Document Table (Student & Public View)
    st.markdown("<h4>Current University Documents in Vector Store</h4>", unsafe_allow_html=True)
    if docs_stats:
        df_docs = pd.DataFrame(docs_stats)
        df_docs.columns = ["Filename", "Category", "Upload Date", "Chunks Count", "Status"]
        st.dataframe(df_docs, use_container_width=True, hide_index=True)
    else:
        st.info("No documents are currently indexed in ChromaDB.")

    st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    # Administrator Document Management (Secured)
    st.markdown("<h4>🔒 Administrator Document Management</h4>", unsafe_allow_html=True)

    if not is_admin_authenticated():
        st.info("Administrative privileges are required to upload, re-index, or delete university documents.")
        with st.form("admin_login_form"):
            col_pwd, col_submit = st.columns([2, 1])
            with col_pwd:
                admin_pwd = st.text_input("Enter Administrator Password:", type="password", placeholder="Default: admin123")
            with col_submit:
                st.write("")
                st.write("")
                login_pressed = st.form_submit_button("🔑 Authenticate Admin", use_container_width=True)

            if login_pressed:
                if login_admin(admin_pwd):
                    st.success("Admin authenticated successfully!")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please verify your administrator credentials.")
        return

    # Admin is authenticated
    st.success("Admin Mode: Active. You have full access to upload, re-index, and manage documents.")
    if st.button("🚪 Log Out of Admin Mode", type="secondary"):
        logout_admin()
        st.rerun()

    tab_upload, tab_manage = st.tabs(["📤 Upload New Documents", "⚙️ Re-index & Delete Operations"])

    with tab_upload:
        st.markdown("<p style='color: #64748B;'>Select one or multiple files (.pdf, .docx, .txt, .csv, .json) to ingest:</p>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload University Documents",
            type=["pdf", "docx", "txt", "csv", "json"],
            accept_multiple_files=True
        )

        if uploaded_files:
            if st.button("🚀 Process & Index Uploaded Documents", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                total_files = len(uploaded_files)
                newly_indexed = 0

                for idx, file in enumerate(uploaded_files):
                    clean_name = sanitize_filename(file.name)
                    status_text.text(f"Processing ({idx+1}/{total_files}): {clean_name}...")

                    # Save file safely to DOCUMENTS_DIR
                    save_path = DOCUMENTS_DIR / clean_name
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())

                    # Process and chunk
                    chunks = process_document(save_path)
                    if chunks:
                        count = index_document_chunks(chunks)
                        newly_indexed += count

                    progress_bar.progress((idx + 1) / total_files)

                status_text.text("Processing complete!")
                st.success(f"Successfully processed {total_files} file(s) and created {newly_indexed} new vectors in ChromaDB!")
                st.rerun()

    with tab_manage:
        col_del, col_reset = st.columns(2)

        with col_del:
            st.markdown("<h5>Delete Document from Vector Store</h5>", unsafe_allow_html=True)
            doc_filenames = [d["filename"] for d in docs_stats]
            if doc_filenames:
                doc_to_delete = st.selectbox("Select document to delete:", options=doc_filenames)
                if st.button("🗑️ Delete Selected Document", type="secondary"):
                    deleted_chunks = delete_document_by_filename(doc_to_delete)
                    # Also remove physical file if exists
                    file_path = DOCUMENTS_DIR / doc_to_delete
                    if file_path.exists():
                        try:
                            file_path.unlink()
                        except Exception:
                            pass
                    st.warning(f"Deleted '{doc_to_delete}' ({deleted_chunks} chunks removed from ChromaDB).")
                    st.rerun()
            else:
                st.caption("No documents available to delete.")

        with col_reset:
            st.markdown("<h5>Rebuild & Reset Collection</h5>", unsafe_allow_html=True)
            st.caption("Re-indexes all existing documents in data/documents/ from scratch.")
            if st.button("🔄 Rebuild Vector Index", type="secondary"):
                reset_collection()
                count = ensure_knowledge_base_initialized()
                st.success(f"Vector index successfully rebuilt with {count} chunks!")
                st.rerun()


# Render page directly when executed
render_knowledge_base_page()
