"""
CampusAI - University FAQs Page
===============================
Provides an organized, searchable repository of official university FAQs.
Features category filtering, keyword searching, expandable FAQ cards,
top breadcrumb navigation, and one-click redirection to the AI Chatbot.
"""

import streamlit as st
from faq_manager import load_all_faqs, get_faq_categories, search_faqs


def get_category_icon(category: str) -> str:
    """Returns an appropriate emoji icon for each category."""
    cat_lower = category.lower()
    if "attendance" in cat_lower:
        return "⏱️"
    elif "exam" in cat_lower:
        return "📝"
    elif "academic" in cat_lower:
        return "📖"
    elif "scholarship" in cat_lower:
        return "🏆"
    elif "hostel" in cat_lower:
        return "🏢"
    elif "library" in cat_lower:
        return "📚"
    elif "service" in cat_lower:
        return "🛠️"
    elif "admission" in cat_lower:
        return "🎯"
    return "📌"


def render_faqs_page():
    """Renders the University FAQs interface."""
    
    # Quick Navigation Bar at Top
    col_head, col_nav_chat, col_nav_home = st.columns([2.2, 1.1, 0.9], gap="small")
    with col_head:
        st.markdown(
            """
            <div>
                <h2 style="margin: 0; color: #1E293B;">📚 University Knowledge FAQs</h2>
                <p style="color: #64748B; margin-top: 4px; font-size: 0.92rem;">
                    Browse officially verified answers or jump directly to the AI Chatbot.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_nav_chat:
        st.write("")
        if st.button("💬 Open AI Chatbot", type="primary", use_container_width=True):
            st.switch_page("pages/chatbot.py")
    with col_nav_home:
        st.write("")
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/home.py")

    st.markdown("<hr style='margin: 12px 0 20px 0; border: none; border-top: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    all_faqs = load_all_faqs()
    categories = ["All"] + get_faq_categories(all_faqs)

    # Search & Filter Controls Bar
    col_search, col_filter = st.columns([2, 1], gap="medium")

    with col_search:
        search_query = st.text_input(
            "Search FAQs by keyword or phrase:",
            placeholder="e.g., attendance shortage, scholarship eligibility, re-evaluation..."
        )

    with col_filter:
        selected_category = st.selectbox(
            "Filter by category:",
            options=categories,
            index=0
        )

    # Filtered FAQs
    filtered_faqs = search_faqs(
        query=search_query,
        category=None if selected_category == "All" else selected_category,
        faqs=all_faqs
    )

    st.markdown(
        f"<p style='font-size: 0.88rem; color: #64748B; margin-top: 10px; margin-bottom: 18px;'>"
        f"Showing <strong>{len(filtered_faqs)}</strong> of {len(all_faqs)} FAQs"
        f"</p>",
        unsafe_allow_html=True
    )

    if not filtered_faqs:
        st.info("No FAQs match your search query or selected category. Try searching for different keywords.")
        return

    # Render Expandable Cards
    for idx, faq in enumerate(filtered_faqs):
        cat = faq.get("category", "General")
        icon = get_category_icon(cat)
        q_text = faq.get("question", "")
        a_text = faq.get("answer", "")
        src = faq.get("source_document", "University Knowledge Corpus")

        card_title = f"{icon} [{cat}] {q_text}"

        with st.expander(card_title, expanded=(idx < 2)):
            st.markdown(f"**Answer:**\n\n{a_text}")
            st.markdown(
                f"<div style='margin-top: 10px; padding: 6px 12px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.85rem; color: #475569;'>"
                f"📑 <strong>Verified Source:</strong> <code>{src}</code>"
                f"</div>",
                unsafe_allow_html=True
            )

            col_spacer, col_ask = st.columns([3, 1])
            with col_ask:
                if st.button(f"💬 Ask in Chat", key=f"ask_faq_{faq.get('faq_id', idx)}", use_container_width=True):
                    st.session_state["pending_query"] = q_text
                    st.switch_page("pages/chatbot.py")


# Render page directly when executed
render_faqs_page()
