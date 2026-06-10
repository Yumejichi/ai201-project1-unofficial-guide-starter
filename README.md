# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
This system covers USC Computer Science course and professor reviews. It makes student experiences with USC CS courses and professors searchable and answerable. The system focuses on information such as teaching style, workload, exam difficulty, grading practices, and course expectations gathered from student reviews and Reddit discussions.
This knowledge is valuable because it reflects the real day-to-day experience of taking a course, something official university channels never capture. Course catalogs describe what a class covers but say nothing about whether the professor is good or not, whether the exams are fair, or whether the workload is manageable for students might working. Students have historically had to rely on word of mouth or scattered Reddit threads to find this information. This system makes it directly searchable.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->


| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Saty Raghavachary — Rate My Professors | RMP reviews | https://www.ratemyprofessors.com/professor/798241 |
| 2 | How is CSCI 572 with Prof. Saty? | Reddit thread (r/USC) | https://www.reddit.com/r/USC/comments/15ud6gx |
| 3 | How CSCI-585 is? | Reddit thread (r/USC) | https://www.reddit.com/r/USC/comments/11jscpe |
| 4 | Professor ID 1104782 — Rate My Professors | RMP reviews | https://www.ratemyprofessors.com/professor/1104782 |
| 5 | The CSCI 571 Misrepresentation Scandal | Reddit thread (r/USC) | https://www.reddit.com/r/USC/comments/15eqr36 |
| 6 | Professor ID 3125237 — Rate My Professors | RMP reviews | https://www.ratemyprofessors.com/professor/3125237 |
| 7 | Professor ID 2294843 — Rate My Professors | RMP reviews | https://www.ratemyprofessors.com/professor/2294843 |
| 8 | Any thoughts on DSCI 552? | Reddit thread (r/USC) | https://www.reddit.com/r/USC/comments/1co1472 |
| 9 | Professor ID 1307919 — Rate My Professors | RMP reviews | https://www.ratemyprofessors.com/professor/1307919 |
| 10 | Anyone taken CSCI 526 or CSCI 538? | Reddit thread (r/USC) | https://www.reddit.com/r/USC/comments/a7ued1 |
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 300 tokens

**Overlap:** 50 tokens

**Why these choices fit your documents:**
The document collection mixes short Rate My Professors reviews (often 2–5 sentences) and some long Reddit threads (multiple paragraphs of discussion). A 300-token chunk is large enough to preserve a complete student opinion — including the professor name, course context, and the actual judgment, while still being small enough to match a specific query precisely. Chunks that are too large would blend multiple opinions about different topics into one embedding, making retrieval imprecise. Chunks that are too small (e.g. 50 tokens) would split individual reviews mid-sentence, losing the context needed to understand the opinion.

The 50-token overlap ensures that a key phrase near the end of one chunk (such as a professor's name or a course number) also appears at the start of the next chunk. This prevents important information from being invisible to retrieval just because it happened to fall at a chunk boundary.

Before chunking, the pipeline cleans each document by removing HTML tags, Reddit navigation chrome (Skip to main content, Open menu, upvote counts), RateMyProfessors UI labels (Logo Professors, Rate Compare, Overall Quality), cookie banners, duplicate lines, and any line under 4 characters. This ensures chunks contain only substantive review text.

**Final chunk count:** 68 chunks across 10 source documents

**Sample chunks:**

1. `csci571.txt` (chunk_id=4, 300 tokens): *"concepts used in the homework assignments. Massive assignments. The workload of this course is too much, especially the last two assignments. Students in later semesters were hoping for those concerns to be resolved as quickly as possible. Professor Papa said no..."*

2. `saty_rmp.txt` (chunk_id=62, 300 tokens): *"passionate about DS and genuinely cares about his students. The 4 HWs were easy but the midterm was hard. He took this feedback and made the final easier. He takes random roll call each class..."*

3. `prof_1104782_rmp.txt` (chunk_id=29, 300 tokens): *"Papa admits to reading this page, I suspect most of the good reviews are by him. Be warned: you pay 9,000 to do a project by yourself. You might as well Google old projects..."*

4. `csci526_538.txt` (chunk_id=0, 300 tokens): *"Anyone taken CSCI 526 or CSCI 538? How are these courses like? Is there excessive coding? How is the grading curve?..."*

5. `dsci552.txt` (chunk_id=21, 300 tokens): *"Any thoughts on the DSCI 552? How hard is it to get an A? The midterms are math heavy, but its simple math. Homework is tedious but doable..."*
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
all-MiniLM-L6-v2 via sentence-transformers, running locally with no API key or rate limits. Embeddings are L2-normalized using normalize_embeddings=True and stored in ChromaDB with cosine similarity (hnsw:space: cosine).

**Production tradeoff reflection:**
I chose all-MiniLM-L6-v2 because it is free, runs entirely locally, and is well-suited for short-to-medium semantic similarity tasks like student reviews. For a production deployment, I would consider several tradeoffs. A larger model like text-embedding-3-large from OpenAI or voyage-large-2 would likely produce higher quality embeddings for domain-specific text, especially for informal student language and course-specific terminology — but both require API calls, adding latency and cost per query. I would also weigh context length: all-MiniLM-L6-v2 has a 256-token limit, which means longer chunks are silently truncated; a model with a longer context window (e.g. text-embedding-ada-002 at 8192 tokens) would handle full reviews without truncation. Multilingual support is not needed here since all sources are in English, but would matter if the system were extended to serve international students posting in other languages. For this project, the local, free model was the right tradeoff given the small corpus and academic context.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

The system prompt in `query.py` uses explicit prohibitions rather than suggestions:

```
You are a helpful assistant for USC students looking up information about CS courses and professors.

STRICT RULES:
1. Answer ONLY using the information provided in the DOCUMENTS section below.
2. Do NOT use your general training knowledge about professors, courses, or universities.
3. If the documents do not contain enough information to answer the question, respond with exactly:
   "I don't have enough information in my sources to answer that question."
4. Always cite which source document(s) your answer draws from, using the format: (Source: filename)
5. Do not make up, infer, or guess anything not explicitly stated in the documents.
6. If multiple documents say different things, summarize both perspectives and cite each.
```

The user message passes retrieved chunks labeled by source:

```
[Document 1 — Source: saty_rmp.txt]
<chunk text>

[Document 2 — Source: csci585.txt]
<chunk text>

QUESTION: What do students say about Saty's teaching style?

Remember: answer only from the documents above. Cite sources using (Source: filename).
```

Temperature is set to 0.2 to reduce creative generation and keep the model close to the retrieved text.

**How source attribution is surfaced in the response:**

Source attribution is guaranteed in two ways. First, the system prompt instructs the model to cite sources inline using `(Source: filename)`. Second, source filenames are collected programmatically in Python from the retrieved chunks, independent of what the LLM produces:

```python
sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))
```

This means the Sources box in the Gradio UI is always populated from the actual retrieved documents, even if the LLM fails to cite them in its answer text.

Out-of-scope refusal test — Query: "What is the best restaurant near USC?" — Response: "I don't have enough information in my sources to answer that question." The system correctly declined rather than hallucinating an answer.
---

## Evaluation Report
<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about Saty Raghavachary's teaching style? | Students describe Saty's teaching style, communication, and classroom effectiveness based on collected reviews | Described mixed opinions: some find him passionate and engaging, others find him disorganized and rambling. Cited saty_rmp.txt and csci585.txt inline. | Relevant | Accurate |
| 2 | How difficult do students think CSCI 572 is? | Students discuss workload, project difficulty, and overall challenge level of CSCI 572 | Returned one quote describing Saty's courses as "more like 100-level than 500-level." Retrieved csci572_saty.txt but also pulled csci571.txt and csci585.txt which are off-topic. | Partially relevant | Partially accurate |
| 3 | What concerns were raised about CSCI 571? | Summary of issues discussed in the CSCI 571 Reddit thread | Accurately summarized the misrepresentation scandal, prerequisite issue, student complaints, and professor dismissiveness. All citations from csci571.txt. | Relevant | Accurate |
| 4 | What do students say about the workload in DSCI 552? | Students describe workload, assignments, and time commitment for DSCI 552 | Correctly described homework as tedious but doable, midterms as math-heavy but simple. Top retrieved result was prof_1104782_rmp.txt (wrong source), dsci552.txt appeared at rank 2. | Partially relevant | Partially accurate |
| 5 | How do students compare CSCI 526 and CSCI 538? | Students compare difficulty, workload, and recommendations for CSCI 526 vs CSCI 538 | Correctly stated there is no direct student comparison in the documents. Named the courses correctly. Did not hallucinate a comparison. | Partially relevant | Partially accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
"How do students compare CSCI 526 and CSCI 538?"

**What the system returned:**
The system correctly said there is no direct comparison in the documents. However, the retrieval returned chunks from csci585.txt, csci572_saty.txt, and csci571.txt alongside csci526_538.txt — none of which contain comparison content. The top result for csci526_538.txt had a distance of 0.37, but the source file itself only produced 2 chunks because the Reddit thread had very few comments.

**Root cause (tied to a specific pipeline stage):**
The failure originates in the document collection stage, not the retrieval or generation stage. The Reddit thread for CSCI 526 and CSCI 538 had only 2 comments, producing only 2 chunks total. There was simply not enough source material for the system to answer the question. When the vector store has limited signal from a source, the embedding model fills the remaining top-k slots with loosely related chunks from other CS course threads. The generation model then correctly identified that none of the retrieved content contained a comparison, but the underlying answer is incomplete because the source was too sparse to begin with.

**What you would change to fix it:**
Collect more source documents specifically about CSCI 526 and CSCI 538 — additional Reddit threads, RateMyProfessors reviews for the professors who teach those courses, or department course evaluation data. More chunks from the right sources would give the embedding model enough signal to return relevant results and give the LLM enough context to produce a substantive answer.
---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Writing the chunking strategy in planning.md before touching any code forced a concrete decision about chunk size and overlap before seeing any output. When the first pipeline run produced chunks with Reddit navigation boilerplate still present, having the spec as a reference made it clear that the cleaning stage had not met its own requirements — the spec explicitly said "remove navigation text." This made debugging much more focused: the question was not "is something wrong?" but "why is the cleaning not matching the spec?" The spec acted as a checklist that surfaced the problem quickly rather than requiring a general inspection of the output.

**One way your implementation diverged from the spec, and why:**
The spec planned for a single cleaning pass before chunking. In practice, cleaning required three iterative passes — each time running the pipeline, inspecting sample chunks, identifying new boilerplate patterns (Reddit sidebar links, RateMyProfessors UI labels like "Logo Professors" and "Caret Down", ad text from Shopify), and adding new regex patterns to the cleaner. The spec assumed the document structure was predictable enough to handle in one pass, but copy-pasted web content turned out to be messier than expected. The final cleaner has roughly 40 boilerplate patterns compared to the approximately 20 originally planned, and the chunk count dropped from 76 to 68 across the three cleaning passes as more noise was removed.
---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My full planning.md spec including the Documents section, Chunking Strategy section (300 tokens, 50 overlap), and the Mermaid architecture diagram showing the five pipeline stages.
- *What it produced:* A complete `ingest_chunks.py` script with a cleaning function, a sliding window chunker, and output to both `.clean.txt` files and `chunks.jsonl`. The initial cleaning patterns covered HTML, Reddit vote counts, and basic nav text.
- *What I changed or overrode:* After running the script and inspecting sample chunks, I directed the AI to add three additional rounds of boilerplate patterns targeting Reddit sidebar links, RateMyProfessors UI labels, and ad text that had slipped through the initial cleaning. I also directed it to apply fixes in-place using Python patch commands rather than regenerating the whole file each time.

**Instance 2**

- *What I gave the AI:* The Retrieval Approach section from planning.md (all-MiniLM-L6-v2, top-k=4, ChromaDB), the pipeline diagram, and the requirement that grounding must be enforced via system prompt with programmatic source attribution guaranteed in Python, not left to the LLM.
- *What it produced:* `query.py` with a retrieve function, a grounded generation function using Groq llama-3.3-70b-versatile, and `app.py` with a Gradio interface. The initial retrieve function used `_model.encode(query, convert_to_list=True)` without normalization.
- *What I changed or overrode:* I directed the AI to fix the embedding call to use `_model.encode([query], normalize_embeddings=True).tolist()` — the correct SentenceTransformer batch pattern with L2 normalization — because the original pattern did not normalize embeddings, which weakens cosine similarity scores in ChromaDB. I verified that source attribution was collected programmatically in Python and not dependent on the LLM citing sources in its own response text.
