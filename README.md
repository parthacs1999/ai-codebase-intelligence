# AI Codebase Intelligence Platform

An AI-powered codebase understanding and retrieval system designed to help developers explore, search, and understand large software repositories using **Retrieval-Augmented Generation (RAG)**, semantic search, and Large Language Models.

The platform is being built to support both **local repositories and GitHub repositories**, enabling developers to ask natural-language questions about unfamiliar codebases and receive answers grounded in the relevant source code.

> **Status:** Active development

---

## Project Goal

Large software repositories can contain thousands of files and tens of thousands of lines of code. Sending an entire repository directly to an LLM is inefficient because of context-window limitations, latency, token usage, and irrelevant context.

This project addresses that problem using a retrieval pipeline:

```text
Repository
    ↓
Repository Ingestion
    ↓
Source Code Discovery
    ↓
Code Parsing & Chunking
    ↓
Embeddings
    ↓
Vector Database
    ↓
Semantic / Hybrid Retrieval
    ↓
Reranking
    ↓
LLM
    ↓
Grounded Answer
```

Instead of providing the entire repository to an LLM, the system retrieves only the code most relevant to the user's question.

---

## Planned Capabilities

The completed platform is intended to support:

- Local repository ingestion
- GitHub repository ingestion
- Multi-language source-code discovery
- Structure-aware code chunking
- Semantic code search
- Vector embeddings
- Vector storage and retrieval
- Hybrid lexical + semantic retrieval
- Retrieval reranking
- Natural-language codebase Q&A
- Source file and line references
- Multi-repository search
- Agentic query processing
- FastAPI backend
- PostgreSQL metadata persistence
- Redis caching
- Dockerized deployment

---

## Example

Given a repository containing:

```text
project/
├── auth.py
├── users.py
├── database.py
└── payment.py
```

A developer could ask:

```text
Where is user authentication handled?
```

Instead of sending the entire repository to the LLM, the system will:

```text
Question
   ↓
Create Query Embedding
   ↓
Search Indexed Code
   ↓
Retrieve Relevant Chunks
   ↓
Rerank Results
   ↓
Provide Context to LLM
   ↓
Generate Grounded Answer
```

A future response could identify the relevant source:

```text
Authentication is primarily implemented in auth.py.

Relevant source:
auth.py:20-48
```

---

## Architecture

```text
                     Repository
                         |
               +---------+---------+
               |                   |
          Local Path           GitHub URL
               |                   |
               |              Repository Clone
               |                   |
               +---------+---------+
                         |
                         v
                Repository Loader
                         |
                         v
                   Code Chunker
                         |
                         v
                  Embedding Model
                         |
                         v
                     ChromaDB
                         |
                         v
                    Retrieval
                         |
                         v
                     Reranker
                         |
                         v
               Agentic RAG Pipeline
                         |
                         v
                      Gemini
                         |
                         v
                Grounded Response
```

Supporting infrastructure planned for later stages:

```text
FastAPI       -> API layer
PostgreSQL    -> repository and application metadata
Redis         -> caching
Docker        -> containerization
```

---

## Tech Stack

### Current

- Python
- Google Gemini API
- Git

### Planned

- ChromaDB
- Sentence Transformers
- LangGraph
- FastAPI
- PostgreSQL
- Redis
- Docker
- GitHub integration

---

## Current Progress

### Day 1 - Repository Ingestion

- [x] Project environment setup
- [x] Gemini API integration
- [x] Environment-variable based API key management
- [x] Recursive repository traversal
- [x] Source-file filtering
- [x] Source-code reading
- [x] File metadata extraction
- [x] UTF-8 decoding error handling

### Day 2 - Code Chunking & Embeddings

- [ ] Line-based code chunking
- [ ] Chunk overlap
- [ ] Chunk metadata and line ranges
- [ ] Understand embedding generation
- [ ] Generate code embeddings
- [ ] Similarity experiments

### Retrieval

- [ ] ChromaDB integration
- [ ] Semantic search
- [ ] Metadata-aware retrieval
- [ ] Hybrid retrieval
- [ ] Reranking

### Generation

- [ ] Retrieval-Augmented Generation pipeline
- [ ] Gemini grounded generation
- [ ] Source attribution
- [ ] Query decomposition

### Production Engineering

- [ ] GitHub repository ingestion
- [ ] Multi-repository support
- [ ] FastAPI service
- [ ] PostgreSQL persistence
- [ ] Redis caching
- [ ] LangGraph orchestration
- [ ] Docker deployment
- [ ] Evaluation pipeline

---

## Current Project Structure

```text
ai-codebase-intelligence/
├── src/
│   └── repository_loader.py
│
├── sample_repo/
│   ├── auth.py
│   ├── main.py
│   └── backend/
│       └── user.js
│
├── test_gemini.py
├── .env
├── .gitignore
└── README.md
```

The structure will evolve as retrieval, API, persistence, caching, and agent components are introduced.

---

## Repository Loader

The current ingestion pipeline recursively discovers supported source files.

Currently supported extensions:

```text
.py     Python
.js     JavaScript
.ts     TypeScript
.java   Java
.cpp    C++
.go     Go
```

For every source file, the loader extracts metadata such as:

```json
{
  "file_path": "../sample_repo/auth.py",
  "file_name": "auth.py",
  "extension": ".py",
  "language": "python"
}
```

The source code and associated metadata will later be passed to the chunking and embedding pipeline.

---

## Environment Variables

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

The API key is loaded using `python-dotenv`.

> **Never commit `.env` or API keys to Git.**

Make sure `.gitignore` contains:

```text
.env
.venv/
__pycache__/
.DS_Store
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ai-codebase-intelligence
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

### 3. Activate it

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

At the current development stage:

```bash
pip install google-genai python-dotenv
```

### 5. Configure Gemini

Create `.env`:

```text
GEMINI_API_KEY=your_api_key
```

### 6. Test the Gemini connection

```bash
python test_gemini.py
```

---

## Key Concepts

This project explores several core AI engineering concepts.

### Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) combines information retrieval with LLM generation. Relevant information is retrieved first and supplied as context to the model.

### Embeddings

Embeddings represent code and natural language as numerical vectors, allowing semantically related content to be discovered even when it does not contain exactly the same keywords.

### Semantic Search

Semantic search searches by meaning rather than exact keyword matches.

For example, a query about:

```text
login
```

may retrieve a function named:

```python
authenticate_user()
```

even though the exact word `login` does not appear in the function name.

### Vector Search

Vector search compares the query embedding against stored code embeddings to identify semantically similar code chunks.

### Metadata-Aware Retrieval

Metadata-aware retrieval preserves information such as:

- Repository
- File path
- File name
- Programming language
- Start line
- End line

This allows retrieved results and generated answers to be traced back to their source.

---

## Development Roadmap

```text
Repository Ingestion
        ↓
Code Chunking
        ↓
Embeddings
        ↓
Vector Database
        ↓
Semantic Search
        ↓
Hybrid Retrieval
        ↓
Reranking
        ↓
RAG
        ↓
GitHub Integration
        ↓
Agentic Retrieval
        ↓
FastAPI
        ↓
PostgreSQL + Redis
        ↓
Docker
        ↓
Evaluation & Optimization
```

---

## Project Motivation

The goal of this project is not simply to build another chatbot. It is to explore how production-oriented AI systems can combine:

- Software engineering
- Information retrieval
- Large Language Models
- Embeddings
- Agent orchestration
- Backend infrastructure
- Caching
- Evaluation
- Observability

The final system aims to provide a practical interface for understanding unfamiliar and large codebases without requiring the entire repository to be placed into an LLM context window.

---

## Development Status

This project is being developed incrementally, with each component implemented and understood from first principles before introducing higher-level frameworks.

Current milestone:

```text
Repository
    ↓
File Discovery
    ↓
Source Reading
    ↓
Metadata
```

**Completed**

Next milestone:

```text
Code Chunking
    ↓
Embeddings
    ↓
Vector Search
```
