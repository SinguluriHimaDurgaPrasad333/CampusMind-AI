import re
from typing import List, Optional, Tuple, Dict, Any
from app.core.config import settings
from app.rag.vector_store import ChunkMetadata
from app.schemas.chat import CitationItem

UNAVAILABLE_INFO_MESSAGE = (
    "I couldn't find reliable information about this in the available university documents. "
    "Please check with the relevant university department."
)

GREETING_RESPONSES = {
    "greeting": (
        "Hello! 👋 I'm **CampusMind AI**, your university academic assistant.\n\n"
        "I can help you with verified institutional information regarding:\n"
        "* 📋 **Attendance Policies & Medical Leaves**\n"
        "* 🏢 **Hostel Curfew, Night-Out Passes & Dorm Rules**\n"
        "* 📝 **Examination Guidelines, Grading System & Re-evaluation**\n"
        "* 🎓 **Merit & Need-Based Scholarships**\n"
        "* 💰 **Fee Schedules & Admission Refund Policies**\n"
        "* 📅 **Academic Calendars & Key Semester Dates**\n"
        "* 📚 **Course Syllabi & Credit Requirements**\n\n"
        "What would you like to know about your campus today?"
    ),
    "thanks": (
        "You're very welcome! 😊 If you have any more questions about university regulations, "
        "deadlines, or policies, feel free to ask anytime. Best of luck with your studies!"
    ),
    "about": (
        "I am **CampusMind AI**, an intelligent assistant powered by **Retrieval-Augmented Generation (RAG)**.\n\n"
        "My mission is to provide university students with reliable, context-aware answers grounded strictly "
        "in official institutional documents. Every policy answer I provide comes with verifiable page citations "
        "so you can always cross-reference official sources."
    )
}


def check_conversational_intent(query: str) -> Optional[str]:
    """Detect common conversational greetings, pleasantries, and meta questions."""
    q = query.strip().lower()
    # Greetings
    if re.match(r"^(hi|hello|hey|hola|greetings|howdy|good\s+(morning|afternoon|evening|day))[\s!.]*$", q):
        return GREETING_RESPONSES["greeting"]
    if re.match(r"^(how\s+are\s+you|how's\s+it\s+going|what's\s+up)[\s!?.]*$", q):
        return GREETING_RESPONSES["greeting"]
    # Thanks
    if re.match(r"^(thanks|thank\s+you|thank\s+you\s+so\s+much|thx|appreciate\s+it)[\s!.]*$", q):
        return GREETING_RESPONSES["thanks"]
    # Who are you / help / what can you do
    if re.match(r"^(who\s+are\s+you|what\s+are\s+you|what\s+can\s+you\s+do|help|what\s+is\s+campusmind)[\s!?.]*$", q):
        return GREETING_RESPONSES["about"]
    return None

SYSTEM_PROMPT = """You are CampusMind AI, an intelligent, conversational ChatGPT-style University Assistant.
Your goal is to converse naturally, helpfully, and articulately with students while strictly basing all facts, policies, percentages, and guidelines on the retrieved official university documents provided inside <context>.

RESPONSE GUIDELINES:
1. Format your response cleanly using Markdown:
   - Use clear, descriptive headings (###)
   - Highlight key figures, dates, and terms in **bold**
   - Use bullet points (* or -) for lists, conditions, and step-by-step procedures
   - Keep paragraphs concise, engaging, and easy to read
2. Maintain a friendly, supportive, and professional tone like ChatGPT.
3. Answer ONLY with facts supported by the <context>. Do not hallucinate or speculate.
4. If the context does not contain the answer, reply ONLY with:
   "I couldn't find reliable information about this in the available university documents. Please check with the relevant university department."
5. At the bottom, include a clean source reference in the format:
   **Source:** [Document Name], Page [Page Number]
"""


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.gemini_client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as e:
                print(f"[LLMService] Gemini client init warning: {e}")

    def sanitize_input(self, text: str) -> str:
        """Sanitize student question against prompt injection attempts."""
        patterns = [
            r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
            r"you\s+are\s+now\s+a",
            r"system\s*:",
            r"<\s*script\s*>",
            r"<\s*/\s*script\s*>",
        ]
        sanitized = text
        for p in patterns:
            sanitized = re.sub(p, "[filtered]", sanitized, flags=re.IGNORECASE)
        return sanitized.strip()

    def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        if not self.gemini_client:
            return None
        try:
            response = self.gemini_client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt
            )
            return response.text.strip() if response.text else None
        except Exception as e:
            print(f"[LLMService] Gemini generation error ({e}), falling back to grounded synthesizer")
            return None

    def _format_chatgpt_style(self, text: str, doc_name: str, page_num: int, query: str) -> str:
        """
        Transforms raw text chunks into articulate, ChatGPT-style structured Markdown.
        """
        clean_doc_title = doc_name.replace(".txt", "").replace(".pdf", "").replace("_", " ")

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Filter out administrative header lines
        content_lines = []
        for line in lines:
            line_upper = line.upper()
            if any(h in line_upper for h in [
                "CAMPUS UNIVERSITY", "OFFICE OF", "DEPARTMENT OF", "DOCUMENT CODE:", "EFFECTIVE DATE:",
                "CATEGORY:", "POLICIES", "COURSE CODE:", "COURSE TITLE:", "ACADEMIC YEAR:"
            ]) and len(line) < 70:
                continue
            if line_upper.startswith("TITLE:"):
                continue
            content_lines.append(line)

        formatted_body = []
        for line in content_lines:
            # Check for section title pattern like "1. MINIMUM ATTENDANCE REQUIREMENT"
            if re.match(r"^\d+\.\s+[A-Z\s]{4,}", line):
                sec_title = re.sub(r"^\d+\.\s+", "", line).title()
                formatted_body.append(f"\n### 📌 {sec_title}\n")
            # Sub-item like 1.2 or (a)
            elif re.match(r"^(\d+\.\d+|\([a-z]\))\s+", line):
                sub_text = re.sub(r"^(\d+\.\d+|\([a-z]\))\s+", "", line)
                # Bold important keywords
                sub_text = re.sub(r"(\b\d+%\b|\bINR\s*\d+[,\d]*\b|\b\d{1,2}:\d{2}\s*(?:AM|PM)\b)", r"**\1**", sub_text)
                sub_text = re.sub(r"(\bdebarred\b|\bprohibited\b|\bsuspended\b|\bmandatory\b)", r"**\1**", sub_text, flags=re.IGNORECASE)
                formatted_body.append(f"- {sub_text}")
            elif line.startswith("- "):
                sub_text = line[2:]
                sub_text = re.sub(r"(\b\d+%\b|\bINR\s*\d+[,\d]*\b)", r"**\1**", sub_text)
                formatted_body.append(f"- {sub_text}")
            else:
                formatted_body.append(line)

        body_text = "\n".join(formatted_body).strip()
        if not body_text:
            body_text = text[:400]

        intro = f"Based on the official **{clean_doc_title}** regulations:"

        return (
            f"{intro}\n\n"
            f"{body_text}\n\n"
            f"---\n"
            f"**Source:** {doc_name}, Page {page_num}"
        )

    def _grounded_synthesizer_fallback(
        self,
        query: str,
        chunks: List[ChunkMetadata],
        citations: List[CitationItem]
    ) -> str:
        """
        Extractive synthesis fallback that produces ChatGPT-like responses grounded strictly in evidence.
        """
        if not chunks:
            return UNAVAILABLE_INFO_MESSAGE

        top_chunk = chunks[0]
        return self._format_chatgpt_style(top_chunk.content, top_chunk.document_name, top_chunk.page_number, query)

    def generate_answer(
        self,
        query: str,
        chunks: List[ChunkMetadata],
        citations: List[CitationItem],
        is_confident: bool,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, bool]:
        """
        Generates grounded response using Gemini or ChatGPT-style deterministic synthesis fallback.
        """
        if not is_confident or not chunks:
            return (UNAVAILABLE_INFO_MESSAGE, False)

        sanitized_query = self.sanitize_input(query)

        # Build context prompt
        context_blocks = []
        for i, chunk in enumerate(chunks):
            context_blocks.append(
                f"[Source {i+1}: {chunk.document_name} (Page {chunk.page_number}, Category: {chunk.category})]\n{chunk.content}"
            )
        formatted_context = "\n\n---\n\n".join(context_blocks)

        history_context = ""
        if history:
            recent_turns = history[-4:]
            history_context = "\nRecent Conversation:\n" + "\n".join([f"{h.get('role', 'user')}: {h.get('content', '')}" for h in recent_turns]) + "\n"

        prompt = f"""{SYSTEM_PROMPT}

<context>
{formatted_context}
</context>
{history_context}
Student Question: {sanitized_query}

Answer in an articulate, well-structured, ChatGPT style with clear markdown headings and bullet points:"""

        # Try Gemini if configured
        if settings.GEMINI_API_KEY and self.gemini_client:
            gemini_ans = self._generate_with_gemini(prompt)
            if gemini_ans:
                return (gemini_ans, True)

        # Use enhanced ChatGPT-style grounded synthesizer
        answer = self._grounded_synthesizer_fallback(sanitized_query, chunks, citations)
        return (answer, True)


llm_service = LLMService()
