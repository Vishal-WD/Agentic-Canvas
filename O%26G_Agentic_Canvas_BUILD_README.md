# O&G Agentic Canvas
## Autonomous Multi-Agent Content Orchestration Engine

> **Build specification + AI coding-agent prompt pack**
>
> This README is the source-of-truth implementation contract for the O&G Agentic Canvas internship MVP.  
> Give the prompts in this document to an AI coding agent **in order**. The agent must inspect the existing repository before changing anything, preserve the O&G design system, implement incrementally, run tests after every major milestone, and never silently weaken requirements to make a build pass.

---

# 1. Product Definition

## 1.1 What we are building

Build an enterprise-grade web application that behaves like an **AI marketing campaign production team**.

A user submits a campaign request such as:

> Create a launch campaign for a new enterprise AI security product.

The system then:

1. Creates an execution/campaign.
2. Orchestrates multiple specialized AI agents.
3. Retrieves the relevant O&G brand rules through RAG/vector search.
4. Generates structured campaign assets.
5. Validates every generated asset against brand guardrails.
6. Automatically repairs/re-generates invalid output when possible.
7. Produces a final structured campaign package.
8. Stores execution traces, decisions, scores, violations, retries and timestamps.
9. Displays the process and results in an Angular dashboard.

### Core flow

```text
User
  |
  v
Campaign Request
  |
  v
Orchestrator
  |
  +--> Copywriter Agent
  |
  +--> Layout Structurer Agent
  |
  +--> Asset Recommender Agent
  |
  v
RAG / Brand Knowledge
  |
  v
Brand Guardrail Engine
  |
  +--> PASS ------+
  |               |
  +--> FAIL -> Repair/Re-generation
                  |
                  v
           Final Campaign
                  |
        +---------+---------+
        |                   |
        v                   v
   PostgreSQL           Angular UI
   Audit Trail          Dashboard
```

---

# 2. Non-Negotiable Requirements

These requirements are higher priority than convenience.

## 2.1 Never compromise the brand

The O&G brand system must be treated as a strict design contract.

### Colors

| Name | Hex | Intended role |
|---|---|---|
| Deep Navy | `#0C2140` | Primary foundation/background |
| Orchestration Blue | `#16528D` | Technology/orchestration elements |
| Secure Azure | `#2674B8` | Innovation/highlights |
| Guardrail Gold | `#D6B25A` | Protection, CTAs, emphasis |
| Cloud White | `#F5F8FC` | Primary readable text |
| Slate | `#5F7188` | Secondary text/details |
| Midnight | `#071426` | Deep/zero-trust background |

Approximate visual hierarchy:

- 60% Deep Navy
- 20% Blue family
- 10% White/neutrals
- 10% Guardrail Gold

### Visual rules

- Prefer Deep Navy or Midnight as major backgrounds.
- Use blue for technology, buttons, links and highlights.
- Use Guardrail Gold sparingly for emphasis, key CTAs and security/guardrail boundaries.
- Use Cloud White for primary text.
- Use Slate for secondary text.
- Maintain strong WCAG-conscious contrast.
- Use subtle blue/gold glows only where they improve hierarchy.
- Avoid excessive gradients, glow, glassmorphism or decorative effects.
- Never introduce arbitrary brand colors.
- Do not replace the supplied palette with generic Bootstrap/Tailwind defaults.
- Do not create a light-theme-first interface.

### Approved gradients

- Navy → Blue
- Blue → Azure
- Navy → Gold
- Midnight → Blue

## 2.2 Typography

Use a modern clean sans-serif family.

Recommended implementation:

- `Inter` or a comparable modern grotesque/sans-serif available through the application's asset strategy.
- Headings: bold/semibold.
- Section labels/taglines: uppercase with controlled letter spacing.
- Body: highly readable Cloud White/Slate.
- Avoid decorative/script fonts.

## 2.3 Tone

Generated and displayed copy must feel:

- Enterprise
- Authoritative
- Technically mature
- Security-focused
- Professional
- Grounded
- Clear
- Trustworthy

Important concepts:

- Zero-trust
- Resilience
- Transparency
- Protection
- Reliability
- Enterprise security
- Safe innovation

Approved taglines:

> Orchestrate Intelligence. Protect Everything.

> Orchestrate. Protect. Elevate.

## 2.4 Logo

The O&G identity uses:

- Protective shield
- Circuit-node motif
- Central lock/security concept
- Bold `O&G`
- Descriptor: `ORCHESTRATION & GUARDRAIL`

The logo must retain strong contrast on dark backgrounds.

**Do not redraw, distort, rotate, stretch, recolor arbitrarily, or invent alternate logo geometry.**

If the repository contains an official logo asset, use it. If not, create a clearly isolated placeholder asset only where necessary and document the replacement point.

---

# 3. Functional Scope

## 3.1 Multi-agent generation pipeline

Implement specialized agents with explicit contracts.

### Copywriter Agent

Input:

- campaign brief
- target audience
- product information
- tone
- retrieved brand rules

Output:

- campaign headline
- subheadline
- value proposition
- CTA
- social copy
- supporting copy

### Layout Structurer Agent

Input:

- generated copy
- campaign type
- brand layout rules

Output:

- semantic layout structure
- content hierarchy
- recommended component types
- visual hierarchy
- placement guidance

It should produce **structured JSON**, not arbitrary HTML.

### Asset Recommender Agent

Input:

- campaign brief
- campaign type
- layout structure
- brand visual rules

Output:

- asset type
- aspect ratio
- subject description
- background recommendation
- gradient recommendation
- accessibility/alt-text guidance
- brand restrictions

This agent recommends assets. It must not silently invent unavailable brand assets.

---

# 4. Brand RAG System

The brand kit is knowledge, not merely frontend styling.

Create a versioned knowledge base containing:

- colors
- color hierarchy
- gradient pairings
- typography
- tone of voice
- taglines
- logo rules
- application rules
- image/visual guidelines
- accessibility requirements

## 4.1 Retrieval behavior

When an agent needs brand information:

```text
Agent question
   |
   v
Embedding
   |
   v
Vector search
   |
   v
Top relevant brand-rule chunks
   |
   v
Agent prompt
   |
   v
Structured output
```

Do not retrieve the entire brand kit for every request if a smaller relevant context can be used.

Each retrieved rule should retain:

- rule ID
- category
- source
- version
- text
- priority/severity

## 4.2 Grounding

Agents must distinguish:

- retrieved brand facts
- campaign/user facts
- generated recommendations

Never present an invented rule as an official O&G rule.

---

# 5. Brand Guardrail Engine

This is a core feature.

The guardrail engine must evaluate generated output against deterministic and semantic rules.

## 5.1 Deterministic checks

At minimum implement checks for:

### Color

- Approved hex values only.
- Approved gradients only.
- Detect unapproved colors.
- Detect excessive Gold usage where structured color information is available.

### Typography

- Approved font family/category.
- Heading hierarchy.
- Readability.

### Logo

- Required where the campaign type demands it.
- Correct logo reference.
- No distortion flags in structured output.

### Tone

Check for:

- enterprise tone
- authoritative language
- security-oriented positioning
- inappropriate casual language
- unsupported claims

### Layout

Check campaign-type-specific rules.

### Accessibility

Check:

- contrast metadata where available
- alt-text requirement for visual assets
- heading hierarchy
- readable text size metadata
- actionable controls

## 5.2 Semantic checks

Use an LLM evaluator only as a **secondary semantic validator**, not as the sole source of truth.

Architecture:

```text
Generated output
      |
      +--> Deterministic Validator
      |
      +--> Semantic Evaluator
      |
      v
   Aggregator
      |
      v
Compliance Result
```

The deterministic validator must be able to reject objective violations regardless of what the LLM evaluator says.

## 5.3 Compliance score

Use a transparent scoring model.

Example:

```text
overall_score =
  color_score * 0.20 +
  typography_score * 0.10 +
  logo_score * 0.15 +
  tone_score * 0.15 +
  layout_score * 0.15 +
  accessibility_score * 0.15 +
  semantic_score * 0.10
```

Make weights configurable rather than hard-coded throughout the codebase.

A score is useful for reporting, but **critical violations must override the numeric score**.

Example:

```text
Score: 96
Critical logo violation: YES

Final status: REJECTED
```

## 5.4 Violation severity

Use:

- `critical`
- `high`
- `medium`
- `low`
- `info`

Every violation should contain:

```json
{
  "rule_id": "COLOR-001",
  "severity": "high",
  "message": "Unapproved color detected.",
  "expected": "#0C2140, #16528D, #2674B8, #D6B25A, #F5F8FC, #5F7188, #071426",
  "actual": "#FF0000",
  "field": "backgroundColor",
  "suggested_fix": "Replace with an approved O&G brand color."
}
```

---

# 6. Repair Loop

The system should not simply fail when a recoverable violation occurs.

```text
Generate
   |
   v
Validate
   |
   +--> PASS --> Continue
   |
   +--> FAIL
          |
          v
       Repair
          |
          v
       Validate
          |
          +--> PASS
          |
          +--> FAIL
                 |
                 v
             Retry limit
                 |
                 v
              FAILED
```

Requirements:

- Maximum retry count must be configurable.
- Default should be conservative, such as 2–3 attempts.
- Every attempt must be logged.
- Never retry indefinitely.
- Never hide failed attempts from the audit trail.
- Critical violations may require human review rather than automatic repair.
- Preserve the original output for auditability.

---

# 7. Orchestration

Implement a clear state machine or workflow.

Suggested states:

```text
CREATED
QUEUED
RUNNING
GENERATING_COPY
STRUCTURING_LAYOUT
RECOMMENDING_ASSETS
VALIDATING_BRAND
REPAIRING
APPROVED
REVIEW_REQUIRED
FAILED
COMPLETED
```

Transitions must be explicit.

No hidden infinite loops.

Every state transition should create an execution event.

Example:

```json
{
  "execution_id": "...",
  "from_state": "GENERATING_COPY",
  "to_state": "STRUCTURING_LAYOUT",
  "timestamp": "...",
  "reason": "Copywriter completed successfully"
}
```

---

# 8. n8n / Workflow Integration

The project may use n8n for external workflow orchestration.

If n8n is used:

- Keep the core business logic in Python where practical.
- Do not make the application dependent on undocumented manual n8n UI changes.
- Version/export workflow definitions where possible.
- Document environment variables.
- Webhook endpoints must validate input.
- Webhook calls must be idempotent.
- Handle retries and duplicate events safely.
- Do not expose secrets in workflow definitions.

If a Python state machine is selected instead, provide an equivalent explicit orchestration layer.

---

# 9. Backend Architecture

Use:

- Python
- FastAPI
- PostgreSQL
- RAG/vector search
- Pydantic models
- Async I/O where appropriate

Suggested structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   └── dependencies.py
│   ├── agents/
│   │   ├── base.py
│   │   ├── copywriter.py
│   │   ├── layout.py
│   │   └── asset_recommender.py
│   ├── orchestration/
│   │   ├── state_machine.py
│   │   ├── executor.py
│   │   └── events.py
│   ├── guardrails/
│   │   ├── engine.py
│   │   ├── deterministic.py
│   │   ├── semantic.py
│   │   └── scoring.py
│   ├── rag/
│   │   ├── ingestion.py
│   │   ├── retrieval.py
│   │   └── embeddings.py
│   ├── db/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   ├── schemas/
│   ├── services/
│   ├── config.py
│   └── logging.py
├── tests/
├── scripts/
├── .env.example
└── requirements.txt
```

Adapt this structure to the actual framework choices, but preserve separation of concerns.

---

# 10. API Contract

At minimum provide:

## Health

`GET /api/health`

Returns service health.

## Create campaign

`POST /api/campaigns`

Request should contain:

```json
{
  "name": "AI Security Launch",
  "brief": "Launch campaign for an enterprise AI security product.",
  "campaign_type": "website",
  "target_audience": "Enterprise technology leaders"
}
```

## Get campaign

`GET /api/campaigns/{campaign_id}`

## Start execution

`POST /api/campaigns/{campaign_id}/execute`

## Get execution

`GET /api/executions/{execution_id}`

## Get execution events

`GET /api/executions/{execution_id}/events`

## Get compliance result

`GET /api/executions/{execution_id}/compliance`

## Get generated assets

`GET /api/campaigns/{campaign_id}/assets`

## Brand rules

`GET /api/brand/rules`

## Dashboard summary

`GET /api/dashboard/summary`

Exact endpoint names may vary, but the capabilities must exist.

Use OpenAPI-generated documentation and typed request/response schemas.

---

# 11. Database Design

Use PostgreSQL.

Suggested tables:

```text
campaigns
executions
execution_events
agent_runs
generated_assets
brand_rules
brand_rule_versions
guardrail_results
guardrail_violations
workflow_runs
```

Important fields should include:

### campaigns

- id
- name
- brief
- campaign_type
- target_audience
- status
- created_at
- updated_at

### executions

- id
- campaign_id
- status
- current_state
- started_at
- completed_at
- retry_count
- final_score
- failure_reason

### agent_runs

- id
- execution_id
- agent_name
- input
- output
- status
- model/provider metadata
- latency
- token/cost metadata if available
- created_at

### guardrail_results

- id
- execution_id
- score
- status
- critical_violation
- evaluator_version
- created_at

### guardrail_violations

- id
- guardrail_result_id
- rule_id
- severity
- field
- expected
- actual
- message
- suggested_fix

Never store API keys or secrets in database records.

---

# 12. Frontend

Use Angular.

The dashboard should provide:

## Dashboard

Show:

- total campaigns
- running executions
- approved campaigns
- failed/review-required campaigns
- average compliance score
- recent executions

## Campaign page

Show:

- campaign brief
- generated copy
- layout structure
- recommended assets
- brand compliance
- final status

## Execution trace

Show the agent pipeline visually:

```text
✓ Copywriter
      |
      v
✓ Layout Structurer
      |
      v
✓ Asset Recommender
      |
      v
✓ Brand Guardrail
      |
      v
✓ Final Output
```

For failures:

```text
✓ Copywriter
      |
      v
✓ Layout
      |
      v
⚠ Brand Guardrail
      |
      v
↻ Repair Attempt 1
      |
      v
✓ Approved
```

## Guardrail report

Show:

- overall score
- category scores
- severity counts
- exact violations
- expected vs actual
- repair history
- approval status

Do not expose internal chain-of-thought. Display concise reasoning/explanations derived from structured validator results only.

---

# 13. Frontend Design Contract

The dashboard itself must look like an O&G enterprise product.

## Required visual language

- Deep Navy/ Midnight foundation.
- Blue/Azure for active technology states.
- Gold for important actions and guardrail emphasis.
- Cloud White for primary text.
- Slate for secondary text.
- Thin borders with restrained contrast.
- Strong spacing and alignment.
- Dense but readable information hierarchy.
- Professional enterprise dashboard.
- Responsive layout.
- Keyboard accessibility.
- Visible focus states.

Avoid:

- cartoonish UI
- excessive rounded cards
- neon cyberpunk styling
- random gradients
- rainbow colors
- excessive animations
- emoji-heavy interface
- generic admin-dashboard appearance
- poor contrast
- unnecessary glassmorphism

Gold is an accent, not the dominant UI color.

---

# 14. Campaign-Type Rules

## Product Dashboard

- Dark mode.
- High contrast.
- Clear metrics.
- Data visibility first.
- Gold reserved for important actions/guardrail states.

## Pitch Deck / Report

- Navy slides/pages.
- Cloud White primary typography.
- Slate details.
- Blue for technology hierarchy.
- Gold for emphasis.

## Website / Landing Page

- Dark theme.
- Approved gradients.
- High-visibility Gold CTA.
- Strong enterprise/security positioning.

## Developer Assets

- Clean technical layout.
- Excellent code readability.
- Accessible contrast.
- Minimal decoration.
- Documentation-first hierarchy.

---

# 15. Security Requirements

Treat this as an enterprise application.

Implement:

- Environment-based secrets.
- `.env` for local development only.
- `.env.example` containing variable names but no secrets.
- Input validation.
- Request size limits where appropriate.
- Safe error responses.
- No secret logging.
- No API-key exposure to Angular.
- CORS restricted to configured frontend origins.
- Database parameterization/ORM.
- Webhook authentication/signature validation where supported.
- Rate limiting where appropriate.
- Idempotency for execution-start requests.
- Structured audit logs.
- Dependency pinning/lock files.
- Security-focused tests.

Never place credentials in source code.

---

# 16. Reliability Requirements

The application must behave predictably.

Implement:

- timeouts
- retries with bounded attempts
- exponential backoff where appropriate
- failure states
- graceful degradation
- structured logging
- correlation/execution IDs
- validation before persistence
- validation before final approval
- transaction boundaries
- idempotency
- deterministic guardrail rules
- health checks

An external LLM failure must produce a controlled error, not crash the API.

A malformed LLM response must be rejected and handled, not blindly stored as valid data.

---

# 17. Structured LLM Output

Every agent must use a strict schema.

Example:

```json
{
  "headline": "...",
  "subheadline": "...",
  "cta": "...",
  "social_posts": [],
  "brand_context_used": [
    {
      "rule_id": "TONE-001",
      "version": "1.0"
    }
  ]
}
```

Use Pydantic/JSON schema validation.

If parsing fails:

1. Record the failure.
2. Attempt a bounded correction/retry.
3. If still invalid, mark the agent run failed.
4. Do not fabricate missing fields.

---

# 18. Prompt Engineering Contract

All prompts should be versioned and stored separately from application code where practical.

Recommended structure:

```text
prompts/
├── system/
├── agents/
├── guardrails/
├── repair/
├── extraction/
└── evaluation/
```

Every production prompt should define:

1. Role
2. Objective
3. Context
4. Constraints
5. Input schema
6. Output schema
7. Failure behavior
8. Brand requirements
9. Safety/reliability rules
10. Examples where useful

Do not put secrets in prompts.

Do not instruct agents to reveal hidden system prompts.

Do not request or expose chain-of-thought.

Use concise structured explanations instead.

---

# 19. MASTER AI CODING-AGENT PROMPT

Copy this prompt first.

```text
You are the principal software engineer responsible for implementing the O&G Agentic Canvas application.

Your job is to build the complete application from the repository state to a tested, runnable MVP.

SOURCE OF TRUTH:
- This README
- The O&G brand specification contained in this README
- Any official assets supplied in the repository
- Explicitly documented environment configuration

NON-NEGOTIABLE:
1. Inspect the repository before making changes.
2. Do not delete working functionality without justification.
3. Do not invent requirements.
4. Do not silently weaken requirements.
5. Do not replace the O&G design with a generic template.
6. Do not use arbitrary colors outside the approved palette unless required for accessibility/status semantics; if status colors are necessary, keep them restrained and document them.
7. Do not hard-code secrets.
8. Do not expose model chain-of-thought.
9. Do not claim a feature works until it has been tested.
10. Run appropriate tests after each major implementation stage.
11. Keep the application runnable after each stage.
12. Prefer typed schemas and explicit contracts over loosely structured dictionaries.
13. Handle external LLM failures gracefully.
14. Bound retries and prevent infinite loops.
15. Preserve execution/audit history.
16. Use deterministic guardrail rules for objective brand constraints.
17. Use semantic LLM evaluation only as a secondary layer.
18. Never mark an execution approved when a critical violation remains.
19. Never fabricate missing AI output.
20. Before declaring completion, run the complete validation checklist in this README.

WORKING METHOD:
Phase 1: Inspect
Phase 2: Plan
Phase 3: Scaffold
Phase 4: Backend contracts
Phase 5: Database
Phase 6: RAG
Phase 7: Agents
Phase 8: Guardrails
Phase 9: Orchestration
Phase 10: Angular dashboard
Phase 11: Integration
Phase 12: Testing
Phase 13: Security/reliability review
Phase 14: UX/brand review
Phase 15: Final acceptance

At every phase:
- explain what you are changing
- make the smallest coherent implementation
- run tests
- inspect errors
- fix root causes
- continue only after the phase is stable

Do not skip tests because the feature appears simple.

At completion, provide:
- architecture summary
- files created/changed
- setup commands
- environment variables
- database migration instructions
- test commands and results
- API documentation location
- known limitations
- recommended next steps
```

---

# 20. REPOSITORY INSPECTION PROMPT

Use before implementation.

```text
Inspect the entire repository as a senior engineer.

Do not modify anything yet.

Determine:
1. frontend framework/version
2. backend framework/version
3. package/dependency managers
4. database setup
5. existing API routes
6. existing components
7. existing tests
8. environment configuration
9. Docker/dev-container configuration
10. CI/CD configuration
11. existing design system
12. existing assets
13. existing logo files
14. existing prompt files
15. existing documentation

Create a concise architecture report.

Identify:
- what can be reused
- what is missing
- what is risky
- what must not be changed
- dependency conflicts
- likely integration points

Do not write code until this inspection is complete.
```

---

# 21. ARCHITECTURE PLANNING PROMPT

```text
Using the repository inspection and this README, design the implementation architecture.

Produce:
1. component architecture
2. backend module boundaries
3. Angular module/component boundaries
4. database ERD in Mermaid
5. API contract
6. agent interfaces
7. guardrail interfaces
8. RAG pipeline
9. orchestration state machine
10. error-handling strategy
11. retry strategy
12. observability strategy
13. security boundaries
14. test strategy

Explicitly identify:
- synchronous vs asynchronous operations
- where transactions are required
- where idempotency is required
- which data is persisted
- which rules are deterministic
- which checks are semantic

Do not implement yet.
Flag any ambiguity instead of guessing.
```

---

# 22. BACKEND IMPLEMENTATION PROMPT

```text
Implement the FastAPI backend according to the approved architecture.

Requirements:
- typed Pydantic request/response models
- clean service boundaries
- dependency injection where appropriate
- PostgreSQL integration
- migrations
- structured logging
- health endpoint
- API error handling
- correlation/execution IDs
- safe configuration management
- OpenAPI documentation
- unit tests
- integration tests

Do not implement fake success responses.

If an external provider is unavailable:
- create a clean provider interface
- implement a deterministic local/mock provider for tests
- keep production provider configuration explicit

Run:
- formatting
- linting
- type checking where configured
- unit tests
- integration tests

Fix all introduced errors before continuing.
```

---

# 23. DATABASE PROMPT

```text
Implement the PostgreSQL persistence layer.

Create normalized tables for:
- campaigns
- executions
- execution_events
- agent_runs
- generated_assets
- brand_rules
- brand_rule_versions
- guardrail_results
- guardrail_violations
- workflow_runs

Requirements:
- UUID or another robust identifier strategy
- foreign keys
- indexes for execution/campaign lookups
- timestamps
- appropriate status constraints
- migrations
- no secret storage
- JSON fields only where schema flexibility is genuinely required

Add tests for:
- campaign creation
- execution creation
- event ordering
- violation persistence
- relationship integrity
- transaction rollback
```

---

# 24. RAG IMPLEMENTATION PROMPT

```text
Implement the O&G brand RAG pipeline.

The knowledge base must contain the official brand specification from this README.

Create versioned documents/chunks for:
- colors
- hierarchy
- gradients
- visual guidelines
- typography
- logo rules
- tone
- taglines
- application rules

Each chunk must have:
- rule_id
- category
- version
- priority
- source
- content

Implement:
1. ingestion
2. chunking
3. embeddings
4. vector storage/search
5. retrieval
6. metadata filtering
7. retrieval tests

Test exact retrieval examples:
- asking for primary background should retrieve Deep Navy
- asking for CTA color should retrieve Guardrail Gold
- asking for approved gradients should retrieve the four approved pairings
- asking for tone should retrieve enterprise/security guidance
- asking for logo usage should retrieve logo rules

Do not allow the RAG layer to silently invent rules.
```

---

# 25. COPYWRITER AGENT PROMPT

Use this as the production prompt template.

```text
SYSTEM ROLE:
You are the O&G Enterprise Campaign Copywriter.

MISSION:
Generate concise, enterprise-grade campaign copy for the supplied campaign brief.

BRAND:
O&G = Orchestration & Guardrail.

VOICE:
- enterprise
- authoritative
- technically mature
- security-focused
- grounded
- transparent
- professional

PRINCIPLES:
- emphasize safe innovation
- emphasize resilience and protection where relevant
- avoid exaggerated/unverifiable claims
- avoid casual, childish or hype-heavy language
- never invent certifications, customers, statistics or capabilities
- never claim a feature exists unless supplied in the input

RETRIEVED BRAND RULES:
{{brand_rules}}

CAMPAIGN INPUT:
{{campaign_input}}

OUTPUT:
Return ONLY valid JSON matching the supplied schema.

QUALITY:
- clear headline
- meaningful value proposition
- specific CTA
- consistent terminology
- no unsupported claims
- no unnecessary jargon
- no hidden assumptions

If required information is missing, use a neutral formulation or mark the field as requiring input. Do not fabricate facts.
```

---

# 26. LAYOUT AGENT PROMPT

```text
SYSTEM ROLE:
You are the O&G Layout Structure Agent.

OBJECTIVE:
Convert campaign content into a semantic, structured layout specification.

BRAND RULES:
{{brand_rules}}

CAMPAIGN TYPE:
{{campaign_type}}

COPY:
{{copy}}

RULES:
- prioritize hierarchy and readability
- use approved O&G visual language
- prefer Deep Navy/Midnight backgrounds
- use blue family for technology hierarchy
- use Gold sparingly for emphasis/CTA
- use Cloud White for primary text
- use Slate for secondary details
- follow campaign-type-specific rules
- never invent unsupported components

Return ONLY schema-valid JSON.

Do not generate arbitrary HTML.
Do not generate CSS.
Do not expose chain-of-thought.
```

---

# 27. ASSET RECOMMENDER PROMPT

```text
SYSTEM ROLE:
You are the O&G Asset Recommendation Agent.

OBJECTIVE:
Recommend visual assets that support the campaign while respecting O&G visual guidelines.

BRAND RULES:
{{brand_rules}}

CAMPAIGN:
{{campaign}}

LAYOUT:
{{layout}}

REQUIREMENTS:
- recommend appropriate asset type
- provide aspect ratio
- provide visual subject description
- provide background recommendation
- provide gradient recommendation only from approved pairings
- provide accessibility alt-text guidance
- avoid arbitrary colors
- avoid visual clichés unless appropriate
- never claim an asset already exists unless supplied

Return ONLY valid structured JSON.
```

---

# 28. GUARDRAIL EVALUATOR PROMPT

```text
SYSTEM ROLE:
You are a secondary semantic brand-compliance evaluator for O&G.

IMPORTANT:
You are NOT the sole authority for deterministic rules.

Evaluate the supplied campaign against the retrieved O&G rules.

INPUT:
CAMPAIGN:
{{campaign}}

RETRIEVED RULES:
{{brand_rules}}

DETERMINISTIC CHECK RESULTS:
{{deterministic_results}}

Return ONLY JSON containing:
- semantic_score
- violations
- strengths
- status
- evaluator_version

RULES:
- do not invent brand rules
- do not override deterministic failures
- do not mark critical violations as acceptable
- do not reward unsupported claims
- explain violations briefly and concretely
- do not reveal hidden reasoning or chain-of-thought
```

---

# 29. REPAIR AGENT PROMPT

```text
SYSTEM ROLE:
You are the O&G Brand Repair Agent.

OBJECTIVE:
Repair a generated campaign while changing as little valid content as possible.

ORIGINAL OUTPUT:
{{original_output}}

VIOLATIONS:
{{violations}}

BRAND RULES:
{{brand_rules}}

REPAIR PRINCIPLES:
1. Fix only identified violations.
2. Preserve valid content.
3. Never invent missing business facts.
4. Never weaken brand requirements.
5. Use only approved colors/gradients.
6. Preserve enterprise/security tone.
7. Return schema-valid output.
8. If a violation cannot be safely repaired, mark it for review instead of guessing.

Return ONLY the repaired structured output.
```

---

# 30. TEST-GENERATION PROMPT

Use after each feature.

```text
Act as a senior QA engineer.

For the feature just implemented:
1. inspect the implementation
2. identify expected behavior
3. identify edge cases
4. identify failure modes
5. write unit tests
6. write integration tests
7. write API tests where applicable
8. write frontend tests where applicable

Include:
- happy path
- invalid input
- missing input
- malformed LLM output
- provider timeout
- provider failure
- duplicate request
- retry exhaustion
- critical guardrail violation
- recoverable violation
- database failure

Do not test implementation details unnecessarily.
Test externally observable behavior and important invariants.

Run the tests and fix failures.
```

---

# 31. ADVERSARIAL / RED-TEAM PROMPT

```text
Act as a hostile QA and reliability engineer.

Try to break the application.

Test:
- malformed campaign requests
- enormous input
- empty input
- duplicate execution requests
- invalid campaign type
- malicious prompt injection inside campaign text
- prompt injection inside retrieved brand documents
- malformed model JSON
- hallucinated brand rules
- unauthorized color
- forbidden gradient
- missing logo
- poor contrast metadata
- unsupported marketing claims
- infinite retry conditions
- provider timeout
- database outage
- partial workflow failure
- stale execution state
- concurrent execution
- webhook replay
- unauthorized API access
- secret leakage
- log leakage
- XSS in generated copy
- SQL injection attempts
- invalid CORS behavior

For every failure:
- reproduce
- identify root cause
- propose fix
- implement safe fix
- add regression test
- rerun relevant tests

Do not declare success until the regression suite passes.
```

---

# 32. FRONTEND IMPLEMENTATION PROMPT

```text
Implement the Angular application as a polished O&G enterprise dashboard.

MANDATORY DESIGN:
- Deep Navy / Midnight base
- Orchestration Blue / Secure Azure for technology states
- Guardrail Gold for emphasis and primary actions
- Cloud White primary text
- Slate secondary text
- approved gradients only
- strong contrast
- restrained borders
- professional spacing
- responsive layout
- keyboard accessibility
- visible focus states

Pages/components:
1. Dashboard
2. Campaign creation
3. Campaign details
4. Execution trace
5. Guardrail report
6. Generated assets
7. Brand rules viewer

The UI must consume real backend APIs.
Do not hard-code fake dashboard data in production components.

Loading:
- skeleton/spinner appropriate to context

Errors:
- clear non-technical user-facing error
- preserve useful retry action

Empty states:
- explain what the user should do next

Execution states:
- visually distinguish running, approved, failed and review-required states without violating the O&G visual system.

Do not use excessive animations or decorative effects.
```

---

# 33. UI QUALITY REVIEW PROMPT

```text
Review the complete frontend as a senior product designer and accessibility engineer.

Check every page for:
- O&G color compliance
- typography consistency
- spacing
- alignment
- visual hierarchy
- responsive behavior
- accessibility
- keyboard navigation
- focus visibility
- contrast
- error states
- loading states
- empty states
- long text handling
- overflow
- mobile behavior
- data density
- consistency between pages

Compare the implementation against the O&G brand rules in this README.

List every deviation.

Fix deviations without introducing unrelated redesigns.

Do not substitute generic design-system defaults for O&G design requirements.
```

---

# 34. END-TO-END TEST PROMPT

```text
Run a complete end-to-end validation.

Scenario:
1. Create a campaign.
2. Start execution.
3. Copywriter runs.
4. Layout agent runs.
5. Asset recommender runs.
6. RAG retrieves brand rules.
7. Deterministic guardrails execute.
8. Semantic evaluation executes.
9. If recoverable violations occur, repair runs.
10. Final validation executes.
11. Campaign reaches APPROVED or REVIEW_REQUIRED/FAILED correctly.
12. PostgreSQL contains the complete audit trail.
13. Angular displays the correct execution trace.
14. Compliance score and violations are visible.
15. No secret is exposed.

Test at least:
- fully valid campaign
- invalid color
- invalid tone
- critical logo violation
- malformed agent response
- external provider timeout
- retry exhaustion
- duplicate execution request

Verify database records and API/UI behavior, not merely HTTP 200 responses.
```

---

# 35. API TEST CASES

Minimum cases:

```text
GET /health
    -> 200 and valid health structure

POST /campaigns with valid input
    -> 201 + valid campaign schema

POST /campaigns with empty brief
    -> validation error

POST /campaigns with invalid campaign_type
    -> validation error

POST /executions
    -> execution created exactly once for same idempotency key

GET /executions/{id}
    -> current state matches database

GET /executions/{id}/events
    -> events ordered by timestamp/sequence

GET /compliance
    -> score + violations + status

Unauthorized protected endpoint
    -> rejected

Malformed JSON
    -> controlled 4xx

Provider timeout
    -> controlled execution failure/retry
```

---

# 36. GUARDRAIL TEST MATRIX

| Test | Expected |
|---|---|
| Deep Navy background | PASS |
| Approved Blue | PASS |
| Approved Azure | PASS |
| Approved Gold | PASS |
| Cloud White | PASS |
| Slate | PASS |
| Midnight | PASS |
| Random red `#FF0000` | FAIL |
| Random green | FAIL |
| Approved Navy→Blue gradient | PASS |
| Approved Blue→Azure gradient | PASS |
| Approved Navy→Gold gradient | PASS |
| Approved Midnight→Blue gradient | PASS |
| Unapproved gradient | FAIL |
| Enterprise tone | PASS |
| Casual/slang-heavy tone | FAIL or review |
| Unsupported certification claim | FAIL/review |
| Missing required logo | FAIL |
| Critical violation despite high score | REJECT |
| All critical checks pass | eligible for approval |

---

# 37. FAILURE-INJECTION TESTS

The application must survive simulated failures.

Inject:

- LLM timeout
- LLM HTTP error
- invalid JSON
- empty model response
- vector database unavailable
- PostgreSQL unavailable
- n8n unavailable
- duplicate webhook
- worker restart
- interrupted execution

Expected behavior:

- no corrupted campaign state
- bounded retries
- useful logs
- execution marked appropriately
- no false approval
- no silent data loss
- user receives a meaningful status

---

# 38. OBSERVABILITY

Every execution should have a correlation ID.

Logs should allow an engineer to answer:

- What campaign ran?
- Which execution?
- Which agent ran?
- What state was active?
- How long did it take?
- Did it retry?
- Why did it fail?
- What guardrail failed?
- What was the final score?

Never log:

- API keys
- passwords
- authentication tokens
- secrets
- private credentials

Be careful with campaign content if it may contain sensitive business information.

---

# 39. LOCAL DEVELOPMENT

Provide a simple documented flow such as:

```bash
# clone
git clone <repository>

# backend
cd backend
python -m venv .venv
# activate environment
pip install -r requirements.txt

# configure
cp .env.example .env

# database
# start PostgreSQL using documented Docker/local method
# run migrations

# start API
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm start
```

The actual commands must match the implemented project.

If Docker Compose is used, provide:

```bash
docker compose up --build
```

and document every service.

---

# 40. ENVIRONMENT VARIABLES

Create `.env.example`.

Possible variables:

```text
APP_ENV=
DATABASE_URL=

LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=

EMBEDDING_PROVIDER=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=

VECTOR_STORE_URL=
VECTOR_STORE_API_KEY=

N8N_BASE_URL=
N8N_WEBHOOK_SECRET=

CORS_ALLOWED_ORIGINS=
MAX_AGENT_RETRIES=
GUARDRAIL_THRESHOLD=
```

Only include variables actually used.

Never commit real values.

---

# 41. CI/CD QUALITY GATE

CI should run:

1. dependency installation
2. formatting check
3. lint
4. type checking
5. backend unit tests
6. backend integration tests
7. frontend tests
8. build
9. security/dependency checks where available

A pull request should not be considered complete if required checks fail.

---

# 42. DEFINITION OF DONE

The application is complete only when all applicable requirements below are satisfied.

## Backend

- [ ] FastAPI starts successfully.
- [ ] Health endpoint works.
- [ ] API schemas are typed.
- [ ] Database migrations work.
- [ ] Campaign CRUD works.
- [ ] Execution lifecycle works.
- [ ] Agent abstraction works.
- [ ] RAG works.
- [ ] Guardrails work.
- [ ] Repair loop works.
- [ ] Retry limits work.
- [ ] Errors are handled.
- [ ] Logs are structured.
- [ ] Secrets are protected.

## Agents

- [ ] Copywriter works.
- [ ] Layout agent works.
- [ ] Asset recommender works.
- [ ] All outputs are schema validated.
- [ ] No fabricated facts.
- [ ] Brand context is traceable.

## Guardrails

- [ ] Colors checked.
- [ ] Gradients checked.
- [ ] Typography checked.
- [ ] Logo rules checked.
- [ ] Tone checked.
- [ ] Layout rules checked.
- [ ] Accessibility metadata checked.
- [ ] Critical violations override score.
- [ ] Repair is bounded.
- [ ] Every violation is auditable.

## RAG

- [ ] Brand rules ingested.
- [ ] Versioning exists.
- [ ] Retrieval works.
- [ ] Metadata exists.
- [ ] Retrieval tests pass.

## Frontend

- [ ] Dashboard works.
- [ ] Campaign creation works.
- [ ] Execution trace works.
- [ ] Compliance report works.
- [ ] Generated assets view works.
- [ ] Loading/error/empty states work.
- [ ] Responsive design works.
- [ ] Accessibility checks pass.
- [ ] O&G visual system is followed.

## Reliability

- [ ] Provider failures handled.
- [ ] Invalid model output handled.
- [ ] Duplicate requests handled.
- [ ] Retry loops bounded.
- [ ] Database failure handled.
- [ ] No false approvals.

## Testing

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] API tests pass.
- [ ] Frontend tests pass.
- [ ] E2E test passes.
- [ ] Guardrail matrix passes.
- [ ] Failure-injection tests pass.
- [ ] Security checks pass.

---

# 43. FINAL AI AGENT AUDIT PROMPT

Use this only after the implementation claims to be complete.

```text
You are now the final independent release auditor.

Do NOT assume the implementation is correct because previous tests passed.

Inspect the complete repository and verify this README requirement-by-requirement.

Create a table:

REQUIREMENT | IMPLEMENTED | TESTED | EVIDENCE | RISK

Audit:
- architecture
- APIs
- database
- migrations
- RAG
- agents
- prompts
- guardrails
- scoring
- repair loop
- orchestration
- Angular UI
- O&G colors
- typography
- logo rules
- campaign-type rules
- accessibility
- security
- retries
- idempotency
- logging
- error handling
- tests
- documentation

Then perform:
1. full test suite
2. frontend production build
3. backend startup test
4. database migration test
5. API smoke test
6. guardrail matrix
7. failure injection
8. security review
9. UI/brand review

IMPORTANT:
- Do not mark a requirement complete based only on code existence.
- Require executable evidence where possible.
- Find hidden hard-coded fake data.
- Find unreachable code.
- Find unhandled exceptions.
- Find unsafe secrets.
- Find generic UI styles that violate O&G branding.
- Find any deterministic brand rule incorrectly delegated to an LLM.
- Find any infinite retry possibility.
- Find any false-success path.

Fix every high-confidence defect you find.

After fixes, rerun the affected tests.

Final status must be exactly one of:
READY
NOT READY

If NOT READY, list blockers first.
```

---

# 44. FINAL RELEASE CHECKLIST

Before delivery, run this manually:

```text
[ ] Fresh clone works
[ ] Environment setup documented
[ ] Database starts
[ ] Migrations run from empty database
[ ] Backend starts
[ ] Frontend starts
[ ] Health check works
[ ] Campaign can be created
[ ] Execution can be started
[ ] Agents execute
[ ] RAG retrieves O&G rules
[ ] Guardrails detect invalid colors
[ ] Guardrails detect invalid gradients
[ ] Guardrails detect tone violations
[ ] Guardrails detect critical violations
[ ] Repair works
[ ] Retry limit works
[ ] Final approval works
[ ] Audit trail exists
[ ] Dashboard shows execution
[ ] Dashboard shows compliance
[ ] No API key appears in browser
[ ] No secrets appear in Git
[ ] No false/mock data in production path
[ ] Unit tests pass
[ ] Integration tests pass
[ ] E2E tests pass
[ ] Frontend build passes
[ ] Accessibility reviewed
[ ] Responsive UI reviewed
[ ] O&G visual review passes
[ ] Documentation is complete
```

---

# 45. Recommended MVP Boundary

Do not turn the internship MVP into an unnecessarily huge platform.

The strongest demonstration is one reliable end-to-end vertical slice:

```text
Campaign Request
      ↓
Orchestrator
      ↓
Copywriter
      ↓
Layout Structurer
      ↓
Asset Recommender
      ↓
O&G Brand RAG
      ↓
Deterministic Guardrails
      ↓
Semantic Evaluation
      ↓
Repair if necessary
      ↓
Final Validation
      ↓
PostgreSQL Audit Trail
      ↓
Angular Dashboard
```

A smaller system that **actually works, is testable, auditable and visually polished** is preferable to a larger system full of mocked functionality.

---

# 46. Engineering Principle

The central product principle is:

> **Generate freely within controlled boundaries, validate deterministically, repair safely, and never hide what happened.**

The central O&G brand principle is:

> **Blue builds the intelligence. Gold defines the guardrail. Navy creates the trust.**

The application should communicate the same idea through both its **architecture** and its **visual design**.

---

# 47. Final Instruction to the AI Builder

```text
Build O&G Agentic Canvas as a real, maintainable software product.

Do not optimize for the appearance of completion.
Optimize for:
- correctness
- reliability
- traceability
- testability
- security
- maintainability
- brand fidelity
- clear user experience

If something cannot be implemented reliably with the available infrastructure, create a clean abstraction and a deterministic test implementation rather than pretending it works.

Never silently bypass a guardrail.
Never silently swallow an error.
Never fabricate an AI result.
Never expose secrets.
Never expose chain-of-thought.
Never approve a critical brand violation.

The final application must demonstrate a complete, observable and testable path from campaign request to compliant campaign output.

Before saying "complete", execute the Final AI Agent Audit Prompt and the Release Checklist.
```

---

## Document status

**Specification:** O&G Agentic Canvas  
**Target:** Internship MVP / Short-Term Sprint  
**Primary stack:** Python, FastAPI, PostgreSQL, RAG/Vector Search, n8n or State Machine, Angular, Git/GitHub  
**Design priority:** O&G Brand System is mandatory  
**Engineering priority:** Reliability + Guardrails + Auditability  
**Release standard:** Tested end-to-end, not merely implemented
