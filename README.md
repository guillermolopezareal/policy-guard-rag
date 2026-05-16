# PolicyGuard RAG

A production-style REST API that ingests security and compliance documents and answers policy questions with grounded citations. When retrieved evidence is weak, the system refuses to answer rather than hallucinating — returning a confidence score and directing the user to consult a security expert.

Supports **PDF** and **TXT** files. Multiple documents can be ingested and queries retrieve from all of them simultaneously, citing which document each answer comes from.

---

## Architecture

```
POST /ingest  →  parse (PDF/TXT)  →  chunk  →  embed (text-embedding-3-small)  →  ChromaDB
POST /query   →  embed question   →  similarity search  →  confidence check  →  GPT-4o-mini  →  cited answer
```

- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vector store**: ChromaDB (local persistent)
- **LLM**: OpenAI `gpt-4o-mini`
- **Confidence guard**: cosine similarity threshold — refuses to answer if best chunk score is below 0.25

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and set your OpenAI API key

# 4. Start the server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs (Swagger UI): `http://localhost:8000/docs`

---

## Endpoints

### GET `/health`
```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

### GET `/documents`
Lists all documents currently in the knowledge base.
```bash
curl http://localhost:8000/documents
```
```json
{
  "documents": ["access_control_policy.pdf", "security_policy.txt"],
  "total": 2
}
```

### POST `/ingest`
Upload a PDF or TXT document. Call once per file; multiple documents coexist in the knowledge base.
```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@security_policy.pdf"
```
```json
{ "status": "ok", "filename": "security_policy.pdf", "chunks_stored": 42 }
```

### POST `/query`
Ask a question. The system searches all ingested documents and returns a grounded answer with source citations.
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How often must passwords be rotated?"}'
```

**Confident answer:**
```json
{
  "answered": true,
  "answer": "Passwords must be rotated every 90 days. (Source 1: security_policy.txt)",
  "confidence": 0.82,
  "sources": [
    {
      "document": "security_policy.txt",
      "excerpt": "All user passwords must be rotated every 90 days...",
      "score": 0.82
    }
  ]
}
```

**Refusal (weak or off-topic question):**
```json
{
  "answered": false,
  "answer": null,
  "reason": "Insufficient evidence in knowledge base. Confidence: -0.61. Please consult a security expert.",
  "confidence": -0.61,
  "sources": []
}
```

---

## Sample documents

Four sample policy documents are included for testing:

| File | Type | Content |
|------|------|---------|
| `sample_security_policy.txt` | TXT | Password policy, MFA, data classification, access control |
| `sample_data_retention_policy.txt` | TXT | Retention schedules, archival, secure disposal, legal holds |
| `sample_access_control_policy.pdf` | PDF | Least privilege, MFA requirements, access reviews, termination |
| `sample_incident_response_policy.pdf` | PDF | Severity levels, response phases, GDPR notification, evidence preservation |

To ingest all four using the included helper script:
```bash
python scripts/test_ingest.py samples/sample_security_policy.txt
python scripts/test_ingest.py samples/sample_data_retention_policy.txt
python scripts/test_ingest.py samples/sample_access_control_policy.pdf
python scripts/test_ingest.py samples/sample_incident_response_policy.pdf
```

To regenerate the PDF files:
```bash
python scripts/generate_sample_pdfs.py
```

---

## Example queries to try

```bash
# Answered from sample_security_policy.txt
{"question": "How often must passwords be rotated?"}

# Answered from sample_data_retention_policy.txt
{"question": "How long must financial records be retained?"}

# Answered from sample_access_control_policy.pdf
{"question": "What MFA methods are allowed?"}

# Answered from sample_incident_response_policy.pdf
{"question": "What must happen within 72 hours of a data breach?"}

# Cross-document answer (cites multiple sources)
{"question": "What are the requirements for third-party vendor access?"}

# Refused (off-topic, no relevant chunks)
{"question": "What is the capital of France?"}
```

---

## How the confidence guard works

Every query embeds the question and runs a cosine similarity search against all stored chunks. The best-matching chunk's score is compared against a threshold (default **0.25**).

- **Score above threshold**: the top chunks are passed as context to GPT-4o-mini, which generates a grounded answer citing the source documents.
- **Score below threshold**: the system returns `answered: false` with the raw confidence score. No LLM call is made.

This prevents the LLM from hallucinating answers using its pretrained knowledge when the retrieved context is irrelevant. In compliance contexts, a confident-sounding but wrong answer about data retention or access control rules can cause real regulatory harm. The confidence score is always returned so callers can decide how to escalate.

---

## Project structure

```
app/
├── main.py                      # FastAPI app, endpoints, timing middleware
├── ingestor.py                  # PDF/TXT parsing, chunking, embedding, ChromaDB upsert
├── retriever.py                 # Question embedding, similarity search, confidence scoring
├── generator.py                 # Confidence gate, GPT-4o-mini grounded generation
└── models.py                    # Pydantic models: IngestResponse, QueryRequest, QueryResponse
docs/
├── GETTING_STARTED.md           # Setup and usage guide
└── TECHNICAL.md                 # RAG architecture and implementation details
samples/
├── sample_security_policy.txt
├── sample_data_retention_policy.txt
├── sample_access_control_policy.pdf
└── sample_incident_response_policy.pdf
scripts/
├── test_ingest.py               # Helper script to ingest a file from the command line
└── generate_sample_pdfs.py      # Generates the two sample PDF policy files
requirements.txt
.env.example                     # OPENAI_API_KEY template
```
