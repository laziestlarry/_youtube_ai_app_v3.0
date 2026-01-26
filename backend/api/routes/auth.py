from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
import json
import logging
import os
import secrets

from backend.core.database import get_async_db
from backend.models.user import User
from backend.models import UserCreate, UserResponse, Token
from backend.core.security import get_password_hash, verify_password, create_access_token
from backend.config.enhanced_settings import settings

# --- SHOPIER KEY ACCESS PROTOCOL (NO STRIPE) ---
logger = logging.getLogger(__name__)

def _load_shopier_key_map() -> dict:
    key_map: dict[str, dict] = {}
    admin_key = settings.security.admin_secret_key or os.getenv("ADMIN_SECRET_KEY")
    if admin_key:
        key_map[admin_key] = {"plan": "admin_unlimited", "role": "admin"}

    raw_map = os.getenv("SHOPIER_ACCESS_KEY_MAP") or os.getenv("SECURITY_SHOPIER_ACCESS_KEY_MAP")
    if raw_map:
        try:
            mapped = json.loads(raw_map)
            if isinstance(mapped, dict):
                for key, info in mapped.items():
                    if not key:
                        continue
                    if isinstance(info, dict):
                        entry = dict(info)
                    else:
                        entry = {"plan": str(info)}
                    entry.setdefault("plan", "pro_monthly")
                    entry.setdefault("role", "customer")
                    key_map[str(key)] = entry
        except json.JSONDecodeError:
            logger.warning("Invalid SHOPIER_ACCESS_KEY_MAP JSON. Expected a JSON object.")

    raw_keys = os.getenv("SHOPIER_ACCESS_KEYS") or os.getenv("SECURITY_SHOPIER_ACCESS_KEYS")
    if raw_keys:
        for key in [item.strip() for item in raw_keys.split(",") if item.strip()]:
            if key not in key_map:
                key_map[key] = {"plan": "pro_monthly", "role": "customer"}
    return key_map

def validate_shopier_key(user_input_key: str) -> dict:
    """
    Validates the user's access key against configured secrets.
    Bypasses Stripe/Database completely for immediate launch.
    """
    key_map = _load_shopier_key_map()
    if not key_map:
        return {
            "valid": False,
            "message": "Shopier key login disabled. Configure SHOPIER_ACCESS_KEYS or SHOPIER_ACCESS_KEY_MAP."
        }

    entry = key_map.get(user_input_key)
    if not entry:
        return {"valid": False, "message": "Invalid Access Key. Please check your purchase email."}

    return {
        "valid": True,
        "plan": entry.get("plan", "pro_monthly"),
        "role": entry.get("role", "customer"),
        "email": entry.get("email"),
        "username": entry.get("username"),
        "message": entry.get("message", "Access granted.")
    }

# ------------------------------------------------

from pydantic import BaseModel

class KeyLoginRequest(BaseModel):
    access_key: str

router = APIRouter()

@router.post("/login-with-key", response_model=Token)
async def login_with_key(data: KeyLoginRequest, db: AsyncSession = Depends(get_async_db)):
    """
    API endpoint for Shopier Key validation. 
    Bypasses traditional password checks for immediate monetization.
    """
    # 1. Validate against the Guard
    result = validate_shopier_key(data.access_key)

    if not result["valid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result["message"]
        )

    # 2. Map to a system user (Fail-safe: Use or create the shopier_user)
    # This ensures the platform's @get_current_user dependencies still work.
    role = result.get("role", "customer")
    email = result.get("email") or ("admin@example.com" if role == "admin" else "customer@shopier.com")
    username = result.get("username") or ("shopier_admin" if role == "admin" else "shopier_user")
    stmt = select(User).where(User.email == email)
    db_result = await db.execute(stmt)
    user = db_result.scalars().first()
    
    if not user:
        # Create a proxy user if it doesn't exist (e.g. database was reset)
        temp_password = secrets.token_urlsafe(32)
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(temp_password),
            is_active=True,
            is_superuser=(role == "admin")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif role == "admin" and not user.is_superuser:
        user.is_superuser = True
        await db.commit()

    # 3. Issue JWT Token
    access_token_expires = timedelta(seconds=settings.security.jwt_expiration)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """Register a new user."""
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """Login to get access token."""
    # Authenticate user
    # Try by email first, then username if not valid email format (or just use username field from form for either)
    # Standard OAuth2 form has 'username' and 'password' fields.
    
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        # Try email
        stmt = select(User).where(User.email == form_data.username)
        result = await db.execute(stmt)
        user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(seconds=settings.security.jwt_expiration)
    access_token = create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

from backend.api.deps import get_current_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user."""
    return current_user
