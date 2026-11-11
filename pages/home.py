"""
CampusAI - Home Page
====================
Landing page with modern educational branding, interactive feature cards,
4-step RAG workflow, and clickable sample question cards.
"""

import streamlit as st
from pathlib import Path


def render_home_page():
    """Renders the CampusAI Landing / Home page."""
    
    # Hero Section
    col_hero_text, col_hero_img = st.columns([1.1, 0.9], gap="large")

    with col_hero_text:
        st.markdown(
            """
            <div class="hero-badge">
                <span>🎓</span> Official University AI Assistant (Project P08)
            </div>
            <h1 style="font-size: 2.8rem; line-height: 1.15; color: #1E293B; margin-bottom: 8px;">
                Meet <span style="color: #2563EB;">CampusAI</span>
            </h1>
            <h3 style="font-size: 1.35rem; font-weight: 600; color: #475569; margin-top: 0; margin-bottom: 16px;">
                Your Intelligent University Assistant
            </h3>
            <p style="font-size: 1.05rem; line-height: 1.6; color: #64748B; margin-bottom: 24px;">
                Get accurate answers about academics, examinations, university regulations,
                campus services, and scholarships — strictly grounded in official university documents.
            </p>
            """,
            unsafe_allow_html=True
        )

        col_btn1, col_btn2 = st.columns([1, 1], gap="small")
        with col_btn1:
            if st.button("💬 Start Chatting", use_container_width=True, type="primary"):
                try:
                    st.switch_page("pages/chatbot.py")
                except Exception:
                    st.session_state["selected_page"] = "AI Chatbot"
                    st.rerun()

        with col_btn2:
            if st.button("📚 Explore University FAQs", use_container_width=True):
                try:
                    st.switch_page("pages/faqs.py")
                except Exception:
                    st.session_state["selected_page"] = "University FAQs"
                    st.rerun()

    with col_hero_img:
        edu_svg_path = Path(__file__).resolve().parent.parent / "assets" / "education.svg"
        if edu_svg_path.exists():
            with open(edu_svg_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            st.markdown(f'<div style="text-align: center;">{svg_content}</div>', unsafe_allow_html=True)
        else:
            st.info("🎓 Educational Illustration")

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # 4 Feature Cards
    st.markdown("<h3 style='margin-bottom: 18px;'>Core Capabilities</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            """
            <div class="feature-box">
                <div class="icon-bubble icon-blue">🎓</div>
                <h4 style="font-size: 1.05rem; margin: 0 0 8px 0;">Academic Assistance</h4>
                <p style="font-size: 0.88rem; color: #64748B; margin: 0; line-height: 1.5;">
                    Find information about courses, syllabuses, attendance, and examinations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="feature-box">
                <div class="icon-bubble icon-purple">🏛️</div>
                <h4 style="font-size: 1.05rem; margin: 0 0 8px 0;">University Information</h4>
                <p style="font-size: 0.88rem; color: #64748B; margin: 0; line-height: 1.5;">
                    Access official university policies, regulations, codes, and campus notices.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="feature-box">
                <div class="icon-bubble icon-green">🤖</div>
                <h4 style="font-size: 1.05rem; margin: 0 0 8px 0;">AI-Powered Search</h4>
                <p style="font-size: 0.88rem; color: #64748B; margin: 0; line-height: 1.5;">
                    Retrieve relevant information from university documents using dense embeddings.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            """
            <div class="feature-box">
                <div class="icon-bubble icon-amber">📑</div>
                <h4 style="font-size: 1.05rem; margin: 0 0 8px 0;">Reliable Sources</h4>
                <p style="font-size: 0.88rem; color: #64748B; margin: 0; line-height: 1.5;">
                    View verifiable documents and page numbers used to support chatbot answers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)

    # How CampusAI Works (4-Step Horizontal Workflow)
    st.markdown("<h3 style='margin-bottom: 6px;'>How CampusAI Works</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #64748B; margin-top: 0; margin-bottom: 16px; font-size: 0.95rem;'>"
        "The Retrieval-Augmented Generation (RAG) architecture guarantees reliable, verifiable answers."
        "</p>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="step-container">
            <div class="step-item">
                <div class="step-num">1</div>
                <div class="step-text">
                    <h5>Ask a Question</h5>
                    <p>Enter natural language query</p>
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-item">
                <div class="step-num">2</div>
                <div class="step-text">
                    <h5>Search Documents</h5>
                    <p>Embed with all-MiniLM-L6-v2</p>
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-item">
                <div class="step-num">3</div>
                <div class="step-text">
                    <h5>Retrieve Top Chunks</h5>
                    <p>Query ChromaDB vectors</p>
                </div>
            </div>
            <div class="step-arrow">➔</div>
            <div class="step-item">
                <div class="step-num">4</div>
                <div class="step-text">
                    <h5>Generate Answer</h5>
                    <p>Grounded in citations</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Clickable Example Questions
    st.markdown("<h3 style='margin-bottom: 8px;'>Frequently Asked Student Inquiries</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; margin-top: 0; margin-bottom: 16px;'>Click any question to immediately query CampusAI:</p>", unsafe_allow_html=True)

    example_questions = [
        "What is the minimum attendance requirement?",
        "Where can I find my course syllabus?",
        "How does the re-evaluation process work?",
        "How can I apply for a scholarship?",
        "What are the university examination regulations?",
        "How can I contact student services?"
    ]

    eq_cols = st.columns(2)
    for idx, eq in enumerate(example_questions):
        col = eq_cols[idx % 2]
        with col:
            if st.button(f"🔍 {eq}", key=f"home_q_{idx}", use_container_width=True):
                st.session_state["pending_query"] = eq
                try:
                    st.switch_page("pages/chatbot.py")
                except Exception:
                    st.session_state["selected_page"] = "AI Chatbot"
                    st.rerun()


# Render page directly when executed
render_home_page()
