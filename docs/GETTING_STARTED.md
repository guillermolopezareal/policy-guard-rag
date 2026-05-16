# Getting Started — PolicyGuard RAG

This guide walks you through setting up and running PolicyGuard RAG from scratch on your local machine.

---

## Prerequisites

- Python 3.10 or higher
- An OpenAI API key (get one at platform.openai.com)
- Git

---

## 1. Clone the repository

```bash
git clone https://github.com/guillermolopezareal/policy-guard-rag.git
cd policy-guard-rag
```

---

## 2. Create a virtual environment

A virtual environment keeps the project's dependencies isolated from your system Python.

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

This installs FastAPI, ChromaDB, OpenAI SDK, PyMuPDF, and the other libraries the project needs.

---

## 4. Configure your API key

Copy the environment template and fill in your key:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your key:

```
OPENAI_API_KEY=sk-...your-key-here...
```

The `.env` file is listed in `.gitignore` so it will never be committed to version control.

---

## 5. Start the server

```bash
uvicorn app.main:app --reload
```

The `--reload` flag automatically restarts the server when you edit a Python file.

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

---

## 6. Verify the server is running

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

Or open **http://localhost:8000/docs** in your browser for the interactive Swagger UI.

---

## 7. Ingest documents

The system starts with an empty knowledge base. You need to upload documents before querying.

**Option A — using the helper script (recommended):**

```bash
python scripts/test_ingest.py samples/sample_security_policy.txt
python scripts/test_ingest.py samples/sample_data_retention_policy.txt
python scripts/test_ingest.py samples/sample_access_control_policy.pdf
python scripts/test_ingest.py samples/sample_incident_response_policy.pdf
```

Each command prints how many chunks were stored:

```
{'status': 'ok', 'filename': 'sample_security_policy.txt', 'chunks_stored': 33}
```

**Option B — using curl:**

```bash
curl -X POST http://localhost:8000/ingest \
  -F "file=@samples/sample_security_policy.txt"
```

**Option C — using the Swagger UI:**

1. Open http://localhost:8000/docs
2. Click **POST /ingest** → **Try it out**
3. Click **Choose File**, select your document
4. Click **Execute**

---

## 8. Check what is in the knowledge base

```bash
curl http://localhost:8000/documents
```

```json
{
  "documents": [
    "sample_access_control_policy.pdf",
    "sample_data_retention_policy.txt",
    "sample_incident_response_policy.pdf",
    "sample_security_policy.txt"
  ],
  "total": 4
}
```

---

## 9. Query the knowledge base

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How often must passwords be rotated?"}'
```

A successful response looks like:

```json
{
  "answered": true,
  "answer": "Passwords must be rotated every 90 days. (Source 1: sample_security_policy.txt)",
  "confidence": 0.82,
  "sources": [
    {
      "document": "sample_security_policy.txt",
      "excerpt": "All user passwords must be rotated every 90 days...",
      "score": 0.82
    }
  ]
}
```

When no relevant content is found, the system refuses to answer:

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

## 10. Sample queries to try

Try these questions to exercise all four sample documents:

| Question | Expected source |
|----------|----------------|
| `How often must passwords be rotated?` | sample_security_policy.txt |
| `How long must financial records be retained?` | sample_data_retention_policy.txt |
| `What MFA methods are allowed?` | Both policy files |
| `What must happen within 72 hours of a data breach?` | sample_incident_response_policy.pdf |
| `How long must employee records be kept after termination?` | sample_data_retention_policy.txt |
| `What are the requirements for third-party vendor access?` | Both policy files |
| `What is the capital of France?` | Refused (off-topic) |

---

## Ingesting your own documents

You can ingest any PDF or TXT file you own:

```bash
python scripts/test_ingest.py your_policy.pdf
```

Or via the Swagger UI at http://localhost:8000/docs. Re-ingesting the same filename updates its chunks in place (upsert).

---

## Stopping the server

Press `CTRL + C` in the terminal where uvicorn is running.

The ChromaDB vector store is persisted to the `chroma_db/` folder, so your ingested documents survive restarts. You do not need to re-ingest every time you start the server.
