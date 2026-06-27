import chromadb
from openai import OpenAI

CONFIDENCE_THRESHOLD = 0.25

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection("policies")


def retrieve(question: str, top_k: int = 5) -> list[dict]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question],
    )
    question_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(documents, metadatas, distances):
        chunks.append({
            "document": meta["document"],
            "excerpt": doc,
            "score": round(1 - (dist ** 2) / 2, 4),
        })

    return chunks


def retrieve_with_trace(question: str, top_k: int = 5) -> tuple[list[dict], int]:
    total = collection.count()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question],
    )
    question_embedding = response.data[0].embedding

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        cosine_similarity = round(1 - (dist ** 2) / 2, 4)
        chunks.append({
            "rank": rank,
            "document": meta["document"],
            "excerpt": doc,
            "chunk_index": meta.get("chunk_index", 0),
            "l2_distance": round(dist, 4),
            "cosine_similarity": cosine_similarity,
            "score": cosine_similarity,
        })

    return chunks, total
