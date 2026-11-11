# CampusAI – AI Student Assistance Chatbot

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-2563EB.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-orange.svg)](https://www.trychroma.com/)
[![Sentence%20Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-7C3AED.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![License](https://img.shields.io/badge/License-MIT-059669.svg)](LICENSE)

**Project Code:** P08  
**Project Title:** AI Student Assistance Chatbot  
**Competition / Reference:** SIH 2024 – SIH1631: AI-Powered Student Assistance Chatbot  
**Author:** B.Tech Computer Science & Engineering (AI & ML)  
**Tagline:** *"Your Smart Companion for University Life"*

---

## 📖 1. Project Overview & Objective

University students routinely struggle to find authentic, verified information across dozens of academic circulars, complex syllabuses, examination codes, hostel rules, and scholarship criteria. Generic AI chatbots (like standard ChatGPT) hallucinate dates, fabricated rules, and fake phone numbers because they do not have access to institutional documents.

**CampusAI** solves this challenge by implementing a genuine **Retrieval-Augmented Generation (RAG)** pipeline:
1. When a student asks an academic question, CampusAI retrieves the exact authoritative policy passages from university documents stored in **ChromaDB**.
2. It generates a verified answer **strictly grounded** in the retrieved passages.
3. Every response cites the **exact source document and page number**.
4. If an inquiry cannot be answered from the available documents (e.g. out-of-domain questions), CampusAI safely abstains rather than inventing fake information.

---

## 🎨 2. Modern Educational Light Theme UI

CampusAI adheres strictly to an educational **Modern Light Theme** designed to look like a university learning platform:

| Element | Color Code | Purpose |
| :--- | :--- | :--- |
| **Main Background** | `#F8FAFF` | Clean, soft canvas without eye strain |
| **Primary Blue** | `#2563EB` | Professional university brand accents & primary buttons |
| **Sky Blue** | `#60A5FA` | Borders, hover states, active indicators |
| **Light Blue** | `#DBEAFE` | Soft card headers and student chat bubbles |
| **Soft Purple** | `#EDE9FE` | Educational badges and AI highlights |
| **Mint Green** | `#D1FAE5` | "Ready to help" status pills and success indicators |
| **White Cards** | `#FFFFFF` | Elevated rounded cards with subtle drop shadows |
| **Main Text** | `#1E293B` | High-contrast, readable slate typography |
| **Secondary Text**| `#64748B` | Subtle metadata, timestamps, and subtitles |

---

## 🏛️ 3. Technology Stack

- **Programming Language:** Python 3.11, 3.12, or 3.13
- **Frontend / Web UI:** Streamlit with custom CSS and SVG illustrations
- **Dense Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional vector space)
- **Vector Database:** `ChromaDB` (Local persistent storage with HNSW cosine distance metric)
- **Document Processing:** `pypdf` (PDF extraction), `python-docx` (Word DOCX), standard `csv` & `json`
- **Dashboard & Analytics:** Plotly Express & Graph Objects
- **LLM Options:**
  - **Local Free LLM:** Ollama (`llama3.2` / `mistral` / `llama3`) running locally on port 11434
  - **Cloud API LLM:** Google Gemini API (`gemini-2.0-flash` or `gemini-1.5-flash`)
  - **Extractive Search Fallback:** 100% offline, zero-dependency extractive synthesis mode

---

## 📂 4. Project Folder Structure

```
AI PROJECT/
├── app.py                          # Master Streamlit entrypoint and page router
├── config.py                       # Centralized configuration, paths, and thresholds
├── rag_pipeline.py                 # Core RAG retrieval, threshold filter, and citations
├── document_processor.py           # Multi-format text extractor (PDF, DOCX, TXT, CSV, JSON)
├── vector_database.py              # ChromaDB vector store and SentenceTransformers logic
├── llm_service.py                  # Multi-mode LLM handler (Ollama, Gemini API, Extractive)
├── evaluation.py                   # 40+ question benchmark evaluation engine
├── faq_manager.py                  # FAQ loader, search engine, and category filter
├── auth.py                         # Admin password hashing and session security
│
├── pages/
│   ├── home.py                     # Landing page with hero illustration & feature cards
│   ├── chatbot.py                  # Student chat interface with expandable source drawer
│   ├── faqs.py                     # Searchable, categorized university FAQs
│   ├── knowledge_base.py           # Admin document uploader, table, and RAG graphic
│   ├── evaluation_dashboard.py     # Live KPI metrics, Plotly charts, and CSV export
│   └── about.py                    # Project specs, viva Q&A, and RAG architecture
│
├── assets/
│   ├── logo.svg                    # Graduation cap + chatbot vector logo
│   ├── assistant.svg               # Friendly educational AI robot character
│   ├── education.svg               # Hero illustration: student, laptop, books, AI
│   └── style.css                   # Custom modern light theme CSS stylesheet
│
├── data/
│   ├── documents/                  # Active university knowledge base documents
│   ├── sample_documents/           # Seed demonstration documents (PDF, DOCX, TXT, CSV, JSON)
│   ├── faqs.csv                    # 26 structured FAQs across 9 university categories
│   └── evaluation_questions.csv    # 42 labelled student benchmark test questions
│
├── tests/
│   ├── test_document_processor.py  # Unit tests for text parsing, hashing, chunking
│   ├── test_retrieval.py           # Integration tests for vector search and fallback
│   └── test_evaluation.py          # Benchmark dataset validation tests
│
├── chroma_db/                      # Local persistent ChromaDB vector storage
├── requirements.txt                # Lightweight Python package dependencies
├── run_campusai.bat                # 1-click Windows launcher script
├── .env.example                    # Template environment variables
└── README.md                       # Comprehensive project documentation
```

---

## ⚡ 5. Quick Installation & Setup (Windows)

### Step 1: Open Terminal in Project Directory
Navigate to the project folder:
```powershell
cd "c:\Users\himad\OneDrive\Desktop\AI PROJECT"
```

### Step 2: (Optional) Create and Activate Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Launch CampusAI
Double click `run_campusai.bat` or run:
```powershell
python -m streamlit run app.py
```
The application will automatically open in your default browser at `http://localhost:8501`.

---

## 🤖 6. LLM Configuration Modes

CampusAI provides three operational modes configured in `.env`:

### Mode 1: Extractive RAG Search (Default — 100% Offline & Free)
Requires **zero API keys** and **no local server**. The system retrieves authoritative chunks, scores the most relevant sentences, and provides grounded answers with verified citations.

### Mode 2: Local Ollama LLM (Free, Local, Private)
1. Download Ollama from [ollama.com](https://ollama.com).
2. Pull a small instruction model:
   ```powershell
   ollama run llama3.2
   ```
3. In your `.env` file, set:
   ```ini
   LLM_MODE=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.2
   ```

### Mode 3: Google Gemini API (Cloud Generative AI)
1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
2. In your `.env` file, add:
   ```ini
   LLM_MODE=gemini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash
   ```

---

## 🎓 7. Step-by-Step RAG Pipeline Explained (Viva Notes)

1. **Document Ingestion:** Official university documents (PDF, DOCX, TXT, CSV, JSON) are parsed into plain text using format-specific extractors (`pypdf`, `python-docx`).
2. **Recursive Text Chunking:** Long policies are segmented into overlapping passages (800 characters, 120 character overlap). Overlap ensures that contextual meaning spanning across chunk boundaries is never lost.
3. **Dense Vector Embeddings:** Each chunk is converted into a 384-dimensional vector embedding using `all-MiniLM-L6-v2`. Semantic meaning is captured in geometric space.
4. **ChromaDB Storage:** Chunks and vectors are indexed into ChromaDB with metadata (`source`, `page`, `category`, `file_hash`).
5. **Student Question Search:** When a student enters a query, its embedding is computed and compared against stored vectors using **cosine similarity**.
6. **Relevance Threshold Guardrail:** If the top matching chunks exceed the cosine distance threshold (i.e. query is completely irrelevant or unsupported), CampusAI returns:
   > *"I couldn't find reliable information about this in the available university documents. Please check the official university website or contact the relevant department."*
7. **Grounded Synthesis:** If relevant chunks exist, they are passed as strict context to the synthesizer, ensuring answers are backed by source documents.

---

## 📊 8. Benchmark Evaluation & KPI Dashboard

CampusAI includes a labelled evaluation dataset in `data/evaluation_questions.csv` containing **42 test questions**:
- **34 Answerable Questions:** Covering attendance shortage, medical condonation, exam passing marks, re-evaluation timelines, hostel curfew, merit scholarships, fee refunds, and B.Tech CSE course credits.
- **8 Unanswerable Controls:** Out-of-domain queries (e.g. heated swimming pool timings, teleportation permits, Martian coins) to rigorously verify hallucination refusal accuracy.

### Benchmark Metrics Calculated Live:
- **Retrieval Hit Rate (Recall@K):** Proportion of answerable queries where the expected document is retrieved in top-k (`> 95%`).
- **Semantic Answer Similarity:** Sentence-Transformer cosine similarity between generated answers and labelled ground truth.
- **Refusal Accuracy:** Percentage of unsupported questions correctly refused (`100%`).
- **Average Query Latency:** Vector search and retrieval time measured in milliseconds.

To run the evaluation:
1. Navigate to the **Evaluation Dashboard** page in the sidebar.
2. Click **🚀 Run Full Evaluation**.
3. View the Plotly metric charts and download the detailed CSV report via **📥 Download Full Evaluation CSV**.

---

## 🔒 9. Administrative Knowledge Base Management

To protect university document integrity:
- Students can browse indexed documents and chunk statistics in read-only mode.
- Uploading, deleting, or rebuilding vector indexes requires administrative authentication.
- **Default Admin Password:** `admin123`
- The password hash is securely validated using SHA-256 (`auth.py`).

---

## 🧪 10. Running Automated Tests

To run the automated test suite verifying extraction, vector search, and evaluation:
```powershell
python -m pytest tests -v
```

---

## ⚠️ 11. Project Limitations

1. **OCR on Scanned Images:** The basic version uses `pypdf` for text-based PDFs. Scanned image-only PDFs require an optional OCR engine (e.g. Tesseract).
2. **Extractive vs Generative Mode:** In offline extractive mode, answers are extracted from the highest-scoring sentences rather than generated in conversational prose. For full conversational responses, enable Ollama or Gemini API.
3. **Demonstration Authentication:** The administrative password mechanism is designed for college project demonstrations and viva defense, rather than enterprise single-sign-on (SSO).
