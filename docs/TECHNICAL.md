# Technical Reference — PolicyGuard RAG

This document explains the architecture, design decisions, and internal workings of PolicyGuard RAG. It is intended for developers who want to understand how the system works, extend it, or adapt it for other use cases.

---

## What is RAG?

RAG stands for **Retrieval-Augmented Generation**. It is a pattern for grounding large language model (LLM) responses in a specific, controlled body of knowledge rather than letting the model answer from its pretrained weights alone.

The three steps in every RAG query are:

1. **Retrieve** — search a vector database for the document chunks most semantically relevant to the question
2. **Augment** — inject those chunks as context into the LLM prompt
3. **Generate** — the LLM produces an answer using only the injected context, not its general knowledge

Without RAG, an LLM asked "what is our password policy?" would answer from training data — which knows nothing about your specific organisation's policies. With RAG, the model is forced to answer from your actual documents.

---

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│                        INGEST PIPELINE                      │
│                                                             │
│  Upload file  →  Parse (PDF/TXT)  →  Chunk  →  Embed       │
│                                              (OpenAI)       │
│                                                  ↓          │
│                                           ChromaDB upsert   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        QUERY PIPELINE                       │
│                                                             │
│  Question  →  Embed (OpenAI)  →  Similarity search         │
│                                  (ChromaDB, top-5)          │
│                                        ↓                    │
│                               Confidence check              │
│                              (score ≥ 0.25?)                │
│                           ↙                  ↘              │
│                      REFUSE                GENERATE         │
│                  (answered: false)    (GPT-4o-mini)         │
│                                            ↓                │
│                                   Cited answer +            │
│                                   source list               │
└─────────────────────────────────────────────────────────────┘
```

---

## File structure

| File | Responsibility |
|------|---------------|
| `app/main.py` | FastAPI app, HTTP endpoints, timing middleware |
| `app/ingestor.py` | Document parsing, chunking, embedding, ChromaDB write |
| `app/retriever.py` | Question embedding, vector similarity search, confidence scoring |
| `app/generator.py` | Confidence gate, prompt construction, LLM call |
| `app/models.py` | Pydantic request/response schemas |
| `scripts/test_ingest.py` | CLI helper to upload a file to `/ingest` |
| `scripts/generate_sample_pdfs.py` | Generates the two sample PDF policy files |
| `samples/` | Four sample policy documents (2 TXT, 2 PDF) |
| `docs/` | GETTING_STARTED.md and TECHNICAL.md |

---

## Ingest pipeline (`ingestor.py`)

### Parsing

Documents are parsed into a list of text chunks before embedding. The parsing strategy differs by file type:

**TXT files (`parse_txt`):**
The raw bytes are decoded as UTF-8 and split on double newlines (`\n\n`). Each resulting block that is at least 50 characters long becomes a chunk. Double newlines are a reliable paragraph boundary in plain text policy documents.

**PDF files (`parse_pdf`):**
PDFs are parsed using **PyMuPDF** (`fitz`). Rather than extracting raw text and splitting on newlines (which fails for PDFs because line endings depend on how the PDF was authored), the function uses PyMuPDF's block-level extractor (`page.get_text("blocks")`). This returns a list of text blocks as the PDF renderer detects them — each block roughly corresponds to a paragraph or section. Within each block, a secondary split on `\n\n` is attempted in case the block contains multiple paragraphs. Blocks shorter than 50 characters are discarded (they are typically headers or artefacts).

### Chunking strategy

The project uses a simple paragraph-level chunking strategy: each paragraph becomes one chunk. This is a deliberate trade-off:

- **Advantage**: paragraphs are semantically self-contained. A chunk about "password rotation" contains only that topic, so its embedding is a tight, focused vector.
- **Trade-off**: if the answer to a question spans two paragraphs, the retriever may only surface one of them. More sophisticated strategies (sliding window, sentence-level with overlap) would improve recall at the cost of more chunks and higher embedding cost.

Chunks smaller than 50 characters are filtered out because they are typically section headers, dividers, or artefacts that add noise without adding semantic value.

### Embedding

Each chunk is converted to a vector using OpenAI's `text-embedding-3-small` model. This model produces a **1536-dimensional** dense vector for each input string. The vectors are **unit-normalized** by default (length = 1), which is an important property for the similarity calculation explained later.

All chunks from a document are embedded in a single API call (batch embedding) to minimise latency and cost.

### Storage

Chunks are stored in **ChromaDB**, a local vector database that persists to disk in the `chroma_db/` folder. Each chunk is stored with:

- **ID**: `{filename}::{chunk_index}` — namespaced by filename so multiple documents coexist without ID collisions
- **Embedding**: the 1536-dimensional float vector
- **Document**: the raw text of the chunk
- **Metadata**: `{"document": filename, "chunk_index": i}`

The storage operation uses `upsert` rather than `insert`. If a document is ingested a second time, its chunks are updated in place rather than duplicated.

---

## Retrieval pipeline (`retriever.py`)

### Question embedding

When a query arrives, the question string is embedded using the same model (`text-embedding-3-small`) that was used during ingestion. Using the same model for both queries and documents is essential — the vectors only have comparable positions in the same embedding space.

### Similarity search

ChromaDB performs an approximate nearest-neighbour search over all stored vectors, returning the `top_k` (default: 5) closest chunks to the question embedding along with their **L2 distances**.

ChromaDB's default distance metric is **L2 (Euclidean distance)**. For two vectors `a` and `b`, L2 distance is:

```
dist = sqrt( sum( (a_i - b_i)^2 ) )
```

### Converting distance to confidence score

L2 distance is a dissimilarity measure — lower is better, and it ranges from 0 (identical) to 2 (opposite) for unit-normalized vectors. The system converts it to a cosine similarity score, which is an intuitive 0-to-1 (or −1-to-1) similarity measure where higher is better.

For unit-normalized vectors, the mathematical relationship between L2 distance and cosine similarity is:

```
cosine_similarity = 1 - (L2_distance² / 2)
```

This identity comes from the vector dot product definition:

```
||a - b||²  =  ||a||² + ||b||² - 2·(a·b)
            =  1 + 1 - 2·cosine_similarity      (since vectors are unit-normalized)
            =  2 - 2·cosine_similarity

∴  cosine_similarity  =  1 - (||a - b||² / 2)
                       =  1 - (dist² / 2)
```

This is the formula used in `retriever.py` line 33:

```python
"score": round(1 - (dist ** 2) / 2, 4)
```

The results are returned sorted by score descending (ChromaDB returns them sorted by distance ascending, which is equivalent).

### Why cosine similarity for this use case

Cosine similarity measures the **angle** between two vectors rather than their absolute distance. This makes it robust to differences in text length — a short question and a long paragraph chunk can still score highly if they discuss the same concept, because both vectors point in the same semantic direction even if their magnitudes differ. This property is important for policy Q&A where questions are short and chunks are paragraph-length.

---

## Confidence gate (`generator.py`)

Before calling the LLM, the system checks whether the best-matching chunk is relevant enough to answer from.

```python
best_score = chunks[0]["score"]   # highest similarity score (chunks are pre-sorted)

if best_score < CONFIDENCE_THRESHOLD:
    return QueryResponse(answered=False, reason=..., confidence=best_score, sources=[])
```

`CONFIDENCE_THRESHOLD` is set to **0.25** in `retriever.py`. This value was determined empirically:

- On-topic questions against matching documents score between **0.25 and 0.85** depending on how specifically the question matches the chunk text. A highly specific question like "how often must passwords be rotated?" directly mirrors the chunk text and scores ~0.82. A broader question like "what MFA methods are allowed?" scores ~0.30 because the chunk text is about general MFA requirements rather than a direct list of methods.
- Off-topic questions (e.g. "what is the capital of France?") return scores below **−0.61** because no stored chunk is semantically close to geography questions.

The gap between the lowest on-topic score and the highest off-topic score provides a safe margin for the threshold.

This gate is the key safety mechanism of the system. A standard RAG pipeline passes retrieved context to the LLM regardless of relevance, and the LLM fills any gaps with its pretrained knowledge. In compliance and security contexts this is dangerous — a confidently-worded but hallucinated answer about data retention periods or access control rules could cause regulatory harm. The confidence gate enforces that the system only generates answers when the evidence meets a minimum quality bar.

---

## Answer generation (`generator.py`)

If the confidence gate passes, the top-5 retrieved chunks are formatted into a context block:

```
[Source 1: sample_security_policy.txt]
All user passwords must be a minimum of 12 characters...

[Source 2: sample_data_retention_policy.txt]
Financial records must be retained for 7 years...
```

This context, along with the original question, is passed to **GPT-4o-mini** with a strict system prompt:

```
You are a security and compliance policy assistant.
Answer the user's question using ONLY the context provided below.
Do not use any external knowledge.
Always reference which document your answer comes from.
```

The model is called with `temperature=0.1` to minimise creative variation and keep answers grounded and consistent. The response includes the answer text plus the full source list (document name, excerpt, and score for each chunk).

When the query spans multiple documents, GPT-4o-mini synthesises the information from all retrieved sources and cites each one by name. This allows the system to reconcile or contrast policies across documents — for example, one document allowing SMS MFA as a fallback while another prohibits it for privileged accounts.

---

## API layer (`main.py`)

The FastAPI application exposes four endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Liveness check |
| GET | `/documents` | List all ingested document filenames |
| POST | `/ingest` | Upload and ingest a PDF or TXT file |
| POST | `/query` | Ask a question against the knowledge base |

Every request is timed by an HTTP middleware that logs the method, path, status code, and duration in milliseconds:

```
2025-05-16 10:23:11 INFO POST /query 200 1432.07ms
```

FastAPI automatically generates interactive API documentation at `/docs` (Swagger UI) and `/redoc` based on the Pydantic models and endpoint signatures.

---

## Data models (`models.py`)

```python
class QueryResponse(BaseModel):
    answered: bool          # true if confidence gate passed and LLM was called
    answer: Optional[str]   # LLM-generated answer (null if answered=false)
    reason: Optional[str]   # refusal reason with confidence score (null if answered=true)
    confidence: float       # cosine similarity of the best-matching chunk
    sources: list[SourceChunk]  # top-5 chunks with document, excerpt, and score
```

The `answered` boolean allows callers to branch on the response type without parsing strings:

```python
if response["answered"]:
    display(response["answer"])
else:
    escalate(response["reason"])
```

---

## Known limitations and potential improvements

| Area | Current behaviour | Possible improvement |
|------|------------------|----------------------|
| Chunking | Paragraph-level, no overlap | Sliding window with overlap to avoid splitting answers across chunk boundaries |
| Multi-document synthesis | Top-5 chunks regardless of source | Group by document, rank documents first, then select best chunks per document |
| PDF extraction | Block-level via PyMuPDF | Table-aware extraction for policy matrices and compliance checklists |
| Confidence threshold | Fixed at 0.25 | Make configurable via environment variable |
| Re-ingestion | Full document upsert | Detect unchanged chunks and skip re-embedding to save API cost |
| Supported formats | PDF and TXT only | Add DOCX, CSV, HTML, Markdown |
