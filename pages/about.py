"""
CampusAI - About Project Page
=============================
Educational and technical overview of CampusAI (Project Code: P08 / SIH1631).
Includes student viva notes, architecture breakdown, and RAG workflow explanation.
"""

import streamlit as st
from config import PROJECT_NAME, PROJECT_CODE, PROJECT_REFERENCE, APP_VERSION


def render_about_page():
    """Renders the About Project information page."""
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <div class="hero-badge">🎓 Academic AI Project Overview</div>
            <h2 style="margin: 0; color: #1E293B;">About CampusAI</h2>
            <p style="color: #64748B; margin-top: 4px; font-size: 1rem;">
                Official project documentation, viva questions guide, and RAG architectural pipeline.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Project Details Card
    st.markdown(
        f"""
        <div class="campus-card">
            <h4 style="margin-top: 0; color: #2563EB;">Institutional Project Specifications</h4>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.95rem;">
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 10px 0; font-weight: 600; width: 220px; color: #475569;">Project Title</td>
                    <td style="padding: 10px 0; color: #1E293B;">{PROJECT_NAME}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 10px 0; font-weight: 600; color: #475569;">Project Code</td>
                    <td style="padding: 10px 0; color: #1E293B;"><code>{PROJECT_CODE}</code></td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 10px 0; font-weight: 600; color: #475569;">Competition / Track</td>
                    <td style="padding: 10px 0; color: #1E293B;">{PROJECT_REFERENCE}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 10px 0; font-weight: 600; color: #475569;">Academic Degree</td>
                    <td style="padding: 10px 0; color: #1E293B;">B.Tech in Computer Science &amp; Engineering (AI &amp; ML)</td>
                </tr>
                <tr>
                    <td style="padding: 10px 0; font-weight: 600; color: #475569;">Core Technology Stack</td>
                    <td style="padding: 10px 0; color: #1E293B;">Python 3.11+, Streamlit, Sentence Transformers (<code>all-MiniLM-L6-v2</code>), ChromaDB, Plotly</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Project Description
    st.markdown("<h4>Project Objective & Motivation</h4>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style="line-height: 1.6; color: #475569;">
            University students routinely navigate dozens of disparate PDF documents, academic circulars,
            examination guidelines, hostel codes, and fee schedules. Standard generative AI models suffer from
            <strong>hallucinations</strong>, inventing incorrect dates, grading rules, or contact information.
        </p>
        <p style="line-height: 1.6; color: #475569;">
            <strong>CampusAI</strong> resolves this problem by implementing <strong>Retrieval-Augmented Generation (RAG)</strong>.
            Before generating any answer, CampusAI retrieves the exact authoritative policy passages from the institutional
            knowledge base. If the verified documents do not contain evidence to answer the query, the chatbot safely abstains,
            preventing misinformation.
        </p>
        """,
        unsafe_allow_html=True
    )

    # RAG Architecture Flowchart
    st.markdown("<h4>System Architecture & Information Flow</h4>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; box-shadow: 0 4px 15px rgba(37,99,235,0.05); margin-bottom: 25px;">
            <div style="font-family: monospace; font-size: 0.9rem; line-height: 1.8; color: #1E293B;">
                <strong>1. Ingestion Phase:</strong><br>
                University Documents (PDF, DOCX, TXT) ➔ Text Extraction ➔ Overlapping Chunking (800c) ➔ Dense Embeddings (384-dim) ➔ ChromaDB Vector Index<br><br>
                <strong>2. Query &amp; Retrieval Phase:</strong><br>
                Student Question ➔ SentenceTransformer Embedding ➔ ChromaDB Nearest-Neighbor Cosine Search ➔ Top-K Chunks Filtered by Relevance Threshold<br><br>
                <strong>3. Grounded Generation Phase:</strong><br>
                Retrieved Context + Strict Grounding System Prompt ➔ Ollama / Gemini API / Extractive Synthesizer ➔ Verified Answer with Source Citations
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Viva Questions and Answers Guide
    st.markdown("<h4>Key Concepts for Project Viva & Evaluation</h4>", unsafe_allow_html=True)

    with st.expander("❓ What is RAG and why is it superior to standard LLM chat for universities?"):
        st.markdown(
            "**Retrieval-Augmented Generation (RAG)** combines information retrieval with language modeling. "
            "Instead of relying on the LLM's static training weights (which hallucinate and lack private campus data), "
            "RAG retrieves authoritative passages from the local university corpus and instructs the model to synthesize "
            "answers exclusively from those passages."
        )

    with st.expander("❓ How does ChromaDB store and retrieve vector embeddings?"):
        st.markdown(
            "ChromaDB stores document chunks alongside dense 384-dimensional vector embeddings generated by "
            "`all-MiniLM-L6-v2`. It uses Hierarchical Navigable Small World (HNSW) graphs to compute cosine distances "
            "in sub-millisecond time."
        )

    with st.expander("❓ How does CampusAI prevent hallucination on out-of-domain queries?"):
        st.markdown(
            "CampusAI implements a cosine distance relevance threshold. If student queries (e.g., flight bookings to Mars) "
            "do not have sufficiently similar document chunks in the vector store, the system automatically triggers an "
            "unverified fallback message without ever invoking generative model speculation."
        )

    with st.expander("❓ What evaluation metrics are implemented in the dashboard?"):
        st.markdown(
            "1. **Retrieval Hit Rate (Recall@K):** Proportion of answerable questions whose expected source document is in top-k.<br>"
            "2. **Semantic Similarity:** Cosine similarity between generated answer and ground-truth benchmark.<br>"
            "3. **Refusal Accuracy:** Correct detection and safe refusal of unsupported queries.<br>"
            "4. **Query Latency:** End-to-end response time in milliseconds.",
            unsafe_allow_html=True
        )


# Render page directly when executed
render_about_page()
