"""O&G Agentic Canvas - Pytest Configuration and Fixtures."""

import asyncio
import os
import pytest

# Ensure testing environment before loading settings
os.environ["APP_ENV"] = "testing"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_ong_canvas.db"
os.environ["DATABASE_URL_SYNC"] = "sqlite:///./test_ong_canvas.db"

from app.config import get_settings
get_settings.cache_clear()

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    from app.db.session import engine, Base, async_session_factory
    from app.db.models import User, UserRole, BrandRule
    from app.core.security import hash_password
    from app.rag.brand_knowledge import get_brand_rules
    from sqlalchemy import select

    async def _init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with async_session_factory() as session:
            admin_user = User(
                email="admin@oandg.ai",
                hashed_password=hash_password("AdminPass123!"),
                full_name="O&G Enterprise Admin",
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin_user)
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

    asyncio.run(_init_models())
    yield
    # Cleanup test db file after session if needed
    if os.path.exists("./test_ong_canvas.db"):
        try:
            os.remove("./test_ong_canvas.db")
        except Exception:
            pass

