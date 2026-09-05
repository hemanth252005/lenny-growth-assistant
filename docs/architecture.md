# Architecture Specification

# The Lenny Growth Assistant

**Version:** 1.0

---

## 1. Architecture Overview

The Lenny Growth Assistant uses a layered architecture separating presentation, API orchestration, retrieval, AI provider integration, persistence, and content-generation skills.

```text
┌──────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                       │
│                                                              │
│ Chat │ Sessions │ Sources │ Model Selector │ Artifact Viewer │
└───────────────────────────────┬──────────────────────────────┘
                                │
                         HTTP / SSE
                                │
┌───────────────────────────────▼──────────────────────────────┐
│                         FastAPI API                           │
│                                                              │
│ Sessions │ Chat │ Health │ Artifact APIs                     │
└───────────────┬───────────────────────┬───────────────────────┘
                │                       │
                ▼                       ▼
       ┌────────────────┐       ┌────────────────────┐
       │   RAG Layer    │       │  Skill Layer       │
       │                │       │                    │
       │ Embeddings     │       │ Ship 30            │
       │ Retrieval      │       │ Artifact Generator │
       │ Thresholding   │       │                    │
       └───────┬────────┘       └─────────┬──────────┘
               │                          │
               ▼                          ▼
       ┌──────────────────────────────────────────┐
       │              Provider Layer              │
       │                                          │
       │     Ollama       │       Cloud           │
       └──────────────────────────────────────────┘
               │
               ▼
       ┌──────────────────────────────────────────┐
       │        PostgreSQL + pgvector             │
       │                                          │
       │ Sessions │ Messages │ Artifacts          │
       │ Transcript Chunks + Embeddings            │
       └──────────────────────────────────────────┘
```

---

## 2. Architectural Principles

### Separation of Concerns

Each layer has a single primary responsibility.

### Provider Independence

Application logic must not directly depend on Ollama, OpenAI, or Anthropic APIs.

### Evidence First

The RAG pipeline runs before answer generation.

### Secure Rendering

Generated HTML is untrusted and must remain isolated from the application origin.

### Operational Simplicity

PostgreSQL and pgvector are preferred over additional infrastructure for the initial corpus size.

---

## 3. Frontend Architecture

The frontend uses Next.js with TypeScript and Tailwind CSS.

### Main Responsibilities

* Render chat interface
* Maintain active session
* Display streaming assistant responses
* Display retrieval sources
* Select model provider
* Select generation mode
* Render artifacts
* Handle API errors
* Provide responsive layout

### Main Components

```text
src/
├── app/
├── components/
│   ├── Chat/
│   ├── Artifact/
│   ├── Sources/
│   ├── Sidebar/
│   └── UI/
├── hooks/
├── lib/
└── types/
```

---

## 4. Backend Architecture

FastAPI acts as the application orchestration layer.

### API Responsibilities

* Request validation
* Authentication boundary for future versions
* Session management
* RAG orchestration
* Provider selection
* Streaming
* Error handling
* Health reporting

---

## 5. Data Model

### Session

```text
Session
├── id UUID
├── title
├── created_at
└── updated_at
```

### Message

```text
Message
├── id UUID
├── session_id UUID
├── role
├── content
├── sources JSONB
└── created_at
```

### Artifact

```text
Artifact
├── id UUID
├── message_id UUID
├── artifact_type
└── content
```

### Transcript Chunk

```text
TranscriptChunk
├── id UUID
├── episode_title
├── guest_name
├── publication_date
├── timestamp_ref
├── chunk_text
├── embedding vector(384)
└── metadata JSONB
```

---

## 6. pgvector Strategy

The initial embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model generates 384-dimensional vectors.

Similarity is calculated using cosine distance.

Conceptually:

```text
similarity = 1 - cosine_distance(query, document)
```

Retrieval:

```text
Query
 ↓
Embedding
 ↓
pgvector cosine similarity
 ↓
Sort descending
 ↓
Apply threshold
 ↓
Top K
```

Default:

```text
K = 5
threshold = 0.65
```

These values remain configurable.

---

## 7. Transcript Ingestion

The ingestion pipeline is:

```text
Transcript Archive
       ↓
Parse Metadata
       ↓
Clean Transcript
       ↓
Split into Chunks
       ↓
Generate Embeddings
       ↓
Persist in PostgreSQL
       ↓
Build HNSW Index
```

### Chunking

Target:

```text
500–800 tokens
100-token overlap
```

Chunk boundaries should prefer semantic boundaries where possible.

---

## 8. Retrieval Pipeline

```text
User Query
     ↓
Normalize Query
     ↓
Generate Embedding
     ↓
Vector Search
     ↓
Top K Candidates
     ↓
Similarity Threshold
     ↓
Context Assembly
     ↓
Grounded Prompt
```

If zero chunks exceed the configured threshold, generation should not proceed normally.

The system returns an insufficient-evidence response.

---

## 9. Prompt Construction

The model receives:

```text
System Instructions
+
Retrieved Transcript Context
+
Conversation History
+
Current User Query
```

The system prompt explicitly instructs the model:

1. Use only supplied transcript context for factual claims.
2. Do not invent sources.
3. Attribute insights to the correct guest/episode.
4. Acknowledge insufficient evidence.
5. Keep answers actionable.
6. Preserve citation references.

---

## 10. Provider Architecture

All providers implement:

```python
class BaseLLMProvider:
    async def generate_response(...):
        ...

    async def stream_response(...):
        ...
```

Implementations:

```text
providers/
├── base.py
├── ollama_provider.py
└── cloud_provider.py
```

Provider selection occurs at runtime.

```text
Request
  │
  ├── provider = ollama → OllamaProvider
  │
  └── provider = cloud  → CloudProvider
```

The RAG layer does not know which provider is being used.

---

## 11. Streaming Architecture

FastAPI returns Server-Sent Events.

Example event:

```json
{
  "type": "token",
  "content": "Activation"
}
```

Other event types:

```text
status
sources
token
artifact
error
done
```

This allows the frontend to progressively construct the response.

---

## 12. Ship 30 Skill Architecture

The Ship 30 capability is implemented as a dedicated skill rather than mixing writing instructions into the retrieval layer.

```text
Retrieved Context
       ↓
Ship 30 Prompt
       ↓
LLM Provider
       ↓
Structured Markdown
       ↓
Artifact
```

The skill enforces:

* Hook
* Curiosity gap
* Short paragraphs
* Headers
* Bold anchors
* Guest attribution
* Actionable framework
* Approximately 1,250 words

---

## 13. Artifact Architecture

Artifacts have two supported representations.

### Markdown

```text
LLM
 ↓
Markdown
 ↓
react-markdown
 ↓
UI
```

### HTML

```text
LLM
 ↓
HTML
 ↓
DOMPurify
 ↓
sandboxed iframe
 ↓
Preview
```

The iframe uses:

```text
sandbox="allow-scripts"
```

and intentionally does not include:

```text
allow-same-origin
```

This prevents generated content from sharing the application's origin.

---

## 14. API Contracts

### POST `/api/sessions`

Creates a session.

### GET `/api/sessions/{session_id}`

Returns session metadata and messages.

### POST `/api/chat`

Starts a streaming chat request.

Request:

```json
{
  "session_id": "uuid",
  "message": "How can I improve activation?",
  "mode": "default",
  "provider": "ollama"
}
```

### GET `/api/health`

Returns dependency status.

Example:

```json
{
  "status": "healthy",
  "database": "healthy",
  "ollama": "healthy",
  "vector_index": "ready"
}
```

---

## 15. Error Handling

The backend handles:

* Invalid request bodies
* Unknown providers
* Missing sessions
* Database failures
* Embedding failures
* LLM timeouts
* Ollama unavailable
* Cloud API failures
* Empty retrieval results

Errors should be returned using consistent JSON structures.

---

## 16. Observability

Structured logging captures:

* Request ID
* Endpoint
* Retrieval latency
* Number of retrieved chunks
* Provider
* Model
* LLM latency
* Error category

Example:

```text
INFO retrieval.completed
query="activation"
chunks=5
latency_ms=183
```

---

## 17. Deployment Architecture

Docker Compose manages:

```text
┌──────────────┐
│ PostgreSQL   │
│ + pgvector   │
└──────┬───────┘
       │
┌──────▼───────┐
│   FastAPI    │
└──────┬───────┘
       │
┌──────▼───────┐
│   Next.js    │
└──────────────┘
```

Ollama can run locally on the host or as an optional service depending on hardware and deployment environment.

---

## 18. Configuration

Configuration is supplied through environment variables.

Examples:

```text
DATABASE_URL
OLLAMA_BASE_URL
OLLAMA_MODEL
DEFAULT_LLM_PROVIDER
OPENAI_API_KEY
ANTHROPIC_API_KEY
EMBEDDING_MODEL
RETRIEVAL_TOP_K
RETRIEVAL_THRESHOLD
```

Secrets must never be committed to source control.

---

## 19. Testing Strategy

### Unit Tests

* Provider selection
* Prompt construction
* Chunking
* Retrieval threshold
* Artifact parsing

### Integration Tests

* PostgreSQL retrieval
* Session persistence
* Chat API
* Health API

### Security Tests

* Artifact sanitization
* iframe sandbox configuration
* malformed input handling

---

## 20. Architectural Trade-offs

### Why PostgreSQL + pgvector?

Minimizes infrastructure while supporting both relational persistence and semantic retrieval.

### Why SSE?

Simple browser-compatible streaming that works well with FastAPI.

### Why provider abstraction?

Prevents vendor lock-in and satisfies local/cloud evaluation requirements.

### Why an iframe?

Provides a clear security boundary for generated HTML artifacts.

### Why not a microservice architecture?

The corpus and expected evaluation traffic do not justify the operational complexity of multiple backend services.

---

## 21. Future Scaling

If corpus size or traffic grows significantly, the architecture can evolve toward:

* Dedicated vector infrastructure
* Redis caching
* Background ingestion workers
* Queue-based generation
* Horizontal API scaling
* Dedicated model gateway
* RAG evaluation service

The current architecture intentionally keeps these concerns out of the MVP.

