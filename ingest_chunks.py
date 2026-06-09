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

# ── Configuration ──────────────────────────────────────────────────────────────

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
CHUNK_TOKENS  = 300   # target chunk size (in whitespace-split tokens)
OVERLAP_TOKENS = 50   # overlap between consecutive chunks
SAMPLE_COUNT  = 5     # how many sample chunks to print at the end

# ── Text cleaning ──────────────────────────────────────────────────────────────

# Patterns that strongly signal boilerplate / non-content lines
_BOILERPLATE_PATTERNS = [
    # HTML tags (residual after basic strip)
    re.compile(r"<[^>]+>"),
    # URLs
    re.compile(r"https?://\S+"),
    re.compile(r"www\.\S+"),
    # Reddit vote/karma noise
    re.compile(r"^\s*\d+\s*(points?|upvotes?|karma|comments?)\s*$", re.I),
    re.compile(r"^\s*(share|save|hide|report|give award|crosspost)\s*$", re.I),
    re.compile(r"^\s*posted by u/\S+", re.I),
    re.compile(r"^\s*r/\w+\s*$", re.I),
    re.compile(r"^\s*(submitted|posted)\s+\d+", re.I),
    # Navigation / UI chrome
    re.compile(r"^\s*(log\s?in|sign\s?up|sign\s?in|register|subscribe|unsubscribe)\s*$", re.I),
    re.compile(r"^\s*(home|about|contact|privacy|terms|faq|help|search|menu)\s*$", re.I),
    re.compile(r"^\s*(next|previous|back|continue|read more|load more|show more)\s*$", re.I),
    re.compile(r"^\s*page \d+ of \d+\s*$", re.I),
    # Cookie / GDPR banners
    re.compile(r"(accept all cookies|cookie policy|we use cookies|gdpr|privacy settings)", re.I),
    re.compile(r"(this site uses cookies|by continuing to browse)", re.I),
    # Generic web headers/footers
    re.compile(r"^\s*(all rights reserved|copyright ©?|\d{4} \w+, inc\.?)\s*$", re.I),
    re.compile(r"^\s*advertisement\s*$", re.I),
    re.compile(r"^\s*sponsored\s*$", re.I),
    # RateMyProfessors / Coursicle / similar site chrome
    re.compile(r"^\s*(add a professor|add a course|compare professors|write a review)\s*$", re.I),
    re.compile(r"^\s*(helpful\?|not helpful|was this review helpful)\s*$", re.I),
    re.compile(r"^\s*(flag|flagged|report this)\s*$", re.I),
    re.compile(r"^\s*(quality|difficulty|would take again|grade received)\s*$", re.I),
    re.compile(r"^\s*(for credit|attendance mandatory|textbook used)\s*$", re.I),
    re.compile(r"^\s*\d+\s*/\s*5\s*$"),          # bare rating lines like "4 / 5"
    re.compile(r"^\s*(awesome|amazing|ok|good|bad|terrible|excellent)\s*$", re.I),  # single-word ratings
    # USC-specific nav noise
    re.compile(r"^\s*(viterbi|trojans?|fight on|usc\.edu)\s*$", re.I),
    # Reddit UI chrome (catches "Skip to main content", "Open menu", "Expand user menu", etc.)
    re.compile(r"skip to main content", re.I),
    re.compile(r"open menu", re.I),
    re.compile(r"expand user menu", re.I),
    re.compile(r"find anything", re.I),
    re.compile(r"go to \w+\s*$", re.I),
    re.compile(r"^\s*r/USC\s*$", re.I),
    re.compile(r"^\s*u/\w+\s*$", re.I),
    re.compile(r"^\s*\d+\s*ago\s*$", re.I),
    re.compile(r"^\s*(new|hot|top|rising|controversial)\s*$", re.I),
    re.compile(r"sort by", re.I),
    re.compile(r"view all comments", re.I),
    re.compile(r"^\s*add a comment\s*$", re.I),
    re.compile(r"^\s*reply\s*$", re.I),
    re.compile(r"^\s*more replies\s*$", re.I),
    re.compile(r"^\s*level \d+\s*$", re.I),
    re.compile(r"^\s*continue this thread\s*$", re.I),
    # RateMyProfessors UI chrome
    re.compile(r"logo professors", re.I),
    re.compile(r"caret down", re.I),
    re.compile(r"pencil icon", re.I),
    re.compile(r"rate compare", re.I),
    re.compile(r"jump to ratings", re.I),
    re.compile(r"down arrow", re.I),
    re.compile(r"overall quality", re.I),
    re.compile(r"based on \d+ ratings", re.I),
    re.compile(r"^\s*would take again\s*$", re.I),
    re.compile(r"^\s*level of difficulty\s*$", re.I),
    re.compile(r"^\s*professor in the .+ department\s*$", re.I),
    re.compile(r"university of southern california", re.I),
    re.compile(r"^\s*computer science\s*$", re.I),
    re.compile(r"^\s*check out similar professors\s*$", re.I),
    re.compile(r"^\s*top tags\s*$", re.I),
    re.compile(r"^\s*(caring|respected|inspirational|hilarious|amazing lectures)\s*$", re.I),
    # Whitespace-only / punctuation-only lines
    re.compile(r"^\s*[\W_]+\s*$"),
    # Reddit sidebar / recommendation noise
    re.compile(r"\d+\s*(upvotes?|comments?|mo ago|yr ago|d ago|h ago)", re.I),
    re.compile(r"^.*(upvotes?|upvoted).*(comments?).*$", re.I),
    re.compile(r"shopify|reach shoppers|thumbnail image", re.I),
    re.compile(r"avatar\s+\w+", re.I),
    re.compile(r"r/\w+ -", re.I),
    re.compile(r"warning: avoid", re.I),
    re.compile(r"^\s*SPOIL", re.I),
    re.compile(r"URGENT:", re.I),
    re.compile(r"pls i need an easy", re.I),
]

def _line_is_boilerplate(line: str) -> bool:
    """Return True if the line is noise that should be dropped."""
    stripped = line.strip()
    if not stripped:
        return True
    # Very short lines that aren't meaningful (< 4 chars)
    if len(stripped) < 4:
        return True
    for pattern in _BOILERPLATE_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def clean_text(raw: str) -> str:
    """
    Clean raw scraped text:
    1. Normalise unicode to ASCII-safe form
    2. Strip HTML tags
    3. Collapse whitespace
    4. Drop boilerplate lines
    5. Deduplicate repeated consecutive lines
    6. Collapse blank lines to single paragraph breaks
    """
    # 1. Unicode normalisation (handles smart quotes, em-dashes, etc.)
    text = unicodedata.normalize("NFKD", raw)
    text = text.encode("ascii", "ignore").decode("ascii")

    # 2. Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove HTML entities (e.g. &amp; &nbsp;)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"&#?\w+;", " ", text)

    # 3. Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 4. Process line-by-line
    lines = text.split("\n")
    cleaned_lines = []
    seen = set()  # for deduplication

    for line in lines:
        # Collapse internal whitespace within the line
        line = re.sub(r"[ \t]+", " ", line).strip()

        if _line_is_boilerplate(line):
            continue

        # Deduplicate repeated lines (case-insensitive, stripped)
        key = line.lower()
        if key in seen:
            continue
        seen.add(key)

        cleaned_lines.append(line)

    # 5. Re-join, collapsing runs of blank lines to a single blank
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    return result.strip()


# ── Tokenisation (whitespace-based) ───────────────────────────────────────────

def tokenise(text: str) -> list[str]:
    """
    Split text into tokens using simple whitespace splitting.
    This approximates GPT-style token counts well enough for
    300-token chunk targets without requiring tiktoken.
    """
    return text.split()


def tokens_to_text(tokens: list[str]) -> str:
    return " ".join(tokens)


# ── Chunking ───────────────────────────────────────────────────────────────────

def chunk_tokens(tokens: list[str], chunk_size: int, overlap: int) -> list[list[str]]:
    """
    Slide a window of `chunk_size` tokens over `tokens` with `overlap` step-back.
    Returns a list of token lists.
    """
    if not tokens:
        return []

    chunks = []
    step = chunk_size - overlap  # how far we advance each iteration
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


# ── Main pipeline ──────────────────────────────────────────────────────────────

def process_file(txt_path: Path, chunk_id_start: int) -> tuple[list[dict], str]:
    """
    Load, clean, and chunk one .txt file.

    Returns:
        (list_of_chunk_records, cleaned_text)
    """
    raw = txt_path.read_text(encoding="utf-8", errors="replace")
    cleaned = clean_text(raw)

    tokens = tokenise(cleaned)
    token_groups = chunk_tokens(tokens, CHUNK_TOKENS, OVERLAP_TOKENS)

    records = []
    for i, toks in enumerate(token_groups):
        text = tokens_to_text(toks)
        # Final safety filter: skip chunks that are effectively empty
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
    # Validate directories
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Raw data directory not found: {RAW_DIR.resolve()}\n"
            "Make sure you run this script from the project root and "
            "that data/raw/ contains your .txt files."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(RAW_DIR.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No .txt files found in {RAW_DIR.resolve()}")

    all_chunks: list[dict] = []
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

        # Save cleaned text
        clean_path = PROCESSED_DIR / (txt_path.stem + ".clean.txt")
        clean_path.write_text(cleaned, encoding="utf-8")

        chunk_id_counter += len(records)
        all_chunks.extend(records)

        print(f"  ✓ {txt_path.name:40s}  →  {len(records):4d} chunks  "
              f"(cleaned: {len(cleaned):,} chars)")

    # Save chunks.jsonl
    chunks_path = PROCESSED_DIR / "chunks.jsonl"
    with chunks_path.open("w", encoding="utf-8") as fh:
        for record in all_chunks:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    # ── Summary ────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("Pipeline complete")
    print(f"{'='*60}")
    print(f"  Total documents processed : {len(txt_files)}")
    print(f"  Total chunks created      : {len(all_chunks)}")
    print(f"  Chunks saved to           : {chunks_path}")
    print(f"{'='*60}\n")

    # ── Sample chunks ──────────────────────────────────────────────────────────
    import random
    sample_indices = random.sample(range(len(all_chunks)), min(SAMPLE_COUNT, len(all_chunks)))
    sample_indices.sort()

    print(f"{'─'*60}")
    print(f"  {SAMPLE_COUNT} sample chunks (randomly selected)")
    print(f"{'─'*60}\n")

    for idx in sample_indices:
        c = all_chunks[idx]
        print(f"  [chunk_id={c['chunk_id']}]  source={c['source']}  tokens={c['token_count']}")
        print(f"  {c['text'][:300]}{'...' if len(c['text']) > 300 else ''}")
        print()

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
