"""
CampusAI - Evaluation Dashboard Page
====================================
Comprehensive evaluation dashboard measuring RAG system performance against
a labelled benchmark dataset of 40+ student questions. Features interactive Plotly
visualizations, category performance matrices, and CSV report export.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from evaluation import run_rag_evaluation, load_evaluation_dataset
from rag_pipeline import ensure_knowledge_base_initialized


def render_evaluation_dashboard_page():
    """Renders the Evaluation Dashboard page."""
    ensure_knowledge_base_initialized()

    st.markdown(
        """
        <div style="margin-bottom: 20px;">
            <h2 style="margin: 0; color: #1E293B;">📊 RAG Evaluation & Benchmark Dashboard</h2>
            <p style="color: #64748B; margin-top: 4px; font-size: 0.95rem;">
                Scientifically benchmark retrieval precision, semantic groundedness, latency,
                and hallucination refusal accuracy against 40+ labelled university questions.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Dataset overview info
    try:
        raw_df = load_evaluation_dataset()
        total_eval_q = len(raw_df)
        answerable_count = (raw_df["answerable"] == True).sum()
        unanswerable_count = (raw_df["answerable"] == False).sum()
    except Exception as e:
        st.error(f"Failed to load evaluation dataset: {e}")
        return

    # Benchmark Execution Controls
    col_ctrl, col_btn = st.columns([2, 1], gap="medium")
    with col_ctrl:
        st.markdown(
            f"<p style='margin: 8px 0; color: #475569;'><strong>Benchmark Corpus:</strong> "
            f"<code>evaluation_questions.csv</code> ({total_eval_q} questions: "
            f"{answerable_count} supported, {unanswerable_count} unanswerable controls)</p>",
            unsafe_allow_html=True
        )
    with col_btn:
        run_btn = st.button("🚀 Run Full Evaluation", type="primary", use_container_width=True)

    # Run evaluation if requested or if already cached in session state
    if run_btn:
        progress_bar = st.progress(0.0)
        status_box = st.empty()

        def update_eval_progress(curr, total, msg):
            progress_bar.progress(curr / total)
            status_box.markdown(f"**Evaluating:** `{curr}/{total}` — {msg}")

        with st.spinner("Executing RAG retrieval and metric computation across questions..."):
            eval_results = run_rag_evaluation(progress_callback=update_eval_progress)

        status_box.success("Benchmark evaluation completed successfully!")
        st.session_state["eval_results"] = eval_results

    # If no evaluation run yet in this session, provide sample preview or prompt to run
    if "eval_results" not in st.session_state:
        st.info("Click **Run Full Evaluation** above to calculate live benchmark metrics, generate performance charts, and review question-level groundedness.")
        
        # Display dataset preview table
        with st.expander("📋 View Benchmark Dataset Questions (Pre-Run Preview)", expanded=True):
            st.dataframe(
                raw_df[["question_id", "category", "question", "expected_source", "answerable"]],
                use_container_width=True,
                hide_index=True
            )
        return

    eval_data = st.session_state["eval_results"]
    summary = eval_data["summary"]
    cat_df = eval_data["category_summary"]
    details_df = eval_data["detailed_results"]

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # 4 Primary Metric Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Retrieval Hit Rate</div>
                <div class="metric-value">{summary['retrieval_hit_rate']}%</div>
                <span style="font-size: 0.78rem; color: #059669;">Expected Source in Top-K</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Semantic Similarity</div>
                <div class="metric-value">{summary['average_similarity']}%</div>
                <span style="font-size: 0.78rem; color: #2563EB;">SentenceTransformer Cosine</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Refusal Accuracy</div>
                <div class="metric-value">{summary['refusal_accuracy']}%</div>
                <span style="font-size: 0.78rem; color: #7C3AED;">Zero-Hallucination Guard</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-value">{summary['average_latency_ms']} ms</div>
                <span style="font-size: 0.78rem; color: #D97706;">Dense Vector Search</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Charts Row 1: Category Performance & Answerability Breakdown
    ch_col1, ch_col2 = st.columns(2)

    with ch_col1:
        st.markdown("<h5>Category-wise Retrieval Hit Rate</h5>", unsafe_allow_html=True)
        if not cat_df.empty:
            fig_bar = px.bar(
                cat_df,
                x="Category",
                y="Retrieval Hit Rate (%)",
                color="Retrieval Hit Rate (%)",
                color_continuous_scale=["#93C5FD", "#2563EB"],
                text="Retrieval Hit Rate (%)"
            )
            fig_bar.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                margin=dict(l=20, r=20, t=20, b=50),
                height=320,
                xaxis_tickangle=-30
            )
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            st.plotly_chart(fig_bar, use_container_width=True)

    with ch_col2:
        st.markdown("<h5>System Answerability & Refusal Distribution</h5>", unsafe_allow_html=True)
        status_counts = details_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_pie = px.pie(
            status_counts,
            names="Status",
            values="Count",
            color="Status",
            color_discrete_map={
                "Success": "#2563EB",
                "Correct Refusal": "#10B981",
                "Mismatch": "#EF4444"
            },
            hole=0.45
        )
        fig_pie.update_layout(
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            margin=dict(l=20, r=20, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # Charts Row 2: Query Latency Distribution
    st.markdown("<h5>Query Latency Across Test Questions</h5>", unsafe_allow_html=True)
    fig_lat = px.line(
        details_df,
        x="question_id",
        y="latency_ms",
        markers=True,
        labels={"question_id": "Question ID", "latency_ms": "Latency (ms)"},
        color_discrete_sequence=["#2563EB"]
    )
    fig_lat.add_hline(y=summary["average_latency_ms"], line_dash="dash", line_color="#F59E0B", annotation_text="Average Latency")
    fig_lat.update_layout(
        plot_bgcolor="#F8FAFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=20, b=20),
        height=260
    )
    st.plotly_chart(fig_lat, use_container_width=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Question-Level Detailed Table with Filter
    st.markdown("<h4>Question-by-Question Evaluation Results</h4>", unsafe_allow_html=True)

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        status_filter = st.selectbox(
            "Filter by Result Status:",
            options=["All", "Success", "Correct Refusal", "Mismatch"]
        )
    with col_f2:
        # Download CSV button
        csv_data = details_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Evaluation CSV",
            data=csv_data,
            file_name="campusai_evaluation_report.csv",
            mime="text/csv",
            use_container_width=True
        )

    view_df = details_df if status_filter == "All" else details_df[details_df["status"] == status_filter]
    st.dataframe(
        view_df[[
            "question_id", "category", "question", "retrieval_hit",
            "semantic_similarity", "status", "retrieved_sources"
        ]],
        use_container_width=True,
        hide_index=True
    )


# Render page directly when executed
render_evaluation_dashboard_page()
