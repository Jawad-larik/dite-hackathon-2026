import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import jwt
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from ...models.database import get_db, DBUser
from ...models.schemas import AuthRequest, AuthResponse, UserResponse
from ...config import settings

logger = logging.getLogger("hr_bot.auth")

router = APIRouter()

def hash_password(password: str) -> str:
    """Hashes password with bcrypt (capped at 72 bytes)."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False

def create_access_token(user_id: str, email: str) -> str:
    """Generates 24-hour HS256 JWT."""
    secret = settings.JWT_SECRET
    payload = {
        "user_id": str(user_id),
        "sub": str(user_id),
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc)
    }
    return jwt.encode(payload, secret, algorithm="HS256")

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    FastAPI dependency: extracts and validates Bearer JWT from Authorization header.
    Returns dict: {'id': user_id, 'email': email}.
    Raises HTTP 401 on missing, expired, or invalid tokens.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Use 'Bearer <token>'"
        )

    token = parts[1]
    secret = settings.JWT_SECRET
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("user_id") or payload.get("sub")
        email = payload.get("email")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing user identifier"
            )
        return {"id": str(user_id), "email": email or ""}
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )


@router.post("/signup", response_model=AuthResponse)
def signup(payload: AuthRequest, db: Session = Depends(get_db)):
    """Registers a new user with unique email and bcrypt password hash."""
    clean_email = payload.email.strip().lower()
    if not clean_email or "@" not in clean_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valid email address is required"
        )
    if not payload.password or len(payload.password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 4 characters"
        )

    # Check for existing user
    existing_user = db.query(DBUser).filter(DBUser.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please log in."
        )

    # Create new user
    pwd_hash = hash_password(payload.password)
    user_id = str(uuid.uuid4())
    user = DBUser(
        id=user_id,
        email=clean_email,
        password_hash=pwd_hash,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user)
    db.commit()

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        token=token,
        user=UserResponse(id=user.id, email=user.email)
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: AuthRequest, db: Session = Depends(get_db)):
    """Authenticates existing user and issues 24-hour JWT."""
    clean_email = payload.email.strip().lower()
    user = db.query(DBUser).filter(DBUser.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        token=token,
        user=UserResponse(id=user.id, email=user.email)
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"]
    )

