# O&G Agentic Canvas

> **Autonomous Multi-Agent Content Orchestration Engine**

Enterprise-grade AI campaign generation with brand guardrails, deterministic validation, and complete audit trails.

> *Blue builds the intelligence. Gold defines the guardrail. Navy creates the trust.*

## Architecture & Agentic Approach

The engine implements an **autonomous multi-agent orchestration pipeline** grounded by Retrieval-Augmented Generation (RAG) and safeguarded by deterministic validation and an LLM-driven self-repair loop.

```
User Campaign Brief
        ↓
Brand RAG Retrieval (ChromaDB)
        ↓
1. Copywriter Agent (LLM)
        ↓  (passes copy output as context)
2. Layout Structurer Agent (LLM)
        ↓  (passes copy + layout context)
3. Asset Recommender Agent (LLM)
        ↓
Deterministic Guardrails + Semantic Evaluator (LLM)
        ↓
   Passed? ─── No ───→ Repair Loop (Autonomous RepairAgent with LLM, up to N retries)
        │                      │
       Yes ←───────────────────┘
        ↓
PostgreSQL Audit Trail & Angular Dashboard
```

### 1. Multi-Agent Ecosystem
Each agent implements a standardized `BaseAgent` interface with strict Pydantic input/output schemas:

- **Copywriter Agent (`copywriter.py`)**: Synthesizes headlines, subheadlines, value propositions, calls-to-action (CTAs), and social copy strictly adhering to brand tone rules.
- **Layout Structurer Agent (`layout.py`)**: Designs wireframes, section hierarchies, color scheme assignments, and visual component arrangements conditioned on the copy output.
- **Asset Recommender Agent (`asset_recommender.py`)**: Recommends visual asset specifications (hero images, iconography, aspect ratios, color palettes, and alt text) conditioned on copy and layout context.
- **Semantic Evaluator (`semantic.py`)**: Functions as an LLM-as-a-judge evaluator assessing brand consistency, messaging tone, and unsupported claims.
- **Brand Repair Agent (`repair.py`)**: An autonomous self-correction agent that takes identified guardrail violations and rewrites/repairs the generated output while preserving valid content.

### 2. Autonomous Orchestration & Self-Correction Loop
- **Sequential Context Flow**: The `OrchestratorExecutor` runs agents in a deterministic sequence where downstream agents receive validated outputs from upstream agents as context.
- **Dual-Layer Guardrail Validation**: Combines fast deterministic rule checks (color hex validation, banned phrase matching, required fields) with LLM semantic evaluation.
- **Bounded Self-Repair**: If compliance scores fall below threshold or violations occur, the system invokes the `RepairAgent` up to `MAX_REPAIR_ATTEMPTS` times to autonomously resolve issues before marking the execution state.

### 3. LLM Provider Layer
Configured in `llm_provider.py` with multi-provider and fallback support:
- **Google Gemini**: Primary REST API integration featuring exponential backoff, retry logic, and dynamic model fallback (`gemini-2.5-flash` → `gemini-flash-latest` → `gemini-2.5-flash-lite`).
- **OpenAI**: Supported provider for GPT-4o and OpenAI-compatible models.
- **Deterministic Mock Provider**: Fallback provider allowing end-to-end testing and CI/CD validation without requiring external API keys.

### 4. Brand RAG Grounding
- **ChromaDB Vector Store**: Brand guidelines, prohibited claims, color rules, and layout constraints are vectorized and dynamically queried via `BrandRAGService` to inject specific brand rules into each agent's system prompt prior to generation.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)

### 1. Start Database
```bash
docker compose up -d
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your GOOGLE_API_KEY or OPENAI_API_KEY (optional — mock provider works without it)

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 4. Open Dashboard
Navigate to http://localhost:4200

## API Documentation

Interactive API docs available at:
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/campaigns` | Create campaign |
| GET | `/api/campaigns/{id}` | Get campaign |
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns/{id}/executions` | Start execution |
| GET | `/api/executions/{id}` | Get execution |
| GET | `/api/executions/{id}/events` | Get execution events |
| GET | `/api/executions/{id}/compliance` | Get compliance results |
| GET | `/api/campaigns/{id}/assets` | Get generated assets |
| GET | `/api/brand/rules` | Get brand rules |
| GET | `/api/dashboard/summary` | Dashboard metrics |

## Testing

```bash
cd backend
pytest tests/ -v
```

## Environment Variables

See `backend/.env.example` for all configurable variables.

Key variables:
- `LLM_PROVIDER` — `gemini` (default) or `openai` (mock provider used when keys are absent)
- `GOOGLE_API_KEY` — Google Gemini API key (powers `gemini-2.5-flash`)
- `OPENAI_API_KEY` — OpenAI API key (optional alternative)
- `DATABASE_URL` — PostgreSQL connection string (`postgresql+asyncpg://...`)
- `MAX_REPAIR_ATTEMPTS` — Maximum guardrail repair attempts (default: 3)
- `GUARDRAIL_PASS_THRESHOLD` — Minimum score for approval (default: 75.0)

## O&G Brand System

| Color | Hex | Role |
|-------|-----|------|
| Deep Navy | `#0C2140` | Primary background (60%) |
| Orchestration Blue | `#16528D` | Technology elements (20%) |
| Secure Azure | `#2674B8` | Innovation/highlights |
| Guardrail Gold | `#D6B25A` | CTAs, emphasis (10%) |
| Cloud White | `#F5F8FC` | Primary text (10%) |
| Slate | `#5F7188` | Secondary text |
| Midnight | `#071426` | Deep backgrounds |

## License

Internal project — O&G Agentic Canvas Internship MVP.
