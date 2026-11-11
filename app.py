"""
CampusAI - Main Streamlit Application
====================================
Master application entrypoint providing structured multi-level navigation,
quick-action switchers, instant student query shortcuts, telemetry,
and Modern Educational Light Theme styling.
"""

import streamlit as st
from pathlib import Path
from config import (
    PROJECT_NAME,
    PROJECT_CODE,
    PROJECT_TAGLINE,
    ASSETS_DIR,
    EMBEDDING_MODEL_NAME
)
from auth import is_admin_authenticated
from vector_database import get_or_create_collection
from rag_pipeline import ensure_knowledge_base_initialized

# Streamlit Page Configuration must be the first command
st.set_page_config(
    page_title="CampusAI – AI Student Assistance Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-initialize Knowledge Base on startup
ensure_knowledge_base_initialized()

# Inject custom light-theme styling
css_path = ASSETS_DIR / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ----------------- SIDEBAR HEADER & BRANDING -----------------
logo_path = ASSETS_DIR / "logo.svg"
logo_svg = ""
if logo_path.exists():
    with open(logo_path, "r", encoding="utf-8") as f:
        logo_svg = f.read()

st.sidebar.markdown(
    f"""
    <div class="sidebar-brand-box">
        <div style="width: 44px; height: 44px; flex-shrink: 0;">
            {logo_svg}
        </div>
        <div>
            <h3 class="brand-title">CampusAI</h3>
            <p class="brand-tagline">AI Student Assistant</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Quick Action Hub (1-Click Primary Buttons at the top of the sidebar)
st.sidebar.markdown("<p style='font-size: 0.78rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 6px;'>⚡ Quick Jump</p>", unsafe_allow_html=True)
q_col1, q_col2 = st.sidebar.columns(2)
with q_col1:
    if st.button("💬 Chatbot", key="sb_quick_chat", use_container_width=True, type="primary"):
        st.switch_page("pages/chatbot.py")
with q_col2:
    if st.button("📚 FAQs", key="sb_quick_faqs", use_container_width=True):
        st.switch_page("pages/faqs.py")

# ----------------- STRUCTURED MULTI-LEVEL NAVIGATION -----------------
# Grouped into clear institutional levels
pages = {
    "🎯 Level 1: Student Assistance": [
        st.Page("pages/home.py", title="Home Dashboard", icon="🏠", default=True),
        st.Page("pages/chatbot.py", title="AI Chatbot Assistant", icon="💬"),
        st.Page("pages/faqs.py", title="University FAQs", icon="📚"),
    ],
    "🗂️ Level 2: Knowledge Base": [
        st.Page("pages/knowledge_base.py", title="Document Ingestion & Vectors", icon="🗄️"),
    ],
    "📊 Level 3: Benchmarks & Evaluation": [
        st.Page("pages/evaluation_dashboard.py", title="RAG Evaluation Dashboard", icon="📈"),
    ],
    "ℹ️ Level 4: Project Info & Viva": [
        st.Page("pages/about.py", title="About Project & Viva Notes", icon="🎓"),
    ]
}

# Run navigation controller
pg = st.navigation(pages)

# ----------------- SIDEBAR QUICK QUERY SHORTCUTS -----------------
with st.sidebar.expander("💡 Instant Question Shortcuts", expanded=False):
    st.caption("Click any question to ask CampusAI directly:")
    if st.button("⏱️ Attendance Requirement", key="sb_q1", use_container_width=True):
        st.session_state["pending_query"] = "What is the minimum attendance requirement?"
        st.switch_page("pages/chatbot.py")
    if st.button("📝 Exam Passing Rules", key="sb_q2", use_container_width=True):
        st.session_state["pending_query"] = "What are the minimum passing marks in exams?"
        st.switch_page("pages/chatbot.py")
    if st.button("🏆 Scholarship Policy", key="sb_q3", use_container_width=True):
        st.session_state["pending_query"] = "How can I apply for a scholarship?"
        st.switch_page("pages/chatbot.py")
    if st.button("🏢 Hostel Curfew Hours", key="sb_q4", use_container_width=True):
        st.session_state["pending_query"] = "What is the hostel curfew time?"
        st.switch_page("pages/chatbot.py")

# ----------------- SIDEBAR SYSTEM TELEMETRY -----------------
try:
    coll = get_or_create_collection()
    chunk_count = coll.count()
except Exception:
    chunk_count = 0

admin_badge = (
    "<span style='color: #059669; font-weight: 600;'>Admin Active</span>"
    if is_admin_authenticated()
    else "<span style='color: #64748B;'>Student View</span>"
)

st.sidebar.markdown(
    f"""
    <div style="margin-top: 15px; border-top: 1px solid #E2E8F0; padding-top: 12px;">
        <p style="font-weight: 700; font-size: 0.78rem; color: #64748B; text-transform: uppercase; margin-bottom: 8px;">System Status</p>
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 10px 12px; font-size: 0.82rem; line-height: 1.6; color: #334155;">
            <div>🟢 <strong>System:</strong> Online</div>
            <div>🧠 <strong>Model:</strong> <code>{EMBEDDING_MODEL_NAME}</code></div>
            <div>🗄️ <strong>Indexed Chunks:</strong> <code>{chunk_count}</code></div>
            <div>👤 <strong>Access Mode:</strong> {admin_badge}</div>
            <div>📌 <strong>Project:</strong> <code>{PROJECT_CODE} (SIH1631)</code></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.caption("CampusAI © 2026 • SIH1631 P08")

# Execute the selected page
pg.run()
