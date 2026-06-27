import time
import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import chromadb

from .models import IngestResponse, QueryRequest, QueryResponse, TraceResponse
from .ingestor import ingest_document
from .retriever import retrieve, retrieve_with_trace
from .generator import generate_answer, generate_answer_with_trace

chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("policies")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="PolicyGuard RAG", version="1.0.0")


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/documents")
async def list_documents():
    results = collection.get(include=["metadatas"])
    docs = {m["document"] for m in results["metadatas"] if m}
    return {"documents": sorted(docs), "total": len(docs)}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    try:
        filename = file.filename or "unknown"
        content_type = file.content_type or ""
        file_bytes = await file.read()

        if filename.lower().endswith(".pdf") or "pdf" in content_type:
            file_type = "pdf"
        else:
            file_type = "txt"

        chunks_stored = ingest_document(filename, file_bytes, file_type)
        return IngestResponse(status="ok", filename=filename, chunks_stored=chunks_stored)
    except Exception as e:
        logger.exception("Ingest failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(body: QueryRequest):
    try:
        chunks = retrieve(body.question, top_k=body.top_k)
        result = generate_answer(body.question, chunks, confidence_threshold=body.confidence_threshold)
        return result
    except Exception as e:
        logger.exception("Query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/trace", response_model=TraceResponse)
async def query_trace(body: QueryRequest):
    try:
        chunks, total = retrieve_with_trace(body.question, top_k=body.top_k)
        return generate_answer_with_trace(
            body.question, chunks, total,
            top_k=body.top_k,
            confidence_threshold=body.confidence_threshold,
        )
    except Exception as e:
        logger.exception("Trace query failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/viz", StaticFiles(directory="app/static", html=True), name="viz")
