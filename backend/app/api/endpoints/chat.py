import time
import json
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import ChatSession, ChatMessage, UnansweredQuery
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatMessageResponse,
    ChatSessionResponse, FeedbackRequest, CitationItem
)
from app.rag.retriever import retriever
from app.rag.llm import llm_service, UNAVAILABLE_INFO_MESSAGE, check_conversational_intent

router = APIRouter(tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def ask_question(request: ChatRequest, db: Session = Depends(get_db)):
    start_time = time.perf_counter()
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 1. Resolve or create chat session
    session = None
    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    
    if not session:
        # Generate title from first 6 words of user query
        words = query.split()
        title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")
        session = ChatSession(id=str(uuid.uuid4()), title=title)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Fetch recent history for conversation context
    prev_msgs = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.desc()).limit(6).all()
    history = [{"role": m.role, "content": m.content} for m in reversed(prev_msgs)]

    # 2. Save user message
    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="user",
        content=query,
        latency_ms=0.0
    )
    db.add(user_msg)
    db.commit()

    # 2.5 Check conversational pleasantries (greetings, thanks, help)
    conversational_reply = check_conversational_intent(query)
    if conversational_reply:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        assistant_msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session.id,
            role="assistant",
            content=conversational_reply,
            sources_json="[]",
            confidence_score=1.0,
            latency_ms=round(elapsed_ms, 2)
        )
        db.add(assistant_msg)
        db.commit()

        return ChatResponse(
            answer=conversational_reply,
            session_id=session.id,
            message_id=assistant_msg.id,
            sources=[],
            confidence_score=1.0,
            latency_ms=round(elapsed_ms, 2),
            is_grounded=True,
            unanswered=False
        )

    # Contextual query reformulation for follow-ups
    effective_query = query
    if len(history) > 0 and len(query.split()) < 7:
        last_user_query = next((h["content"] for h in reversed(history) if h["role"] == "user"), "")
        if last_user_query:
            effective_query = f"{query} {last_user_query}"

    # 3. Retrieve relevant university document chunks
    retrieval_res = retriever.retrieve(effective_query)
    # If effective query had no hits, try raw query
    if not retrieval_res.chunks:
        retrieval_res = retriever.retrieve(query)

    # 4. Generate grounded answer
    answer, is_grounded = llm_service.generate_answer(
        query=query,
        chunks=retrieval_res.chunks,
        citations=retrieval_res.citations,
        is_confident=retrieval_res.is_confident,
        history=history
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # 5. Check if unanswered / low confidence
    is_unanswered = (answer == UNAVAILABLE_INFO_MESSAGE) or (not retrieval_res.is_confident)
    if is_unanswered:
        unanswered_record = UnansweredQuery(
            session_id=session.id,
            query=query,
            max_similarity=round(retrieval_res.max_score, 4),
            reason="Retrieved score below confidence threshold or unavailable in docs"
        )
        db.add(unanswered_record)

    # 6. Save assistant message
    sources_payload = [c.model_dump() for c in retrieval_res.citations]
    assistant_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="assistant",
        content=answer,
        sources_json=json.dumps(sources_payload),
        confidence_score=round(retrieval_res.max_score, 4),
        latency_ms=round(elapsed_ms, 2)
    )
    db.add(assistant_msg)
    db.commit()

    return ChatResponse(
        answer=answer,
        session_id=session.id,
        message_id=assistant_msg.id,
        sources=retrieval_res.citations,
        confidence_score=round(retrieval_res.max_score, 4),
        latency_ms=round(elapsed_ms, 2),
        is_grounded=is_grounded,
        unanswered=is_unanswered
    )


@router.get("/chats", response_model=List[ChatSessionResponse])
def list_chats(db: Session = Depends(get_db)):
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()
    results = []
    for s in sessions:
        count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        results.append(
            ChatSessionResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=count
            )
        )
    return results


@router.get("/chats/{chat_id}", response_model=List[ChatMessageResponse])
def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == chat_id
    ).order_by(ChatMessage.created_at.asc()).all()

    response = []
    for m in messages:
        sources = []
        if m.sources_json:
            try:
                raw_sources = json.loads(m.sources_json)
                sources = [CitationItem(**s) for s in raw_sources]
            except Exception:
                sources = []

        response.append(
            ChatMessageResponse(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                content=m.content,
                sources=sources,
                confidence_score=m.confidence_score,
                latency_ms=m.latency_ms,
                feedback=m.feedback,
                created_at=m.created_at
            )
        )
    return response


@router.delete("/chats/{chat_id}")
def delete_chat_session(chat_id: str, db: Session = Depends(get_db)):
    session = db.query(ChatSession).filter(ChatSession.id == chat_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    db.delete(session)
    db.commit()
    return {"message": "Chat session deleted successfully."}


@router.post("/feedback")
def submit_feedback(req: FeedbackRequest, db: Session = Depends(get_db)):
    msg = db.query(ChatMessage).filter(ChatMessage.id == req.message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found.")
    msg.feedback = req.feedback
    if req.comment:
        msg.feedback_comment = req.comment
    db.commit()
    return {"message": "Feedback submitted successfully.", "feedback": req.feedback}
