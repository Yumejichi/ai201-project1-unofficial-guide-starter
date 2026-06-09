# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
USC CS Course and Professor Reviews
This project makes student experiences with USC computer science courses and professors searchable. The system focuses on information such as teaching style, workload, exam difficulty, grading practices, and course expectations gathered from student reviews and discussions. This knowledge is difficult to find through official university channels because course catalogs and department websites describe course content but rarely capture the day-to-day experiences and opinions shared by students.


---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Saty Raghavachary (RMP) | Student reviews discussing teaching style, workload, exams, and overall course experience. | https://www.ratemyprofessors.com/professor/798241 |
| 2 | USC Reddit - CSCI 572 with Saty | Student discussion about taking CSCI 572 with Professor Saty Raghavachary. | https://www.reddit.com/r/USC/comments/15ud6gx/how_is_csci_572_with_prof_saty/ |
| 3 | USC Reddit - CSCI 585 | Student discussion about workload, projects, and difficulty of CSCI 585. | https://www.reddit.com/r/USC/comments/11jscpe/how_csci585_is/ |
| 4 | Professor Reviews (RMP) | Student reviews for professor ID 1104782 covering grading, teaching quality, and course expectations. | https://www.ratemyprofessors.com/professor/1104782 |
| 5 | USC Reddit - CSCI 571 Discussion | Student discussion regarding experiences and concerns related to CSCI 571. | https://www.reddit.com/r/USC/comments/15eqr36/the_csci_571_misrepresentation_scandal/ |
| 6 | Professor Reviews (RMP) | Student reviews for professor ID 3125237 discussing course structure and instructor effectiveness. | https://www.ratemyprofessors.com/professor/3125237 |
| 7 | Professor Reviews (RMP) | Student reviews for professor ID 2294843 discussing workload, grading, and teaching style. | https://www.ratemyprofessors.com/professor/2294843 |
| 8 | USC Reddit - DSCI 552 | Student discussion about DSCI 552 workload, difficulty, and grading policies. | https://www.reddit.com/r/USC/comments/1co1472/any_thoughts_on_the_dsci_552_how_hard_is_it_to/ |
| 9 | Professor Reviews (RMP) | Student reviews for professor ID 1307919 discussing classroom experience and course expectations. | https://www.ratemyprofessors.com/professor/1307919 |
| 10 | USC Reddit - CSCI 526 / CSCI 538 | Student discussion comparing experiences in CSCI 526 and CSCI 538. | https://www.reddit.com/r/USC/comments/a7ued1/anyone_taken_csci_526_or_csci_538/ |

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
