# 📚 Complete Guide to MeTTa Self-Reflective RAG System

## Table of Contents
1. [What This Project Does](#what-this-project-does)
2. [Overall Architecture](#overall-architecture)
3. [Backend Deep Dive](#backend-deep-dive)
4. [Frontend Structure](#frontend-structure)
5. [Complete User Flow](#complete-user-flow)
6. [How Self-Reflective RAG Works](#how-self-reflective-rag-works)
7. [Code Walkthrough with Examples](#code-walkthrough)

---

## What This Project Does

### The Problem It Solves
Traditional chatbots that use RAG (Retrieval-Augmented Generation) often produce:
- ❌ **Factually incorrect answers** (claims not in the documents)
- ❌ **Irrelevant responses** (based on poorly retrieved documents)
- ❌ **Incomplete answers** (missing important information)

### The Solution: Self-Reflective RAG
this system adds **automatic self-correction**:
- ✅ **Checks document relevance** before generating answers
- ✅ **Validates factuality** (all claims must be supported)
- ✅ **Evaluates usefulness** (answers must actually help)
- ✅ **Auto-fixes problems** by rewriting queries or refining answers
- ✅ **Shows the AI's thinking** with full trace visualization

---

## Overall Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • Login/Signup Pages                                │  │
│  │  • Main Chat Interface                               │  │
│  │  • Trace Visualization                              │  │
│  │  • Authentication Context                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND (Flask)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  API Layer   │→ │  Auth Layer │→ │  RAG Engine  │      │
│  │  (app.py)    │  │ (auth.py)   │  │(orchestrator)│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                   ↓           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Database    │  │  Vector DB   │  │  LLM Client  │      │
│  │ (SQLite)     │  │ (ChromaDB)   │  │  (Gemini)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Deep Dive

### 📁 File-by-File Breakdown

#### **1. `app.py` - The Main Entry Point**
**Role**: Flask application, API endpoints, request routing

**What it does**:
- Defines all HTTP endpoints (`/health`, `/auth/signup`, `/upload_pdf`, `/ask`)
- Handles authentication via JWT tokens
- Processes file uploads
- Routes questions to the RAG pipeline

**Key functions**:
```python
@app.route("/ask", methods=["POST"])
@token_required  # Requires JWT authentication
def ask(current_user_id):
    query = request.get_json()["query"]
    result = run_pipeline(query)  # Send to RAG engine
    return jsonify(result)
```

---

#### **2. `models.py` - Database Models**
**Role**: User database structure

**What it does**:
- Defines the `User` table with SQLAlchemy
- Stores: username, email, password hash, creation date
- Provides password hashing with bcrypt

**Key structure**:
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    email = Column(String(120), unique=True)
    password_hash = Column(String(128))
    created_at = Column(DateTime)
    is_active = Column(Boolean)
```

---

#### **3. `core/orchestrator.py` - The Brain of the System**
**Role**: Orchestrates the entire Self-Reflective RAG pipeline

**What it does**:
- Coordinates retrieval → relevance check → generation → critique → refinement
- Handles multi-round refinement loops
- Manages query rewriting when documents are irrelevant
- Returns complete trace of reasoning process

**Critical flow**:
```python
def run_pipeline(query):
    1. Retrieve documents (vector search)
    2. Check relevance (ISREL)
    3. If not relevant → rewrite query → re-retrieve
    4. Generate initial answer
    5. Check factuality (ISSUP)
    6. Check usefulness (ISUSE)
    7. If critiques fail → refine answer
    8. Return final answer + trace
```

---

#### **4. `services/auth.py` - Authentication Service**
**Role**: User registration, login, JWT token management

**What it does**:
- Validates user credentials
- Hashes passwords securely
- Generates and verifies JWT tokens
- Provides decorator for protected routes

**Key functions**:
```python
def register_user(username, email, password):
    # Validate inputs
    # Check if user exists
    # Hash password
    # Save to database
    # Return user_id

def verify_token(token):
    # Decode JWT
    # Check expiration
    # Return user_id

@token_required  # Decorator for protected routes
def protected_function():
    # Only accessible with valid JWT
```

---

#### **5. `services/vector_store.py` - Document Storage & Retrieval**
**Role**: Manages ChromaDB vector database

**What it does**:
- Stores PDF chunks with embeddings
- Retrieves similar documents using semantic search
- Uses Sentence Transformers for embeddings
- Returns top-k most relevant chunks

**Key functions**:
```python
def add_chunks(chunks):
    # Convert text to embeddings
    # Store in ChromaDB
    # Index for fast retrieval

def retrieve_by_text(query, top_k=6):
    # Convert query to embedding
    # Find similar documents
    # Return top-k results
```

---

#### **6. `services/pdf_loader.py` - PDF Processing**
**Role**: Converts PDFs into processable chunks

**What it does**:
- Reads PDF files page by page
- Extracts text content
- Splits into overlapping chunks
- Adds metadata (filename, chunk_id, page_number)

**Key functions**:
```python
def pdf_to_chunks(pdf_path):
    # Read PDF
    # Extract text
    # Split into chunks (1000 chars with 200 overlap)
    # Return list of chunk dictionaries

def save_pdf(file_storage):
    # Save uploaded file
    # Return file path
```

---

#### **7. `services/critique.py` - Self-Reflection Engine**
**Role**: Three critique functions that evaluate answer quality

**What it does**:
- **ISREL**: Checks if retrieved documents are relevant to query
- **ISSUP**: Checks if answer is fully supported by documents
- **ISUSE**: Checks if answer is useful and addresses the question

**Critical functions**:

**ISREL (Relevance Check)**:
```python
def grade_relevance(query, retrieved_docs):
    # Ask LLM: "Are these docs relevant to the query?"
    # Return: {is_relevant: true/false, score: 0.85, reason: "..."}
```

**ISSUP (Factuality Check)**:
```python
def grade_grounding(answer, retrieved_docs):
    # Ask LLM: "Are all claims in answer supported by docs?"
    # Return: {
    #   fully_supported: false,
    #   unsupported_claims: ["claim X not found"],
    #   contradictions: [],
    #   missing_items: ["return types"]
    # }
```

**ISUSE (Usefulness Check)**:
```python
def grade_usefulness(answer, query):
    # Ask LLM: "Is this answer useful and complete?"
    # Return: {
    #   useful: true/false,
    #   score: 0.92,
    #   comment: "Answer is clear and complete"
    # }
```

---

#### **8. `services/llm_client.py` - LLM Interface**
**Role**: Communicates with Google Gemini 2.0 Flash

**What it does**:
- Sends prompts to Gemini API
- Handles API responses
- Manages rate limiting
- Caches results to reduce API calls

**Key functions**:
```python
def generate_text(prompt, max_tokens=800):
    # Send prompt to Gemini
    # Get response
    # Parse result
    # Cache result
    # Return text
```

---

#### **9. `services/embeddings.py` - Text Embeddings**
**Role**: Converts text to vectors for semantic search

**What it does**:
- Uses Sentence Transformers model (`all-MiniLM-L6-v2`)
- Converts text to 384-dimensional vectors
- Enables semantic similarity search

**Key function**:
```python
def embed_texts(texts):
    # Convert list of texts to embeddings
    # Return numpy array of vectors
```

---

#### **10. `config.py` - Configuration Settings**
**Role**: Centralized configuration management

**What it does**:
- Loads environment variables
- Defines default settings
- Configured for all components

**Key settings**:
```python
class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    CHROMA_DB_DIR = "./data/chroma_db"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    TOP_K = 6  # Number of documents to retrieve
    MAX_REWRITE_ATTEMPTS = 2
    MAX_REFINEMENT_ROUNDS = 2
```

---

#### **11. `services/cache_store.py` - Result Caching**
**Role**: Caches critique results to avoid redundant API calls

**What it does**:
- Stores critique results in JSON
- Keyed by query/content hash
- Reduces LLM API costs

---

#### **12. `utils/` - Utility Functions**
**Role**: Helper functions for logging and text processing

- **`logger.py`**: Records trace data for debugging
- **`text_utils.py`**: Cleans and normalizes text

---

## Frontend Structure

### **Main Components**:

#### **1. `app/page.js` - Main Chat Interface**
**Role**: The main user interface

**What it does**:
- Displays chat messages
- Handles user input
- Sends requests to backend
- Shows trace visualization
- Manages user authentication

**Key features**:
- Real-time message display
- Trace expand/collapse
- Authentication redirects
- Sidebar with user info

---

#### **2. `contexts/AuthContext.js` - Authentication State**
**Role**: Manages global authentication state

**What it does**:
- Stores user info and JWT token
- Provides login/logout functions
- Auto-verifies token on page load
- Adds auth headers to API requests

---

#### **3. `login/page.js` - Login Page**
**Role**: User login interface

**What it does**:
- Collects username/email and password
- Calls `/auth/login` endpoint
- Stores JWT token on success
- Redirects to chat on success

---

#### **4. `signup/page.js` - Registration Page**
**Role**: User registration interface

**What it does**:
- Collects username, email, password
- Validates password strength
- Calls `/auth/signup` endpoint
- Automatically logs in user after signup

---

## Complete User Flow

### 🎯 Scenario 1: User Asks a Question

#### **Step 1: Frontend Receives Question**
```
User types: "What is the add-atom function?"
Frontend (page.js) captures input
Clicks send button
```

#### **Step 2: Authentication Check**
```
Frontend checks if user is logged in
Retrieves JWT token from localStorage
Adds Authorization header to request
```

#### **Step 3: API Request**
```
POST /ask
Headers: {"Authorization": "Bearer <token>", "Content-Type": "application/json"}
Body: {"query": "What is the add-atom function?"}
```

#### **Step 4: Backend Receives Request (app.py)**
```
@app.route("/ask", methods=["POST"])
@token_required  # Validates JWT token
def ask(current_user_id):
    query = request.get_json()["query"]
    result = run_pipeline(query)  # Send to orchestrator
    return jsonify(result)
```

#### **Step 5: Document Retrieval (orchestrator.py:16)**
```python
retrieved = retrieve_by_text(query, top_k=6)
# Uses vector_store.py to find similar documents
# Returns: [{"id": "doc1_chunk_1", "text": "...", "distance": 0.12}, ...]
```

**What happens**:
1. Query text converted to embedding vector
2. ChromaDB searches for similar embeddings
3. Returns top 6 most similar document chunks
4. Each chunk has text, ID, and similarity score

#### **Step 6: Relevance Check (ISREL) (critique.py:71)**
```python
isrel = grade_relevance(query, retrieved)
# Sends prompt to LLM asking if docs are relevant
# Returns: {
#   "is_relevant": True,
#   "relevance_score": 0.85,
#   "reason": "Documents contain information about add-atom function"
# }
```

**LLM Prompt**:
```
You are a quick relevance evaluator.

Query: "What is the add-atom function?"

Retrieved documents:
[doc1_chunk_1] The add-atom function is used to...
[doc2_chunk_3] Functions for atomic operations...

Question: Do the retrieved documents contain information that is relevant 
and helpful for answering the user's query?

Return JSON: {"is_relevant": true/false, "reason": "brief", "score": 0.0}
```

**Success criteria**: `is_relevant == True`

#### **Step 7: Answer Generation (orchestrator.py:52)**
```python
context = "\n\n".join([f"[{d['id']}]\n{d['text']}" for d in retrieved])
gen_prompt = f"User query: {query}\n\nContext:\n{context}\n\nProvide a concise, grounded answer and cite document ids."
answer = generate_text(gen_prompt, max_output_tokens=800)
```

**LLM Prompt**:
```
User query: What is the add-atom function?

Context:
[doc1_chunk_1]
The add-atom function is used to add a new atom to the knowledge base...

[doc2_chunk_3]
Atomic operations in MeTTa involve...

Provide a concise, grounded answer and cite document ids.
```

**LLM Response**:
```
The add-atom function (doc1_chunk_1) is used to insert a new atom into 
the knowledge base. It takes an atom expression as input and adds it to 
the current environment (doc2_chunk_3).
```

#### **Step 8: Factuality Check (ISSUP) (critique.py:83)**
```python
issup = grade_grounding(answer, retrieved)
# Sends answer and documents to LLM for fact-checking
```

**LLM Prompt**:
```
You are a fact checker.

Generated answer:
"The add-atom function is used to insert a new atom into the knowledge base..."

Retrieved context:
[doc1_chunk_1]
The add-atom function is used to add a new atom to the knowledge base...
[doc2_chunk_3]
Atomic operations in MeTTa involve...

Tasks:
1) Does the generated answer rely on and align with the evidence present?
2) Fact-Checking: List unsupported statements.
3) Grounding Checks: Identify contradictions.
4) Missing Evidence: What aspects were not covered?

Return JSON:
{
  "fully_supported": true/false,
  "unsupported_claims": [...],
  "contradictions": [...],
  "missing_items": [...],
  "comment": "summary"
}
```

**LLM Response**:
```json
{
  "fully_supported": true,
  "unsupported_claims": [],
  "contradictions": [],
  "missing_items": [],
  "comment": "All claims are fully supported by the retrieved documents"
}
```

#### **Step 9: Usefulness Check (ISUSE) (critique.py:101)**
```python
isuse = grade_usefulness(answer, query)
```

**LLM Prompt**:
```
You are an evaluator of usefulness.

Query: What is the add-atom function?
Generated answer: "The add-atom function is used to insert a new atom..."

Question: Is the generated answer clear, complete, and useful for the user?

Return JSON: {"useful": true/false, "score": 0.0-1.0, "comment": "..."}
```

**LLM Response**:
```json
{
  "useful": true,
  "score": 0.92,
  "comment": "Answer is clear, complete, and directly addresses the question"
}
```

#### **Step 10: Success - Return Final Answer**
```python
# Both critiques passed!
trace["final_answer"] = answer
trace["passed"] = True
return {"answer": answer, "trace": trace}
```

#### **Step 11: Frontend Displays Answer**
```javascript
// Extract final answer from response
text: response.data.answer

// Display in chat bubble
// Show trace visualization (collapsible)
```

---

### 🎯 Scenario 2: Factuality Check Fails (ISSUP Failure)

**Query**: "What are the exact return types and error conditions for the match-types function?"

**Round 1 - Initial Generation**:
```
Retrieved documents contain partial information
Generated answer includes unverified claims:
- "Returns TypeError on invalid input" (NOT in documents)
- "Throws ValueError for empty strings" (NOT in documents)
```

**ISSUP Check Fails**:
```json
{
  "fully_supported": false,
  "unsupported_claims": [
    "Returns TypeError on invalid input",
    "Throws ValueError for empty strings"
  ],
  "missing_items": [
    "Complete error handling documentation",
    "Return type specifications"
  ]
}
```

**System Triggers Refinement** (orchestrator.py:95):
```python
# Refine answer with critique feedback
ref_prompt = f"""Refine the previous answer using critiques.

Previous answer: The match-types function returns...

Critiques:
Grounding: {{"fully_supported": false, "unsupported_claims": [...]}}

Context: documents doc1_chunk_2, doc3_chunk_1
Use the context to produce a corrected, fully-supported final answer.
Return final answer only."""
```

**Round 2 - Refinement**:
```python
# LLM generates corrected answer using ONLY supported information
new_answer = generate_text(ref_prompt, max_output_tokens=800)
```

**LLM Refined Answer**:
```
The match-types function is used to match patterns in the knowledge base (doc1_chunk_2).
Based on the available documentation, it processes matching operations but specific
error handling details are not documented in the retrieved sources.
```

**Re-check ISSUP**: ✅ Now passes! All claims are supported

**Return Final Answer**: Refined version with only supported claims

---

### 🎯 Scenario 3: Relevance Check Fails (ISREL Failure)

**Query**: "What is metta?"

**Round 1 - Initial Retrieval**:
```
Vector search retrieves documents about:
- Buddhist meditation practices
- "Metta" (loving-kindness) in Buddhism
- Meditation techniques
```

**ISREL Check Fails**:
```json
{
  "is_relevant": false,
  "relevance_score": 0.2,
  "reason": "Documents discuss Buddhist meditation, not MeTTa programming language"
}
```

**System Triggers Query Rewrite** (orchestrator.py:30):
```python
# Generate rewritten query
rewrite_prompt = f"""Rewrite the user's query to get better retrieval results.
Original: {query}
Reason: {isrel.get('reason')}
Return only the rewritten query."""
```

**Query Rewrite Loop**:
```python
new_query = generate_text(rewrite_prompt, max_output_tokens=128)
# Result: "What is the MeTTa programming language?"
```

**Round 2 - Re-retrieval**:
```python
# Use rewritten query for new search
retrieved = retrieve_by_text(new_query, top_k=6)
# Now retrieves MeTTa programming language documentation
```

**Re-check ISREL**: ✅ Now passes!

**Continue with Generation**: Generate answer about MeTTa programming language

---

## How Self-Reflective RAG Works

### 🔄 The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER ASKS QUESTION                           │
└────────────────────────────┬────────────────────────────────────┘
                              ↓
                    ┌──────────────────┐
                    │  1. RETRIEVAL     │
                    │  Find similar    │
                    │  documents       │
                    └──────┬───────────┘
                           ↓
                    ┌──────────────────┐      NO
                    │  2. ISREL CHECK   │ ←──────┐
                    │  Are docs         │        │
                    │  relevant?       │        │
                    └──────┬───────────┘        │
                           YES                  │
                           ↓                    │
                    ┌──────────────────┐       │
                    │  3. GENERATE      │       │
                    │  Initial answer  │       │
                    └──────┬───────────┘       │
                           ↓                    │
                    ┌──────────────────┐       │
                    │  4. ISSUP CHECK   │       │
                    │  Fully supported?│       │
                    └──────┬───────────┘       │
                 NO         YES                   │
                 │           ↓                   │
                 ├───────────┴───────────────────┤
                 ↓                                 ↓
         ┌──────────────────┐           ┌──────────────────┐
         │  5. REFINE       │           │  6. ISUSE CHECK  │
         │  Generate better │           │  Is it useful?  │
         │  answer          │           └──────┬──────────┘
         └──────┬───────────┘                NO│     YES
                │                               │     ↓
                └───────────────────────────────┴─────┘
                                              │
                                              ↓
                                         ┌──────────┐
                                         │  SUCCESS │
                                         │  Return  │
                                         │  answer  │
                                         └──────────┘
```

### 🎯 The Three Critique Functions

#### **ISREL - Relevance Check**
**Purpose**: Ensure retrieved documents are actually relevant

**Problem it solves**: Prevents answers based on irrelevant context

**Example**:
```
Query: "How do I use Python for data analysis?"
Retrieved: Documents about Java programming
ISREL Result: {"is_relevant": false, "reason": "Documents are about Java, not Python"}

System Action: Rewrite query to "Python data analysis libraries" → Re-retrieve
```

#### **ISSUP - Support Check (Factuality)**
**Purpose**: Ensure all claims in answer are supported by documents

**Problem it solves**: Prevents hallucinations and unsupported claims

**Example**:
```
Answer: "The function returns an error on invalid input"
Documents: Don't mention error handling
ISSUP Result: {"fully_supported": false, "unsupported_claims": ["error handling"]}

System Action: Refine answer to only include supported claims
```

#### **ISUSE - Usefulness Check**
**Purpose**: Ensure answer actually helps the user

**Problem it solves**: Prevents unhelpful, vague, or incomplete answers

**Example**:
```
Query: "What is the add-atom function?"
Answer: "It's a function"
ISUSE Result: {"useful": false, "score": 0.2, "comment": "Answer is too vague"}

System Action: Refine to provide specific, actionable information
```

### 🔧 How Refinement Works

When a critique fails, the system doesn't just give up. It:

1. **Analyzes the failure** - What's wrong with the current answer?
2. **Gathers feedback** - What claims are unsupported? What's missing?
3. **Generates correction prompt** - Tells LLM exactly what to fix
4. **Re-runs generation** - Creates improved answer
5. **Re-checks critiques** - Ensures fixes worked
6. **Repeats if needed** - Up to 2 refinement rounds

**Refinement Prompt Example**:
```
Refine the previous answer using critiques.

Previous answer:
The match-types function returns a TypeError on invalid input.

Critiques:
Grounding: {
  "fully_supported": false,
  "unsupported_claims": ["Returns TypeError on invalid input"],
  "missing_items": ["Complete error handling documentation"]
}

Context: documents doc1_chunk_2, doc3_chunk_1
Use the context to produce a corrected, fully-supported final answer.
Return final answer only.
```

**LLM generates improved answer**:
```
The match-types function is used to match patterns in the knowledge base.
Based on the available documentation, it processes matching operations,
though specific error handling details are not documented in the retrieved sources.
```

### 📊 Trace Data Structure

Every request returns complete trace data showing:

```json
{
  "answer": "Final answer text",
  "trace": {
    "query": "Original user query",
    "final_answer": "Final processed answer",
    "passed": true,
    "stages": [
      {"stage": "retrieval", "retrieved_ids": [...]},
      {"stage": "isrel", "result": {...}},
      {"stage": "generation", "answer": "..."},
      {"stage": "issup", "result": {...}},
      {"stage": "isuse", "result": {...}},
      {"stage": "refinement", "new_answer": "...", "rounds": 1}
    ]
  }
}
```

**Frontend uses this trace to visualize**:
- Which documents were retrieved
- Whether each check passed
- How many refinement rounds occurred
- What the LLM was "thinking" at each step

---

## Summary

### What Makes This Special

1. **Self-Correction**: System automatically fixes its own mistakes
2. **Transparency**: Users see the AI's reasoning process
3. **Reliability**: Multiple validation steps ensure quality answers
4. **Flexibility**: Adapts by rewriting queries or refining answers

### Key Innovation

Traditional RAG: **Query → Retrieve → Generate → Return**

The System: **Query → Retrieve → **Validate** → Generate → **Critique** → **Refine** → **Re-validate** → Return**

The bolded steps are what make this system revolutionary!

---


