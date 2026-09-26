"""O&G Agentic Canvas - Authentication Schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    BRAND_GUARDIAN = "brand_guardian"
    CAMPAIGN_ARCHITECT = "campaign_architect"
    COMPLIANCE_OFFICER = "compliance_officer"


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: str = Field(..., description="Enterprise email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 chars)")
    full_name: str = Field(..., min_length=2, description="User's full name")
    role: UserRoleEnum = Field(default=UserRoleEnum.CAMPAIGN_ARCHITECT, description="User enterprise role")


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: str = Field(..., description="Enterprise email address")
    password: str = Field(..., description="User password")


class UserUpdateRequest(BaseModel):
    """Request schema for updating current user profile."""
    full_name: Optional[str] = Field(None, min_length=2, description="User's full name")
    email: Optional[str] = Field(None, description="Enterprise email address")
    role: Optional[UserRoleEnum] = Field(None, description="User enterprise role")
    password: Optional[str] = Field(None, min_length=6, description="New password (optional)")


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: uuid.UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
