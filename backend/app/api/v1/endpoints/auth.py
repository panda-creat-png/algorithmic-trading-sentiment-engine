from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, LoginRequest
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register New User")
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registers a new user account with hashed password and returns access JWT token."""
    email_clean = payload.email.lower().strip()
    
    # Check if user already exists
    stmt = select(User).where(User.email == email_clean)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Create new user
    hashed = get_password_hash(payload.password)
    user = User(
        email=email_clean,
        hashed_password=hashed,
        full_name=payload.full_name or email_clean.split("@")[0].capitalize(),
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Generate token
    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser
        }
    )


@router.post("/login", response_model=Token, summary="Login and Obtain JWT")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticates user with email and password and returns signed JWT access token."""
    email_clean = payload.email.lower().strip()
    stmt = select(User).where(User.email == email_clean)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account."
        )

    token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser
        }
    )


@router.get("/me", response_model=UserResponse, summary="Get Current Authenticated User")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Returns profile information for the currently authenticated user."""
    return current_user
