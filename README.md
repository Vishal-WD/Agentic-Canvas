# O&G Agentic Canvas

> **Autonomous Multi-Agent Content Orchestration Engine**

Enterprise-grade AI campaign generation with brand guardrails, deterministic validation, and complete audit trails.

> *Blue builds the intelligence. Gold defines the guardrail. Navy creates the trust.*

## Architecture

```
User → Angular Dashboard → FastAPI Backend → Orchestrator
                                                 ↓
                                    Copywriter Agent
                                    Layout Structurer Agent
                                    Asset Recommender Agent
                                                 ↓
                                    Brand RAG (ChromaDB)
                                                 ↓
                                    Deterministic Guardrails
                                    Semantic Evaluator
                                                 ↓
                                    Repair Loop (bounded)
                                                 ↓
                                    PostgreSQL Audit Trail
```

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
# Edit .env with your OPENAI_API_KEY (optional — mock provider works without it)

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
