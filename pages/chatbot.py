"""
CampusAI - AI Chatbot Page (ChatGPT-Style University & General Assistant)
========================================================================
Interactive student chatbot powered by RAG, ChromaDB, Sentence Transformers,
and ChatGPT-grade conversational intelligence. Answers university regulations
with verified citations, coding & CS questions with working code, and general
queries with structured insights.
"""

import streamlit as st
from pathlib import Path
from rag_pipeline import answer_student_query, ensure_knowledge_base_initialized
from config import UNVERIFIED_FALLBACK_MESSAGE


def render_chatbot_page():
    """Renders the CampusAI Chatbot interactive interface."""

    # Ensure knowledge base has been indexed on startup
    ensure_knowledge_base_initialized()

    # Chat Header Bar with Quick Action Navigation
    col_hdr, col_faq_btn, col_home_btn = st.columns([2.2, 1.0, 0.8], gap="small")
    with col_hdr:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="font-size: 2.2rem; background: #EFF6FF; border-radius: 14px; padding: 6px 12px; box-shadow: 0 2px 6px rgba(37,99,235,0.08);">🤖</div>
                <div>
                    <h3 style="margin: 0; font-size: 1.35rem; color: #1E293B; font-weight: 700;">CampusAI Assistant</h3>
                    <p style="margin: 0; font-size: 0.88rem; color: #64748B;">ChatGPT-Style AI Assistant & University Knowledge Base</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_faq_btn:
        st.write("")
        if st.button("📚 Explore FAQs", use_container_width=True):
            st.switch_page("pages/faqs.py")
    with col_home_btn:
        st.write("")
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/home.py")

    # Status & Mode Indicator Row
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin: 10px 0 16px 0;">
            <div class="chat-status-pill">
                <span class="status-dot"></span>
                <span>Ready to help • Grounded in university documents</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I'm **CampusAI**, your AI Student Assistant — designed like ChatGPT, "
                    "specialized for university academics and student life! 🎓🤖\n\n"
                    "You can ask me **ANYTHING**:\n"
                    "- 📜 **University Regulations:** Minimum attendance rules, exam passing marks, re-evaluation, syllabus, scholarships, fees, and hostel rules.\n"
                    "- 💻 **Computer Science & Coding:** Python programming, Data Structures, Algorithms, Operating Systems, DBMS, Networks, and AI/ML.\n"
                    "- ✉️ **Student Writing:** Professional email templates to professors, viva defense questions, and exam study tips.\n"
                    "- 🌐 **General Knowledge & Open Q&A:** Science, math formulas, technology concepts, or casual conversation!\n\n"
                    "How can I help you today?"
                ),
                "sources": [],
                "retrieved_chunks": []
            }
        ]

    # Clear chat button in an action bar
    col_hist_info, col_clear = st.columns([3, 1])
    with col_hist_info:
        st.caption(f"Session history: {len(st.session_state['messages'])} message(s)")
    with col_clear:
        if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
            st.session_state["messages"] = [
                {
                    "role": "assistant",
                    "content": (
                        "Chat history cleared. I'm ready for your questions!"
                    ),
                    "sources": [],
                    "retrieved_chunks": []
                }
            ]
            st.rerun()

    # Suggested Questions (displayed when history only contains welcome message)
    if len(st.session_state["messages"]) <= 1:
        st.markdown("<p style='font-weight: 600; color: #475569; margin-bottom: 8px;'>Suggested Inquiries:</p>", unsafe_allow_html=True)
        sq1, sq2 = st.columns(2)
        with sq1:
            if st.button("🎓 Attendance Requirement & Shortage Rules", key="sq_1", use_container_width=True):
                st.session_state["pending_query"] = "What is the minimum attendance requirement?"
                st.rerun()
            if st.button("💻 Explain Binary Search with Python Code", key="sq_2", use_container_width=True):
                st.session_state["pending_query"] = "Explain binary search algorithm with Python code and complexity"
                st.rerun()
        with sq2:
            if st.button("📝 Draft Sick Leave Email to Professor", key="sq_3", use_container_width=True):
                st.session_state["pending_query"] = "Draft a formal sick leave email to my professor"
                st.rerun()
            if st.button("🤖 What is Machine Learning and RAG?", key="sq_4", use_container_width=True):
                st.session_state["pending_query"] = "What is Machine Learning and how does RAG work?"
                st.rerun()

    # Display chat messages from history
    for msg_idx, message in enumerate(st.session_state["messages"]):
        role = message["role"]
        avatar = "🎓" if role == "assistant" else "👤"

        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])

            # Render verifiable sources and expandable chunks if present
            sources = message.get("sources", [])
            retrieved_chunks = message.get("retrieved_chunks", [])
            latency = message.get("latency_ms")

            if sources:
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                chips_html = "".join([
                    f"<span class='citation-chip'>📑 {src['display']}</span>"
                    for src in sources
                ])
                st.markdown(
                    f"<div class='citation-box'><strong>Verified University Sources:</strong><br>{chips_html}</div>",
                    unsafe_allow_html=True
                )

                # Expandable passaged chunk inspector
                with st.expander(f"🔍 Inspect {len(retrieved_chunks)} Retrieved Passages & Similarity Scores"):
                    for c_idx, chunk in enumerate(retrieved_chunks, 1):
                        meta = chunk.get("metadata", {})
                        sim = chunk.get("similarity", 0.0)
                        st.markdown(
                            f"**Passage {c_idx}** — *{meta.get('source', 'Doc')}* (Page {meta.get('page', 1)}) | "
                            f"**Relevance Similarity:** `{sim:.1%}`"
                        )
                        st.code(chunk.get("text", "").strip(), language="text")

            if latency:
                st.caption(f"⚡ Latency: {latency} ms | Provider: {message.get('provider', 'CampusAI')}")

    # Process pending query or chat input
    user_query = st.chat_input("Ask me anything! e.g., 'hi', Python code, email templates, attendance rules, scholarships...")
    
    # Check if a pending query was selected from home page or suggested questions
    if "pending_query" in st.session_state and st.session_state["pending_query"]:
        user_query = st.session_state.pop("pending_query")

    if user_query:
        # Append student message
        st.session_state["messages"].append({
            "role": "user",
            "content": user_query
        })

        # Display immediately
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)

        # Generate response with spinner
        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("CampusAI is thinking..."):
                active_api_key = st.session_state.get("user_gemini_key", "")
                result = answer_student_query(user_query, user_api_key=active_api_key)

            st.markdown(result["answer"])

            if result["sources"]:
                chips_html = "".join([
                    f"<span class='citation-chip'>📑 {src['display']}</span>"
                    for src in result["sources"]
                ])
                st.markdown(
                    f"<div class='citation-box'><strong>Verified University Sources:</strong><br>{chips_html}</div>",
                    unsafe_allow_html=True
                )

                with st.expander(f"🔍 Inspect {len(result['retrieved_chunks'])} Retrieved Passages & Similarity Scores"):
                    for c_idx, chunk in enumerate(result["retrieved_chunks"], 1):
                        meta = chunk.get("metadata", {})
                        sim = chunk.get("similarity", 0.0)
                        st.markdown(
                            f"**Passage {c_idx}** — *{meta.get('source', 'Doc')}* (Page {meta.get('page', 1)}) | "
                            f"**Relevance Similarity:** `{sim:.1%}`"
                        )
                        st.code(chunk.get("text", "").strip(), language="text")

            st.caption(f"⚡ Latency: {result['latency_ms']} ms | Provider: {result['provider']}")

        # Save assistant message into history
        st.session_state["messages"].append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "retrieved_chunks": result["retrieved_chunks"],
            "latency_ms": result["latency_ms"],
            "provider": result["provider"]
        })
        st.rerun()


# Render page directly when executed
render_chatbot_page()
