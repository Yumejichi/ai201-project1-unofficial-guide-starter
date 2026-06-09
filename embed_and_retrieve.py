"""
embed_and_retrieve.py
=====================
Project 1: The Unofficial Guide — USC CS Course & Professor Reviews
Milestone 4: Embed chunks -> store in ChromaDB -> test retrieval

Usage:
    python embed_and_retrieve.py
"""

import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH   = Path("data/processed/chunks.jsonl")
CHROMA_DIR    = Path("data/chroma")
COLLECTION    = "usc_cs_reviews"
EMBED_MODEL   = "all-MiniLM-L6-v2"
TOP_K         = 4

TEST_QUERIES = [
    "What do students say about Saty Raghavachary's teaching style?",
    "How difficult do students think CSCI 572 is?",
    "What concerns were raised about CSCI 571?",
    "What do students say about the workload in DSCI 552?",
    "How do students compare CSCI 526 and CSCI 538?",
]

def load_chunks(path):
    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks

def build_collection(chunks, model):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    if collection.count() == 0:
        print(f"  Embedding {len(chunks)} chunks with {EMBED_MODEL}...")
        texts = [c["text"] for c in chunks]
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_list=True)
        collection.upsert(
            ids        = [str(c["chunk_id"]) for c in chunks],
            embeddings = embeddings,
            documents  = [c["text"] for c in chunks],
            metadatas  = [{"source": c["source"], "chunk_id": c["chunk_id"], "token_count": c["token_count"]} for c in chunks],
        )
        print(f"  Stored {collection.count()} chunks in ChromaDB.\n")
    else:
        print(f"  Collection already has {collection.count()} chunks — skipping re-embedding.\n")
    return collection

def retrieve(query, collection, model, k=TOP_K):
    query_embedding = model.encode(query, convert_to_list=True)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "chunk_id":    results["metadatas"][0][i]["chunk_id"],
            "source":      results["metadatas"][0][i]["source"],
            "token_count": results["metadatas"][0][i]["token_count"],
            "distance":    round(results["distances"][0][i], 4),
            "text":        results["documents"][0][i],
        })
    return hits

def main():
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(
            f"chunks.jsonl not found at {CHUNKS_PATH}\n"
            "Run ingest_chunks.py first."
        )
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print("USC CS Unofficial Guide — Embedding + Retrieval")
    print(f"{'='*60}\n")

    chunks = load_chunks(CHUNKS_PATH)
    print(f"  Loaded {len(chunks)} chunks from {CHUNKS_PATH}\n")

    print(f"  Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)
    print(f"  Model loaded.\n")

    collection = build_collection(chunks, model)

    print(f"{'='*60}")
    print(f"  Retrieval test — top {TOP_K} chunks per query")
    print(f"{'='*60}\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"  Query {i}: {query}")
        print(f"  {'─'*54}")
        hits = retrieve(query, collection, model)
        for rank, hit in enumerate(hits, 1):
            flag = "✓" if hit["distance"] < 0.5 else "⚠"
            print(f"  [{rank}] {flag} distance={hit['distance']}  source={hit['source']}  chunk_id={hit['chunk_id']}")
            preview = hit["text"][:200].replace("\n", " ")
            print(f"      {preview}...")
            print()
        print()

    print(f"{'='*60}")
    print("  Distance guide: < 0.3 excellent  |  0.3-0.5 good  |  > 0.5 weak")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
