"""O&G Agentic Canvas - Authentication Unit & Integration Tests."""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_register_and_login_flow():
    """Test full registration, login, and profile fetching flow."""
    unique_email = f"test_architect_{uuid.uuid4().hex[:8]}@oandg.ai"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register new user
        reg_res = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "StrongPassword123!",
                "full_name": "Test Architect",
                "role": "campaign_architect",
            },
        )
        assert reg_res.status_code == 201
        reg_data = reg_res.json()
        assert "access_token" in reg_data
        assert reg_data["user"]["email"] == unique_email
        assert reg_data["user"]["full_name"] == "Test Architect"

        # 2. Duplicate registration should fail
        dup_res = await client.post(
            "/api/auth/register",
            json={
                "email": unique_email,
                "password": "AnotherPassword123!",
                "full_name": "Duplicate User",
                "role": "brand_guardian",
            },
        )
        assert dup_res.status_code == 409

        # 3. Login with correct credentials
        login_res = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": "StrongPassword123!",
            },
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        assert token

        # 4. Login with incorrect password
        bad_login_res = await client.post(
            "/api/auth/login",
            json={
                "email": unique_email,
                "password": "WrongPassword!",
            },
        )
        assert bad_login_res.status_code == 401

        # 5. Access /api/auth/me with Bearer token
        me_res = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == unique_email
        assert me_data["full_name"] == "Test Architect"

        # 6. Access /api/auth/me without token
        unauth_res = await client.get("/api/auth/me")
        assert unauth_res.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token_rejection():
    """Test that invalid tokens are rejected."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_demo_admin_login():
    """Test that default demo admin account can log in."""
    from app.db.session import async_session_factory
    from app.db.models import User, UserRole
    from app.core.security import hash_password
    from sqlalchemy import select

    # Ensure admin user is in db
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/auth/login",
            json={"email": "admin@oandg.ai", "password": "AdminPass123!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["user"]["email"] == "admin@oandg.ai"
        assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_update_profile_flow():
    """Test updating user profile details (name, email, role, password)."""
    email_a = f"user_a_{uuid.uuid4().hex[:8]}@oandg.ai"
    email_b = f"user_b_{uuid.uuid4().hex[:8]}@oandg.ai"
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user A
        res_a = await client.post(
            "/api/auth/register",
            json={
                "email": email_a,
                "password": "Password123!",
                "full_name": "Original Name",
                "role": "campaign_architect",
            },
        )
        token_a = res_a.json()["access_token"]

        # Register user B
        await client.post(
            "/api/auth/register",
            json={
                "email": email_b,
                "password": "Password123!",
                "full_name": "User B",
                "role": "brand_guardian",
            },
        )

        # 1. Update Full Name and Role
        update_res = await client.put(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token_a}"},
            json={
                "full_name": "Updated Architect Name",
                "role": "brand_guardian",
            },
        )
        assert update_res.status_code == 200
        up_data = update_res.json()
        assert up_data["user"]["full_name"] == "Updated Architect Name"
        assert up_data["user"]["role"] == "brand_guardian"
        new_token = up_data["access_token"]

        # 2. Attempt to update email to existing user B's email (should fail 409)
        conflict_res = await client.put(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
            json={"email": email_b},
        )
        assert conflict_res.status_code == 409

        # 3. Update password and verify login with new password
        pw_res = await client.put(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
            json={"password": "NewSecretPassword999!"},
        )
        assert pw_res.status_code == 200

        login_res = await client.post(
            "/api/auth/login",
            json={"email": email_a, "password": "NewSecretPassword999!"},
        )
        assert login_res.status_code == 200
        assert login_res.json()["user"]["full_name"] == "Updated Architect Name"

