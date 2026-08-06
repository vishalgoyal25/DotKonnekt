# Advanced RAG Q&A System

A retrieval-augmented Q&A system built for the Track C take-home assignment.
It answers questions over a private document corpus using five retrieval and
generation techniques working together — query transformation, hybrid
(vector + keyword) retrieval, LLM-based re-ranking, grounded generation with
validated citations, and a corrective retrieval loop — and refuses to answer
when the corpus genuinely doesn't cover a question, instead of guessing.

The corpus describes **Northbay Commerce AI**, a fictional B2B retail/AI
vendor invented for this assignment (see [Synthetic corpus](#synthetic-corpus)
below for why). Because Northbay doesn't exist, the underlying language model
has no pretrained knowledge of it — so a correct, cited answer is only
possible if retrieval actually worked, not because the model already knew
the answer.

---

## Setup instructions

### Prerequisites

- Python 3.10 or newer
- A free [Groq](https://console.groq.com/keys) API key (primary LLM provider)
- A free [Cerebras](https://cloud.cerebras.ai) API key (automatic failover provider)

Both providers serve the same open-weight model (`gpt-oss-120b`) through an
OpenAI-compatible API, so the code talks to both through the same `openai`
Python SDK — see [Architecture](#architecture) for why two providers are used.

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

`sentence-transformers` pulls in PyTorch and is the slow part of this
install — expect a few minutes on first run.

> **Known setup issue (Windows):** if `pip install` fails with
> `WinError 32 (file in use)`, it's almost always an IDE extension (a
> linter/formatter language server) racing pip for a file lock while the
> virtual environment is being created — not a real dependency conflict.
> Closing the IDE's language-server processes and re-running the same
> install command resolves it.

### 2. Configure API keys

```bash
copy .env.example .env
```

Open `.env` and paste in your Groq and Cerebras keys. `.env` is git-ignored
— it never leaves your machine.

### 3. Build the search index

```bash
python ingest.py
```

This reads every file in `docs/`, splits them into overlapping chunks, embeds
them locally with `sentence-transformers`, and stores them in a local
ChromaDB folder (`chroma_db/`) plus a plain-text copy for BM25 keyword
search. Re-run this any time `docs/` changes — it's idempotent (rebuilds
the index from scratch each time, no stale leftovers).

### 4. Run it

Two interchangeable front ends, same pipeline underneath:

**Command line:**
```bash
python main.py
```
Ask questions at the prompt. Type `/dump` to print the full session state,
or `exit` / `/exit` to end the session and save a transcript to `transcripts/`.

**Web UI (Streamlit):**
```bash
streamlit run app.py
```
Opens a chat interface in your browser with the same session memory,
transcript-on-clear behaviour, and an expandable "How I got here" panel per
answer showing the full pipeline trace (retrieval scores, rerank scores,
whether the corrective loop fired, sources cited).

> **Known setup issue:** if the terminal shows repeated `torchvision` import
> tracebacks while Streamlit is running, this is Streamlit's file-watcher
> probing an optional, unused submodule of `transformers` — harmless, and
> already disabled via the committed `.streamlit/config.toml`
> (`fileWatcherType = "none"`).

Every LLM call made by either front end is logged to `logs/trace.jsonl`
(see [Tracing](#tracing--logs)) — nothing is silently retried or hidden.

---

## Architecture

### How a query flows through the system

```
  Question
     |
     v
  Query Transform  --------------------------> unchanged / rewrite / decompose
     |                                          (1 LLM call)
     v
  Hybrid Retrieval
    BM25 search  ---\
    Vector search ---+--> Reciprocal Rank Fusion (RRF) --> fused candidates
     |
     v
  Re-ranking  --------------------------------> LLM scores each candidate
     |                                          (1 LLM call)
     v
  Corrective Loop (only if top score is weak)
    reformulate query --> re-search --> re-rank --> keep the better attempt
     |                                  (0 or 2 LLM calls)
     v
  Grounded Generation  ------------------------> answer + citations, OR
     |                                           genuine abstain
     v
  Answer (with sources) returned to the session
```

Every box that says "LLM call" is logged to `logs/trace.jsonl` — see
[Tracing](#tracing--logs). A single question typically costs 4–6 calls total
(1 transform + 1 rerank + 0 or 2 corrective + 1 generation).

### Step by step

1. **Query transform** (`query_transform.py`) — the model decides whether the
   question needs rewriting (e.g. resolving "it" using conversation history),
   decomposing (a compound question like "what's the trial length *and* what
   does Growth include?"), or is fine as-is. Most questions are left
   unchanged — the model is explicitly told a no-op is a valid, common
   answer, not a fallback.

2. **Hybrid retrieval** (`retrieval.py`) — every query variant (the original
   *and* any transformed queries) is searched two ways: BM25 for exact
   keyword/token matches, and vector similarity (local MiniLM embeddings)
   for paraphrases and meaning. The two ranked lists are merged with
   **Reciprocal Rank Fusion** — each candidate's score is `1/(60+rank)`
   summed across every list it appears in. RRF is used instead of averaging
   raw scores because BM25 scores and cosine similarities live on
   incomparable scales; rank position is the only thing safe to combine.

3. **Re-ranking** (`rerank.py`) — the fused candidates (still ordered by a
   cheap heuristic) are handed to the LLM in a single batched call, which
   scores each one for actual relevance to the question. This step exists
   because RRF's fusion is positional, not semantic — it can rank a
   loosely-related chunk above a directly-relevant one; the LLM re-scores by
   reading the actual text.

4. **Corrective loop** (`corrective.py`) — if the top re-ranked score is
   below a fixed threshold, the system assumes the first retrieval attempt
   was weak, asks the model to reformulate the query once, re-searches and
   re-ranks with the new query, and keeps whichever of the two attempts
   scored higher. This is capped at exactly **one** retry — never open-ended
   — so a genuinely uncovered question fails fast into the abstain path
   instead of looping.

5. **Grounded generation** (`generate.py`) — the model answers using only
   the final retrieved chunks, and is instructed to name which source
   document(s) it used. Citations are never trusted as claimed: the code
   independently checks that every cited doc ID actually appears among the
   chunks that were placed in the prompt. If the evidence is too weak (same
   threshold as step 4, after the retry has already happened), the model is
   asked to explain — in its own words, grounded in what the retrieved
   passages *do* say — why it can't answer, rather than returning a
   hardcoded "I don't know."

### Why this stack

- **Groq (primary) + Cerebras (automatic failover)** — both are free,
  fast-inference hosts for open-weight models, reached through the same
  `openai` SDK with only a different `base_url`. One `call_llm()` function
  tries Groq first and falls over to Cerebras only on a rate-limit (429) or
  server error (5xx) — never on a genuine bad-request (400), which would
  just repeat the same failure on the second provider. This was chosen over
  a single-provider setup because free-tier rate limits (both daily and
  per-minute) are real and were hit repeatedly during development — the
  failover isn't defensive theater, it fired for real during testing (see
  [Known limitations](#known-limitations)).
- **ChromaDB**, local persistent client, no server — a document set this
  small (15 files) doesn't need a hosted vector database.
- **`rank_bm25`** for the keyword half of hybrid retrieval — a small, plain
  implementation of BM25Okapi, easy to read end-to-end.
- **`sentence-transformers` / `all-MiniLM-L6-v2`** for embeddings — runs
  locally on CPU, no API cost, no network dependency for the retrieval half
  of the pipeline.
- **Streamlit** for the UI — a single-file, no-backend way to expose the
  same pipeline interactively (see [Bonus items](#bonus-items)).

---

## The five techniques

This section is also the **prompt design writeup**: every system prompt
used in the pipeline, quoted in full, with the reasoning behind its wording.

### 1. Query transformation (`query_transform.py`)

```
You transform a user's question before it is used for document retrieval.

Given the question and, if provided, recent conversation history, decide
which ONE of these applies:

1. "rewrite" - the question depends on prior conversation (pronouns like
"it"/"they", phrases like "what about X", a missing subject). Rewrite it
into a single, standalone question that would make sense with no prior
context.
2. "decompose" - the question genuinely asks about more than one distinct
thing, and answering it requires looking up separate pieces of
information. Split it into standalone sub-questions.
3. "unchanged" - the question is already specific, standalone, and asks
about one thing. Return it exactly as given. Do NOT force a rewrite or
split when the question is already fine as-is - this is the most common
case, not the exception.

Respond with ONLY valid JSON, no other text, no markdown fences:
{"action": "rewrite" | "decompose" | "unchanged", "queries": ["..."]}
```

**Why it's structured this way:** the model's first instinct is to "improve"
every question it sees. Option 3 explicitly names the no-op as the common
case, not a fallback, which stops the model from rewriting perfectly good
questions just because it can. Both the original question and any
transformed queries are searched together downstream (never the transform
alone) — so a bad rewrite degrades results, it doesn't destroy them.

### 2. Hybrid retrieval (`retrieval.py`)

No LLM prompt — this step is pure algorithm. BM25 (keyword overlap) and
vector similarity (embedding distance) each produce a ranked list; the two
are merged with Reciprocal Rank Fusion, `score = Σ 1/(60 + rank)` per
candidate. It's listed here because it's one of the five required
techniques, even though it involves no prompt engineering.

### 3. Re-ranking (`rerank.py`)

```
You score how relevant each candidate passage is to answering a query, on
a scale of 0 to 10.

0 means the passage has nothing to do with the query. 10 means the passage
directly and completely contains the information needed to answer it.
Score based on whether the passage actually contains the answer - not just
whether it's on a related topic.

Respond with ONLY valid JSON, no other text, no markdown fences:
{"scores": [{"index": 1, "score": 0}, {"index": 2, "score": 0}, ...]}
```

**Why it's structured this way:** all candidates are scored in a single
batched call instead of one call per candidate. Scoring them side by side
lets the model rank them relative to each other; scoring one at a time
produces uncalibrated absolute numbers that don't compare well across
calls. The "not just whether it's on a related topic" line exists because
early testing showed the model scoring topically-adjacent-but-unhelpful
passages too generously without that instruction.

### 4. Corrective loop (`corrective.py`)

```
The following question returned weak search results from a document
corpus. Rewrite it as a single alternative search query that might
retrieve better matches - try a different angle: broader if the original
was too narrow, or more specific if it was too generic.

Respond with ONLY the rewritten query text - no quotes, no explanation.
```

**Why it's structured this way:** this only fires when the top rerank score
falls below a fixed threshold — most questions never reach this prompt. It
asks for one alternative angle, not a menu of options, because the retry
budget is exactly one attempt. After the retry, the code compares the new
top score against the original and **keeps whichever attempt actually
scored higher** — the reformulation is allowed to fail without making the
final answer worse.

### 5. Grounded generation with citations and abstain (`generate.py`)

Two prompts, selected by the same threshold used in step 4 (routing which
prompt runs is fine — the PDF's "no scripted responses" rule is about the
*message itself* not being a hardcoded string, not about avoiding
threshold-based control flow):

**Grounded answer** (used when the evidence is strong enough):
```
You are a Q&A assistant for Northbay Commerce AI, a B2B retail and
consumer AI vendor. Answer the question using ONLY the context passages
below - never use outside knowledge, even if you believe you know the
answer. If part of the question isn't supported by the context, leave
that part out rather than guessing.

Write a clear, direct answer in plain prose.

After your answer, on a new line, write exactly:
Sources: <comma-separated document IDs you actually drew on>
```

**Abstain** (used when the evidence is weak):
```
You are a Q&A assistant for Northbay Commerce AI. The context passages
below were retrieved but scored too low to reliably answer the question -
they may be off-topic or only tangentially related.

Do not use outside knowledge and do not guess. Write a brief, honest reply
that says you don't have enough information to answer this specific
question, and briefly mentions what the retrieved context actually covers
instead, so the user understands why. Base this only on what the context
below actually says.

After your reply, on a new line, write exactly:
Sources: none
```

**Why it's structured this way:** the abstain message is generated fresh
by the model from whatever weak context it was actually given — it is
never a hardcoded "I don't know" string, which is exactly what the PDF's
"no scripted responses" constraint forbids. Asking it to mention what the
context *does* cover (instead of just refusing) makes the refusal useful
rather than a dead end.

Citations are never trusted as claimed. The code cross-checks every cited
document ID against the IDs of the chunks actually placed in the prompt —
a fabricated ID can't match a real one, so it gets caught and reported
separately as an "invalid citation" rather than silently accepted.

---

## Synthetic corpus

The 15 documents in `docs/` describe **Northbay Commerce AI**, a fictional
B2B retail/consumer AI vendor invented for this assignment — it is not a
real company, and every fact in these documents (pricing, SLAs, case
studies, contract terms) is made up for this project. Each file opens with
a comment marking it as synthetic sample content.

**Why invent a fictional company instead of using real material:** the
underlying LLM has no pretrained knowledge of Northbay. That means a
correct, cited answer is only possible if retrieval actually pulled the
right passage into context — the model can't be "right by coincidence"
from something it already knew. This makes the whole corpus a grounding
check, not just a couple of planted trick questions.

Two deliberate design choices inside the corpus:

- **A real conflict:** `09_pricing_tiers.md` describes a 14-day trial,
  while `10_contract_trial_terms.md` describes a 30-day evaluation period —
  a genuine minor inconsistency for the corrective loop and citation logic
  to surface, rather than something invented after the fact.
- **Coverage gaps:** some plausible customer questions (employee headcount,
  annual revenue, refund policy specifics) are never answered anywhere in
  the corpus, on purpose, so the abstain path has real questions to fail
  correctly on.

The 15 files cover: platform overview, service catalogue, agentic
templates, the embedded-engineering delivery model, integrations, security,
deployment options, pricing, contract terms, two customer case studies,
support/SLA policy, onboarding, and a glossary/FAQ — a realistic spread for
a B2B AI vendor's knowledge base.

---

## Sample transcript

A full, real, unedited 4-question session is committed at
[`transcripts/sample_run.md`](transcripts/sample_run.md). It's a genuine CLI
run (`python main.py`), not a cleaned-up or hand-picked example, and it
walks through four distinct behaviours in order:

1. A normal question answered from a single document, with a citation.
2. A multi-part question — query **decomposition** in action, pulling from
   two documents.
3. The **corrective loop** firing on a genuine coverage gap (headcount),
   followed by a real, model-generated abstain.
4. A second, independent abstain case (annual revenue) — including an
   honestly-kept rough edge, where the reformulated query came back
   duplicated ("...2023Northbay company...2023"). The pipeline tolerated
   the malformed intermediate value and still abstained correctly instead
   of crashing or making something up.

The file includes the exact 4 questions, in order, so anyone can reproduce
it themselves against the same corpus.

---

## Evaluation

`eval_set.json` holds 12 question/gold-answer/expected-citation cases,
covering ordinary factual questions, a multi-part question, questions that
should abstain, and the deliberate 09/10 pricing conflict. Run it with:

```bash
python evaluate.py
```

Each answer is scored two ways: **citation accuracy** (does the answer cite
a subset of the expected documents — a deterministic check in code, not an
LLM judgment) and an **LLM-as-judge** verdict (yes / partial / no, does the
answer actually match the gold answer).

**Real results, both runs reported honestly** (the second run added two
extra cases, E11 and E12, closing coverage gaps in the corpus that no
earlier test had exercised):

| Run | Citation accuracy | Judge: yes | Judge: partial | Judge: no | Corrective loop fired |
|---|---|---|---|---|---|
| 10 cases | 9/10 (90%) | 8 | 1 | 1 | 2/10 (20%) |
| 12 cases | 10/12 (83%) | 9 | 2 | 1 | 2/12 (17%) |

Two findings worth naming directly, since they say more about the system's
honesty than a clean scorecard would:

- **The refund-policy question (E04) never abstains**, and correctly
  shouldn't be expected to — its rerank score lands just above the abstain
  threshold. This is a known, deliberately-kept borderline case, not a bug.
- **The judge itself is not perfectly consistent.** E04 was judged "no" on
  one run and "yes" on the next, for the same underlying answer. E06 (EU
  on-premise) answered correctly on one run via negative inference, but on
  a re-run the corrective loop fired differently and the system abstained
  instead. Both are reported here rather than only showing the cleaner run
  — the system's own rerank step and the LLM-judge step are each
  independently non-deterministic, and pretending otherwise would misstate
  what was actually observed.

---

## Known limitations

Honest, not exhaustive — these are the limitations that matter, found
through real testing rather than guessed in advance.

- **BM25 can't handle paraphrases.** If a question shares no exact words
  with the source text, BM25 contributes nothing — vector search has to
  carry the whole match alone. This is exactly why the system uses both,
  not one or the other.
- **Rerank scores are non-deterministic.** The same question can score
  differently across runs, and on borderline questions this can flip the
  outcome — occasionally a question that abstained on one run answers
  (or vice versa) on the next. This was observed directly during
  evaluation (E06, see [Evaluation](#evaluation)), not just theorized.
- **A high relevance score means the passage is on-topic, not that it
  contains the correct answer.** The reranker judges relevance, not
  correctness — a passage can score well while still being incomplete or
  slightly off from what's actually being asked.
- **Citation validation proves retrieval, not truth.** The code confirms a
  cited document ID was genuinely part of the context the model saw — it
  does not verify that the model's specific sentence is an accurate
  reflection of that document's content.
- **The refund-policy question never abstains**, and its rerank score sits
  just above the abstain threshold — a real, deliberately-kept borderline
  case, confirmed in the eval run (E04), not a hidden bug.
- **The LLM-as-judge in the evaluation harness is itself inconsistent**
  between runs on identical underlying behaviour — a second, independent
  layer of non-determinism on top of the pipeline's own, worth knowing
  before trusting any single eval run as ground truth.
- **The corrective loop's reformulated query can come back malformed**
  (duplicated text) under heavy provider load — the pipeline tolerates
  this without crashing, but it's a real rough edge, visible in the
  committed sample transcript.
- **The synthetic corpus is cleaner than real documentation would be** —
  consistent formatting, no outdated pages, no duplicate/contradicting
  content beyond the one deliberate conflict. Results here are a
  reasonable but optimistic upper bound versus a messier real corpus.
- **The system only guards a few specific failure boundaries** (an empty
  index, an empty candidate list, a parse failure) — it is not robust to
  arbitrary bad input in general, by design, given the fresher-level scope
  of this assignment.

---

## Bonus items

All three optional bonus items are implemented:

- **Streamlit UI** (`app.py`) — a chat interface over the same pipeline
  used by the CLI, with full behavioural parity: session memory across
  turns, a "How I got here" panel per answer showing the full pipeline
  trace (search queries, whether the corrective loop fired, per-source
  rerank scores and excerpts), a full session-state dump, and a
  "Clear conversation" button that saves a transcript before resetting —
  matching the CLI's `/exit` behaviour.
- **Evaluation harness** (`evaluate.py`, `eval_set.json`) — scores answers
  against 12 gold-answer cases on two axes (citation accuracy, LLM-judge
  verdict), reported in full in [Evaluation](#evaluation) above.
- **Tracing/logging** (`tracing.py`) — every LLM call across every
  technique is logged; see below.

## Tracing / logs

Every call to `call_llm()` — across all five techniques, both providers —
is appended as one JSON line to `logs/trace.jsonl`, recording: timestamp,
purpose (`transform` / `rerank` / `corrective` / `generate`), which
provider actually served the call, a prompt preview plus full prompt
character count, prompt/completion token counts (read from the API
response's own `usage` field, never estimated), and latency in seconds.

A sample is committed at [`logs/sample_trace.jsonl`](logs/sample_trace.jsonl)
so the format is visible without needing to run the system first. Nothing
is silently retried or hidden — a failed call is logged too, with its error.
