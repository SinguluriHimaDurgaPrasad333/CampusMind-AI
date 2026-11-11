"""
CampusAI - Configuration Module
===============================
Provides centralized configuration settings, file paths, model parameters,
and environment variable bindings for CampusAI.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Enforce offline mode for Hugging Face Hub & Transformers (avoids connection retries)
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# Load environment variables from .env file if available
load_dotenv()

# Base Directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
SAMPLE_DOCUMENTS_DIR = DATA_DIR / "sample_documents"
CHROMA_DIR = BASE_DIR / "chroma_db"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure essential directories exist
for path in [DATA_DIR, DOCUMENTS_DIR, SAMPLE_DOCUMENTS_DIR, CHROMA_DIR, ASSETS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Data Files
FAQS_FILE = DATA_DIR / "faqs.csv"
EVALUATION_FILE = DATA_DIR / "evaluation_questions.csv"

# Project Metadata
PROJECT_NAME = "CampusAI – AI Student Assistance Chatbot"
PROJECT_CODE = "P08"
PROJECT_REFERENCE = "SIH 2024 – SIH1631: AI-Powered Student Assistance Chatbot"
PROJECT_TAGLINE = "Your Smart Companion for University Life"
APP_VERSION = "2.0.0"

# RAG & Chunking Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))
# ChromaDB cosine distance range is [0, 2], where 0 is identical.
# Normalized similarity = 1 - (distance / 2) or Cosine similarity = 1 - distance.
# Chunks with distance > COSINE_DISTANCE_THRESHOLD are considered unsupported.
COSINE_DISTANCE_THRESHOLD = float(os.getenv("COSINE_DISTANCE_THRESHOLD", "0.55"))

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "campusai_knowledge")

# LLM Configuration
# Modes: "auto", "ollama", "gemini", "extractive"
LLM_MODE = os.getenv("LLM_MODE", "auto")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Admin Security (Demonstration Password Hash)
# Default password is 'admin123' (SHA-256 hash)
DEFAULT_ADMIN_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", DEFAULT_ADMIN_HASH)

# Fallback response for unanswerable / low-confidence queries
UNVERIFIED_FALLBACK_MESSAGE = (
    "I couldn't find reliable information about this in the available university documents. "
    "Please check the official university website or contact the relevant department."
)
