# Product Design Specification

# The Lenny Growth Assistant

**Version:** 1.0

---

## 1. Design Vision

The interface should feel like a modern AI workspace rather than a traditional chatbot.

The design prioritizes:

* Focus
* Evidence
* Speed
* Trust
* Discoverability
* Artifact creation

The visual hierarchy should make the conversation primary while keeping sources and generated artifacts immediately accessible.

---

## 2. Application Layout

The desktop interface uses a two-pane workspace.

```text
┌────────────────────────────────────────────────────────────┐
│ Header                                                     │
├───────────────────────────────┬────────────────────────────┤
│                               │                            │
│       Conversation            │       Artifact             │
│                               │                            │
│       Chat messages           │       Preview              │
│                               │                            │
│                               │                            │
├───────────────────────────────┴────────────────────────────┤
│ Composer                                                   │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Left Pane — Conversation

The conversation pane contains:

### Header

* Product identity
* Current model
* Connection state
* Session controls

### Message Area

Messages are visually separated by role.

User messages should be concise and visually distinct.

Assistant messages support:

* Markdown
* Code blocks
* Citations
* Sources
* Streaming state

### Composer

The composer contains:

* Multi-line input
* Send button
* Mode selector
* Provider selector

---

## 4. Right Pane — Artifact Workspace

The artifact pane is collapsible.

It contains:

* Artifact title
* Artifact type
* Preview
* Source/content toggle where appropriate
* Close/collapse control

Example:

```text
┌─────────────────────────────────────┐
│ Activation Framework     HTML       │
├─────────────────────────────────────┤
│                                     │
│          ARTIFACT PREVIEW           │
│                                     │
│                                     │
└─────────────────────────────────────┘
```

---

## 5. Responsive Behavior

### Desktop

Two-pane layout.

### Tablet

Conversation receives approximately 60% width while artifact panel receives approximately 40%.

### Mobile

Only one pane is visible at a time.

The artifact viewer opens as a full-screen overlay or drawer.

---

## 6. Session Sidebar

The sidebar provides:

* New session
* Recent sessions
* Session titles
* Active session indicator

Sessions are grouped by recency.

Example:

```text
RECENT

Today
  Activation strategy
  Retention tactics

Yesterday
  Growth loops
  Product discovery
```

---

## 7. Model Selector

The model selector communicates both provider and model.

Example:

```text
🦙 Ollama
llama3.2:3b
```

Cloud:

```text
☁ Cloud
Configured model
```

The selected provider should remain visible during generation.

---

## 8. Generation States

The interface has explicit states.

### Idle

```text
Ask Lenny anything...
```

### Retrieving

```text
Searching Lenny's transcripts...
```

### Retrieved

```text
Found 5 relevant sources
```

### Generating

```text
Generating with Ollama...
```

### Complete

Response and sources are displayed.

### Error

The UI provides a human-readable recovery action.

---

## 9. Source Presentation

Sources appear beneath the relevant response.

Example:

```text
Sources

┌──────────────────────────────────────┐
│ Brian Chesky                         │
│ Product Strategy                     │
│ 23:14                                │
│                                      │
│ "Relevant transcript excerpt..."     │
│                                      │
│ Relevance 92%                        │
└──────────────────────────────────────┘
```

Sources should never visually overwhelm the generated answer.

---

## 10. Retrieval Confidence

A lightweight grounding indicator can communicate retrieval strength.

Example:

```text
Grounding
█████████░ 91%
5 sources
```

The UI must not represent this as a guarantee of answer correctness.

The tooltip should explain:

> Retrieval score reflects similarity between the question and indexed transcript passages. It is not a probability that the answer is correct.

---

## 11. Ship 30 Mode

The mode selector should make the difference between answering and writing obvious.

```text
Ask
Write
```

### Ask

Optimized for concise, practical answers.

### Write

Optimized for the Ship 30 for 30 format.

The writing mode displays an approximate target:

```text
~1,250 words
```

---

## 12. Artifact Detection

The backend or frontend detects artifact blocks such as:

```text
<artifact type="html" title="Activation Framework">
...
</artifact>
```

The artifact is removed from the normal assistant text and displayed in the artifact workspace.

Supported types:

```text
markdown
html
```

Unknown artifact types should not be executed.

---

## 13. Artifact Security

Generated HTML is untrusted.

Processing:

```text
Generated HTML
      ↓
Sanitization
      ↓
Sandboxed iframe
```

Iframe:

```html
<iframe sandbox="allow-scripts">
```

`allow-same-origin` is intentionally omitted.

The generated document therefore cannot access the application's origin, cookies, local storage, or parent DOM.

---

## 14. Visual Language

The interface should use:

* High contrast typography
* Restrained color palette
* Rounded cards
* Subtle borders
* Minimal shadows
* Generous spacing
* Clear hover states

The UI should feel sophisticated without becoming visually noisy.

---

## 15. Accessibility

The application should provide:

* Semantic HTML
* Keyboard navigation
* Visible focus states
* Accessible button labels
* Appropriate ARIA attributes
* Sufficient color contrast
* Screen-reader-friendly status messages

Streaming status should use an appropriate live region.

---

## 16. Empty State

When no conversation exists:

```text
What are you trying to solve?

Ask about:

Product strategy
Growth
Activation
Retention
Experimentation
Product discovery
```

Example prompts can be displayed as quick-start buttons.

---

## 17. No-Evidence State

When retrieval produces insufficient evidence:

```text
No strong evidence found

I couldn't find sufficient information in
Lenny's Podcast archive to answer this reliably.

Try asking about product, growth, retention,
experimentation, or strategy.
```

This is intentionally different from a generic error state.

---

## 18. Error State

For infrastructure failures:

```text
Something went wrong

The local model isn't reachable.

Try:
• Starting Ollama
• Switching providers
• Retrying the request
```

The UI should never expose raw stack traces.

---

## 19. Interaction Principles

### Immediate Feedback

Every action should produce visible feedback.

### Progressive Disclosure

Advanced information such as raw source excerpts should be available without overwhelming the primary response.

### Trust Through Evidence

Sources are always visually connected to the answer.

### Recovery Over Failure

Every recoverable error provides a next action.

---

## 20. Motion

Animations should be subtle.

Recommended:

* Streaming cursor
* Source card reveal
* Artifact panel transition
* Sidebar transitions

Avoid excessive animations that distract from reading.

---

## 21. Performance

The frontend should:

* Stream responses.
* Avoid unnecessary re-renders.
* Lazy-render large artifacts.
* Limit expensive Markdown processing.
* Keep artifact previews isolated.

---

## 22. Design Success Criteria

The design is successful when a new user can:

1. Understand what the product does within seconds.
2. Ask a question without instructions.
3. See that the answer is grounded in podcast sources.
4. Identify the active model provider.
5. Switch between Ask and Write modes.
6. Understand when an artifact has been generated.
7. Recover from model or retrieval failures.
8. Use the interface comfortably on desktop and mobile.

