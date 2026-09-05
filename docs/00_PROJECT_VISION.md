# Purely Sports — Project Vision

## 1. Purpose

Purely Sports is an AI-native sports media and sports intelligence company.

The initial objective is to build a proof-of-concept newsroom capable of discovering, researching, verifying, producing, quality-checking and preparing sports stories for human approval.

The long-term objective is to create a reusable AI-native media platform capable of powering multiple media verticals.

Sports is the first vertical.

The underlying technology must therefore avoid unnecessary coupling to sports-specific concepts.

---

## 2. Core Concept

Purely Sports combines:

* AI newsroom agents
* structured information and claims
* human editorial oversight
* automated content production
* multi-platform distribution
* audience analytics
* sports data
* eventually, human creators and personalities

The company should eventually be able to operate a large media network with a relatively small core human team.

AI provides operational leverage.

Humans provide judgement, accountability, personality, creativity and culture.

---

## 3. Human Role

The founder is initially:

**Chief Editor / CEO**

The human is the final publishing authority.

During the proof-of-concept:

* AI may discover stories.
* AI may research stories.
* AI may verify information.
* AI may write drafts.
* AI may create content packages.
* AI may perform QA.
* AI may recommend publication.
* AI MUST NOT publish externally without explicit human approval.

Human approval must be represented explicitly in the system.

---

## 4. AI Newsroom

The initial newsroom contains these conceptual roles:

### PS-NEWSROOM

Coordinates the newsroom and manages workflow.

### PS-SCOUT

Discovers potentially relevant stories from approved sources.

### PS-VERIFIER

Determines which claims are supported by reliable evidence.

### PS-EDITOR

Determines whether a verified story should be published and what format it should use.

### PS-WRITER

Creates publication-ready content from verified information.

### PS-QA

Attempts to identify factual, editorial, legal, rights, quality and platform problems before publication.

These are logical responsibilities.

They do not necessarily need to be implemented as independent software services.

Prefer a simple architecture where appropriate.

---

## 5. Source-of-Truth Principle

Every publishable story must have a canonical structured representation.

A story should contain:

* story identity
* sport
* competition
* entities
* sources
* claims
* verification status
* confidence
* editorial decision
* content outputs
* approval state

Content should be generated from structured verified information rather than from an uncontrolled conversation between agents.

---

## 6. Claims-Based Journalism

Important factual statements should be represented as claims.

Example:

Claim:
"Player X signed for Club Y."

Source:
Official Club Y announcement.

Confidence:
1.0

Status:
VERIFIED

A second claim may have a different source and confidence.

The system must support:

* multiple claims per story
* multiple sources per claim
* source reliability
* confidence
* verification status
* timestamps
* contradictory evidence
* unresolved claims

Writers must not knowingly use claims marked as unverified or rejected.

---

## 7. Story-First, Format-Second

Purely Sports is a newsroom, not a video factory.

Every story should first be evaluated as a story.

The editorial system should determine which outputs are appropriate.

Possible outputs include:

* article
* breaking-news post
* Facebook post
* Instagram post
* X post
* TikTok script
* YouTube Shorts script
* graphic
* carousel
* newsletter item
* video
* creator brief

Not every story requires every format.

---

## 8. Content Pipelines

The system should eventually support three broad pipelines.

### Breaking

Fast-moving stories requiring rapid verification and publication.

### Daily

Normal news and scheduled editorial output.

### Evergreen

Long-lasting stories, explainers, historical content and other non-time-sensitive material.

These pipelines should share common infrastructure.

---

## 9. Human Creators

The long-term company may employ or partner with high-quality human sports creators.

Potential creator formats include:

* podcasts
* livestreams
* interviews
* analysis
* comedy
* reactions
* debates
* original reporting

The AI newsroom should eventually support creators by producing creator briefs containing:

* important stories
* verified facts
* statistics
* context
* talking points
* interview questions
* potential angles
* graphics
* supporting articles

AI should augment creators rather than eliminate the need for strong human personalities.

---

## 10. Multi-Vertical Future

The long-term platform may support additional media verticals such as:

* general news
* business
* technology
* entertainment
* history
* crime and courts
* other high-interest niches

The core platform should therefore use generic concepts wherever practical:

* Source
* Story
* Claim
* Entity
* Event
* Content
* Publication
* Workflow
* Audience
* Creator

Sports-specific concepts such as teams, leagues and athletes should be implemented as extensions of the generic domain where practical.

---

## 11. Architecture Principles

1. Prefer simple systems over unnecessary complexity.
2. Keep business logic separate from presentation.
3. Keep AI model providers behind abstractions.
4. Keep workflows observable and restartable.
5. Make important AI decisions auditable.
6. Never rely on unstructured agent conversations for critical state.
7. Store important state in the database.
8. Make human approval explicit.
9. Never hard-code secrets.
10. Write automated tests for critical business logic.
11. Minimise unnecessary dependencies.
12. Design for eventual horizontal scaling without prematurely implementing it.
13. Prefer configuration over duplicated code.
14. Treat external sources as untrusted input.
15. Fail safely.

---

## 12. Model Independence

The system must not assume that one AI provider will always be used.

All model calls should pass through a model abstraction/router.

The router should eventually support:

* local models
* low-cost API models
* premium reasoning models
* fallback providers

The application should specify the task and required capability rather than embedding a provider-specific implementation throughout the codebase.

---

## 13. Cost Awareness

AI usage is a business expense.

The system should eventually record:

* model used
* task
* input tokens where available
* output tokens where available
* estimated cost
* latency
* success/failure
* story ID
* agent/workflow ID

This will allow us to calculate:

**cost per discovered story**

**cost per verified story**

**cost per published story**

**cost per content package**

---

## 14. Auditability

Every important newsroom action should eventually be traceable.

We should be able to answer:

* What happened?
* Which agent performed it?
* Which model was used?
* What information was supplied?
* Which sources were considered?
* Which claims were accepted?
* Which claims were rejected?
* Who approved publication?
* When was it approved?
* What was published?

---

## 15. Proof-of-Concept Goal

The first working system should demonstrate:

RAW STORY

→ discovery

→ source collection

→ claim extraction

→ verification

→ editorial evaluation

→ article generation

→ social generation

→ QA

→ human approval

The system does not need to solve the entire media industry in V0.

It needs to prove that the core newsroom loop works reliably.

---

## 16. Definition of Success

V0 is successful when a real sports story can pass through the system with:

* traceable sources
* structured claims
* reliable verification
* useful editorial judgement
* high-quality content
* automated QA
* clear human approval
* reproducible workflow
* logged AI usage
* automated tests

Only after this works should we significantly expand the system.
