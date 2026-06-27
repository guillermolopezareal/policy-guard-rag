# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Start the server:**
```powershell
venv\Scripts\activate
uvicorn app.main:app --reload
```

**Install dependencies:**
```powershell
pip install -r requirements.txt
```

**Ingest a document (server must be running):**
```powershell
python scripts/test_ingest.py samples/sample_security_policy.txt
```

**Health check:**
```powershell
curl http://localhost:8000/health
```

**Interactive API docs:** http://localhost:8000/docs (Swagger UI, available when server is running)

**Regenerate sample PDFs:**
```powershell
python scripts/generate_sample_pdfs.py
```

## Architecture

PolicyGuard RAG is a FastAPI service that answers questions about company policy documents using the RAG (Retrieval-Augmented Generation) pattern. It uses OpenAI for embeddings and generation, and ChromaDB as a local vector store.

**Request flow — ingest:**
`POST /ingest` → `ingestor.py` parses PDF/TXT into paragraph chunks → embeds via `text-embedding-3-small` → upserts into ChromaDB collection `"policies"` at `./chroma_db/`

**Request flow — query:**
`POST /query` → `retriever.py` embeds the question → similarity searches ChromaDB (top-5) → converts L2 distances to cosine similarity scores → `generator.py` applies a confidence gate (threshold 0.25) → if passed, calls `gpt-4o-mini` with context-only system prompt → returns `QueryResponse`

**Confidence gate:** The system refuses to answer (`answered: false`) when the best-matching chunk scores below 0.25. This prevents hallucination from pretrained LLM knowledge. The score formula is `1 - (L2_distance² / 2)`, which converts ChromaDB's L2 output to cosine similarity for unit-normalized vectors.

**ChromaDB persistence:** The vector store is saved to `chroma_db/` (git-ignored). Re-ingesting the same filename upserts (overwrites) existing chunks using IDs of the form `{filename}::{chunk_index}`.

## Key files

| File | Role |
|------|------|
| `app/main.py` | FastAPI app, four endpoints, timing middleware |
| `app/ingestor.py` | PDF/TXT parsing, chunking, embedding, ChromaDB write |
| `app/retriever.py` | Question embedding, vector search, L2→cosine conversion; defines `CONFIDENCE_THRESHOLD` |
| `app/generator.py` | Confidence gate, prompt assembly, GPT-4o-mini call |
| `app/models.py` | Pydantic schemas for all request/response types |
| `scripts/test_ingest.py` | CLI wrapper around `POST /ingest` (takes a file path as argv[1]) |

## Environment

Requires a `.env` file with `OPENAI_API_KEY`. Copy `.env.example` to get started. The app loads `.env` via `python-dotenv` at startup (`app/main.py` line 5).

## Windows / PowerShell notes

`scripts/test_ingest.py` uses `httpx` (not `curl`) so it works cross-platform. On PowerShell 5.1, use `python scripts/test_ingest.py <path>` rather than curl multipart commands, as PowerShell 5.1's `Invoke-WebRequest` has quirks with multipart form data.
