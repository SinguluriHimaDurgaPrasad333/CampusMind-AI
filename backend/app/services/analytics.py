from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Document, DocumentChunk, ChatSession, ChatMessage, UnansweredQuery
from app.schemas.analytics import AnalyticsResponse, CategoryStat, UnansweredQueryItem


class AnalyticsService:
    @staticmethod
    def get_system_analytics(db: Session) -> AnalyticsResponse:
        total_documents = db.query(Document).count()
        total_chunks = db.query(DocumentChunk).count()
        total_chat_sessions = db.query(ChatSession).count()
        
        # User questions asked
        total_questions = db.query(ChatMessage).filter(ChatMessage.role == "user").count()
        
        # Latency
        avg_latency = db.query(func.avg(ChatMessage.latency_ms)).filter(ChatMessage.role == "assistant").scalar() or 0.0

        # Feedback stats
        likes = db.query(ChatMessage).filter(ChatMessage.feedback == "like").count()
        dislikes = db.query(ChatMessage).filter(ChatMessage.feedback == "dislike").count()
        total_feedback = likes + dislikes
        satisfaction_rate = (likes / total_feedback * 100.0) if total_feedback > 0 else 100.0

        # Unanswered queries count
        unanswered_count = db.query(UnansweredQuery).count()

        # Category distribution
        category_rows = db.query(
            Document.category, func.count(Document.id)
        ).group_by(Document.category).all()

        category_stats = [
            CategoryStat(category=cat or "General", count=cnt)
            for cat, cnt in category_rows
        ]

        # Recent unanswered queries
        unanswered_rows = db.query(UnansweredQuery).order_by(
            UnansweredQuery.created_at.desc()
        ).limit(10).all()

        recent_unanswered = [
            UnansweredQueryItem(
                id=u.id,
                query=u.query,
                max_similarity=round(u.max_similarity, 4),
                reason=u.reason,
                created_at=u.created_at
            )
            for u in unanswered_rows
        ]

        return AnalyticsResponse(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_questions_asked=total_questions,
            total_chat_sessions=total_chat_sessions,
            average_latency_ms=round(float(avg_latency), 2),
            satisfaction_rate_percent=round(satisfaction_rate, 1),
            total_positive_feedback=likes,
            total_negative_feedback=dislikes,
            unanswered_count=unanswered_count,
            category_distribution=category_stats,
            recent_unanswered_queries=recent_unanswered
        )

    @staticmethod
    def get_query_suggestions(db: Session) -> List[str]:
        """Generate smart query suggestions based on available university documents."""
        default_suggestions = [
            "What is the minimum attendance requirement for semester exams?",
            "What is the hostel curfew time on weekdays?",
            "When are the mid-term examinations for the Fall semester?",
            "Who is eligible for the Merit Scholarship?",
            "What are the rules and deadlines for fee refunds on admission withdrawal?",
            "How do I request an official academic transcript?"
        ]

        docs = db.query(Document).filter(Document.status == "processed").all()
        if not docs:
            return default_suggestions

        categories = {d.category for d in docs}
        dynamic_suggestions = []

        if "Attendance Policies" in categories or any("attendance" in d.filename.lower() for d in docs):
            dynamic_suggestions.append("What is the minimum attendance requirement for semester exams?")
            dynamic_suggestions.append("What is the medical condonation policy for attendance shortages?")

        if "Hostel Rules and Regulations" in categories or any("hostel" in d.filename.lower() for d in docs):
            dynamic_suggestions.append("What is the hostel curfew time on weekdays?")
            dynamic_suggestions.append("Are induction cooktops or kettles allowed in hostel rooms?")

        if "Scholarship Information" in categories or any("scholarship" in d.filename.lower() for d in docs):
            dynamic_suggestions.append("What are the criteria to qualify for the Merit Scholarship?")
            dynamic_suggestions.append("What are the family income limits for Need-Based Financial Aid?")

        if "Examination Guidelines" in categories or any("exam" in d.filename.lower() for d in docs):
            dynamic_suggestions.append("What are the passing criteria for end-semester exams?")
            dynamic_suggestions.append("What is the procedure and fee to apply for re-evaluation?")

        if "Academic Calendars" in categories or any("calendar" in d.filename.lower() for d in docs):
            dynamic_suggestions.append("When are the mid-term examinations for the Fall semester?")

        return list(dict.fromkeys(dynamic_suggestions + default_suggestions))[:6]


analytics_service = AnalyticsService()
