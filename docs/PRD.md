# Product Requirements Document

# The Lenny Growth Assistant

**Version:** 1.0
**Status:** MVP / Assessment Build
**Product:** The Lenny Growth Assistant

---

## 1. Product Overview

The Lenny Growth Assistant is an AI-powered product and growth intelligence application that enables product managers and growth leaders to retrieve actionable knowledge from Lenny's Podcast transcripts without manually searching through hundreds of hours of conversations.

The system combines retrieval-augmented generation (RAG), local and cloud language models, persistent conversations, source attribution, and a secure artifact-generation experience.

The product is designed around one core principle:

> **The assistant should be useful because it is grounded in evidence, not because it sounds confident.**

---

## 2. Problem Statement

Product managers frequently need practical answers to questions involving:

* Product strategy
* Growth
* Activation
* Retention
* Experimentation
* Product discovery
* Pricing
* Team building
* Product-led growth

Lenny's Podcast contains a large amount of relevant knowledge from experienced product leaders and growth practitioners. However, finding a specific insight often requires listening to or searching through long-form podcast content.

The Lenny Growth Assistant solves this discovery problem by turning the transcript archive into an interactive knowledge interface.

---

## 3. Target Persona

### Primary Persona — Growth/Product Manager

A product or growth professional who:

* Has limited time.
* Needs actionable answers rather than long-form browsing.
* Wants to understand how experienced operators approach product problems.
* Values evidence and source attribution.
* Wants to turn research into reusable frameworks and documents.

### Example Scenario

A Growth PM asks:

> "What are effective ways to improve activation?"

The assistant retrieves relevant transcript sections, generates a grounded answer, and attributes the underlying insights to the appropriate podcast episodes and guests.

The user can then transform the answer into a structured Ship 30 for 30-style essay or visual artifact.

---

## 4. Product Goals

### Primary Goals

1. Provide grounded answers based exclusively on the indexed Lenny's Podcast transcript corpus.
2. Provide transparent source attribution for retrieved knowledge.
3. Support local LLM inference through Ollama.
4. Support cloud LLM inference through a provider abstraction.
5. Stream model responses to provide immediate feedback.
6. Transform retrieved knowledge into actionable long-form content.
7. Render generated Markdown and HTML artifacts securely.
8. Persist conversations and generated artifacts.
9. Provide a reproducible Docker-based deployment.
10. Demonstrate production-oriented engineering practices.

### Non-Goals

The MVP will not attempt to:

* Answer arbitrary general-knowledge questions.
* Replace professional product strategy consulting.
* Infer facts that are absent from the transcript corpus.
* Train or fine-tune a language model.
* Build a general-purpose web search engine.
* Store or process private podcast content outside the permitted transcript corpus.

---

## 5. Core User Journey

```text
Open Application
       ↓
Create / Select Session
       ↓
Ask Product or Growth Question
       ↓
Generate Query Embedding
       ↓
Retrieve Relevant Transcript Chunks
       ↓
Evaluate Retrieval Confidence
       ↓
Build Grounded Prompt
       ↓
Select LLM Provider
       ↓
Stream Response
       ↓
Display Sources
       ↓
Optional: Generate Ship 30 Artifact
       ↓
Preview Artifact
```

---

## 6. Core Features

### 6.1 Grounded Question Answering

The assistant retrieves relevant transcript chunks before generating an answer.

Every substantive answer should provide source attribution in the format:

```text
[Episode: Guest Name, Timestamp/Topic]
```

If sufficient evidence cannot be retrieved, the assistant must explicitly state:

> I do not have sufficient information in Lenny's podcast archive to answer this reliably.

---

### 6.2 Source Attribution

Retrieved sources will expose:

* Episode title
* Guest
* Timestamp/topic reference
* Transcript excerpt
* Retrieval similarity score

Sources are displayed separately from the generated response to make the evidence chain easy to inspect.

---

### 6.3 Dual LLM Provider Layer

The application will support:

**Local**

* Ollama
* llama3.2:3b or another configured local model

**Cloud**

* OpenAI or Anthropic

Both providers implement a common asynchronous interface.

The RAG and application layers must remain independent of the selected model provider.

---

### 6.4 Ship 30 for 30 Content Engine

Users can transform retrieved insights into an approximately 1,250-word article.

The generated content should include:

* Curiosity-driven headline
* Strong opening hook
* Short paragraphs
* Markdown headings
* Bold anchor concepts
* Bullet lists
* Guest attribution
* Practical frameworks
* Actionable conclusion

The content must remain grounded in retrieved transcript evidence.

---

### 6.5 Artifact Viewer

The application supports two artifact types:

**Markdown**

Rendered using a Markdown renderer supporting GitHub-flavored Markdown.

**HTML**

Rendered in an isolated sandboxed iframe.

Generated HTML is considered untrusted content.

The iframe must use:

```text
sandbox="allow-scripts"
```

and must not grant `allow-same-origin`.

---

### 6.6 Conversation Persistence

Users can create and revisit sessions.

Each session stores:

* Session metadata
* User messages
* Assistant messages
* Sources
* Generated artifacts
* Timestamps

---

### 6.7 Streaming Responses

Responses should stream progressively rather than waiting for the complete LLM response.

The UI should communicate intermediate states such as:

```text
Retrieving transcripts...
Found 5 relevant sources.
Generating response...
```

---

## 7. Success Metrics

### Retrieval Citation Accuracy

**Target: ≥ 90%**

At least 90% of evaluated factual claims should be supported by retrieved transcript evidence.

---

### Local Inference Time to First Token

**Target: < 4 seconds**

Measured from completion of retrieval/prompt construction to the first generated token under the evaluation environment.

---

### Artifact Render Safety

**Target: 0 known XSS vulnerabilities**

Generated HTML must be isolated from the parent application using sanitization and a restricted iframe sandbox.

---

### Retrieval Relevance

The majority of top-K retrieved chunks should contain information directly useful for answering the user's question.

---

### System Availability

The application should gracefully handle unavailable dependencies rather than returning unhandled server errors.

---

## 8. Product Quality Principles

### Grounded Over Fluent

A cautious answer supported by evidence is preferable to a confident unsupported answer.

### Transparent Over Magical

Users should be able to inspect the sources behind an answer.

### Fast Feedback Over Silent Waiting

Streaming and intermediate status messages make model latency understandable.

### Secure By Default

Generated artifacts are treated as untrusted content.

### Provider Agnostic

Business logic must not depend on one LLM vendor.

---

## 9. Key Product Risks

| Risk                     | Impact               | Mitigation                               |
| ------------------------ | -------------------- | ---------------------------------------- |
| Poor retrieval           | Incorrect answers    | Similarity threshold + source inspection |
| LLM hallucination        | Loss of trust        | Strict grounding prompt                  |
| Local model limitations  | Lower answer quality | Provider abstraction + cloud fallback    |
| Slow local inference     | Poor UX              | Streaming + visible status               |
| Malicious generated HTML | XSS                  | Sanitization + sandboxed iframe          |
| Database unavailable     | Application failure  | Health checks + graceful errors          |
| Incomplete transcripts   | Knowledge gaps       | Explicit insufficient-evidence response  |

---

## 10. Trade-offs

### Local 3B/8B Model vs Cloud Model

Local inference provides:

* Privacy
* No per-request cloud cost
* Reproducible evaluation

However, smaller local models may have weaker reasoning and generation quality.

Cloud models provide stronger capabilities but introduce:

* API cost
* External dependency
* Network latency
* Credential management

Therefore the architecture uses a provider abstraction instead of coupling the product to either option.

---

### PostgreSQL + pgvector vs Dedicated Vector Database

PostgreSQL with pgvector was selected because:

* The corpus is moderate in size.
* Relational and vector data can coexist.
* It reduces infrastructure complexity.
* Docker deployment remains simple.
* PostgreSQL is already required for persistence.

A dedicated vector database can be introduced later if corpus size or query volume grows significantly.

---

## 11. MVP Definition

The MVP is considered complete when a user can:

1. Start the application with Docker Compose.
2. Create a session.
3. Ask a product/growth question.
4. Retrieve transcript evidence.
5. Receive a streamed grounded response.
6. Inspect citations.
7. Switch between local and cloud providers.
8. Generate a Ship 30-style article.
9. Preview a Markdown or HTML artifact.
10. Restart the application without losing persisted conversations.
11. Query the health endpoint.
12. Run the automated test suite.

---

## 12. Future Opportunities

Potential future versions could add:

* Episode browsing
* Semantic source search
* Saved frameworks
* Team workspaces
* User authentication
* Evaluation dashboards
* Retrieval feedback loops
* Query rewriting
* Hybrid keyword + vector retrieval
* RAG evaluation datasets
* Automated citation verification
* Model quality benchmarking

These capabilities are intentionally outside the MVP scope.

