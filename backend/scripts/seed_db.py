"""O&G Agentic Canvas - Database Seed Script.

Seeds the database with brand rules from the knowledge base.
"""

import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.db.models import BrandRule
from app.db.session import Base
from app.rag.brand_knowledge import BRAND_RULES


async def seed_database():
    """Create tables and seed brand rules."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=True)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed brand rules idempotently
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        from sqlalchemy import delete
        await session.execute(delete(BrandRule))
        for rule_data in BRAND_RULES:
            rule = BrandRule(
                rule_id=rule_data["rule_id"],
                category=rule_data["category"],
                version=rule_data["version"],
                priority=rule_data["priority"],
                source=rule_data["source"],
                content=rule_data["content"],
                active=True,
            )
            session.add(rule)

        await session.commit()
        print(f"[OK] Seeded {len(BRAND_RULES)} brand rules")

        # Seed default admin user
        from app.db.models import User, UserRole
        from app.core.security import hash_password
        from sqlalchemy import select

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
            print("[OK] Seeded default admin user: admin@oandg.ai / AdminPass123!")

    await engine.dispose()
    print("[OK] Database seeded successfully")


if __name__ == "__main__":
    asyncio.run(seed_database())
