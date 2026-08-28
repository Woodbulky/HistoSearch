# CLAUDE.md — ChronosGraph

## 0. HOW CLAUDE CODE MUST OPERATE

You are the implementation engineer for **ChronosGraph**.

ChronosGraph is a research project, not a generic software app. Your job is to implement the system, automate repetitive work, run checks, maintain reproducibility, and report results clearly.

The human researcher owns:
- research questions
- source selection and approval
- historical interpretation
- annotation decisions
- gold answers
- experiment design
- training decisions
- interpretation of results
- final research claims

Claude Code owns:
- code
- data pipelines
- database implementation
- APIs
- retrieval implementation
- model integration
- training/evaluation scripts
- tests
- automation
- frontend implementation
- documentation
- reproducible experiment execution

### Absolute rule

**Never assume that a required user decision, dataset, credential, source approval, annotation, or experiment has been completed. Check the repository state first.**

When a phase starts:
1. Read this file completely.
2. Read `PROJECT_STATE.md` if it exists.
3. Inspect the repository and existing artifacts.
4. Determine the current phase from actual evidence, not memory.
5. Check the phase's required inputs.
6. If required input is missing, ask the user only for the missing item.
7. Do not implement later-phase work while a required earlier-phase gate is blocked.
8. If the current phase is complete, do not silently start the next phase. First produce the next-phase handoff checklist.

### Two kinds of prerequisites

**Immediate prerequisites** are required to start the current phase.  
If they are missing, stop and ask.

**Future prerequisites** are not needed now but will be required by a later phase.  
Do not block the current phase. Instead, when the current phase finishes, report them under:

> **BEFORE STARTING PHASE N: YOU MUST DO THESE**

This rule is mandatory.

---

# 1. WHAT WE ARE BUILDING

ChronosGraph is an academic historical research system for evidence-grounded question answering over the Indian Independence and Partition period.

It does six major things:

1. Collects historical primary and secondary sources with provenance.
2. Converts them into traceable passages and structured historical claims.
3. Represents people, places, organizations, events, time, claims, and relationships.
4. Retrieves evidence for a historical question using semantic, lexical, temporal, graph, and evidence signals.
5. Detects disagreements between historical claims and classifies the disagreement.
6. Produces an evidence-backed research answer showing sources, competing accounts, chronology, provenance, and uncertainty.

The final system should behave more like a **research assistant** than a chatbot.

A good answer is not merely fluent. It must make it possible to inspect:

```text
Question
  ↓
Retrieved evidence
  ↓
Historical claims
  ↓
Events / people / places
  ↓
Temporal relationships
  ↓
Conflicting accounts
  ↓
Evidence and provenance
  ↓
Final answer
```

---

# 2. RESEARCH PURPOSE

Everything in the project should support the following research questions.

### RQ1 — Temporal reasoning

Does explicitly modelling historical time improve historical question answering?

### RQ2 — Evidence and provenance

Does evidence-aware retrieval improve citation/support quality?

### RQ3 — Historical disagreement

Can the system distinguish a genuinely contested historical interpretation from an ordinary state change where a newer fact supersedes an older one?

### RQ4 — Specialized model

Does a model fine-tuned specifically for historical conflict classification outperform general or zero-shot baselines?

### RQ5 — Multilingual historical reasoning

Can a shared historical representation support English and Hindi evidence and improve cross-language historical research?

---

# 3. CORE RESEARCH CONTRIBUTIONS

## Contribution A — Conflict classification

When claims conflict, ChronosGraph must not automatically select the newest claim.

The supported classification is:

| Label | Meaning |
|---|---|
| `NOT_CONTRADICTION` | The claims are not actually contradictory. |
| `RESOLVABLE_BY_RECENCY` | The underlying state changed and the newer source legitimately supersedes the older state. |
| `PERMANENTLY_CONTESTED` | Sources describe or interpret the same past event differently; publication date does not resolve the disagreement. |
| `UNKNOWN` | There is insufficient evidence to safely classify the disagreement. |

`PERMANENTLY_CONTESTED` is a first-class research result. Never suppress it to produce a cleaner answer.

## Contribution B — Evidence confidence is not factual truth

The system must separately represent:
- how strongly a passage supports a claim
- how many sources support or mention it
- what type of source it is
- how confidently extraction/classification was performed
- whether the historical proposition itself is disputed

Never compress all of this into one generic confidence number.

---

# 4. HISTORICAL CORPUS

## Initial frozen corpus

Primary corpus:
- UK Hansard
- Constituent Assembly Debates (CAD), India

Initial study window:
- August–December 1947

The corpus is frozen for the main experiment once the acquisition manifest is finalized.

The Hansard × CAD pairing is central because the same historical events can be discussed from different institutional and political positions.

### Planned expansion sources

Add only after the core pipeline is working:
- National Archives of India / Abhilekh Patal
- Nehru Archive
- Gandhi Heritage Portal
- other reputable archival or public-domain collections

### Multilingual target

Hindi is a design target from the beginning, but Hindi corpus acquisition must not block the English pipeline.

The representation layer must carry language information so that later English and Hindi evidence can coexist in the same historical representation.

---

# 5. WHAT THE FINAL USER EXPERIENCE SHOULD DO

A user should be able to enter a question in English or Hindi.

The system should return:

```text
answer
evidence
timeline
conflicting_accounts
uncertainty
provenance
```

### Example conceptual answer

Question:

> Why did violence increase in Punjab in 1947?

The system should be able to communicate:

- what the available evidence says
- which sources make each claim
- when those claims were made
- which historical event each claim concerns
- where sources agree
- where they disagree
- whether the disagreement is resolvable or permanently contested
- what remains unknown
- links or references back to the exact evidence passages

The UI must never hide a meaningful conflict merely because the answer is easier to write without it.

---

# 6. SYSTEM ARCHITECTURE

The system has these major layers:

```text
                HISTORICAL SOURCES
                        ↓
                 SOURCE REGISTRY
                        ↓
                     INGEST
                        ↓
              CLEAN / NORMALIZE / OCR
                        ↓
                   PASSAGES
                        ↓
             MULTILINGUAL EMBEDDINGS
                        ↓
             CLAIM / ENTITY / EVENT
                  EXTRACTION
                        ↓
              HISTORICAL KNOWLEDGE
                    REPRESENTATION
                        ↓
       ┌────────────────┼─────────────────┐
       ↓                ↓                 ↓
   RETRIEVAL        TEMPORAL          EVIDENCE
       └────────────────┼─────────────────┘
                        ↓
              CONFLICT DETECTION
                        ↓
             CONFLICT CLASSIFICATION
                        ↓
       ┌────────────────┼─────────────────┐
       ↓                ↓                 ↓
    RECENCY         CONTESTED          UNKNOWN
       └────────────────┼─────────────────┘
                        ↓
                ANSWER COMPOSITION
                        ↓
                  BACKEND API
                        ↓
                    FRONTEND
```

---

# 7. TECHNOLOGY DECISIONS

These are the current implementation decisions.

Do not change them silently.

If a change is needed, explain the reason and ask before making a research-impacting architectural change.

## Core

- Python 3.11+
- `uv`
- Git + GitHub

## Storage and search

- PostgreSQL 16 as the source of truth
- `pgvector` for embeddings
- PostgreSQL lexical search for exact historical terms
- HNSW vector index
- local Docker database during research
- Supabase only for the final read-only hosted demo

Do **not** point extraction, training, or evaluation at Supabase.

## Historical knowledge representation

The graph is represented inside PostgreSQL using:
- `nodes`
- `edges`
- recursive SQL queries for traversal

Do not add Neo4j or another graph database unless the human researcher explicitly approves the change.

## Models

- Extraction model: free-tier LLM API behind a provider interface
- Embeddings: multilingual model capable of English and Hindi
- Conflict classifier: small encoder/cross-encoder fine-tuned for the project
- Training: Google Colab/Kaggle free GPU where available
- Model storage: Hugging Face when useful

## Backend

- FastAPI

## Frontend

- Next.js
- TypeScript

The frontend is thin. Research logic must remain in the backend/research layers.

## Experiment tracking

- reproducible local experiment directories
- MLflow or equivalent local tracking when useful
- timestamp + git commit + model version for every official result

## Explicitly avoid

- n8n for core research pipeline
- LangChain/LlamaIndex as the abstraction layer for retrieval logic
- paid APIs as a required dependency
- proprietary hosted vector databases
- training a foundation model from scratch

---

# 8. DATA MODEL

The core entities are:

```text
Document
Passage
Entity
Event
Claim
EvidenceLink
Contradiction
Node
Edge
```

A practical relational representation is:

```sql
documents
  id
  source
  title
  date
  language
  url
  archive_id
  sha256
  retrieved_at
  license_note

passages
  id
  document_id
  speaker
  speaker_role
  turn_index
  sub_index
  language
  text
  char_start
  char_end
  embedding

entities
  id
  type
  canonical_name
  aliases

events
  id
  label
  t_start
  t_end
  granularity
  is_interval
  language

claims
  id
  text
  claim_type
  subject_entity_id
  event_id
  asserted_at
  language
  extraction_confidence

evidence_links
  id
  claim_id
  passage_id
  relation
  char_start
  char_end
  support

contradictions
  id
  claim_a_id
  claim_b_id
  label
  rationale
  scope
  classifier_version
  evidence_confidence

nodes
  id
  kind
  ref_id

edges
  src_node_id
  dst_node_id
  rel
  t_start
  t_end
```

---

# 9. NON-NEGOTIABLE RESEARCH INVARIANTS

These are correctness rules, not optional preferences.

1. Every claim must have at least one evidence link.
2. Every evidence link must point to a real passage and exact character span.
3. `asserted_at` means when the claim was made.
4. Event time means when the described event happened.
5. Never infer an event date more precisely than the source supports.
6. Evidence confidence must not determine conflict class.
7. Every contradiction must retain both claims.
8. `PERMANENTLY_CONTESTED` must never be silently removed.
9. `UNKNOWN` must remain available.
10. Raw source files are immutable.
11. Official evaluation data must never be regenerated just to improve a score.
12. Train/test leakage must be prevented by splitting by document/source grouping where appropriate.
13. Every model result must record model/version/config.
14. Every experiment must be reproducible from a recorded commit and dataset snapshot.
15. Any unexpected row loss between pipeline stages must be reported, not silently discarded.

---

# 10. PROVENANCE RULE

The system must maintain:

```text
claim
  ↓
evidence_link
  ↓
passage
  ↓
document
  ↓
original source
```

A user should be able to inspect the exact passage supporting a generated claim.

A claim that cannot be traced to evidence is an extraction failure, not a normal output.

---

# 11. CHUNKING RULE

For parliamentary debates:

**One speaker intervention = one passage.**

Do not use arbitrary fixed-token windows across speaker boundaries.

If an intervention is extremely long:
- split at paragraph boundaries
- preserve the same speaker
- preserve the same turn index
- add a sub-index
- preserve exact character offsets

Procedural material may be retained but should be separately flagged and excluded from claim extraction when it does not contain substantive historical assertions.

Reason:

```text speaker attribution
       +
date
       +
exact passage
       =
reliable historical provenance
```

Destroying those boundaries can manufacture false contradictions.

---

# 12. PIPELINE RULES

## Extraction

- Cache every LLM request.
- Cache key must include model, prompt version, and input hash.
- Validate structured output.
- Retry schema failures once.
- Send persistent failures to a failure log.
- Never silently coerce invalid output.
- Make extraction resumable.
- Store provider and model version.
- Preserve extraction confidence separately from historical truth.

## Retrieval

Use multiple retrieval signals:

```text
lexical
+
dense semantic
+
temporal
+
evidence
+
graph expansion
```

Start with:
1. lexical retrieval
2. dense retrieval
3. rank fusion
4. controlled graph expansion
5. temporal/evidence reranking

Do not let graph expansion grow without bounds.

## Conflict pairing

Do not compare every claim with every other claim.

Generate candidate pairs based on signals such as:
- shared entity
- shared event
- relevant topic
- overlapping time
- semantic similarity

Then apply contradiction detection.

---

# 13. ANSWER CONTRACT

The backend must produce a structured response object containing:

```text
answer
evidence[]
timeline[]
conflicting_accounts[]
uncertainty
provenance[]
```

### Meaning

`answer`
- direct response to the question

`evidence`
- source passages
- source title
- speaker where available
- date
- exact span

`timeline`
- temporally relevant events in order

`conflicting_accounts`
- both claims
- both sources
- contradiction label
- rationale
- classifier version

`uncertainty`
- missing or insufficient evidence
- unresolved classification
- ambiguity that materially affects the answer

`provenance`
- claim → passage → document trace

An empty `conflicting_accounts` means **no conflicts were identified**.

It must never mean that conflicts were found and suppressed.

---

# 14. FRONTEND REQUIREMENTS

The frontend is a research interface, not a decorative chatbot.

Minimum views:

## Search / question

- question input
- language selection or automatic language detection
- example research questions

## Answer

- direct answer
- uncertainty
- source-backed statements

## Evidence panel

For every important claim:
- source
- date
- speaker
- passage
- exact evidence span

## Conflict panel

Show:
- Claim A
- Claim B
- source A
- source B
- conflict class
- rationale

Especially highlight:

`PERMANENTLY_CONTESTED`

## Timeline

When useful:
- events
- dates
- relationships
- ordering

## Research provenance

Allow the user to move from:

```text
answer
→ claim
→ evidence
→ original passage
→ source
```

## Multilingual behavior

The same historical event can be connected to:
- English evidence
- Hindi evidence

The UI should make the language of each source obvious.

Do not translate away the original evidence when the original language is important.

---

# 15. BACKEND REQUIREMENTS

The backend must expose structured research operations.

At minimum:

```text
POST /query
GET  /documents/{id}
GET  /passages/{id}
GET  /claims/{id}
GET  /events/{id}
GET  /conflicts/{id}
GET  /health
GET  /metadata
```

`POST /query` should return the full answer contract.

Backend responsibilities:
- validate requests
- retrieve evidence
- run graph/temporal reasoning
- invoke classifier where needed
- compose answer
- return provenance
- never expose internal secrets
- log request/experiment/model versions appropriately

The frontend must not contain research logic that belongs in the backend.

---

# 16. MODEL TRAINING

We are **fine-tuning an existing pretrained model**, not training a foundation model from scratch.

The first focused model is the historical conflict classifier.

Input:

```text
claim A
claim B
historical context
source/context metadata where appropriate
```

Output:

```text
NOT_CONTRADICTION
RESOLVABLE_BY_RECENCY
PERMANENTLY_CONTESTED
UNKNOWN
```

### Training ownership

Claude Code:
- prepares data loaders
- creates training scripts
- creates evaluation scripts
- creates Colab notebook
- creates configuration
- creates inference integration
- creates reproducible experiment commands

Human researcher:
- reviews labels
- approves dataset
- runs/owns the training experiments in Colab
- chooses model/checkpoint based on evidence
- interprets results
- decides whether a training change is research-significant

### Baselines

The trained model must be compared on the same held-out test set against:
- zero-shot general LLM classifier
- appropriate off-the-shelf NLI/encoder baseline

Do not report only the fine-tuned model.

---

# 17. ANNOTATION

Annotation is a research-critical step.

Before labeling starts, create:

```text
annotation/GUIDELINES.md
```

It must explain:
- every label
- positive and negative examples
- `PERMANENTLY_CONTESTED` vs `UNKNOWN`
- contradiction vs difference in scope
- temporal change vs historical interpretation
- how source context is used

Use human labels for the gold dataset.

Double-annotate a meaningful subset and compute inter-annotator agreement.

Record rationales for difficult cases.

Split data to prevent leakage.

Never create a test set from the same document after seeing model predictions.

---

# 18. MULTILINGUAL / HINDI DESIGN

Hindi must be designed into the representation layer from the start but does not block the first English milestone.

Requirements:

- every document and passage has a language field
- every claim records its language
- embeddings support cross-language retrieval
- entity identity is independent of language
- event identity is independent of language
- original text is preserved
- translations are supplementary, not replacements for evidence

The goal is:

```text
English claim
       \
        → same historical event ← Hindi claim
       /
English source             Hindi source
```

The graph should represent the historical entity/event once while retaining language-specific evidence.

Later experiments should compare:
- English-only evidence
- Hindi-only evidence
- English + Hindi evidence

for both English and Hindi questions.

---

# 19. PHASED EXECUTION MODEL

## PHASE 0 — Research and environment foundation

### Goal

Create the repository, project state, environment, research specification, and source acquisition plan.

### Claude must check for

- Git repository
- project directory
- `CLAUDE.md`
- `PROJECT_STATE.md`
- environment configuration
- database availability
- baseline directory structure
- dependency configuration

### Human must provide/decide

- project name and ownership information
- initial research scope
- initial corpus window
- approved source collections
- free-tier account/API details only where actually required

### Claude may implement

- repository structure
- configuration
- Docker setup
- database bootstrap
- migrations
- tests
- source registry structure
- state tracking files

### Phase 0 completion criteria

All environment components needed for Phase 1 work.

### BEFORE STARTING PHASE 1

Claude must print:

```text
PHASE 0 COMPLETE

Before starting Phase 1, the user must:
1. Approve the initial source list.
2. Confirm the historical date window.
3. Confirm access/credentials for any source that requires them.
4. Confirm the local data directory is available.
5. Confirm whether any source has explicit usage/license restrictions.

Ready for Phase 1 after these are satisfied.
```

Do not ask for Phase 2 information yet unless it is needed to prevent Phase 1 from proceeding.

---

# PHASE 1 — Corpus acquisition

### Goal

Acquire the approved historical source corpus and create an immutable source manifest.

### Claude checks first

- Are approved source names already present?
- Are source URLs/archive identifiers present?
- Are license/provenance notes present?
- Are credentials already configured where necessary?
- Has the user already selected the scope?
- Does raw data already exist?
- Does `manifest.jsonl` already exist?
- Are there previous downloads that can be resumed?

### If something required is missing

Ask only for the missing information.

Example:

> Phase 1 cannot start because the approved Hansard source identifiers are not present. Please provide or approve them.

Do not ask about training parameters, frontend design, or Hindi data here because they are not Phase 1 blockers.

### Claude does

- source discovery scripts
- downloads
- retries/resume
- checksum generation
- immutable raw storage
- metadata extraction
- manifest creation
- source count reporting
- download validation

### Human does

- approve discovered sources
- reject irrelevant/unusable sources
- confirm research relevance
- review a sample of acquired source records
- resolve copyright/license questions when needed

### Phase 1 output

```text
data/raw/
data/manifest.jsonl
source acquisition report
```

### Completion gate

Cannot leave Phase 1 until:
- raw sources exist
- hashes exist
- manifest is internally consistent
- source provenance is recorded
- acquisition counts are reported
- no approved corpus side is silently missing

### BEFORE STARTING PHASE 2

Claude must list only actual upcoming requirements, for example:

```text
PHASE 1 COMPLETE

Before Phase 2, the user must:
1. Review and approve the corpus acquisition report.
2. Confirm the source set is frozen for the ingestion experiment.
3. Confirm any unresolved OCR/source-quality exceptions.
4. Ensure the machine has sufficient disk space for processed text and embeddings.

Not required yet:
- conflict labels
- model training
- Colab
- Hugging Face publication
- frontend decisions
```

---

# PHASE 2 — Parsing, cleaning, and passage creation

### Goal

Turn raw historical files into reliable, traceable passages.

### Claude checks

- raw files exist
- manifest is valid
- parsers exist
- OCR tools are available when needed
- source-specific parsing rules are defined

### Claude does

- parse HTML/PDF/text
- OCR where needed
- normalize text
- identify speaker/date metadata
- perform speech-turn chunking
- preserve character offsets
- write processed data
- generate quality reports
- flag parsing failures

### Human does

- manually inspect samples
- approve chunk quality
- identify systematic OCR problems
- decide whether a source requires special handling

### Completion gate

- passage count reconciles with source counts
- sample passages are correct
- speaker boundaries are preserved
- offsets work
- no silent row loss

### BEFORE STARTING PHASE 3

Prepare/approve:
- extraction schema
- extraction prompts
- entity/event definitions
- claim definitions
- extraction quality sample
- model/provider credentials if needed

Do not require training labels yet.

---

# PHASE 3 — Claim, entity, event, and temporal extraction

### Goal

Convert passages into structured historical knowledge.

### Claude does

- extraction schemas
- extraction prompts
- cached model calls
- validation
- resumable extraction
- entity normalization
- event creation
- claim creation
- evidence links
- temporal anchors
- failure reporting

### Human does

- inspect extraction samples
- approve schema semantics
- identify systematic extraction errors
- approve whether the extracted representation is historically meaningful

### Completion gate

Every stored claim has traceable evidence.

### BEFORE STARTING PHASE 4

Prepare:
- baseline research questions
- gold answer plan
- evaluation rubric
- expected question types
- frozen evaluation set design

---

# PHASE 4 — Baseline retrieval and QA

### Goal

Create a simple baseline before adding the research contributions.

Required systems:

```text
System A: LLM without retrieval
System B: LLM + retrieval
```

Optional but useful:

```text
System C: Graph-assisted retrieval
```

### Human must provide

- evaluation questions
- gold answers or gold evidence expectations
- question categories

### Claude does

- retrieval
- baseline answer pipeline
- evaluation runner
- citation collection
- score calculation

### Completion gate

Baseline results exist on a frozen test set.

### BEFORE STARTING PHASE 5

Prepare:
- temporal questions
- duration/order questions
- evidence evaluation criteria
- source-quality rubric

---

# PHASE 5 — Temporal and evidence reasoning

### Goal

Add explicit temporal and evidence-aware reasoning.

### Claude does

- temporal relationships
- temporal filtering/reranking
- evidence ranking
- provenance-aware retrieval
- experiments with and without temporal/evidence signals

### Human does

- validate temporal relations
- review evidence ranking samples
- approve evidence-quality criteria

### Completion gate

Ablation-ready retrieval system exists.

### BEFORE STARTING PHASE 6

Prepare:
- candidate claim pairs
- annotation guidelines
- annotator plan
- contradiction label definitions
- agreement evaluation plan

---

# PHASE 6 — Contradiction dataset and classification pipeline

### Goal

Build the human-validated contradiction dataset.

### Claude does

- candidate pairing
- pair export
- annotation interface/data format
- dataset splitting utilities
- evaluation scripts
- zero-shot baseline runner

### Human does

- label claim pairs
- write difficult-case rationales
- double-annotate the agreement subset
- resolve disagreements
- freeze the test set

### Completion gate

- labeled dataset exists
- agreement statistic exists
- train/validation/test split is frozen
- no document leakage
- test set cannot be regenerated casually

### BEFORE STARTING PHASE 7

Prepare:
- approved labeled dataset
- Google Colab access
- model choice approval
- training configuration
- compute plan
- Hugging Face account if publishing the model

---

# PHASE 7 — Fine-tuning

### Goal

Fine-tune the specialized historical conflict classifier.

### Claude does

- training code
- notebook
- configuration
- checkpointing
- evaluation
- confusion matrix
- baseline comparison scripts
- model integration

### Human does

- run training in Colab/Kaggle
- inspect training curves
- compare checkpoints
- decide final model
- record research observations
- decide whether to run additional experiments

### Mandatory comparisons

```text
Zero-shot general LLM
        vs
Off-the-shelf baseline
        vs
Fine-tuned ChronosGraph classifier
```

### Completion gate

- final model saved
- test score recorded
- baseline scores recorded
- experiment configuration recorded
- model version recorded

### BEFORE STARTING PHASE 8

Prepare:
- Hindi/English source candidates
- multilingual evaluation questions
- cross-language entity mapping review
- multilingual test design

---

# PHASE 8 — Hindi and multilingual extension

### Goal

Extend the same historical representation across English and Hindi.

### Claude does

- Hindi ingestion support
- language-aware passage storage
- multilingual embedding integration
- cross-language retrieval
- multilingual classifier integration
- multilingual API responses

### Human does

- approve Hindi sources
- inspect Hindi extraction
- verify cross-language entity/event links
- create multilingual evaluation questions
- inspect translation/retrieval failures

### Completion gate

The same historical event can be connected to evidence in both languages without losing original text/provenance.

### BEFORE STARTING PHASE 9

Prepare:
- final evaluation set
- Hindi evaluation set
- conflict evaluation set
- gold answers
- experiment matrix
- frozen dataset snapshot

---

# PHASE 9 — Full evaluation and ablation

### Goal

Produce the research evidence.

Mandatory systems:

```text
1. LLM only
2. LLM + vector/lexical retrieval
3. Graph-assisted system
4. ChronosGraph
5. ChronosGraph + fine-tuned classifier
```

Mandatory research comparison:

```text
ChronosGraph with contested-preserving classification
            VS
same system with recency-wins classification
```

### Metrics

- factual accuracy
- citation/evidence accuracy
- temporal accuracy
- contradiction precision/recall/F1
- hallucination/unsupported-claim rate
- multilingual retrieval/answer performance
- classifier performance

### Claude does

- run experiments
- generate metrics
- generate tables/plots
- store exact configurations
- write experiment summaries

### Human does

- inspect failures
- perform qualitative analysis
- interpret results
- determine which hypotheses are supported or rejected
- decide what belongs in the paper

### Completion gate

All official tables can be regenerated from frozen inputs.

---

# PHASE 10 — Backend/API

### Goal

Expose the validated research system through a stable backend.

### Claude does

- FastAPI implementation
- request validation
- response schema
- query pipeline
- provenance endpoints
- health checks
- logging
- API tests

### Human does

- approve API behavior
- validate answer quality through the API
- approve which research information is exposed

### Completion gate

The API can reproduce the validated research pipeline.

---

# PHASE 11 — Frontend

### Goal

Provide a usable research interface.

### Claude does

- Next.js application
- question/search interface
- answer view
- evidence view
- timeline
- conflict view
- provenance navigation
- Hindi/English support
- loading/error states
- responsive layout

### Human does

- approve information hierarchy
- test real research questions
- identify confusing displays
- ensure uncertainty and conflict remain visible

### Completion gate

A user can conduct a historical research query and inspect how the answer was constructed.

---

# PHASE 12 — Release, reproducibility, and paper

### Goal

Produce the research artifact.

Claude prepares:

```text
source manifest
dataset snapshot
database dump
trained model reference
experiment configs
evaluation outputs
reproduction instructions
API documentation
frontend deployment
paper-support tables
```

Human prepares:

```text
research interpretation
final claims
limitations
discussion
paper narrative
presentation
```

---

# 20. PHASE GATE PROTOCOL FOR EVERY SESSION

At the beginning of every Claude Code session:

```text
1. Read CLAUDE.md.
2. Read PROJECT_STATE.md.
3. Inspect git status.
4. Determine current phase.
5. Check required inputs.
6. Check whether prior work already satisfies the gate.
7. Report:
   - current phase
   - what is already complete
   - missing immediate prerequisites
   - what you can do now
8. Only then make edits.
```

At the end of every substantial task:

```text
1. Run tests/checks.
2. Update PROJECT_STATE.md.
3. Record changed files.
4. Record data/model counts.
5. Record unresolved issues.
6. State whether the phase is complete.
7. If complete, print the next-phase prerequisites.
8. Do not silently start the next phase.
```

---

# 21. PROJECT_STATE.md REQUIREMENTS

Maintain this file continuously.

Recommended structure:

```yaml
project: ChronosGraph

current_phase: 0

phase_status:
  phase_0: pending
  phase_1: pending
  phase_2: pending
  phase_3: pending
  phase_4: pending
  phase_5: pending
  phase_6: pending
  phase_7: pending
  phase_8: pending
  phase_9: pending
  phase_10: pending
  phase_11: pending
  phase_12: pending

human_inputs:
  research_scope: pending
  source_approval: pending
  source_access: pending
  gold_questions: pending
  annotation: pending
  colab_training: pending
  hindi_sources: pending
  final_evaluation: pending

artifacts:
  raw_corpus: pending
  manifest: pending
  processed_passages: pending
  extracted_claims: pending
  graph: pending
  baseline_results: pending
  annotation_dataset: pending
  trained_model: pending
  multilingual_dataset: pending
  final_results: pending
  api: pending
  frontend: pending

last_verified_commit: null
last_updated: null
```

Claude must update this only from verified repository evidence.

Do not mark a human-owned task complete merely because a file exists.

---

# 22. USER INPUT CHECKLIST

Whenever Claude reaches a gate, classify requirements as:

```text
ALREADY PROVIDED
ALREADY COMPLETED
NEEDED NOW
NEEDED LATER
NOT REQUIRED
```

Example:

```text
PHASE 1 PRE-CHECK

ALREADY PROVIDED
- historical window
- source categories

NEEDED NOW
- approved source identifiers for CAD

NEEDED LATER
- conflict annotation decisions
- Colab training configuration
- Hindi evaluation questions

NOT REQUIRED NOW
- frontend design
- production deployment
```

This is the required interaction pattern.

Do not overwhelm the user with future requirements before they are relevant.

---

# 23. HOW CLAUDE SHOULD ASK THE USER

When blocked:

Bad:

> We need more information about the entire project before proceeding.

Good:

> Phase 1 can start, but I am missing the approved CAD source identifier. Please provide or approve it. No training or frontend information is needed yet.

When a phase completes:

Good:

> Phase 1 is complete. Before Phase 2, please review the acquisition report and resolve the 3 source-quality flags below. Phase 2 does not require your training or Hindi decisions yet.

---

# 24. NO-SCOPE-DRIFT RULE

Do not add features because they are interesting.

Before adding a feature ask:

1. Does it support a research question?
2. Does it improve reproducibility?
3. Does it improve evidence/provenance?
4. Does it improve evaluation?
5. Is it necessary for the current user workflow?

If no, defer it.

Potentially deferred work:
- agents
- complex conversational memory
- unrelated automation
- decorative UI
- unnecessary model training
- unsupported source expansion
- additional databases without measurable benefit

---

# 25. CURRENT PROJECT PRIORITY

When in doubt, prioritize in this order:

```text
1. Research validity
2. Data quality
3. Provenance
4. Reproducibility
5. Evaluation
6. Model quality
7. Retrieval quality
8. Backend stability
9. Frontend polish
```

A visually impressive frontend must never take priority over a broken evaluation set.

---

# 26. MINIMUM ACCEPTANCE CRITERIA FOR THE FINISHED SYSTEM

The project is not considered research-complete until it can:

- answer historical questions using traceable evidence
- distinguish source claims from model-generated synthesis
- represent historical time explicitly
- identify and preserve genuine conflicting accounts
- classify conflict as recency-resolvable, permanently contested, unknown, or not actually contradictory
- expose exact supporting evidence
- provide explicit uncertainty
- compare against baseline systems
- report results on a frozen evaluation set
- demonstrate whether the trained classifier adds measurable value
- demonstrate multilingual behavior for English and Hindi
- reproduce official results from stored artifacts

---

# 27. FINAL RULE

The system should never hide uncertainty to appear more intelligent.

When evidence is insufficient:

```text
UNKNOWN
```

is acceptable.

When historical sources disagree:

```text
PERMANENTLY_CONTESTED
```

is a valid result.

When a newer source genuinely supersedes an older state:

```text
RESOLVABLE_BY_RECENCY
```

is valid.

When the supposed contradiction is not actually a contradiction:

```text
NOT_CONTRADICTION
```

is valid.

The research goal is not to make every question have one decisive answer.

The goal is to make the system **better at knowing what the evidence supports, what changed, what is disputed, and what remains unknown.**
