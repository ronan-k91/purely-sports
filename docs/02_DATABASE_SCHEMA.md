Purely Sports — Database Schema
Status: V0 — Locked Database Specification
Document: `docs/02_DATABASE_SCHEMA.md`
Last Updated: 2026-09-05
---
1. Purpose
This document defines the V0 PostgreSQL database schema for Purely Sports.
The database is the persistent system of record for the AI-native newsroom.
The schema must preserve the complete editorial chain:
```text
SOURCE
   ↓
SOURCE OBSERVATION
   ↓
STORY
   ↓
CLAIM
   ↓
EVIDENCE
   ↓
VERIFICATION
   ↓
EDITORIAL DECISION
   ↓
CONTENT VERSION
   ↓
QA REVIEW
   ↓
HUMAN APPROVAL
   ↓
PUBLICATION
```
The database must support:
story discovery
source tracking
source observation
structured claims
claim-level verification
evidence provenance
entities
events
editorial decisions
content generation
content versioning
QA
human approval
publication tracking
AI agent observability
auditability
future expansion beyond sports
The V0 schema should be the smallest relational model capable of reliably supporting this workflow.
---
2. Technology
V0 database:
```text
PostgreSQL
```
ORM:
```text
SQLAlchemy
```
Migrations:
```text
Alembic
```
Application validation:
```text
Pydantic
```
The database is the authoritative persistent store.
Workflow-engine state must not be the only place where critical business state exists.
---
3. Core Design Principles
3.1 Relational First
Important business concepts must be represented as relational records.
JSONB should not be used as a substitute for relational modelling.
Use JSONB only where the structure is intentionally flexible.
---
3.2 Provenance First
Every important factual claim should be traceable to evidence.
The preferred provenance chain is:
```text
CLAIM
  ↓
EVIDENCE
  ↓
SOURCE_OBSERVATION
  ↓
SOURCE
```
Do not duplicate provenance unnecessarily.
For example, `evidence` does not need its own `source_id` because its `source_observation_id` already identifies the Source.
---
3.3 Verification Is Not Approval
These are different concepts:
```text
VERIFIED
```
means:
> The available evidence sufficiently supports the claim.
```text
APPROVED
```
means:
> An authorised human has approved this specific content version for publication.
```text
PUBLISHED
```
means:
> A publication attempt actually succeeded on a specific channel.
None of these states should be treated as interchangeable.
---
3.4 AI Recommendations Are Not Authority
AI may:
discover
research
verify
score
recommend
write
QA
AI may not bypass application rules or human approval.
Critical publication rules must be enforced by application code.
---
3.5 History Matters
Editorial records should normally be append-only or versioned.
Do not silently overwrite:
approved content
published content
verification decisions
editorial decisions
QA reviews
publication results
Historical records are part of the newsroom audit trail.
---
4. Table Inventory
The V0 schema contains the following tables:
```text
sports
entities
leagues
teams
athletes

sources
source_observations

stories
story_source_observations

claims
evidence

story_entities

events
story_events

editorial_decisions

content_outputs
content_claims

agent_runs
qa_reviews
approvals
publication_records
```
---
5. Relationship Overview
```text
SPORT
 ├── LEAGUE
 ├── TEAM
 └── ATHLETE


ENTITY
 ├── LEAGUE
 ├── TEAM
 └── ATHLETE


SOURCE
 └── SOURCE_OBSERVATION
          │
          ├───────────────┐
          ↓               ↓
        STORY           EVIDENCE
          │               ↑
          ↓               │
        CLAIM ─────────────┘
          │
          │
          ├── ENTITY
          │
          └── EVENT
          
STORY
 ├── EDITORIAL_DECISION
 └── CONTENT_OUTPUT
          │
          ├── CONTENT_CLAIM
          ├── QA_REVIEW
          ├── APPROVAL
          └── PUBLICATION_RECORD

AGENT_RUN
 └── STORY
```
The core publication provenance chain is:
```text
SOURCE
   ↓
SOURCE_OBSERVATION
   ↓
EVIDENCE
   ↓
CLAIM
   ↓
CONTENT_OUTPUT
   ↓
APPROVAL
   ↓
PUBLICATION_RECORD
```
---
6. Primary Key Standard
All major tables use:
```text
UUID PRIMARY KEY
```
Recommended SQLAlchemy generation:
```text
uuid.uuid4()
```
IDs must not be predictable sequential integers.
---
7. Timestamp Standard
Use:
```text
TIMESTAMPTZ
```
for timestamps.
Major mutable tables should include:
```text
created_at
updated_at
```
Immutable observation/event records may only require `created_at` plus their domain timestamp.
The application should use UTC internally.
---
8. Status Standard
Workflow/status fields should use:
```text
VARCHAR(50)
```
rather than PostgreSQL ENUMs in V0.
Allowed values are application-level constants validated by Pydantic/domain logic.
This keeps workflow evolution straightforward.
---
9. SPORTS
Purpose
Represents a sport.
Examples:
```text
Football
Rugby
Tennis
Formula 1
Boxing
MMA
Golf
Basketball
```
Columns
```text
id              UUID PRIMARY KEY
name            VARCHAR(100) NOT NULL
slug            VARCHAR(100) NOT NULL UNIQUE
description     TEXT NULL
is_active       BOOLEAN NOT NULL DEFAULT TRUE
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
---
10. ENTITIES
Purpose
Provides a generic canonical identity for identifiable things that may appear throughout the media system.
The Entity layer supports future expansion beyond sports.
Examples:
```text
Manchester United
Liverpool FC
Premier League
A named organisation
A person
```
Columns
```text
id              UUID PRIMARY KEY
entity_type     VARCHAR(50) NOT NULL
name            VARCHAR(300) NOT NULL
slug            VARCHAR(300) NOT NULL
description     TEXT NULL
metadata        JSONB NULL
created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
Entity Types
```text
ATHLETE
TEAM
LEAGUE
ORGANISATION
PERSON
OTHER
```
Constraints
```text
UNIQUE(entity_type, slug)
```
Important Design Rule
Do not put nullable columns such as:
```text
team_id
athlete_id
league_id
```
inside `entities`.
The generic Entity table must not become a polymorphic foreign-key container.
Instead, sport-specific records use Entity as their canonical identity.
---
11. LEAGUES
Purpose
Represents a league or competition.
Examples:
```text
Premier League
Champions League
Six Nations
ATP Tour
Formula 1 World Championship
```
Columns
```text
id              UUID PRIMARY KEY

entity_id       UUID NOT NULL UNIQUE
                REFERENCES entities(id)

sport_id        UUID NOT NULL
                REFERENCES sports(id)

country         VARCHAR(100) NULL
description     TEXT NULL

is_active       BOOLEAN NOT NULL DEFAULT TRUE

created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
Entity Rule
The referenced Entity must have:
```text
entity_type = LEAGUE
```
This is an application/domain invariant.
---
12. TEAMS
Purpose
Represents a sports team or club.
Columns
```text
id              UUID PRIMARY KEY

entity_id       UUID NOT NULL UNIQUE
                REFERENCES entities(id)

sport_id        UUID NOT NULL
                REFERENCES sports(id)

country         VARCHAR(100) NULL
description     TEXT NULL

is_active       BOOLEAN NOT NULL DEFAULT TRUE

created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
Entity Rule
The referenced Entity must have:
```text
entity_type = TEAM
```
League Relationship
A Team must not have a permanent `league_id`.
Teams may participate in different leagues or competitions over time.
A historical competition-membership model may be added later.
---
13. ATHLETES
Purpose
Represents an individual athlete.
Columns
```text
id              UUID PRIMARY KEY

entity_id       UUID NOT NULL UNIQUE
                REFERENCES entities(id)

sport_id        UUID NOT NULL
                REFERENCES sports(id)

date_of_birth   DATE NULL
nationality     VARCHAR(100) NULL
description     TEXT NULL

is_active       BOOLEAN NOT NULL DEFAULT TRUE

created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
Entity Rule
The referenced Entity must have:
```text
entity_type = ATHLETE
```
Team membership is intentionally not modelled in V0 because athlete-team relationships are time-dependent.
---
14. SOURCES
Purpose
Represents an origin of information.
Examples:
```text
Official club website
League website
Sports publication
Journalist
Athlete social account
Press conference
Interview
Public database
```
Columns
```text
id              UUID PRIMARY KEY

name            VARCHAR(300) NOT NULL

source_type     VARCHAR(50) NOT NULL

url             TEXT NULL

publisher       VARCHAR(300) NULL

trust_level     VARCHAR(50) NOT NULL DEFAULT 'UNKNOWN'

is_active       BOOLEAN NOT NULL DEFAULT TRUE

created_at      TIMESTAMPTZ NOT NULL
updated_at      TIMESTAMPTZ NOT NULL
```
Source Types
```text
OFFICIAL
SPORTS_MEDIA
JOURNALIST
SOCIAL_MEDIA
INTERVIEW
PRESS_CONFERENCE
DATABASE
OTHER
```
Trust Levels
```text
PRIMARY
TRUSTED
STANDARD
LOW
UNKNOWN
```
Trust level is an editorial aid.
It is not proof of truth.
---
15. SOURCE_OBSERVATIONS
Purpose
Represents a specific observation/retrieval from a Source.
This distinction is fundamental.
A Source is:
```text
Official Club Website
```
A Source Observation is:
```text
The specific announcement retrieved from that website at a particular time.
```
Columns
```text
id                  UUID PRIMARY KEY

source_id           UUID NOT NULL
                    REFERENCES sources(id)

url                 TEXT NULL

title               TEXT NULL

retrieval_method    VARCHAR(50) NOT NULL

observed_at         TIMESTAMPTZ NOT NULL

published_at        TIMESTAMPTZ NULL

content_hash        VARCHAR(128) NULL

content_excerpt     TEXT NULL

raw_metadata        JSONB NULL

created_at          TIMESTAMPTZ NOT NULL
```
Retrieval Methods
```text
WEB
API
RSS
SOCIAL
MANUAL
OTHER
```
Content Hash
`content_hash` represents a hash of the observed source payload/content when available.
It may be used to detect changes or duplicate observations.
It is not itself evidence of truth.
---
16. STORIES
Purpose
The Story is the central newsroom object.
A Story represents a developing or potentially publishable editorial subject.
A Story may aggregate multiple Source Observations.
Columns
```text
id                  UUID PRIMARY KEY

sport_id            UUID NULL
                    REFERENCES sports(id)

title               VARCHAR(500) NOT NULL

summary             TEXT NULL

status              VARCHAR(50) NOT NULL

priority            VARCHAR(50) NOT NULL DEFAULT 'NORMAL'

urgency             VARCHAR(50) NULL

news_value          NUMERIC(5,2) NULL

viral_score         NUMERIC(5,2) NULL

audience_score      NUMERIC(5,2) NULL

commercial_score    NUMERIC(5,2) NULL

search_score        NUMERIC(5,2) NULL

created_at          TIMESTAMPTZ NOT NULL

updated_at          TIMESTAMPTZ NOT NULL
```
Story Status
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
Priority
```text
LOW
NORMAL
HIGH
URGENT
BREAKING
```
Urgency
```text
LOW
NORMAL
HIGH
URGENT
```
Scores
Each score must be between:
```text
0.00
```
and:
```text
100.00
```
These are current advisory assessments.
They are not authoritative workflow decisions.
They may be recalculated as the Story develops.
V0 does not require historical score storage.
---
17. STORY_SOURCE_OBSERVATIONS
Purpose
Connects Stories to the Source Observations that contributed to them.
A Story may have many Source Observations.
Columns
```text
story_id                 UUID NOT NULL
                         REFERENCES stories(id)

source_observation_id    UUID NOT NULL
                         REFERENCES source_observations(id)

relationship             VARCHAR(50) NOT NULL DEFAULT 'DISCOVERY'

created_at               TIMESTAMPTZ NOT NULL
```
Primary Key
```text
PRIMARY KEY(story_id, source_observation_id)
```
Relationship Types
```text
DISCOVERY
CORROBORATION
UPDATE
BACKGROUND
CONTEXT
```
---
18. CLAIMS
Purpose
Represents an individual factual assertion associated with a Story.
Claims are first-class objects.
Example:
```text
Player X signed for Club Y.
```
Columns
```text
id                  UUID PRIMARY KEY

story_id            UUID NOT NULL
                    REFERENCES stories(id)

sequence            INTEGER NOT NULL

statement           TEXT NOT NULL

verification_status VARCHAR(50) NOT NULL DEFAULT 'UNVERIFIED'

confidence          NUMERIC(5,4) NULL

verification_notes  TEXT NULL

created_at          TIMESTAMPTZ NOT NULL

updated_at          TIMESTAMPTZ NOT NULL

verified_at         TIMESTAMPTZ NULL
```
Constraints
```text
UNIQUE(story_id, sequence)
```
Sequence
Claims should have a deterministic sequence within each Story:
```text
1
2
3
...
```
This provides stable identification such as:
```text
Claim 1
Claim 2
Claim 3
```
---
19. CLAIM VERIFICATION
Verification Status
```text
UNVERIFIED
UNDER_REVIEW
SUPPORTED
CONTRADICTED
VERIFIED
REJECTED
```
Confidence
Range:
```text
0.0000 - 1.0000
```
Confidence is an assessment.
It is not proof.
The authoritative state is:
```text
verification_status
```
Important Rule
The Writer must not knowingly use:
```text
REJECTED
```
claims.
Claims with insufficient verification should also normally be excluded from publishable factual copy unless explicitly handled by editorial logic.
---
20. EVIDENCE
Purpose
Represents specific information supporting or contradicting a Claim.
Evidence must point to a specific Source Observation.
Columns
```text
id                      UUID PRIMARY KEY

claim_id                UUID NOT NULL
                        REFERENCES claims(id)

source_observation_id   UUID NOT NULL
                        REFERENCES source_observations(id)

relationship            VARCHAR(30) NOT NULL

evidence_text           TEXT NOT NULL

locator                 TEXT NULL

created_at              TIMESTAMPTZ NOT NULL
```
Relationship Types
```text
SUPPORTS
CONTRADICTS
```
Locator
`locator` identifies where the evidence can be found when useful.
Examples:
```text
Paragraph 4
Official statement
Quote timestamp 01:24
Section: Transfer announcement
```
Important Rule
Do not store `source_id` on Evidence.
The provenance chain is:
```text
Evidence
   ↓
Source Observation
   ↓
Source
```
This avoids duplicated foreign-key relationships that could become inconsistent.
---
21. STORY_ENTITIES
Purpose
Associates a Story with relevant canonical Entities.
Columns
```text
story_id        UUID NOT NULL
                REFERENCES stories(id)

entity_id       UUID NOT NULL
                REFERENCES entities(id)

role            VARCHAR(50) NULL

created_at      TIMESTAMPTZ NOT NULL
```
Primary Key
```text
PRIMARY KEY(story_id, entity_id)
```
Roles
```text
SUBJECT
TEAM
OPPONENT
COMPETITION
MANAGER
LOCATION
OTHER
```
---
22. EVENTS
Purpose
Represents something that happens or is scheduled to happen.
An Event is distinct from a Story.
One Event may be discussed by multiple Stories.
Examples:
```text
Match
Transfer
Signing
Fight
Race
Injury
Managerial appointment
Retirement
```
Columns
```text
id              UUID PRIMARY KEY

sport_id        UUID NULL
                REFERENCES sports(id)

event_type      VARCHAR(100) NOT NULL

name            VARCHAR(500) NULL

description     TEXT NULL

occurred_at     TIMESTAMPTZ NULL

scheduled_at    TIMESTAMPTZ NULL

status          VARCHAR(50) NULL

metadata        JSONB NULL

created_at      TIMESTAMPTZ NOT NULL

updated_at      TIMESTAMPTZ NOT NULL
```
Event Types
```text
MATCH
TRANSFER
SIGNING
INJURY
FIGHT
RACE
TOURNAMENT
APPOINTMENT
RETIREMENT
OTHER
```
V0 does not attempt to model every sport-specific event field.
---
23. STORY_EVENTS
Purpose
Associates Stories with Events.
Columns
```text
story_id        UUID NOT NULL
                REFERENCES stories(id)

event_id        UUID NOT NULL
                REFERENCES events(id)

relationship    VARCHAR(50) NOT NULL DEFAULT 'ABOUT'

created_at      TIMESTAMPTZ NOT NULL
```
Primary Key
```text
PRIMARY KEY(story_id, event_id)
```
Relationship Types
```text
ABOUT
UPDATE
PREVIEW
REACTION
BACKGROUND
```
---
24. EDITORIAL_DECISIONS
Purpose
Stores editorial assessments/decisions concerning a Story.
Verification asks:
> Is the claim sufficiently supported?
Editorial decision asks:
> Should Purely Sports publish or continue working on this Story?
These must remain separate.
Columns
```text
id                  UUID PRIMARY KEY

story_id            UUID NOT NULL
                    REFERENCES stories(id)

decision            VARCHAR(50) NOT NULL

reason              TEXT NULL

recommended_format  VARCHAR(50) NULL

editorial_score     NUMERIC(5,2) NULL

risk_level          VARCHAR(50) NULL

created_by_type     VARCHAR(30) NOT NULL

created_by_id       UUID NULL

created_at          TIMESTAMPTZ NOT NULL
```
Decisions
```text
PUBLISH
DO_NOT_PUBLISH
HOLD
NEEDS_MORE_INFORMATION
```
Created By
```text
AI
HUMAN
SYSTEM
```
Important Rule
Multiple Editorial Decisions may exist for the same Story.
They form an audit trail.
The latest valid decision may represent the current editorial recommendation.
---
25. CONTENT_OUTPUTS
Purpose
Represents a specific content version generated from a Story.
Examples:
```text
Article
Social post
Video script
Newsletter item
Creator brief
```
Columns
```text
id                  UUID PRIMARY KEY

story_id            UUID NOT NULL
                    REFERENCES stories(id)

content_type        VARCHAR(50) NOT NULL

version             INTEGER NOT NULL

status              VARCHAR(50) NOT NULL

title               TEXT NULL

body                TEXT NULL

structured_content  JSONB NULL

metadata            JSONB NULL

generated_by_type   VARCHAR(30) NOT NULL

created_at          TIMESTAMPTZ NOT NULL

updated_at          TIMESTAMPTZ NOT NULL
```
Constraints
```text
UNIQUE(story_id, content_type, version)
```
Content Types
```text
ARTICLE
SOCIAL_POST
VIDEO_SCRIPT
VIDEO
GRAPHIC
NEWSLETTER
CREATOR_BRIEF
```
Status
```text
DRAFT
IN_QA
QA_FAILED
AWAITING_APPROVAL
APPROVED
REJECTED
PUBLISHED
SUPERSEDED
ARCHIVED
```
Generated By
```text
AI
HUMAN
SYSTEM
```
Important Rule
Each meaningful revision is a new version.
Do not overwrite an approved or published version.
---
26. CONTENT_CLAIMS
Purpose
Associates a specific Content Output version with the Claims it uses.
This is essential for traceability.
Columns
```text
content_output_id              UUID NOT NULL
                               REFERENCES content_outputs(id)

claim_id                       UUID NOT NULL
                               REFERENCES claims(id)

claim_statement_snapshot       TEXT NOT NULL

claim_verification_status_snapshot
                               VARCHAR(30) NOT NULL

claim_confidence_snapshot      NUMERIC(5,4) NULL

created_at                     TIMESTAMPTZ NOT NULL
```
Primary Key
```text
PRIMARY KEY(content_output_id, claim_id)
```
The snapshot fields preserve the factual/verification state actually used by that content version even if the canonical Claim is later updated as a story develops.
This allows the system to answer:
> Which claims were used by this exact content version?
It also preserves the claim statement and verification assessment that existed when the content version was associated with the claim.
Important Rule
`content_claims` is a historical snapshot boundary. Updating a canonical Claim must not rewrite the claim snapshot stored against an existing Content Output version.
---
27. AGENT_RUNS
Purpose
Tracks AI agent executions.
Used for:
observability
debugging
evaluation
reliability
model comparison
cost tracking
performance analysis
Columns
```text
id                  UUID PRIMARY KEY

story_id            UUID NULL
                    REFERENCES stories(id)

agent_name          VARCHAR(100) NOT NULL

task_type           VARCHAR(100) NOT NULL

provider            VARCHAR(100) NULL

model               VARCHAR(200) NULL

status              VARCHAR(50) NOT NULL

input_metadata      JSONB NULL

output_metadata     JSONB NULL

input_tokens        INTEGER NULL

output_tokens       INTEGER NULL

estimated_cost      NUMERIC(12,6) NULL

latency_ms          INTEGER NULL

error_message       TEXT NULL

created_at          TIMESTAMPTZ NOT NULL

completed_at        TIMESTAMPTZ NULL
```
Agent Names
```text
PS-NEWSROOM
PS-SCOUT
PS-VERIFIER
PS-EDITOR
PS-WRITER
PS-QA
```
Task Types
Examples:
```text
DISCOVER
RESEARCH
EXTRACT_CLAIMS
VERIFY
EDITORIAL_ASSESSMENT
WRITE
QA
SUMMARISE
CLASSIFY
```
Status
```text
RUNNING
SUCCEEDED
FAILED
CANCELLED
```
---
28. QA_REVIEWS
Purpose
Stores structured quality-assurance reviews of a specific Content Output version.
PS-QA should act adversarially:
> TRY TO KILL THE STORY.
Columns
```text
id                  UUID PRIMARY KEY

content_output_id   UUID NOT NULL
                    REFERENCES content_outputs(id)

result              VARCHAR(50) NOT NULL

findings            JSONB NULL

agent_run_id        UUID NULL
                    REFERENCES agent_runs(id)

created_at          TIMESTAMPTZ NOT NULL
```
Results
```text
PASS
FAIL
NEEDS_REVISION
```
Finding Structure
Example:
```json
[
  {
    "type": "FACTUAL",
    "severity": "HIGH",
    "message": "Transfer fee is unsupported."
  },
  {
    "type": "EDITORIAL",
    "severity": "MEDIUM",
    "message": "Headline overstates the evidence."
  }
]
```
Finding Types
Examples:
```text
FACTUAL
SOURCE
EDITORIAL
LEGAL
RIGHTS
HEADLINE
STYLE
PLATFORM
ORIGINALITY
OTHER
```
Important Rule
QA is associated with the exact Content Output version.
A new version requires a new QA review.
---
29. APPROVALS
Purpose
Records explicit human approval/rejection of a specific Content Output version.
Columns
```text
id                  UUID PRIMARY KEY

content_output_id   UUID NOT NULL
                    REFERENCES content_outputs(id)

decision            VARCHAR(30) NOT NULL

decided_by           UUID NULL

notes               TEXT NULL

created_at          TIMESTAMPTZ NOT NULL
```
Decisions
```text
APPROVE
REJECT
REQUEST_EDIT
```
Important Rule
Approval is version-specific.
Example:
```text
Article v1
```
approved does not imply:
```text
Article v2
```
approved.
---
30. Approval Identity
V0 does not include a full user/authentication schema.
Therefore:
```text
decided_by UUID
```
is an application-level identity reference.
It is not a foreign key in V0.
A future authentication system can introduce:
```text
users
roles
permissions
```
and convert this relationship into a formal foreign key if appropriate.
---
31. PUBLICATION_RECORDS
Purpose
Records the actual publication attempt/result for a specific Content Output version.
Approval and publication are deliberately separate.
Columns
```text
id                  UUID PRIMARY KEY

content_output_id   UUID NOT NULL
                    REFERENCES content_outputs(id)

channel             VARCHAR(100) NOT NULL

status              VARCHAR(50) NOT NULL

external_id         VARCHAR(300) NULL

external_url        TEXT NULL

scheduled_for       TIMESTAMPTZ NULL

published_at        TIMESTAMPTZ NULL

error_message       TEXT NULL

created_at          TIMESTAMPTZ NOT NULL

updated_at          TIMESTAMPTZ NOT NULL
```
Channels
Examples:
```text
WEBSITE
X
INSTAGRAM
YOUTUBE
NEWSLETTER
OTHER
```
Status
```text
PENDING
PUBLISHING
PUBLISHED
FAILED
CANCELLED
```
One Content Output may have multiple Publication Records.
Example:
```text
Article v3
 ├── Website
 ├── X
 ├── Instagram
 └── Newsletter
```
Each publication is independently auditable.
---
32. Publication Safety Rules
The application must validate all publication requirements before a publication is allowed to succeed.
At minimum:
```text
1. Content Output exists.

2. Content Output version exists.

3. Content Output is not SUPERSEDED.

4. Required QA has passed.

5. Valid human approval exists.

6. Approval applies to this exact Content Output version.

7. Content Output is not REJECTED.

8. Publication is authorised for the requested channel.

9. The application must prevent accidental duplicate successful publication records for the same Content Output version and channel unless the operation is explicitly treated as a separate publication event.
```
In V0, channel authorization and rights checks may be enforced through application configuration and service-layer rules rather than dedicated database entities. A full rights and publication-channel model is intentionally deferred.
AI must never directly bypass these checks.
The application, not the language model, controls publication authority.
---
33. Content Version Lifecycle
Example:
```text
ARTICLE v1
   ↓
QA_FAILED
   ↓
ARTICLE v2
   ↓
QA PASS
   ↓
AWAITING_APPROVAL
   ↓
HUMAN APPROVE
   ↓
APPROVED
   ↓
PUBLICATION
   ↓
PUBLISHED
```
If an edit is required after approval:
```text
ARTICLE v2
   ↓
SUPERSEDED
   ↓
ARTICLE v3
   ↓
QA
   ↓
HUMAN APPROVAL
   ↓
PUBLICATION
```
The previous version remains in the database.
---
34. Story Status vs Content Status
Story status and Content Output status represent different layers.
Example:
```text
Story.status
=
IN_PRODUCTION
```
while:
```text
ContentOutput.status
=
DRAFT
```
This is valid.
Likewise:
```text
Story.status
=
AWAITING_APPROVAL
```
while:
```text
ContentOutput.status
=
AWAITING_APPROVAL
```
may also be valid.
The Content Output version and Approval records remain the authoritative records for content approval.
Story status is a workflow summary.
---
35. Story APPROVED State
`stories.status = APPROVED` is a workflow summary only.
It must not be used as proof that a particular Content Output version is approved.
The authoritative approval relationship is:
```text
CONTENT_OUTPUT
      ↓
APPROVAL
```
This prevents a Story-level approval from accidentally authorising a later content version.
---
36. Evidence and Verification Rules
A Claim may have:
```text
zero evidence
one piece of evidence
multiple supporting pieces
supporting and contradicting evidence
```
Example:
```text
Claim:
Player X signed Club Y.

Evidence A:
Official club announcement
SUPPORTS

Evidence B:
Trusted journalist
SUPPORTS

Evidence C:
Later club statement
CONTRADICTS
```
All three remain stored.
The verifier determines the current Claim verification status.
---
37. Source Observation and Story Rules
A Source Observation does not automatically create a new Story.
Example:
```text
Observation 1
Rumour

Observation 2
Offer reported

Observation 3
Official confirmation
```
These may all belong to one Story.
Therefore:
```text
Source Observation
```
and:
```text
Story
```
must remain separate concepts.
---
38. Story and Event Rules
A Story is an editorial object.
An Event is a real-world occurrence or scheduled occurrence.
Example:
```text
EVENT:
Player X signs Club Y.

STORY:
Purely Sports reports that Player X has signed for Club Y.
```
Multiple Stories may reference the same Event.
---
39. Entity Rules
The generic Entity layer is the canonical identity layer.
For sport-specific entities:
```text
Entity
   ↓
Team
```
or:
```text
Entity
   ↓
Athlete
```
or:
```text
Entity
   ↓
League
```
The relationship is one-to-one.
Therefore:
```text
teams.entity_id UNIQUE
athletes.entity_id UNIQUE
leagues.entity_id UNIQUE
```
The application must ensure the Entity type matches the subtype.
For example:
```text
teams.entity_id → Entity(entity_type = TEAM)
```
not:
```text
Entity(entity_type = ATHLETE)
```
---
40. Deletion Policy
Important editorial records should generally not be hard-deleted.
Prefer status transitions such as:
```text
ARCHIVED
REJECTED
SUPERSEDED
INACTIVE
```
Foreign-key deletion should therefore normally use restrictive behaviour for important editorial records.
Do not cascade-delete a Story and silently erase its:
```text
Claims
Evidence
QA
Approvals
Publication history
Agent runs
```
Historical newsroom information must remain recoverable.
---
41. Recommended Foreign-Key Behaviour
For editorial relationships, the default policy should effectively be:
```text
ON DELETE RESTRICT
```
unless there is a clear reason otherwise.
For many-to-many join tables, cascading deletion of the join row may be acceptable when the parent record is deliberately deleted during development, but production editorial data should generally not be deleted.
V0 should prefer archiving over deletion.
---
42. Recommended Indexes
The following indexes should be created initially.
Stories
```text
INDEX stories_status_idx
ON stories(status)

INDEX stories_priority_idx
ON stories(priority)

INDEX stories_created_at_idx
ON stories(created_at)

INDEX stories_updated_at_idx
ON stories(updated_at)
```
Source Observations
```text
INDEX source_observations_source_id_idx
ON source_observations(source_id)

INDEX source_observations_observed_at_idx
ON source_observations(observed_at)
```
Claims
```text
INDEX claims_story_id_idx
ON claims(story_id)

INDEX claims_verification_status_idx
ON claims(verification_status)
```
Evidence
```text
INDEX evidence_claim_id_idx
ON evidence(claim_id)

INDEX evidence_source_observation_id_idx
ON evidence(source_observation_id)
```
Content
```text
INDEX content_outputs_story_id_idx
ON content_outputs(story_id)

INDEX content_outputs_status_idx
ON content_outputs(status)

INDEX content_outputs_story_type_idx
ON content_outputs(story_id, content_type)
```
QA
```text
INDEX qa_reviews_content_output_id_idx
ON qa_reviews(content_output_id)
```
Approvals
```text
INDEX approvals_content_output_id_idx
ON approvals(content_output_id)

INDEX approvals_created_at_idx
ON approvals(created_at)
```
Publications
```text
INDEX publication_records_content_output_id_idx
ON publication_records(content_output_id)

INDEX publication_records_status_idx
ON publication_records(status)
```
Agent Runs
```text
INDEX agent_runs_story_id_idx
ON agent_runs(story_id)

INDEX agent_runs_status_idx
ON agent_runs(status)

INDEX agent_runs_created_at_idx
ON agent_runs(created_at)
```
Do not create large numbers of speculative indexes in V0.
---
43. Database-Level Checks
Where practical, PostgreSQL CHECK constraints should enforce simple numerical invariants.
Examples:
```text
news_value BETWEEN 0 AND 100

viral_score BETWEEN 0 AND 100

audience_score BETWEEN 0 AND 100

commercial_score BETWEEN 0 AND 100

search_score BETWEEN 0 AND 100

editorial_score BETWEEN 0 AND 100

confidence BETWEEN 0 AND 1

claims.sequence > 0

content_outputs.version > 0
```
These are appropriate database constraints because they are stable structural rules.
Workflow transitions remain application-level rules.
---
44. Application-Level Invariants
The application must enforce rules that require business context.
Examples:
```text
Entity subtype must match entity_type.

Only authorised humans may create APPROVE decisions.

A content version cannot inherit approval from another version.

Publication requires valid approval.

Publication requires successful QA.

Rejected content cannot publish.

Superseded content cannot newly publish.

Rejected claims cannot knowingly be used as factual support.

Workflow transitions must be valid.

AI cannot directly publish.
```
Do not attempt to encode all of these as database triggers in V0.
The service/application layer is the correct location for these business rules.
---
45. Auditability
The database should allow the newsroom to answer:
```text
Who discovered the Story?

Which Sources contributed?

Which Source Observations were used?

Which Claims were extracted?

Which Evidence supports each Claim?

Which Evidence contradicts each Claim?

What was the verification status?

What editorial decision was made?

Which Content Output version was created?

Which Claims were used by that version?

What QA review did it receive?

What findings were raised?

Who approved the exact version?

Where was it published?

When was it published?

Did publication succeed or fail?

Which AI agents participated?
```
This is a core requirement of the system.
---
46. Agent Observability
Agent Runs should provide enough information to evaluate the newsroom without storing unnecessary sensitive data.
Useful fields include:
```text
agent_name
task_type
provider
model
status
token counts
estimated cost
latency
error
```
Do not store secrets in:
```text
input_metadata
output_metadata
error_message
```
Never store:
```text
API keys
access tokens
passwords
credentials
session secrets
```
unless a future dedicated secrets system explicitly requires it.
---
47. Transaction Boundaries
Important operations should be transactional.
Examples:
```text
Create verification result

Create content version

Record QA result

Record human approval

Create publication record

Transition workflow state
```
The application/service layer owns transaction boundaries.
The database owns referential integrity.
---
48. Alembic Migration Order
The initial migration should create tables in dependency order.
Recommended order:
```text
1. sports

2. entities

3. leagues
4. teams
5. athletes

6. sources
7. source_observations

8. stories

9. story_source_observations

10. claims

11. evidence

12. story_entities

13. events
14. story_events

15. editorial_decisions

16. content_outputs
17. content_claims

18. agent_runs

19. qa_reviews

20. approvals

21. publication_records
```
This order minimises foreign-key dependency problems.
---
49. V0 Intentionally Excluded
Do not add the following simply because they may eventually be useful:
```text
users
roles
permissions

creators
creator_profiles

matches
statistics
standings

team_league_history

athlete_team_history

media_assets
asset_rights

social_accounts

publication_channel_configuration

analytics_events

external_entity_ids

corrections

workflow_runs

knowledge_graph_edges
```
These are future extensions.
They should be introduced only when actual product requirements justify them.
---
50. Future Expansion
The architecture is intentionally extensible.
Possible future additions include:
```text
users
roles
permissions

creators
creator_profiles

matches
statistics
standings

team_league_memberships
athlete_team_memberships

media_assets
asset_rights

publication_channels
publication_jobs

external_entity_ids

corrections
correction_records

workflow_runs

content_revisions

analytics_events
```
The V0 schema should not attempt to solve these problems prematurely.
---
51. V0 Editorial Data Flow
The complete intended flow is:
```text
                    ┌─────────────┐
                    │    SOURCE   │
                    └──────┬──────┘
                           │
                           ↓
                 ┌───────────────────┐
                 │ SOURCE OBSERVATION│
                 └─────────┬─────────┘
                           │
                           ↓
                    ┌────────────┐
                    │   STORY    │
                    └─────┬──────┘
                          │
             ┌────────────┼────────────┐
             ↓            ↓            ↓
         ┌───────┐   ┌─────────┐   ┌────────┐
         │ CLAIM │   │ ENTITY  │   │ EVENT  │
         └───┬───┘   └─────────┘   └────────┘
             │
             ↓
        ┌──────────┐
        │ EVIDENCE │
        └────┬─────┘
             │
             ↓
       VERIFICATION
             │
             ↓
   EDITORIAL DECISION
             │
             ↓
    CONTENT OUTPUT vN
             │
       ┌─────┴─────┐
       ↓           ↓
   CONTENT      QA REVIEW
    CLAIMS          │
       │            ↓
       │       QA PASS/FAIL
       │            │
       └─────┬──────┘
             ↓
      HUMAN APPROVAL
             │
             ↓
    PUBLICATION RECORD
```
---
52. Critical Safety Boundary
The database supports the workflow but does not itself grant AI publication authority.
The final publication decision must pass through:
```text
QA
 ↓
Human Approval
 ↓
Application Validation
 ↓
Publication
```
The language model cannot simply produce:
```text
"publish": true
```
and cause publication.
The application must independently verify the required conditions.
---
53. Final V0 Rules
The following rules are considered foundational.
Rule 1
A Source is not the same thing as a Source Observation.
Rule 2
A Source Observation is not automatically a Story.
Rule 3
A Story may contain multiple Claims.
Rule 4
Claims are the fundamental units of factual verification.
Rule 5
Evidence belongs to Claims.
Rule 6
Evidence points to Source Observations.
Rule 7
Do not duplicate `source_id` on Evidence.
Rule 8
Verification is not editorial approval.
Rule 9
Editorial Decision is not publication.
Rule 10
Content Output represents a specific version.
Rule 11
Every meaningful content revision creates a new version.
Rule 12
Approval belongs to the exact Content Output version.
Rule 12A
Content Claims preserve a snapshot of the claim statement and verification assessment used by that exact Content Output version.
Rule 13
Approval of one version never automatically approves another.
Rule 14
QA belongs to the exact Content Output version.
Rule 15
Publication belongs to the exact Content Output version.
Rule 16
One Content Output may have multiple Publication Records.
Rule 16A
The application must prevent accidental duplicate successful publication records for the same Content Output version and channel unless explicitly treated as a separate publication event.
Rule 17
AI cannot bypass human approval.
Rule 18
Story status is a workflow summary, not proof of approval.
Rule 19
Claim verification status is authoritative for claim verification.
Rule 20
The database preserves editorial history.
---
54. V0 Success Criteria
The database design is considered successful when Purely Sports can reliably trace:
```text
Published Article
      ↓
Exact Content Version
      ↓
Human Approval
      ↓
QA Review
      ↓
Claims Used
      ↓
Claim Verification
      ↓
Evidence
      ↓
Source Observation
      ↓
Source
```
And when the system can independently determine:
```text
What happened?
Where did the information come from?
What claims are being made?
What evidence supports them?
What evidence contradicts them?
Has each claim been verified?
Should the Story proceed?
What content version was created?
Did QA pass?
Who approved it?
Was it actually published?
Where?
When?
What did the AI do?
```
---
55. Final Principle
The Purely Sports database is not merely an article database.
It is the structured memory and accountability layer of the newsroom.
The fundamental model is:
```text
SOURCE
   ↓
SOURCE OBSERVATION
   ↓
STORY
   ↓
CLAIM
   ↓
EVIDENCE
   ↓
VERIFICATION
   ↓
EDITORIAL DECISION
   ↓
CONTENT VERSION
   ↓
QA
   ↓
HUMAN APPROVAL
   ↓
PUBLICATION
```
Every important factual statement should have a path toward evidence.
Every publishable content version should have a path toward approval.
Every publication should have a recorded outcome.
Every important AI action should be observable.
The schema should make correct newsroom behaviour easy, traceable and auditable, while making unsafe shortcuts difficult.
This schema is the V0 database contract.
Do not add complexity until the product demonstrates that the complexity is necessary.
