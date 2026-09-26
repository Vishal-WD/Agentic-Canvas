"""O&G Agentic Canvas - Authentication Routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User, UserRole
from app.db.session import get_db
from app.schemas.auth import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new enterprise user."""
    email_clean = data.email.lower().strip()
    existing = await db.execute(select(User).where(User.email == email_clean))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    role_val = data.role.value if hasattr(data.role, "value") else str(data.role)

    user = User(
        email=email_clean,
        hashed_password=hash_password(data.password),
        full_name=data.full_name.strip(),
        role=role_val,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": role_str})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate with email and password to receive a JWT access token."""
    email_clean = data.email.lower().strip()
    result = await db.execute(select(User).where(User.email == email_clean))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated",
        )

    role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": role_str})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """Get profile of currently logged-in user."""
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=TokenResponse)
@router.patch("/me", response_model=TokenResponse)
async def update_my_profile(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile details (name, email, role, password)."""
    if data.email is not None:
        new_email = data.email.lower().strip()
        if new_email != current_user.email:
            existing = await db.execute(select(User).where(User.email == new_email))
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this email already exists",
                )
            current_user.email = new_email

    if data.full_name is not None:
        name_clean = data.full_name.strip()
        if len(name_clean) >= 2:
            current_user.full_name = name_clean

    if data.role is not None:
        role_val = data.role.value if hasattr(data.role, "value") else str(data.role)
        current_user.role = role_val

    if data.password:
        current_user.hashed_password = hash_password(data.password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    role_str = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    new_token = create_access_token({"sub": str(current_user.id), "email": current_user.email, "role": role_str})

    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        user=UserResponse.model_validate(current_user),
    )

