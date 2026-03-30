# 📚 Course-RAG — AI-Powered Course Planning Assistant

An **agentic RAG (Retrieval-Augmented Generation)** system that reads your course materials (PDFs & HTML files) and answers academic questions using AI — with proper citations.

Built with **LangChain**, **FAISS**, **HuggingFace Embeddings**, and **CrewAI** multi-agent framework.

---

## 🧠 How It Works (The Big Picture)

The system works in two main phases:

1. **Ingestion Phase** — Read documents, break them into chunks, convert them into numbers (embeddings), and store them in a searchable database.
2. **Query Phase** — When you ask a question, the AI searches the database, retrieves relevant chunks, and uses multiple AI agents to build a well-cited answer.

---

## 🔄 The Complete Pipeline

### Step 1: Document Ingestion (Loading)

> **What happens:** The system reads all your course material files from the `data/` folder.

- **PDF files** are loaded using `PyPDFLoader` — it reads each page separately and keeps track of which page the content came from.
- **HTML files** are loaded using `BSHTMLLoader` (BeautifulSoup) — useful for web-based policies or catalog pages.
- Each loaded page/document gets a **source tag** (e.g., `Lesson_13_OOP.pdf (Page 3)`) so the system always knows where the information came from.

**In simple words:** _Think of this step as a librarian reading every book and marking which page and book each paragraph belongs to._

📁 **Source:** `src/ingest.py` → `ingest_data()`

---

### Step 2: Chunking (Splitting into Smaller Pieces)

> **What happens:** Each document is split into smaller, overlapping pieces called **chunks**.

- Uses `RecursiveCharacterTextSplitter` from LangChain.
- **Chunk size:** 1000 characters (roughly a paragraph).
- **Chunk overlap:** 150 characters — the end of one chunk overlaps with the start of the next, so no information is lost at the boundaries.

**Why chunk?** LLMs (Large Language Models) have a limit on how much text they can process at once. By breaking documents into smaller pieces, we can search and retrieve only the most relevant parts instead of sending entire PDFs to the AI.

**In simple words:** _Imagine cutting a long newspaper article into index cards, where each card slightly overlaps with the next so you don't miss anything at the edges._

📁 **Source:** `src/ingest.py` → `RecursiveCharacterTextSplitter`

---

### Step 3: Embedding (Converting Text to Numbers)

> **What happens:** Each chunk is converted into a **vector** (a list of numbers) that captures its meaning.

- Uses the **`all-MiniLM-L6-v2`** model from HuggingFace (via `sentence-transformers`).
- This is a lightweight, fast model that runs **locally** — no API calls needed.
- Each chunk becomes a 384-dimensional vector — a list of 384 numbers that represent what the text is about.

**Why embeddings?** Computers can't understand text directly, but they're great with numbers. Embeddings capture the _meaning_ of text so that similar topics end up with similar numbers. For example, "prerequisites for C++" and "what do I need before learning C++" would have very similar vectors even though the words are different.

**In simple words:** _This step translates each index card from English into a secret code of numbers. Cards about similar topics get similar codes._

📁 **Source:** `src/ingest.py` → `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")`

---

### Step 4: Vector Store (Saving the Searchable Database)

> **What happens:** All the chunk vectors are stored in a **FAISS index** — a fast, in-memory database optimized for finding similar vectors.

- **FAISS** (Facebook AI Similarity Search) is a library built by Meta for efficiently searching through millions of vectors.
- The index is saved locally to the `embeddings/` folder as two files:
  - `index.faiss` — the actual vector index
  - `index.pkl` — the metadata (source names, page numbers, original text)
- Once saved, you **don't need to re-run ingestion** — just load the existing index.

**How search works:** When you ask a question, your question is also converted into a vector using the same embedding model. FAISS then finds the **top 3 chunks** whose vectors are closest to your question's vector (using similarity search). These are the most relevant pieces of your course material.

**In simple words:** _Think of FAISS as a magical filing cabinet. You describe what you're looking for, and it instantly pulls out the 3 most relevant index cards._

📁 **Source:** `src/rag_tool.py` → `CatalogRetrievalTool`  
📂 **Stored at:** `embeddings/index.faiss` + `embeddings/index.pkl`

---

### Step 5: Multi-Agent Query System (CrewAI)

> **What happens:** When you ask a question, a team of 4 AI agents work together in sequence to give you the best possible answer.

The agents run **sequentially** — each one passes its output to the next:

| # | Agent | Role | What It Does |
|---|-------|------|-------------|
| 1 | **Intake Agent** | Student Intake Specialist | Classifies your question as either a **Knowledge Query** (e.g., "What is DBMS?") or a **Planning Query** (e.g., "Can I take CS301?"). Prepares the question for the next agent. |
| 2 | **Retriever Agent** | Catalog Research Specialist | Uses the FAISS vector store to search for relevant chunks. Returns the most relevant facts with source citations. This is the only agent with access to the search tool. |
| 3 | **Planner Agent** | Academic Advisor & Knowledge Expert | Takes the retrieved information and builds a comprehensive answer. For knowledge queries, it explains concepts. For planning queries, it checks prerequisites and proposes course plans. |
| 4 | **Verifier Agent** | Quality & Citation Auditor | Final quality check — ensures every claim has a citation, the answer addresses the question, and the response follows a structured format. If the docs don't have the answer, it enforces safe abstention. |

**In simple words:** _It's like asking a question at a university help desk with four staff members — one understands your question, one looks up the records, one drafts the answer, and one double-checks everything before giving you the final response._

📁 **Source:** `src/agents.py`, `src/tasks.py`, `src/main.py`

---

## 📁 Project Structure

```
Course-RAG/
├── data/                    # 📄 Your course materials (PDFs + HTML)
│   ├── Lesson_01_Fundamentals.pdf
│   ├── Lesson_12_Intro_to_C++.pdf
│   ├── Overview_Of_Computer_Science_Syllabus.pdf
│   ├── Cancellation of Admission & Refund Policy.html
│   └── ... (28 documents total)
│
├── src/                     # 🧠 Core source code
│   ├── ingest.py            # Document loading, chunking, embedding, and FAISS storage
│   ├── rag_tool.py          # CrewAI tool that searches the FAISS vector store
│   ├── agents.py            # Defines the 4 AI agents and their roles
│   ├── tasks.py             # Defines what each agent should do
│   └── main.py              # Entry point — runs a query through the full pipeline
│
├── embeddings/              # 💾 FAISS vector store (generated by ingest.py)
│   ├── index.faiss
│   └── index.pkl
│
├── scripts/
│   └── evaluate.py          # 🧪 25-query evaluation suite across 4 categories
│
├── output/                  # 📊 Evaluation results
│   ├── eval_log.txt
│   └── report_log.txt
│
├── requirements.txt         # 📦 Python dependencies
├── .env                     # 🔑 API keys (OPENROUTER_API_KEY)
└── README.MD                # 📖 You are here!
```

---

## 🚀 Getting Started

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up API Key

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

The LLM runs via [OpenRouter](https://openrouter.ai/) using the `nvidia/nemotron-3-super-120b` model.

### 3. Add Your Course Materials

Place your PDF and HTML files in the `data/` folder.

### 4. Run Ingestion (One-Time Setup)

```bash
python -m src.ingest
```

This will:
- Load all PDFs and HTML files from `data/`
- Split them into ~1000-character chunks with 150-character overlap
- Generate embeddings using `all-MiniLM-L6-v2`
- Save the FAISS index to `embeddings/`

You only need to run this once (or again if you add new documents).

### 5. Ask a Question

```bash
python -m src.main "What is DBMS?"
python -m src.main "Can I study arrays without learning control statements first?"
python -m src.main "What is the exam paper structure for Computer Science?"
```

---

## 🧪 Evaluation

The project includes a **25-query evaluation suite** across 4 categories:

| Category | # Queries | Purpose |
|----------|-----------|---------|
| Prerequisite Checks | 10 | Tests if the system can correctly determine course prerequisites |
| Prerequisite Chain Questions | 5 | Tests multi-hop reasoning across multiple lessons |
| Program Requirement Questions | 5 | Tests knowledge of syllabus structure, exam format, and policies |
| Not-in-Docs / Trick Questions | 5 | Tests if the system correctly refuses to answer when info isn't available |

Run the evaluation:

```bash
python -m scripts.evaluate
```

Results are saved to `output/eval_log.txt` and `output/report_log.txt`.

---

## 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Document Loading | LangChain (`PyPDFLoader`, `BSHTMLLoader`) | Read PDFs and HTML files |
| Text Splitting | LangChain (`RecursiveCharacterTextSplitter`) | Break documents into searchable chunks |
| Embeddings | HuggingFace (`all-MiniLM-L6-v2`) | Convert text to 384-dim vectors (runs locally) |
| Vector Store | FAISS (Facebook AI Similarity Search) | Fast similarity search over vectors |
| LLM | OpenRouter (`nvidia/nemotron-3-super-120b`) | Powers the AI agents' reasoning |
| Agent Framework | CrewAI | Orchestrates the 4-agent sequential pipeline |

---

## 📝 Key Concepts Explained

### What is RAG?
**Retrieval-Augmented Generation** — instead of asking the AI to answer from memory (which can hallucinate), we first _retrieve_ relevant documents and then _generate_ an answer based on those documents. This makes the answers grounded in your actual course materials.

### What is an Embedding?
A way to represent text as a list of numbers that captures its meaning. Similar texts get similar numbers, making it possible to search by meaning rather than exact keywords.

### What is a Vector Store?
A database optimized for storing and searching embeddings. FAISS can find the most similar vectors in milliseconds, even with thousands of chunks.

### What is CrewAI?
A framework for building teams of AI agents that work together. Each agent has a specific role and passes its work to the next agent, creating a pipeline of intelligent processing.

### What is Agentic RAG?
Regular RAG just retrieves and generates. **Agentic RAG** adds intelligent agents that can classify queries, make decisions, verify citations, and handle edge cases — making the system smarter and more reliable.
