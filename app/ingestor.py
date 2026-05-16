import fitz  # PyMuPDF
import chromadb
from openai import OpenAI

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("policies")


def parse_pdf(file_bytes: bytes) -> list[str]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    paragraphs = []
    for page in doc:
        for block in page.get_text("blocks"):
            text = block[4].strip()
            if not text:
                continue
            sub_chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
            for chunk in (sub_chunks or [text]):
                if len(chunk) >= 50:
                    paragraphs.append(chunk)
    return paragraphs


def parse_txt(file_bytes: bytes) -> list[str]:
    text = file_bytes.decode("utf-8", errors="replace")
    paragraphs = []
    for block in text.split("\n\n"):
        chunk = block.strip()
        if len(chunk) >= 50:
            paragraphs.append(chunk)
    return paragraphs


def _embed(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    return [item.embedding for item in response.data]


def ingest_document(filename: str, file_bytes: bytes, file_type: str) -> int:
    if file_type == "pdf":
        chunks = parse_pdf(file_bytes)
    else:
        chunks = parse_txt(file_bytes)

    if not chunks:
        return 0

    embeddings = _embed(chunks)

    ids = [f"{filename}::{i}" for i in range(len(chunks))]
    metadatas = [{"document": filename, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)
