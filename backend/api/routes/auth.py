from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta

from backend.core.database import get_async_db
from backend.models.user import User
from backend.models import UserCreate, UserResponse, Token
from backend.core.security import get_password_hash, verify_password, create_access_token
from backend.config.enhanced_settings import settings

# --- SHOPIER KEY ACCESS PROTOCOL (NO STRIPE) ---
import os

def validate_shopier_key(user_input_key):
    """
    Validates the user's access key against hardcoded secrets.
    Bypasses Stripe/Database completely for immediate launch.
    """
    
    # 1. THE MASTER KEY (Your Backdoor)
    # Use this to log in yourself for testing/demos
    if user_input_key == "LAZY_MASTER_2025_ADMIN":
        return {
            "valid": True, 
            "plan": "admin_unlimited", 
            "message": "Welcome back, Commander."
        }

    # 2. THE EARLY BIRD KEY (For Customers)
    # The key you email to people who buy on Shopier
    # Change this string every month (e.g., "FEB_ACCESS_2025")
    if user_input_key == "YOUTUBE_AI_EARLY_ACCESS_2025":
        return {
            "valid": True, 
            "plan": "pro_monthly", 
            "message": "Access Granted: Early Bird Tier"
        }
        
    # 3. INVALID KEY
    return {"valid": False, "message": "Invalid Access Key. Please check your purchase email."}

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
    email = "admin@example.com" if "admin" in result["plan"] else "customer@shopier.com"
    stmt = select(User).where(User.email == email)
    db_result = await db.execute(stmt)
    user = db_result.scalars().first()
    
    if not user:
        # Create a proxy user if it doesn't exist (e.g. database was reset)
        user = User(
            email=email,
            username="shopier_user",
            hashed_password="N/A",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

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
