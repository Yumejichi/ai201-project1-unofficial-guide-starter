import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_DIR   = Path("data/chroma")
COLLECTION   = "usc_cs_reviews"
EMBED_MODEL  = "all-MiniLM-L6-v2"
GROQ_MODEL   = "llama-3.3-70b-versatile"
TOP_K        = 4

SYSTEM_PROMPT = """You are a helpful assistant for USC students looking up information about CS courses and professors.

STRICT RULES:
1. Answer ONLY using the information provided in the DOCUMENTS section below.
2. Do NOT use your general training knowledge about professors, courses, or universities.
3. If the documents do not contain enough information to answer the question, respond with exactly: "I don't have enough information in my sources to answer that question."
4. Always cite which source document(s) your answer draws from, using the format: (Source: filename)
5. Do not make up, infer, or guess anything not explicitly stated in the documents.
6. If multiple documents say different things, summarize both perspectives and cite each."""

print("Loading embedding model...")
_model = SentenceTransformer(EMBED_MODEL)
_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_collection = _client.get_collection(name=COLLECTION)
_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
print(f"Ready. Vector store has {_collection.count()} chunks.\n")

def retrieve(query, k=TOP_K):
    query_embedding = _model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()
    results = _collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    hits = []
    for i in range(len(results["ids"][0])):
        hits.append({
            "text":     results["documents"][0][i],
            "source":   results["metadatas"][0][i]["source"],
            "chunk_id": results["metadatas"][0][i]["chunk_id"],
            "distance": round(results["distances"][0][i], 4),
        })
    return hits

def ask(question):
    chunks = retrieve(question)
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Document {i} — Source: {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)
    user_message = f"""DOCUMENTS:
{context}

QUESTION: {question}

Remember: answer only from the documents above. Cite sources using (Source: filename)."""

    response = _groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_message},
        ],
        temperature=0.2,
        max_tokens=1000,
    )
    answer = response.choices[0].message.content.strip()
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))
    return {"answer": answer, "sources": sources, "chunks": chunks}
