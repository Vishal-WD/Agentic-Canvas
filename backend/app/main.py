"""O&G Agentic Canvas - FastAPI Application Entry Point."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import auth, brand, campaigns, dashboard, executions, health, webhook
from app.config import get_settings
from app.logging_config import get_logger, setup_logging

settings = get_settings()
setup_logging("INFO" if settings.app_env.value != "production" else "WARNING")
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("app_starting", env=settings.app_env.value, version=settings.app_version)

    # Ingest brand rules on startup
    try:
        from app.rag.retrieval import BrandRAGService
        rag = BrandRAGService()
        count = rag.ingest_brand_rules()
        logger.info("brand_rules_loaded", count=count)
    except Exception as e:
        logger.warning("brand_rules_ingestion_skipped", error=str(e))

    # Seed default admin user and brand rules if missing
    try:
        from app.db.session import async_session_factory, Base, engine
        from app.db.models import User, UserRole, BrandRule
        from app.core.security import hash_password
        from app.rag.brand_knowledge import get_brand_rules
        from sqlalchemy import select

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session_factory() as session:
            user_res = await session.execute(select(User).where(User.email == "admin@oandg.ai"))
            if not user_res.scalar_one_or_none():
                admin_user = User(
                    email="admin@oandg.ai",
                    hashed_password=hash_password("AdminPass123!"),
                    full_name="O&G Enterprise Admin",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                session.add(admin_user)
                await session.commit()
                logger.info("demo_admin_seeded", email="admin@oandg.ai")

            rule_res = await session.execute(select(BrandRule).limit(1))
            if not rule_res.scalar_one_or_none():
                rules_data = get_brand_rules()
                for r in rules_data:
                    session.add(BrandRule(
                        rule_id=r["rule_id"],
                        category=r["category"],
                        version=r.get("version", "1.0"),
                        priority=r.get("priority", "medium"),
                        source=r.get("source", "O&G Brand Kit"),
                        content=r["content"],
                        active=True,
                    ))
                await session.commit()
                logger.info("demo_brand_rules_seeded", count=len(rules_data))
    except Exception as e:
        logger.warning("db_seeding_skipped", error=str(e))

    yield

    logger.info("app_shutting_down")


app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description=(
        "Agentic Canvas Platform — Autonomous Multi-Agent Content Orchestration Engine. "
        "Enterprise-grade AI campaign generation with brand guardrails, "
        "deterministic validation, and complete audit trails."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    max_age=600,
)

# ─── Routes ───────────────────────────────────────────────────────
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(executions.router, prefix="/api")
app.include_router(brand.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")



# ─── Global Error Handler ────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions — never expose internals to clients."""
    logger.error(
        "unhandled_exception",
        path=str(request.url.path),
        method=request.method,
        error=str(exc),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again.",
            "error_type": "internal_server_error",
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found."},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env.value == "development",
    )
