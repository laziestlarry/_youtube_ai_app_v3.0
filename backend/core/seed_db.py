import logging
import os
from sqlalchemy import select
import backend.core.database as database
from backend.models.user import User
from backend.core.security import get_password_hash
from backend.core.config import settings

logger = logging.getLogger(__name__)

def _resolve_admin_seed() -> tuple[str, str, str] | None:
    admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD")

    environment = str(getattr(settings, "environment", "")).lower()
    if not admin_password:
        if environment in ("production", "prod"):
            logger.warning("DEFAULT_ADMIN_PASSWORD not set. Skipping admin seed in production.")
            return None
        admin_password = "admin123"
        logger.info("DEFAULT_ADMIN_PASSWORD not set. Using dev default for admin seed.")

    return admin_email, admin_username, admin_password

async def seed_db():
    """Seed the database with initial data (e.g., default admin user)."""
    async with database.AsyncSessionLocal() as db:
        try:
            # Check if admin user exists
            admin_seed = _resolve_admin_seed()
            if not admin_seed:
                return
            admin_email, admin_username, admin_password = admin_seed
            result = await db.execute(select(User).where(User.email == admin_email))
            admin_user = result.scalars().first()
            
            if not admin_user:
                logger.info(f"Admin user {admin_email} not found. Creating...")

                db_user = User(
                    email=admin_email,
                    username=admin_username,
                    hashed_password=get_password_hash(admin_password),
                    is_active=True,
                    is_superuser=True
                )
                db.add(db_user)
                await db.commit()
                logger.info("Default admin user created: %s", admin_email)
            else:
                logger.info(f"Admin user {admin_email} already exists. Skipping seed.")
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await db.rollback()
