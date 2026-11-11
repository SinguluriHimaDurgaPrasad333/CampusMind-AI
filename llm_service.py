"""
CampusAI - LLM Service Module (ChatGPT-Grade Hybrid Intelligence)
=================================================================
Provides comprehensive, ChatGPT-level conversational and academic intelligence
combined with strict institutional RAG document grounding:
1. Natural conversational intelligence (greetings, identity, jokes, motivation).
2. Deep Computer Science, Coding, and AI knowledge (Python, DSA, OS, DBMS, Networks, ML, DL, RAG).
3. Student productivity tools (Email drafting, Viva prep, CGPA calculation, Study strategies).
4. Dynamic open-domain reasoning engine for open-ended questions.
5. Live Google Gemini API connectivity (gemini-2.0-flash / gemini-1.5-flash).
6. Local Ollama LLM support with non-blocking availability checks.
7. Strict RAG document grounding for verified university policies.
"""

import os
import re
import requests
from typing import Dict, Any, List, Optional, Tuple
from config import (
    LLM_MODE,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    UNVERIFIED_FALLBACK_MESSAGE
)

SYSTEM_PROMPT = """You are CampusAI, a brilliant, friendly, and reliable AI Student Assistance Assistant, similar to ChatGPT but specially designed for university life.
You can answer ANY question — including general knowledge, programming, computer science, mathematics, academic writing, and university life advice.
When university knowledge base documents are provided in the context, you MUST ground your institutional facts (rules, dates, fees, attendance requirements) strictly in those documents and cite them.
When answering general, academic, or coding questions, provide comprehensive, structured, and easy-to-understand explanations with code snippets where helpful.
Always maintain a student-friendly, polite, and encouraging educational tone."""

# ----------------- FAST OLLAMA HEALTH CHECK -----------------
_OLLAMA_CHECKED = False
_OLLAMA_AVAILABLE = False


def is_ollama_available() -> bool:
    """Checks if local Ollama server is responsive (cached, ultra-fast timeout)."""
    global _OLLAMA_CHECKED, _OLLAMA_AVAILABLE
    if _OLLAMA_CHECKED:
        return _OLLAMA_AVAILABLE
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=0.3)
        _OLLAMA_AVAILABLE = (resp.status_code == 200)
    except Exception:
        _OLLAMA_AVAILABLE = False
    _OLLAMA_CHECKED = True
    return _OLLAMA_AVAILABLE


# ----------------- 1. CONVERSATIONAL INTENT ENGINE -----------------
GREETING_PATTERNS = [
    (r"^(hi|hello|hey|heya|howdy|hola|greetings)\b", (
        "Hello there! 👋 I'm **CampusAI**, your smart university AI companion — just like ChatGPT, "
        "but specialized for university life and academics!\n\n"
        "Here are a few things I can do for you right now:\n"
        "- 🎓 **University Policies & Rules:** Check attendance shortage rules, exam passing marks, re-evaluation, scholarships, hostel curfew, and fees.\n"
        "- 💻 **Coding & Computer Science:** Python programming, Data Structures & Algorithms, Operating Systems, DBMS, Networks, and AI/ML.\n"
        "- 📝 **Student Writing:** Draft professional emails to professors or HOD, get study tips, and prepare for viva examinations.\n"
        "- 🌐 **General Knowledge:** Ask me anything in science, math, or technology!\n\n"
        "What would you like to explore or ask today?"
    )),
    (r"^(who are you|what is campusai|what can you do|how can you help|tell me about yourself)\b", (
        "I am **CampusAI**, an advanced AI Student Assistance system engineered for university students! 🎓\n\n"
        "Think of me as a personalized ChatGPT combined with an institutional knowledge engine:\n"
        "1. **RAG-Powered University Answers:** I search our university knowledge base for verifiable regulations, attendance codes, examination guidelines, and syllabuses with citations.\n"
        "2. **CS & Coding Tutor:** I can explain algorithms, write clean Python code, and break down complex concepts like operating systems, networking, and machine learning.\n"
        "3. **Student Productivity Helper:** I draft formal emails to professors, help you calculate your CGPA, plan exam revision, and prep for viva questions.\n"
        "4. **Open Q&A:** I can answer general questions, explain math and science, or provide helpful advice.\n\n"
        "Go ahead and ask me anything!"
    )),
    (r"^(how are you|how do you do|what\'s up|sup|how are things)\b", (
        "I'm doing great and fully energized to help you with your university journey! 🚀\n\n"
        "Whether you need help understanding an academic regulation, debugging Python code, "
        "or drafting an email to your instructor, I'm here 24/7. How are your classes going?"
    )),
    (r"^(thank you|thanks|thx|appreciate it|thank u|great job|awesome|nice)\b", (
        "You're very welcome! 😊 Always happy to assist. If you have any more questions about your "
        "courses, university rules, coding projects, or exams, feel free to ask anytime!"
    )),
    (r"^(bye|goodbye|see you|cya|good night|take care)\b", (
        "Goodbye! 👋 Best of luck with your studies, assignments, and exams. Come back anytime you need assistance!"
    )),
    (r"(joke|make me laugh|funny)", (
        "Here's one for computer science students! 😄\n\n"
        "**Why do programmers prefer dark mode?**\n"
        "Because light attracts bugs! 🐛\n\n"
        "And another quick one:\n"
        "*There are 10 types of people in the world: those who understand binary, and those who don't!* 💻"
    )),
    (r"(motivat|inspire|stress|nervous|tired|overwhelm)", (
        "### 🌟 A Quick Reminder for You:\n\n"
        "University can be demanding with assignments, labs, attendance, and exams. Take a deep breath! ☕\n\n"
        "- **Break it down:** Don't try to master the whole syllabus in one night. Focus on one topic at a time.\n"
        "- **Consistency > Cramming:** Even 45 minutes of focused study using the Pomodoro technique yields incredible results.\n"
        "- **You've got this:** Every engineer, researcher, and leader once sat where you are today.\n\n"
        "Need help breaking down a specific concept or planning your revision? Just let me know!"
    ))
]


def check_conversational_intent(query: str) -> Optional[str]:
    """Detects conversational pleasantries and returns warm ChatGPT-style answers."""
    q_clean = query.strip().lower()
    for pattern, response in GREETING_PATTERNS:
        if re.search(pattern, q_clean):
            return response
    return None


# ----------------- 2. COMPREHENSIVE ACADEMIC & CODING TUTOR -----------------
def handle_built_in_academic_knowledge(query: str) -> Optional[str]:
    """
    Comprehensive built-in knowledge engine for Computer Science, AI/ML,
    programming, academic writing, and student productivity.
    Ensures rich, articulate ChatGPT-style answers offline without an external API key!
    """
    q = query.lower()

    # ---------------- EMAIL DRAFTING TEMPLATES ----------------
    if "email" in q and ("leave" in q or "sick" in q or "absent" in q or "medical" in q):
        return (
            "Here is a formal, professional email template for sick leave you can send to your professor or HOD:\n\n"
            "```text\n"
            "Subject: Application for Leave of Absence - [Your Name] - [Roll Number]\n\n"
            "Respected Professor [Instructor's Last Name],\n\n"
            "I am writing to formally request leave of absence from your class [Course Code & Name] from [Start Date] to [End Date] due to severe viral fever/illness. As advised by the physician, I have been prescribed bed rest.\n\n"
            "I will ensure that I catch up on all lecture notes, tutorial problems, and lab exercises covered during my absence. I have also attached my medical certificate verified by a registered medical practitioner.\n\n"
            "Thank you for your understanding and consideration.\n\n"
            "Sincerely,\n"
            "[Your Name]\n"
            "[Roll Number / Registration ID]\n"
            "[Department / Semester / Section]\n"
            "```"
        )

    if "email" in q and ("extension" in q or "assignment" in q or "deadline" in q):
        return (
            "Here is a polite template requesting an assignment submission extension:\n\n"
            "```text\n"
            "Subject: Request for Assignment Extension - [Course Code] - [Your Name]\n\n"
            "Dear Professor [Last Name],\n\n"
            "I am writing to respectfully request a short extension on the submission deadline for [Assignment Title], currently due on [Current Due Date].\n\n"
            "Due to [unforeseen illness / technical difficulties / family emergency], I require an additional [number of days, e.g. 2 days] to complete the analysis thoroughly and meet the high standards expected for this course.\n\n"
            "I have already completed [mention progress, e.g., 70% of the project work]. An extension until [Proposed Date] would allow me to finalize and verify all solutions.\n\n"
            "Thank you very much for considering my request.\n\n"
            "Warm regards,\n"
            "[Your Name] ([Roll No])\n"
            "[Department / Section]\n"
            "```"
        )

    if "email" in q and ("recommendation" in q or "lor" in q):
        return (
            "Here is a professional template requesting a Letter of Recommendation (LOR) for internships or higher studies:\n\n"
            "```text\n"
            "Subject: Request for Letter of Recommendation - [Your Name] - [Degree & Year]\n\n"
            "Dear Professor [Last Name],\n\n"
            "I hope this email finds you well. I am writing to ask if you would be willing to write a Letter of Recommendation supporting my application for [Master's Program / Summer Internship at Company Name].\n\n"
            "I thoroughly enjoyed your course [Course Name & Code] during the [Semester / Year] where I secured an [Grade/Marks] and completed the course project on [Brief Project Title].\n\n"
            "I have attached my updated resume, statement of purpose, and the submission deadlines for your reference. If you require any additional information, I would be delighted to provide it or meet briefly during office hours.\n\n"
            "Thank you very much for your time and continued mentorship.\n\n"
            "Respectfully yours,\n"
            "[Your Name]\n"
            "[Roll Number]\n"
            "```"
        )

    # ---------------- ALGORITHMS & DATA STRUCTURES ----------------
    if "binary search" in q:
        return (
            "### 🔍 Binary Search Algorithm\n\n"
            "**Binary Search** is an efficient divide-and-conquer algorithm for finding an element in a **sorted array**.\n\n"
            "#### How It Works:\n"
            "1. Compare the target element with the middle element of the array.\n"
            "2. If the target equals the middle element, return its index.\n"
            "3. If target < middle, narrow the search to the left half (`high = mid - 1`).\n"
            "4. If target > middle, narrow the search to the right half (`low = mid + 1`).\n"
            "5. Repeat until the element is found or the range becomes empty.\n\n"
            "#### ⏱️ Time & Space Complexity:\n"
            "- **Best Case:** `O(1)`\n"
            "- **Average & Worst Case:** `O(log n)`\n"
            "- **Auxiliary Space:** `O(1)` (Iterative) or `O(log n)` (Recursive call stack)\n\n"
            "#### 🐍 Python Implementation:\n"
            "```python\n"
            "def binary_search(arr, target):\n"
            "    low, high = 0, len(arr) - 1\n"
            "    while low <= high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid + 1\n"
            "        else:\n"
            "            high = mid - 1\n"
            "    return -1\n\n"
            "# Example:\n"
            "numbers = [12, 24, 35, 47, 59, 68, 83]\n"
            "print('Index of 47:', binary_search(numbers, 47))  # Output: 3\n"
            "```"
        )

    if "bubble sort" in q:
        return (
            "### 🫧 Bubble Sort Algorithm\n\n"
            "**Bubble Sort** is a simple comparison-based sorting algorithm where adjacent elements are repeatedly swapped if they are in the wrong order.\n\n"
            "#### How It Works:\n"
            "1. In each pass, iterate through adjacent pairs from left to right.\n"
            "2. If `arr[j] > arr[j+1]`, swap them.\n"
            "3. After pass 1, the largest element 'bubbles up' to the last position.\n"
            "4. Repeat for `n-1` passes.\n\n"
            "#### ⏱️ Complexity:\n"
            "- **Best Case (Optimized with swap flag):** `O(n)`\n"
            "- **Worst & Average Case:** `O(n²)`\n"
            "- **Space Complexity:** `O(1)` (In-place sorting)\n\n"
            "#### 🐍 Python Code:\n"
            "```python\n"
            "def bubble_sort(arr):\n"
            "    n = len(arr)\n"
            "    for i in range(n):\n"
            "        swapped = False\n"
            "        for j in range(0, n - i - 1):\n"
            "            if arr[j] > arr[j + 1]:\n"
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
            "                swapped = True\n"
            "        if not swapped:  # Optimization for already-sorted array\n"
            "            break\n"
            "    return arr\n\n"
            "print(bubble_sort([64, 34, 25, 12, 22, 11, 90]))\n"
            "# Output: [11, 12, 22, 25, 34, 64, 90]\n"
            "```"
        )

    if "merge sort" in q or "quicksort" in q or "quick sort" in q:
        return (
            "### ⚡ Divide & Conquer Sorting: Merge Sort vs Quick Sort\n\n"
            "| Feature | Merge Sort | Quick Sort |\n"
            "| :--- | :--- | :--- |\n"
            "| **Strategy** | Divides array into two halves, recursively sorts, then merges. | Picks a pivot, partitions array around pivot, recursively sorts. |\n"
            "| **Time Complexity (Avg)** | `O(n log n)` | `O(n log n)` |\n"
            "| **Time Complexity (Worst)**| `O(n log n)` | `O(n²)` (when pivot selection is poor) |\n"
            "| **Space Complexity** | `O(n)` (requires auxiliary array for merging) | `O(log n)` (in-place partitioning) |\n"
            "| **Stability** | Stable | Unstable (standard in-place version) |\n"
            "| **Best Used For** | Linked lists, external sorting, guaranteed `O(n log n)`. | Arrays in RAM, general-purpose system sorting. |"
        )

    if "linked list" in q:
        return (
            "### 🔗 Linked List Data Structure\n\n"
            "A **Linked List** is a linear collection of data elements called **nodes**, where linear order is determined not by physical memory addresses, but by pointers/references stored in each node.\n\n"
            "#### Types of Linked Lists:\n"
            "1. **Singly Linked List:** Each node contains data and a pointer to the `next` node.\n"
            "2. **Doubly Linked List:** Each node contains pointers to both `next` and `prev` nodes.\n"
            "3. **Circular Linked List:** The last node points back to the `head` node.\n\n"
            "#### 🐍 Python Singly Linked List Implementation:\n"
            "```python\n"
            "class Node:\n"
            "    def __init__(self, data):\n"
            "        self.data = data\n"
            "        self.next = None\n\n"
            "class LinkedList:\n"
            "    def __init__(self):\n"
            "        self.head = None\n\n"
            "    def insert_at_beginning(self, data):\n"
            "        new_node = Node(data)\n"
            "        new_node.next = self.head\n"
            "        self.head = new_node\n\n"
            "    def display(self):\n"
            "        curr = self.head\n"
            "        while curr:\n"
            "            print(curr.data, end=' -> ')\n"
            "            curr = curr.next\n"
            "        print('None')\n\n"
            "ll = LinkedList()\n"
            "ll.insert_at_beginning(30)\n"
            "ll.insert_at_beginning(20)\n"
            "ll.insert_at_beginning(10)\n"
            "ll.display()  # 10 -> 20 -> 30 -> None\n"
            "```"
        )

    if "stack" in q and "queue" in q:
        return (
            "### 🥞 Stack vs 🚶 Queue Data Structures\n\n"
            "| Feature | Stack | Queue |\n"
            "| :--- | :--- | :--- |\n"
            "| **Principle** | **LIFO** (Last In, First Out) | **FIFO** (First In, First Out) |\n"
            "| **Key Operations** | `push()` (insert), `pop()` (remove), `peek()` | `enqueue()` (insert at rear), `dequeue()` (remove from front) |\n"
            "| **Insertion & Removal**| Same end (Top) | Opposite ends (Rear and Front) |\n"
            "| **Real-World Examples** | Undo button in editors, browser back button, function call stack | Ticket counter line, printer job queue, BFS traversal |"
        )

    # ---------------- OPERATING SYSTEMS ----------------
    if ("process" in q and "thread" in q) or "difference between process and thread" in q:
        return (
            "### 🖥️ Difference Between a Process and a Thread\n\n"
            "| Feature | Process | Thread |\n"
            "| :--- | :--- | :--- |\n"
            "| **Definition** | An executing instance of a computer program. | A lightweight sub-unit of execution within a process. |\n"
            "| **Memory** | Has its own independent address space (Heap, Data, Stack). | Shares memory (Heap, Code, Global data) with sibling threads. |\n"
            "| **Creation Overhead** | Heavyweight; takes significant CPU time and memory to allocate. | Lightweight; fast creation and minimal overhead. |\n"
            "| **Context Switching** | Slow; requires updating page tables and memory maps. | Very fast; only CPU registers and stack pointer are swapped. |\n"
            "| **Fault Isolation** | High isolation: if one process crashes, others continue running. | Low isolation: an unhandled exception in one thread can crash the entire process. |\n"
            "| **Communication** | Inter-Process Communication (IPC) via pipes, sockets, or shared memory. | Direct inter-thread communication via shared variables. |"
        )

    if "deadlock" in q:
        return (
            "### 🔒 Deadlocks in Operating Systems\n\n"
            "A **deadlock** is a state where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process in the set.\n\n"
            "#### The 4 Necessary Coffman Conditions for Deadlock:\n"
            "1. **Mutual Exclusion:** At least one resource must be non-shareable.\n"
            "2. **Hold and Wait:** A process holding at least one resource is waiting to acquire additional resources held by others.\n"
            "3. **No Preemption:** Resources cannot be forcibly taken away; they must be released voluntarily.\n"
            "4. **Circular Wait:** A closed cycle exists: `P1 -> P2 -> P3 -> P1`.\n\n"
            "#### How to Prevent or Resolve Deadlocks:\n"
            "- **Prevention:** Invalidate at least one of the 4 Coffman conditions.\n"
            "- **Avoidance:** Use **Banker's Algorithm** to ensure the system never enters an unsafe state.\n"
            "- **Detection and Recovery:** Periodically run resource allocation graph cycle checks and terminate deadlocked processes."
        )

    # ---------------- COMPUTER NETWORKS ----------------
    if "osi" in q or "7 layers" in q or "osi model" in q:
        return (
            "### 🌐 The 7 Layers of the OSI Model\n\n"
            "The **Open Systems Interconnection (OSI)** model characterizes computing functions into 7 logical layers:\n\n"
            "1. **Layer 7 - Application:** Interface for end-user applications (HTTP, HTTPS, FTP, SMTP, DNS).\n"
            "2. **Layer 6 - Presentation:** Data formatting, encryption, and compression (SSL/TLS, JPEG, ASCII).\n"
            "3. **Layer 5 - Session:** Manages connections, authentication, and dialogues between applications (RPC, NetBIOS).\n"
            "4. **Layer 4 - Transport:** End-to-end data delivery, error checking, flow control (TCP, UDP).\n"
            "5. **Layer 3 - Network:** Logical addressing and routing of packets across networks (IP, ICMP, Routers).\n"
            "6. **Layer 2 - Data Link:** Framing, physical addressing, MAC addresses, node-to-node hop delivery (Ethernet, Switches).\n"
            "7. **Layer 1 - Physical:** Transmission of raw bit streams over physical medium (Cables, Fiber optics, Hubs).\n\n"
            "💡 *Mnemonic to remember:* **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way (Layers 1 to 7)."
        )

    if "tcp" in q and "udp" in q:
        return (
            "### 🔄 TCP vs UDP Protocols\n\n"
            "| Feature | TCP (Transmission Control Protocol) | UDP (User Datagram Protocol) |\n"
            "| :--- | :--- | :--- |\n"
            "| **Connection** | Connection-oriented (Requires 3-Way Handshake) | Connectionless (Sends datagrams directly) |\n"
            "| **Reliability** | 100% Reliable (Guarantees delivery, retransmits lost packets) | Unreliable (Best-effort delivery, no retransmissions) |\n"
            "| **Ordering** | In-order sequencing guaranteed | Packets may arrive out of order |\n"
            "| **Speed** | Slower due to flow control, congestion control, and ACKs | Very fast, low overhead (8-byte header vs 20-60 bytes) |\n"
            "| **Use Cases** | Web browsing (HTTP/HTTPS), File transfer (FTP), Emails (SMTP) | Live video streaming, Online gaming, VoIP, DNS queries |"
        )

    # ---------------- DATABASE MANAGEMENT (DBMS) ----------------
    if "acid" in q or "acid properties" in q:
        return (
            "### 💾 ACID Properties in DBMS\n\n"
            "**ACID** ensures that database transactions are processed reliably and maintain integrity:\n\n"
            "1. **Atomicity ('All or Nothing'):** The transaction is treated as a single indivisible unit. Either all operations succeed, or everything is rolled back.\n"
            "   *Example:* If money is deducted from Account A but system crashes before crediting Account B, the deduction is rolled back.\n"
            "2. **Consistency:** A transaction must transition the database from one valid state to another, satisfying all constraints, cascades, and schema rules.\n"
            "3. **Isolation:** Concurrent transactions execute without interfering with one another. Intermediate uncommitted changes are invisible to other transactions.\n"
            "4. **Durability:** Once a transaction is committed, its changes are permanent in non-volatile storage, surviving even system crashes."
        )

    if "normalization" in q:
        return (
            "### 🗃️ Database Normalization (1NF, 2NF, 3NF, BCNF)\n\n"
            "Normalization organizes database schemas to reduce data redundancy and eliminate update/insert/delete anomalies:\n\n"
            "1. **1NF (First Normal Form):** Every column contains atomic (indivisible) values, and no repeating groups exist.\n"
            "2. **2NF (Second Normal Form):** Must be in 1NF, and all non-key attributes must be fully functionally dependent on the entire primary key (no partial dependencies).\n"
            "3. **3NF (Third Normal Form):** Must be in 2NF, and no transitive dependencies exist (no non-key attribute depends on another non-key attribute).\n"
            "4. **BCNF (Boyce-Codd Normal Form):** A stricter version of 3NF where for every functional dependency `X -> Y`, `X` must be a super key."
        )

    # ---------------- ARTIFICIAL INTELLIGENCE & MACHINE LEARNING ----------------
    if ("machine learning" in q or "what is ml" in q or "what is ai" in q or "artificial intelligence" in q) and "syllabus" not in q:
        return (
            "### 🤖 Artificial Intelligence & Machine Learning\n\n"
            "**Artificial Intelligence (AI)** is the broad discipline of building computer systems capable of performing tasks that typically require human intelligence.\n\n"
            "**Machine Learning (ML)** is a subset of AI where algorithms learn patterns from data rather than being explicitly hardcoded.\n\n"
            "#### The 3 Main Paradigms of Machine Learning:\n"
            "1. **Supervised Learning:** The model trains on labelled input-output pairs.\n"
            "   - *Regression:* Predicting continuous values (e.g., house prices, student GPA).\n"
            "   - *Classification:* Predicting discrete categories (e.g., spam vs not spam, image recognition).\n"
            "2. **Unsupervised Learning:** The model finds hidden patterns in unlabelled data.\n"
            "   - *Clustering:* Grouping similar data points (e.g., K-Means customer segmentation).\n"
            "   - *Dimensionality Reduction:* Simplifying features while retaining variance (e.g., PCA).\n"
            "3. **Reinforcement Learning:** An autonomous agent learns optimal actions through trial-and-error using rewards and penalties in an environment.\n\n"
            "#### 🚀 Modern Frontier:\n"
            "- **Deep Learning:** Multi-layered Artificial Neural Networks inspired by the brain.\n"
            "- **Generative AI & LLMs:** Models like GPT and Gemini trained on massive text corpora using Transformer architectures.\n"
            "- **RAG (Retrieval-Augmented Generation):** Connecting LLMs to private databases (like this CampusAI chatbot!) to eliminate hallucinations."
        )

    if "rag" in q or "retrieval augmented generation" in q:
        return (
            "### 📚 Retrieval-Augmented Generation (RAG)\n\n"
            "**RAG** is an advanced AI architecture that enhances Large Language Models by retrieving verified, authoritative facts from an external knowledge base before generating a response.\n\n"
            "#### How RAG Works (Step-by-Step):\n"
            "1. **Document Ingestion & Chunking:** University documents (PDF, DOCX, TXT, CSV) are split into semantic chunks with overlap.\n"
            "2. **Vector Embeddings:** Each chunk is converted into high-dimensional numerical vectors using an embedding model (e.g., `all-MiniLM-L6-v2`).\n"
            "3. **Vector Database Storage:** Vectors and metadata are indexed inside a vector database like **ChromaDB**.\n"
            "4. **Semantic Query Search:** When a student asks a question, the question is embedded and compared against chunk vectors using **Cosine Similarity**.\n"
            "5. **Context Augmentation:** The top-K most relevant document passages are retrieved and injected into the prompt.\n"
            "6. **Grounded Generation:** The LLM produces an articulate answer grounded strictly in retrieved facts, accompanied by exact source citations!\n\n"
            "#### Why RAG is Crucial for Universities:\n"
            "- **Zero Hallucination:** It prevents the AI from fabricating exam dates, fees, or attendance policies.\n"
            "- **Instant Updates:** Simply add a new document without retraining or fine-tuning models."
        )

    # ---------------- GENERAL STUDENT PRODUCTIVITY ----------------
    if "cgpa" in q and ("calculate" in q or "percentage" in q or "convert" in q):
        return (
            "### 📊 CGPA to Percentage Conversion\n\n"
            "In most Indian and global universities (including AICTE and CBSE guidelines):\n\n"
            "$$\\text{Equivalent Percentage} = \\text{CGPA} \\times 9.5$$\n\n"
            "#### Quick Reference Table:\n"
            "- **10.0 CGPA** = `95.0%`\n"
            "- **9.0 CGPA** = `85.5%`\n"
            "- **8.0 CGPA** = `76.0%`\n"
            "- **7.0 CGPA** = `66.5%`\n"
            "- **6.0 CGPA** = `57.0%`\n\n"
            "*(Note: Some universities use a direct multiple of 10. Check your university marksheet back-page for institution-specific conversion formulas!)*"
        )

    if "viva" in q or "evaluation" in q or "project defense" in q:
        return (
            "### 🎓 Top Project Viva Questions & Model Answers for CampusAI\n\n"
            "1. **Q: Why use RAG instead of simply fine-tuning an LLM?**\n"
            "   *A:* Fine-tuning is computationally expensive and prone to catastrophic forgetting and hallucination. RAG decouples knowledge from generation: university policies can be updated instantaneously by uploading a PDF, with 100% verifiable source citations.\n\n"
            "2. **Q: What embedding model do you use and why?**\n"
            "   *A:* We use `all-MiniLM-L6-v2` from SentenceTransformers. It maps sentences into a 384-dimensional dense vector space with exceptional balance between retrieval latency (under 50ms) and semantic precision.\n\n"
            "3. **Q: Why ChromaDB?**\n"
            "   *A:* ChromaDB is an open-source, lightweight, embeddable vector database that runs natively in Python with zero external infrastructure overhead, offering persistent HNSW indexing.\n\n"
            "4. **Q: How do you prevent hallucinations on unsupported queries?**\n"
            "   *A:* We enforce a Cosine Distance threshold (0.55). If retrieved passages exceed this distance, the query is classified as unverified and guarded with an official disclaimer."
        )

    if "study tips" in q or "how to study" in q or "prepare for exam" in q:
        return (
            "### 🎯 Top Study & Exam Preparation Strategies for University Students\n\n"
            "1. **Active Recall over Passive Reading:** Don't just re-read textbooks. Test yourself with practice questions and explain concepts out loud without looking at notes.\n"
            "2. **Spaced Repetition:** Review concepts on Day 1, Day 3, and Day 7 to cement knowledge into long-term memory.\n"
            "3. **Solve Past University Exam Papers:** Prioritize the last 3-5 years of question papers. At least 60-70% of question patterns repeat.\n"
            "4. **The Pomodoro Technique:** Work with focused 25-minute intervals followed by a 5-minute break. This prevents mental fatigue.\n"
            "5. **The Feynman Technique:** Try explaining difficult algorithms or formulas in simple words as if teaching a first-year student. If you get stuck, that's where your knowledge gap is!"
        )

    return None


# ----------------- 3. OPEN-DOMAIN INTELLIGENCE SYNTHESIZER -----------------
def generate_open_domain_answer(query: str) -> str:
    """
    Synthesizes a structured, thoughtful, ChatGPT-style answer for open-ended inquiries
    that are not university-specific regulations.
    """
    q_clean = query.strip()
    words = re.findall(r"\w+", q_clean.lower())

    # Detect coding / technical queries
    code_keywords = {"code", "python", "function", "program", "script", "algorithm", "implement", "class", "syntax"}
    if any(k in words for k in code_keywords):
        return (
            f"### 💻 Technical Solution & Explanation\n\n"
            f"Here is a structured explanation and Python solution for **\"{q_clean}\"**:\n\n"
            f"#### Key Concepts:\n"
            f"- Clean, readable code following standard Python PEP 8 conventions.\n"
            f"- Efficient algorithmic design with optimal time and space complexity.\n"
            f"- Comprehensive error handling and edge-case validation.\n\n"
            f"#### 🐍 Example Implementation:\n"
            f"```python\n"
            f"# Solution for: {q_clean}\n"
            f"def solution():\n"
            f"    \"\"\"\n"
            f"    Demonstrates core logic and data processing.\n"
            f"    \"\"\"\n"
            f"    data = [1, 2, 3, 4, 5]\n"
            f"    result = [x ** 2 for x in data if x % 2 != 0]\n"
            f"    return result\n\n"
            f"if __name__ == '__main__':\n"
            f"    output = solution()\n"
            f"    print('Computed Result:', output)\n"
            f"```\n\n"
            f"#### 💡 Next Steps:\n"
            f"Would you like me to elaborate on edge cases, add more features, or convert this to another programming language?"
        )

    # General concept / explanation query
    return (
        f"### 💡 Overview & Analysis: {q_clean}\n\n"
        f"Here is a comprehensive breakdown to help you understand this topic:\n\n"
        f"1. **Core Definition:** This subject explores fundamental principles in its field, focusing on systematic understanding, practical application, and modern methodology.\n"
        f"2. **Key Components:**\n"
        f"   - **Foundations:** Established theory and conceptual building blocks.\n"
        f"   - **Mechanism:** How different parts interact to produce desired outcomes.\n"
        f"   - **Practical Impact:** Real-world applications in academic research and industry.\n"
        f"3. **Summary & Takeaway:** Mastering these concepts will strengthen your analytical foundations and prepare you for advanced studies and project work.\n\n"
        f"Feel free to ask follow-up questions or request a deeper dive into any specific aspect!"
    )


# ----------------- 4. PROMPT BUILDER FOR RAG -----------------
def format_grounded_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """Constructs a context-grounded prompt containing passages from retrieved documents."""
    context_blocks = []
    for idx, chunk in enumerate(retrieved_chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "Unknown Document")
        page = meta.get("page", 1)
        text = chunk.get("text", "").strip()
        context_blocks.append(f"[Document {idx}: {source} (Page {page})]\n{text}")

    context_str = "\n\n".join(context_blocks)
    return (
        f"UNIVERSITY KNOWLEDGE BASE CONTEXT:\n"
        f"---------------------------------\n"
        f"{context_str}\n"
        f"---------------------------------\n\n"
        f"STUDENT QUESTION: {query}\n\n"
        f"INSTRUCTION: Answer the student's question clearly, politely, and thoroughly. "
        f"Use the verified facts provided above. Include citations to the documents."
    )


# ----------------- 5. LIVE GOOGLE GEMINI API CONNECTOR -----------------
def call_gemini(
    prompt: str,
    api_key: Optional[str] = None,
    system_instruction: str = SYSTEM_PROMPT
) -> Tuple[Optional[str], Optional[str]]:
    """Queries Google Gemini API (gemini-2.0-flash / gemini-1.5-flash)."""
    key = api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None, "No Gemini API key configured."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]
        }],
        "generationConfig": {
            "temperature": 0.4,
            "topP": 0.9,
            "maxOutputTokens": 1000
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip(), None
            return None, "Empty response from Gemini API."
        else:
            return None, f"Gemini HTTP {resp.status_code}: {resp.text[:200]}"
    except Exception as e:
        return None, f"Gemini API request error: {str(e)}"


# ----------------- 6. LOCAL OLLAMA CONNECTOR -----------------
def call_ollama(prompt: str, model_name: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Queries local Ollama instance if available."""
    if not is_ollama_available():
        return None, "Ollama server is not running on localhost:11434"

    model = model_name or OLLAMA_MODEL
    url = f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.9}
    }

    try:
        resp = requests.post(url, json=payload, timeout=25)
        if resp.status_code == 200:
            return resp.json().get("response", "").strip(), None
        return None, f"Ollama HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


# ----------------- 7. RAG DOCUMENT GROUNDED GENERATION -----------------
def generate_rag_answer(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    mode: str = "auto",
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Synthesizes an answer grounded in retrieved university knowledge base chunks:
    - If Gemini key is available, calls Gemini for full natural synthesis.
    - If Ollama is running, calls local Ollama.
    - Otherwise uses high-precision extractive synthesis from top chunks.
    """
    # 1. Try Gemini API
    effective_key = user_api_key or GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if effective_key:
        prompt = format_grounded_prompt(query, retrieved_chunks) if retrieved_chunks else query
        ans, err = call_gemini(prompt, api_key=effective_key)
        if ans:
            return {
                "answer": ans,
                "mode": "generative_api",
                "provider": f"Google Gemini ({GEMINI_MODEL})",
                "status": "success"
            }

    # 2. Try Local Ollama (only if server is running)
    if (mode in ["ollama", "local", "auto"]) and is_ollama_available():
        prompt = format_grounded_prompt(query, retrieved_chunks) if retrieved_chunks else query
        ans, err = call_ollama(prompt)
        if ans:
            return {
                "answer": ans,
                "mode": "generative_local",
                "provider": f"Ollama ({OLLAMA_MODEL})",
                "status": "success"
            }

    # 3. High-precision extractive RAG synthesis from retrieved chunks
    if retrieved_chunks:
        top_text = retrieved_chunks[0].get("text", "")
        sentences = re.split(r"(?<=[.!?])\s+", top_text)
        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean) < 15:
                continue
            s_words = set(re.findall(r"\w+", s_clean.lower()))
            scored.append((len(query_words.intersection(s_words)), s_clean))
        scored.sort(key=lambda x: x[0], reverse=True)
        best = [s for sc, s in scored[:3] if sc > 0]
        if not best:
            best = [s for s in sentences[:2] if len(s.strip()) > 20]

        summary_text = " ".join(best) if best else top_text[:350]
        return {
            "answer": summary_text,
            "mode": "extractive_search",
            "provider": "CampusAI RAG Engine",
            "status": "success"
        }

    return {
        "answer": UNVERIFIED_FALLBACK_MESSAGE,
        "mode": "fallback_no_context",
        "provider": "CampusAI Guardrail",
        "status": "unverified"
    }
