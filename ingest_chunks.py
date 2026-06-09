"""
ingest_chunks.py
================
Project 1: The Unofficial Guide — USC CS Course & Professor Reviews
Pipeline: load → clean → chunk → save

Usage:
    python ingest_chunks.py

Outputs:
    data/processed/<name>.clean.txt   — cleaned source text
    data/processed/chunks.jsonl        — one JSON record per chunk
"""

import os
import re
import json
import unicodedata
from pathlib import Path

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CHUNK_TOKENS  = 300
OVERLAP_TOKENS = 50
SAMPLE_COUNT  = 5

_BOILERPLATE_PATTERNS = [
    re.compile(r"<[^>]+>"),
    re.compile(r"https?://\S+"),
    re.compile(r"www\.\S+"),
    re.compile(r"^\s*\d+\s*(points?|upvotes?|karma|comments?)\s*$", re.I),
    re.compile(r"^\s*(share|save|hide|report|give award|crosspost)\s*$", re.I),
    re.compile(r"^\s*posted by u/\S+", re.I),
    re.compile(r"^\s*r/\w+\s*$", re.I),
    re.compile(r"^\s*(submitted|posted)\s+\d+", re.I),
    re.compile(r"^\s*(log\s?in|sign\s?up|sign\s?in|register|subscribe|unsubscribe)\s*$", re.I),
    re.compile(r"^\s*(home|about|contact|privacy|terms|faq|help|search|menu)\s*$", re.I),
    re.compile(r"^\s*(next|previous|back|continue|read more|load more|show more)\s*$", re.I),
    re.compile(r"^\s*page \d+ of \d+\s*$", re.I),
    re.compile(r"(accept all cookies|cookie policy|we use cookies|gdpr|privacy settings)", re.I),
    re.compile(r"(this site uses cookies|by continuing to browse)", re.I),
    re.compile(r"^\s*(all rights reserved|copyright ©?|\d{4} \w+, inc\.?)\s*$", re.I),
    re.compile(r"^\s*advertisement\s*$", re.I),
    re.compile(r"^\s*sponsored\s*$", re.I),
    re.compile(r"^\s*(add a professor|add a course|compare professors|write a review)\s*$", re.I),
    re.compile(r"^\s*(helpful\?|not helpful|was this review helpful)\s*$", re.I),
    re.compile(r"^\s*(flag|flagged|report this)\s*$", re.I),
    re.compile(r"^\s*(quality|difficulty|would take again|grade received)\s*$", re.I),
    re.compile(r"^\s*(for credit|attendance mandatory|textbook used)\s*$", re.I),
    re.compile(r"^\s*\d+\s*/\s*5\s*$"),
    re.compile(r"^\s*(awesome|amazing|ok|good|bad|terrible|excellent)\s*$", re.I),
    re.compile(r"^\s*(viterbi|trojans?|fight on|usc\.edu)\s*$", re.I),
    re.compile(r"^\s*[\W_]+\s*$"),
]

def _line_is_boilerplate(line):
    stripped = line.strip()
    if not stripped:
        return True
    if len(stripped) < 4:
        return True
    for pattern in _BOILERPLATE_PATTERNS:
        if pattern.search(stripped):
            return True
    return False

def clean_text(raw):
    text = unicodedata.normalize("NFKD", raw)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"&#?\w+;", " ", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    cleaned_lines = []
    seen = set()
    for line in lines:
        line = re.sub(r"[ \t]+", " ", line).strip()
        if _line_is_boilerplate(line):
            continue
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned_lines.append(line)
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()

def tokenise(text):
    return text.split()

def tokens_to_text(tokens):
    return " ".join(tokens)

def chunk_tokens(tokens, chunk_size, overlap):
    if not tokens:
        return []
    chunks = []
    step = chunk_size - overlap
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk = tokens[start:end]
        if chunk:
            chunks.append(chunk)
        if end == len(tokens):
            break
        start += step
    return chunks

def process_file(txt_path, chunk_id_start):
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_text(raw)
    tokens = tokenise(cleaned)
    token_groups = chunk_tokens(tokens, CHUNK_TOKENS, OVERLAP_TOKENS)
    records = []
    for i, toks in enumerate(token_groups):
        text = tokens_to_text(toks)
        if not text.strip():
            continue
        records.append({
            "chunk_id":    chunk_id_start + i,
            "source":      txt_path.name,
            "token_count": len(toks),
            "text":        text,
        })
    return records, cleaned

def main():
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DIR.resolve()}\n"
            "Make sure data/raw/ exists and contains your .txt files."
        )
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    txt_files = sorted(RAW_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {RAW_DIR.resolve()}")

    all_chunks = []
    chunk_id_counter = 0

    print(f"\n{'='*60}")
    print("USC CS Unofficial Guide — Ingestion Pipeline")
    print(f"{'='*60}")
    print(f"Source directory : {RAW_DIR.resolve()}")
    print(f"Output directory : {PROCESSED_DIR.resolve()}")
    print(f"Files found      : {len(txt_files)}")
    print(f"Chunk size       : {CHUNK_TOKENS} tokens")
    print(f"Overlap          : {OVERLAP_TOKENS} tokens")
    print(f"{'='*60}\n")

    for txt_path in txt_files:
        records, cleaned = process_file(txt_path, chunk_id_counter)
        clean_path = PROCESSED_DIR / (txt_path.stem + ".clean.txt")
        clean_path.write_text(cleaned, encoding="utf-8")
        chunk_id_counter += len(records)
        all_chunks.extend(records)
        print(f"  + {txt_path.name:40s}  ->  {len(records):4d} chunks  (cleaned: {len(cleaned):,} chars)")

    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as fh:
        for record in all_chunks:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print("Pipeline complete")
    print(f"{'='*60}")
    print(f"  Total documents processed : {len(txt_files)}")
    print(f"  Total chunks created      : {len(all_chunks)}")
    print(f"  Chunks saved to           : {chunks_path}")
    print(f"{'='*60}\n")

    import random
    sample_indices = random.sample(range(len(all_chunks)), min(SAMPLE_COUNT, len(all_chunks)))
    sample_indices.sort()

    print(f"{'─'*60}")
    print(f"  {SAMPLE_COUNT} sample chunks")
    print(f"{'─'*60}\n")

    for idx in sample_indices:
        c = all_chunks[idx]
        print(f"  [chunk_id={c['chunk_id']}]  source={c['source']}  tokens={c['token_count']}")
        print(f"  {c['text'][:300]}{'...' if len(c['text']) > 300 else ''}")
        print()

    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
