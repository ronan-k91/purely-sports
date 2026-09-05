# Purely Sports — V0 Implementation Plan

**Status:** V0 — Implementation Plan
**Purpose:** Define the controlled engineering sequence for building the Purely Sports V0 system.

---

# 1. Purpose

This document defines how the approved Purely Sports product and architecture will be implemented.

It is an **implementation plan**, not a replacement for the product or architecture documents.

The implementation must remain consistent with:

1. `docs/00_PROJECT_VISION.md`
2. `docs/01_ARCHITECTURE.md`
3. `docs/02_DATABASE_SCHEMA.md`
4. `docs/03_IMPLEMENTATION_PLAN.md`
5. `.github/copilot-instructions.md`

The project vision defines the product direction.

The architecture defines the system architecture and workflow.

The database schema is the authoritative database contract.

This implementation plan defines the order in which those approved decisions are built.

If these documents ever appear to conflict, implementation must stop and the conflict must be resolved explicitly rather than guessed.

---

# 2. V0 Engineering Objective

Build the smallest complete Purely Sports newsroom loop:

```text
DISCOVER
    ↓
RESEARCH
    ↓
VERIFY
    ↓
EDITORIAL
    ↓
WRITE
    ↓
QA
    ↓
HUMAN APPROVAL
    ↓
PUBLISH
```

The first end-to-end content type is an **ARTICLE**.

The system must preserve:

* source provenance
* structured claims
* evidence
* verification state
* editorial decisions
* content versions
* QA results
* human approval
* publication records
* auditability

throughout the workflow.

The goal is not to build a complete media company platform immediately.

The goal is to prove the core Purely Sports operating model.

---

# 3. Core Engineering Principles

## 3.1 Database as System of Record

PostgreSQL is the authoritative store for critical business state.

A workflow engine, agent runtime, API request, or in-memory object must not become the sole source of truth for:

* stories
* claims
* verification
* content versions
* approvals
* publication state
* audit records

---

## 3.2 Human Approval Is a First-Class Boundary

AI may discover, research, verify, recommend, write, and perform QA.

AI must not independently approve or publish content.

Publication must require valid human approval for the exact content version being published.

---

## 3.3 Claims Are First-Class Data

Important factual statements must be represented as structured claims.

Writers must not treat arbitrary research text as verified fact.

Content must be traceable through:

```text
CONTENT OUTPUT
    ↓
CONTENT CLAIM
    ↓
CLAIM
    ↓
EVIDENCE
    ↓
SOURCE OBSERVATION
    ↓
SOURCE
```

---

## 3.4 Confidence Is Not Proof

Confidence is an assessment.

Verification status is authoritative.

The implementation must never treat a high confidence score as equivalent to verification.

---

## 3.5 Historical Traceability

Content versions must preserve the factual basis used to create them.

Where the database schema defines claim snapshots in `content_claims`, those snapshots must be implemented and tested.

A later modification to a canonical claim must not silently rewrite the factual representation of an already-created content version.

---

## 3.6 Application Rules Must Be Enforced in Code

AI recommendations are not business rules.

Critical rules must be enforced by application/domain code, including:

* publication requirements
* approval requirements
* content-version validity
* workflow transitions
* claim eligibility
* entity subtype consistency
* publication idempotency
* AI publication prohibition

---

## 3.7 External Content Is Untrusted

Source content, retrieved webpages, feeds, social content, and AI-generated text are untrusted inputs.

External content must never override application instructions, system rules, security controls, or publication requirements.

---

## 3.8 Keep V0 Simple

V0 should be a simple single application.

Do not introduce:

* microservices
* Kubernetes
* event buses
* distributed workflow infrastructure
* premature queues
* unnecessary caching
* complex service meshes
* speculative abstractions

unless a concrete approved requirement makes them necessary.

---

# 4. V0 Scope

The initial implementation must support the foundations required for:

```text
Source
    ↓
Source Observation
    ↓
Story
    ↓
Claims
    ↓
Evidence
    ↓
Verification
    ↓
Editorial Decision
    ↓
Article Content Version
    ↓
QA
    ↓
Human Approval
    ↓
Publication
```

The first engineering milestone does **not** require the complete newsroom agent system.

The first milestone establishes the application and database foundation on which that system will be built.

---

# 5. Implementation Phases

## Phase 1 — Project Foundation

Create the basic Python application foundation.

Expected work:

* Python 3.12+ project
* project/package structure
* dependency management
* FastAPI application entry point
* configuration/settings management
* environment variable handling
* PostgreSQL connection configuration
* SQLAlchemy configuration
* Alembic configuration
* structured logging foundation
* basic error-handling foundation
* health-check endpoint
* Dockerfile
* Docker Compose development environment
* `.env.example`
* pytest foundation
* basic linting/formatting configuration
* basic type-checking configuration where appropriate
* development README/setup instructions

Phase 1 must not implement newsroom agents.

Phase 1 must not implement the full workflow.

Phase 1 must not introduce additional business entities.

### Phase 1 Definition of Done

A new developer must be able to:

1. clone the repository
2. configure the environment using documented steps
3. start PostgreSQL
4. start the application
5. connect the application to PostgreSQL
6. run the test suite
7. run configured quality checks
8. receive a successful health response

The project must work from a clean development environment without undocumented manual steps.

---

# 6. Phase 2 — SQLAlchemy Database Models

Implement the SQLAlchemy models defined by:

`docs/02_DATABASE_SCHEMA.md`

The database schema is authoritative.

Do not add speculative tables or fields.

Do not remove required tables or fields.

Do not change relationships without an explicit architecture/schema decision.

---

## 6.1 Model Implementation Order

Implement models in dependency order:

1. `sports`
2. `entities`
3. `leagues`
4. `teams`
5. `athletes`
6. `sources`
7. `source_observations`
8. `stories`
9. `story_source_observations`
10. `claims`
11. `evidence`
12. `story_entities`
13. `events`
14. `story_events`
15. `editorial_decisions`
16. `content_outputs`
17. `content_claims`
18. `agent_runs`
19. `qa_reviews`
20. `approvals`
21. `publication_records`

---

## 6.2 Model Requirements

SQLAlchemy models must accurately represent:

* primary keys
* foreign keys
* nullable/non-nullable fields
* unique constraints
* indexes
* relationships
* timestamps
* status fields
* JSON/JSONB fields
* database-level checks where specified

Models should use SQLAlchemy 2.x conventions appropriate to the approved technology stack.

Do not introduce unnecessary ORM complexity.

---

# 7. Domain Model vs API Schema vs Database Model

These concepts must remain separate.

## Database Models

Represent persistence and relationships.

Example:

```text
app/models/
```

## API Schemas

Represent validated API request/response structures.

Example:

```text
app/schemas/
```

## Domain Services

Represent business rules and application invariants.

Example:

```text
app/services/
```

Do not place critical business rules exclusively inside:

* FastAPI route handlers
* Pydantic models
* SQLAlchemy relationship definitions
* agent prompts

Critical rules must be enforceable through application/domain services.

---

# 8. Phase 3 — Alembic Migration

After the SQLAlchemy model layer has been reviewed, create the initial Alembic migration representing the approved V0 schema.

The migration must:

* create tables in dependency order
* create foreign keys
* create required indexes
* create database-level check constraints where specified
* preserve required uniqueness constraints
* use the correct PostgreSQL types
* be reproducible
* run successfully against an empty PostgreSQL database

The migration must not contain speculative schema additions.

---

## 8.1 Migration Verification

A clean database must be able to go from:

```text
empty PostgreSQL database
        ↓
alembic upgrade head
        ↓
complete V0 schema
```

The resulting database must match the approved schema.

Where practical, downgrade behaviour must also be tested.

---

# 9. Phase 4 — Database Tests

Create tests covering both persistence behaviour and application-level invariants.

Tests should cover:

### Structural Rules

* primary keys
* foreign keys
* required fields
* uniqueness
* relationships
* indexes where testable
* database check constraints

### Data Rules

* score ranges
* confidence ranges
* claim sequence requirements
* version numbering
* valid statuses
* timestamp behaviour

### Entity Rules

* generic entity creation
* subtype relationships
* entity subtype/entity type consistency

### Provenance

Test:

```text
Evidence
    ↓
Source Observation
    ↓
Source
```

and ensure evidence does not require redundant direct source ownership.

### Content Versioning

Test:

* multiple content versions
* version numbering
* claim associations
* historical claim snapshots

### Approval

Test:

* approval attached to exact content version
* approval does not automatically transfer to another version
* approval identity is recorded correctly
* invalid approval states are rejected

### Publication

Test:

* publication requires valid approval
* publication requires required QA
* rejected content cannot publish
* superseded content cannot publish
* duplicate publication is prevented according to the approved idempotency rule

---

# 10. Phase 5 — Domain Models and Services

After the database foundation is stable, implement domain/application services.

Expected service areas:

* source service
* source observation service
* story service
* claim service
* evidence service
* verification service
* editorial decision service
* content service
* QA service
* approval service
* publication service

Services must enforce application-level invariants.

API routes and agents must use these services rather than directly manipulating critical state in ways that bypass business rules.

---

# 11. Transaction Boundaries

Transactions must be explicit.

Operations that modify related pieces of authoritative business state should execute within appropriate database transactions.

Examples include:

```text
Create/Update Story
    +
Create Claims
    +
Attach Evidence
```

and:

```text
Create Content Version
    +
Attach Content Claims
```

and:

```text
Record Approval
    +
Update relevant workflow state
```

and:

```text
Publish Content
    +
Create Publication Record
```

The exact transaction boundaries may be refined during implementation, but critical state changes must not be left to accidental session behaviour.

---

# 12. Phase 6 — API Foundation

Create the initial FastAPI API around controlled domain operations.

Initial API areas may include:

* sources
* source observations
* stories
* claims
* evidence
* editorial decisions
* content outputs
* QA reviews
* approvals
* publication records

API design should remain minimal.

Do not expose unrestricted database CRUD merely because a table exists.

API operations should correspond to legitimate application/domain actions.

---

# 13. Phase 7 — Newsroom Workflow

Implement the approved V0 newsroom workflow:

```text
START
 ↓
DISCOVER
 ↓
RESEARCH
 ↓
VERIFY
 ↓
EDITORIAL
 ↓
WRITE
 ↓
QA
 ↓
HUMAN_APPROVAL
 ↓
PUBLISH
```

The workflow engine may coordinate execution.

It must not become the sole source of critical business state.

The database remains authoritative.

Workflow transitions must be validated.

Invalid transitions must fail safely.

---

# 14. Phase 8 — Agents

Implement the six logical newsroom responsibilities:

1. `PS-NEWSROOM`
2. `PS-SCOUT`
3. `PS-VERIFIER`
4. `PS-EDITOR`
5. `PS-WRITER`
6. `PS-QA`

These are logical responsibilities, not microservices.

Agents should operate through controlled application services.

---

## 14.1 Agent Rules

Agents must:

* receive clearly defined inputs
* produce structured outputs where appropriate
* record meaningful execution information
* respect verification state
* respect workflow state
* respect human approval boundaries
* fail safely
* avoid directly bypassing domain services

Agents must not:

* approve content
* publish content
* override verification
* convert uncertainty into fact
* use rejected claims as factual support
* modify critical records without the appropriate application pathway

---

# 15. LangGraph

LangGraph should be introduced when the workflow/agent implementation requires it.

It should not be forced into Phase 1 or Phase 2 merely because it is part of the approved technology direction.

The initial database and application foundation should remain independent of the workflow orchestration implementation.

---

# 16. Phase 9 — Human Approval

Implement the human editorial approval boundary.

The system must support:

```text
APPROVE
REJECT
REQUEST_EDIT
```

Approval must reference the exact content version being decided upon.

If a new content version is generated:

```text
Content v1 → Approved
Content v2 → Not automatically approved
```

Approval does not inherit across versions.

AI cannot provide the authoritative human approval.

---

# 17. Phase 10 — Publication

Implement controlled article publication.

Publication requires all applicable conditions to be satisfied:

1. valid content output
2. valid content version
3. required QA completed successfully
4. valid human approval for that exact version
5. publication authorization
6. content is not rejected
7. content is not superseded where publication is prohibited
8. publication has not already successfully occurred for the same content/channel event

Publication must be application-controlled.

Successful publication must create a `publication_records` entry.

---

# 18. Publication Idempotency

Publication operations must be safe against accidental retries.

A repeated request caused by:

* network failure
* timeout
* user retry
* worker retry
* application restart

must not unintentionally create duplicate successful publication events for the same content version/channel combination.

The implementation may use an appropriate database constraint, idempotency key, application check, or combination of these, consistent with the approved schema.

---

# 19. Testing Strategy

Testing should exist at several levels.

## Unit Tests

Test:

* domain rules
* validation
* state transitions
* scoring validation
* claim eligibility
* publication rules

## Database/Integration Tests

Test:

* PostgreSQL persistence
* relationships
* constraints
* migrations
* transactions

## API Tests

Test:

* request validation
* response behaviour
* authorization boundaries
* error handling
* domain service integration

## Workflow Tests

Test the complete state progression.

## End-to-End Acceptance Test

Eventually the system must successfully execute a controlled scenario equivalent to:

```text
Source
 ↓
Observation
 ↓
Story
 ↓
Claim
 ↓
Evidence
 ↓
Verification
 ↓
Editorial Decision
 ↓
Article v1
 ↓
QA
 ↓
Human Approval
 ↓
Publication Record
```

The test must verify that the final published content can be traced back to its factual evidence.

---

# 20. Observability and Auditability

Important operations must be observable.

At minimum, the system should make it possible to determine:

* what happened
* when it happened
* which entity was affected
* which agent/process performed the operation
* what content version was involved
* what decision was made
* who made a human approval decision
* what was ultimately published

`agent_runs` must support meaningful agent execution auditing once agents are implemented.

Do not log secrets, credentials, tokens, or unnecessary sensitive information.

---

# 21. Error Handling

The system must fail safely.

Examples:

### Verification failure

Do not silently mark a claim as verified.

### QA failure

Do not allow the content to proceed to publication.

### Approval missing

Do not allow publication.

### Database failure

Do not report a business operation as successful unless the authoritative transaction succeeded.

### Agent failure

Record the failure appropriately and leave the underlying business state consistent.

### Publication retry

Do not create duplicate successful publication records.

---

# 22. Data Deletion

V0 should favour archival and state transitions over destructive deletion.

Use states such as:

```text
ARCHIVED
REJECTED
SUPERSEDED
INACTIVE
```

where appropriate.

Avoid hard deletes of important editorial history.

Foreign-key behaviour should follow the approved database schema.

---

# 23. Security Boundaries

The implementation must preserve the distinction between:

```text
AI recommendation
        ↓
Application validation
        ↓
Human authority
        ↓
Publication
```

AI-generated content must never be treated as trusted simply because it was generated by an internal agent.

External content must never be treated as an instruction source.

Secrets must be supplied through environment/configuration mechanisms rather than committed to Git.

`.env` files containing secrets must not be committed.

---

# 24. No Speculative V0 Features

Do not add the following unless an explicit product/architecture decision changes V0 scope:

* users table
* roles/permissions system
* creator network
* media asset management
* analytics platform
* advanced rights-management system
* social account management
* automated publishing
* advanced sports statistics
* live match infrastructure
* recommendation engine
* advertising system
* monetisation infrastructure
* multi-tenancy
* microservices
* Kubernetes
* event bus
* large distributed queue infrastructure
* knowledge graph
* additional media verticals

The existence of a future requirement is not sufficient justification for adding it to V0.

---

# 25. Development Data

Development/test seed data may be introduced when useful for testing.

Seed data must:

* be clearly identified as development/test data
* never be required for the production schema
* never silently alter production behaviour
* not introduce additional schema entities
* not be committed with secrets or sensitive information

---

# 26. Code Quality

The implementation should favour:

* clear Python
* small modules
* explicit types
* deterministic behaviour
* testable functions
* meaningful names
* minimal abstraction
* clear error handling
* explicit transactions

Avoid:

* premature generic frameworks
* unnecessary design patterns
* speculative abstractions
* duplicated business rules
* hidden side effects
* large monolithic functions

---

# 27. Documentation During Implementation

Implementation should update documentation only when the implementation reveals a genuine architectural or product decision.

Do not silently modify:

* project vision
* architecture
* database schema

to make implementation easier.

If implementation exposes a contradiction or missing decision:

1. identify it
2. stop the affected work
3. explain the issue
4. propose the smallest reasonable resolution
5. obtain the architectural/product decision
6. update the appropriate document
7. resume implementation

---

# 28. Copilot Implementation Rules

GitHub Copilot should be used as an implementation assistant.

Copilot must:

* read the approved documentation before implementing
* work in small scoped tasks
* follow the implementation order
* avoid inventing requirements
* avoid adding speculative infrastructure
* preserve safety boundaries
* write tests alongside functionality
* keep commits logically scoped

Copilot must not independently redefine:

* product requirements
* architecture
* database schema
* publication rules
* human approval rules
* verification rules

If Copilot encounters ambiguity that affects architecture or business behaviour, it should stop and surface the ambiguity rather than guessing.

---

# 29. Commit Strategy

Commits should be small and logically scoped.

Preferred examples:

```text
docs: add V0 implementation plan
feat: add project foundation
feat: add database configuration
feat: add sports and entity models
feat: add source models
feat: add story and claim models
feat: add content and approval models
test: add database constraint tests
```

Avoid giant commits containing unrelated architecture, database, API, and agent changes.

---

# 30. Initial Implementation Scope

Immediately after this plan is approved, implement only:

## Phase 1

Project foundation.

## Phase 2

SQLAlchemy database models.

Do not begin the full newsroom workflow or agents yet.

Do not create the initial production migration until the model layer has been reviewed.

---

# 31. Initial Engineering Milestone

The first engineering milestone is:

```text
Repository
    ↓
Python application foundation
    ↓
PostgreSQL development environment
    ↓
SQLAlchemy configuration
    ↓
Complete V0 SQLAlchemy model layer
    ↓
Alembic configured
    ↓
Tests
    ↓
Ready for initial migration
```

The milestone is complete when the approved V0 database schema can be represented cleanly and accurately in SQLAlchemy and the application is ready for the initial Alembic migration.

---

# 32. Phase Completion Rule

A phase is not complete merely because:

* the application starts
* code imports successfully
* a migration file exists
* tests were written but not run
* an endpoint returns a response

A phase is complete only when its defined behaviour works and its relevant tests pass.

---

# 33. V0 Definition of Done

The Purely Sports V0 system is considered functionally complete when it can:

1. ingest a source
2. create a source observation
3. create or update a story
4. associate the relevant source observations with the story
5. create structured claims
6. attach evidence to claims
7. verify claims
8. make an editorial decision
9. create an article content version
10. associate the content version with its factual claims
11. preserve the historical claim information required by the schema
12. run QA
13. present the exact content version to a human editor
14. record the human decision
15. prevent unapproved content from publishing
16. publish only the approved content version
17. prevent invalid or duplicate publication
18. create a publication record
19. preserve an auditable chain from published content back to source evidence

---

# 34. V0 Success Test

The definitive V0 test is:

> Can Purely Sports take a real or controlled source observation, turn it into a verified story, generate an article, subject that exact article version to QA and human approval, publish it safely, and subsequently demonstrate exactly which evidence and source observations supported the factual claims used by that published version?

If the answer is yes, the core Purely Sports operating model has been proven.

---

# 35. Final Engineering Principle

Build deliberately.

Do not build for hypothetical scale.

Do not add complexity because it might be useful later.

Do not allow AI-generated implementation decisions to silently redefine the product.

The objective is not to build the largest possible system.

The objective is to build the **smallest trustworthy system that proves the Purely Sports newsroom model and establishes the foundation for the future Purely Media OS.**

