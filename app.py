"""
CampusAI - Flask Web Application
================================
Lightweight, beginner-friendly web application for university student assistance.
Powered by Flask, ChromaDB, SentenceTransformers, and RAG.
Runs natively locally (python app.py) and on Render (gunicorn app:app).
"""

import os
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import pandas as pd

from config import (
    DOCUMENTS_DIR,
    FAQS_FILE,
    EVALUATION_FILE,
    PROJECT_NAME,
    PROJECT_CODE,
    PROJECT_TAGLINE
)
from rag_pipeline import answer_student_query, ensure_knowledge_base_initialized
from vector_database import get_or_create_collection, index_document_chunks
from document_processor import process_document, detect_document_category
from faq_manager import load_all_faqs, get_faq_categories
from evaluation import load_evaluation_dataset, run_rag_evaluation

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.urandom(24)

import threading

# Initialize knowledge base asynchronously so Gunicorn binds to port instantly
def _init_knowledge_base():
    try:
        ensure_knowledge_base_initialized()
    except Exception as e:
        print(f"Knowledge base auto-init note: {e}")

threading.Thread(target=_init_knowledge_base, daemon=True).start()


# ----------------- PAGE ROUTES -----------------
@app.route("/")
def home():
    """Renders the Home landing page."""
    return render_template("home.html", active_page="home")


@app.route("/chat")
def chat():
    """Renders the AI Chatbot interface."""
    return render_template("chat.html", active_page="chat")


@app.route("/faqs")
def faqs_page():
    """Renders the Frequently Asked Questions page."""
    faqs_data = load_all_faqs()
    categories = get_faq_categories(faqs_data)
    return render_template("faqs.html", active_page="faqs", faqs=faqs_data, categories=categories)


@app.route("/knowledge-base")
def knowledge_base_page():
    """Renders the Knowledge Base management page."""
    doc_files = []
    if DOCUMENTS_DIR.exists():
        supported_exts = {".txt", ".pdf", ".docx", ".csv", ".json"}
        for p in sorted(DOCUMENTS_DIR.glob("*")):
            if p.suffix.lower() in supported_exts:
                doc_files.append({
                    "name": p.name,
                    "category": detect_document_category(p.name),
                    "extension": p.suffix.upper(),
                    "size_kb": round(p.stat().st_size / 1024, 1)
                })

    try:
        col = get_or_create_collection()
        total_chunks = col.count()
    except Exception:
        total_chunks = 0

    return render_template(
        "knowledge_base.html",
        active_page="kb",
        documents=doc_files,
        total_chunks=total_chunks
    )


@app.route("/evaluation")
def evaluation_page():
    """Renders the RAG Evaluation Benchmark Dashboard."""
    try:
        df_eval = load_evaluation_dataset()
        questions = df_eval.to_dict(orient="records")
    except Exception:
        questions = []

    return render_template("evaluation.html", active_page="eval", questions=questions)


@app.route("/about")
def about_page():
    """Renders the Project Details and Viva Notes page."""
    return render_template("about.html", active_page="about")


# ----------------- REST API ENDPOINTS -----------------
@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for student questions."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "query": "",
            "answer": "Please ask a question or say hello!",
            "sources": [],
            "latency_ms": 0.0,
            "provider": "Validation Guard"
        })

    result = answer_student_query(query)
    return jsonify(result)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Handles document upload and auto-indexing into ChromaDB."""
    if "document" not in request.files:
        flash("No file part provided", "error")
        return redirect(url_for("knowledge_base_page"))

    file = request.files["document"]
    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("knowledge_base_page"))

    filename = file.filename
    target_path = DOCUMENTS_DIR / filename
    file.save(str(target_path))

    # Process and index
    try:
        chunks = process_document(target_path)
        if chunks:
            index_document_chunks(chunks)
            flash(f"Successfully uploaded and indexed {filename} ({len(chunks)} chunks)!", "success")
        else:
            flash(f"Uploaded {filename}, but no text chunks could be extracted.", "warning")
    except Exception as e:
        flash(f"Error processing {filename}: {str(e)}", "error")

    return redirect(url_for("knowledge_base_page"))


@app.route("/api/evaluate", methods=["POST"])
def api_evaluate():
    """Executes live benchmark evaluation and returns KPI metrics."""
    try:
        results = run_rag_evaluation(limit=10)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e), "summary": {}}), 500


# ----------------- MAIN ENTRYPOINT -----------------
if __name__ == "__main__":
    # Local development server
    port = int(os.environ.get("PORT", 8501))
    print(f"Starting CampusAI Flask application on http://localhost:{port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
