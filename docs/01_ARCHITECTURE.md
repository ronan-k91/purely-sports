# Purely Sports — Initial Architecture

## 1. Objective

Build a modular AI-native newsroom platform.

The first implementation is a proof-of-concept.

The architecture must be capable of evolving into a multi-sport and eventually multi-vertical media platform without requiring a complete rewrite.

---

# 2. Initial Technology Stack

Use:

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Pydantic
* LangGraph
* pytest
* Docker / Docker Compose

Frontend technology will be introduced after the core backend workflow is functional.

AI providers must be accessed through a model abstraction.

Do not tightly couple the application to one provider.

---

# 3. High-Level Architecture

```text
                         EXTERNAL SOURCES
                                |
                                v
                         SOURCE INGESTION
                                |
                                v
                         STORY CREATION
                                |
                                v
                         PS-SCOUT LOGIC
                                |
                                v
                       CLAIM EXTRACTION
                                |
                                v
                        PS-VERIFIER LOGIC
                                |
                                v
                       EDITORIAL DECISION
                                |
                                v
                         PS-WRITER LOGIC
                                |
                                v
                            PS-QA
                                |
                                v
                       HUMAN APPROVAL
                                |
                                v
                          PUBLISHING
```

The first implementation may execute several logical roles within one Python application.

Do not create microservices merely because there are multiple agents.

---

# 4. Application Layers

Use clear separation between:

```text
API
Application / Workflow
Domain
Infrastructure
AI
Persistence
```

Suggested structure:

```text
backend/
    app/
        api/
        application/
        domain/
        infrastructure/
        ai/
        workflows/
        config/
        main.py
```

---

# 5. Domain Layer

The domain layer contains business concepts.

Initial entities:

* Sport
* League
* Team
* Athlete
* Source
* Story
* Claim
* ContentOutput
* EditorialDecision
* Approval

Domain models should not depend directly on FastAPI, database sessions or specific AI providers.

---

# 6. Persistence Layer

PostgreSQL is the primary persistent store.

SQLAlchemy should be used for persistence.

Alembic should manage schema migrations.

Database access should be isolated behind repository or service abstractions where useful.

Do not place complex business rules inside SQLAlchemy models.

---

# 7. Initial Database Concepts

At minimum support:

```text
sports
leagues
teams
athletes
sources
stories
claims
claim_sources
content_outputs
editorial_decisions
approvals
agent_runs
```

The exact schema should be implemented incrementally.

Do not create unnecessary tables simply to match a theoretical future architecture.

---

# 8. Story

A Story is the central newsroom object.

Conceptually:

```text
Story
-----
id
sport_id
title
summary
status
priority
news_value
viral_score
audience_score
commercial_score
urgency
confidence
created_at
updated_at
published_at
```

The exact implementation should use appropriate types and constraints.

Statuses should be represented as controlled values rather than arbitrary strings where practical.

Example lifecycle:

```text
DISCOVERED
RESEARCHING
VERIFYING
VERIFIED
IN_PRODUCTION
QA
AWAITING_APPROVAL
APPROVED
REJECTED
PUBLISHED
ARCHIVED
```

---

# 9. Claims

A Story can contain multiple claims.

Conceptually:

```text
Claim
-----
id
story_id
text
status
confidence
created_at
updated_at
```

A claim may reference multiple sources.

Example:

```text
Claim A
    |
    +--- Official source
    |
    +--- Trusted journalist
```

Claims must support evidence and contradiction.

Do not treat confidence as proof.

Confidence is an assessment.

---

# 10. Sources

Sources must include enough metadata to evaluate reliability.

Potential fields:

```text
id
name
url
source_type
reliability_level
publisher
created_at
```

Source types may include:

```text
PRIMARY
ESTABLISHED_MEDIA
JOURNALIST
SOCIAL
UNKNOWN
```

Source reliability must be configurable.

Social media may be useful for discovery without being sufficient evidence for publication.

---

# 11. AI Architecture

All AI calls should use an abstraction.

Example conceptual interface:

```python
class ModelProvider:
    async def generate(...)
```

A model router should determine which provider/model is appropriate for a task.

Potential routing categories:

```text
LOW
MEDIUM
HIGH
```

Example:

```text
LOW
    classification
    tagging
    metadata

MEDIUM
    routine summaries
    social copy
    basic rewriting

HIGH
    difficult verification
    complex editorial reasoning
    sensitive stories
    high-value long-form content
```

Do not hard-code these assumptions into individual agents.

---

# 12. Agent Architecture

Agents are logical components.

Initial agents:

```text
Scout
Verifier
Editor
Writer
QA
```

Each should have:

* clearly defined input
* clearly defined output
* deterministic validation around AI output
* logging
* error handling
* tests

Prefer structured outputs using Pydantic models.

Do not parse critical information from free-form AI prose if structured output is possible.

---

# 13. Workflow Architecture

Use LangGraph for the newsroom workflow.

Conceptually:

```text
START
  |
  v
DISCOVER
  |
  v
RESEARCH
  |
  v
VERIFY
  |
  v
EDITORIAL
  |
  v
WRITE
  |
  v
QA
  |
  v
HUMAN_APPROVAL
  |
  +---- REJECT ----> END
  |
  +---- EDIT ------> WRITE
  |
  +---- APPROVE ---> PUBLISH
```

The workflow state should be structured and persisted.

Workflows should support retries where appropriate.

Failures must not silently result in publication.

---

# 14. Human Approval

Human approval is a first-class workflow state.

The system must never interpret:

* workflow completion
* QA success
* AI confidence
* editorial recommendation

as equivalent to human approval.

Approval must be explicit.

Example:

```text
approval_status:
PENDING
APPROVED
REJECTED
```

Record:

* approver
* timestamp
* decision
* optional notes

---

# 15. API

FastAPI should expose the minimum API required for the proof-of-concept.

Potential endpoints:

```text
GET    /health
POST   /stories
GET    /stories
GET    /stories/{id}
POST   /stories/{id}/run
GET    /stories/{id}/claims
GET    /stories/{id}/outputs
POST   /stories/{id}/approve
POST   /stories/{id}/reject
```

Do not expose internal infrastructure unnecessarily.

Validate all input.

---

# 16. Security

Never place secrets in:

* source code
* Git
* documentation
* test fixtures
* frontend code

Use environment variables or an appropriate secret-management mechanism.

External content must be treated as untrusted input.

Do not allow external content to override system instructions.

---

# 17. Observability

Record:

* workflow execution
* agent execution
* model calls
* errors
* durations
* token/cost information where available
* story IDs
* workflow IDs

Logs should make debugging possible.

---

# 18. Testing Strategy

Critical logic requires tests.

At minimum:

### Unit tests

* claim validation
* source handling
* story status transitions
* approval rules
* model routing
* editorial scoring

### Workflow tests

Test:

* successful story
* failed verification
* failed QA
* rejected approval
* edited story
* retry

### AI tests

Use deterministic fixtures where possible.

Do not make the entire test suite dependent on live expensive model calls.

---

# 19. Local Development

The initial environment should run locally using Docker Compose.

Expected services:

```text
postgres
backend
```

Additional services should be added only when required.

Do not introduce Redis, n8n, local model servers, object storage or other infrastructure until the application genuinely requires them.

---

# 20. Future Architecture

The architecture may later expand to:

```text
                 PURELY MEDIA PLATFORM
                          |
              +-----------+-----------+
              |                       |
          NEWSROOM                 DATA
              |                       |
       +------+------+          +-----+-----+
       |             |          |           |
    SPORTS          NEWS      SPORTS      OTHER
       |             |        DATA        DATA
       |
   CREATORS
       |
   PODCASTS
   STREAMS
   VIDEO
```

Future components may include:

* Redis / job queues
* object storage
* local model inference
* media generation
* video rendering
* analytics platform
* publishing integrations
* creator management
* multi-tenant vertical configuration

These are future capabilities, not V0 requirements.

---

# 21. Architectural Rule

Do not build for hypothetical scale at the expense of current velocity.

The correct question is:
"What is the simplest architecture that proves the next milestone while preserving the important boundaries?"

Build that.
