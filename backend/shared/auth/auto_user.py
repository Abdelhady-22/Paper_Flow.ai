"""
Shared — User auto-provisioning utility

Ensures a user record exists for the given user_id before
any foreign-key-dependent operation (chat, upload, summarize, etc.).

In production, this would be replaced by proper authentication.
For demo / local deployment, we auto-create anonymous users.
"""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shared.models.domain import User
from shared.logger.logger import get_logger

logger = get_logger(__name__)


async def ensure_user_exists(session: AsyncSession, user_id: uuid.UUID) -> User:
    """
    Check if a user exists in the database; if not, create one.
    Returns the User object.
    """
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is not None:
        return user

    # Auto-create an anonymous user for demo mode
    user = User(
        id=user_id,
        email=f"anon-{str(user_id)[:8]}@paperflow.local",
        hashed_pwd="not-applicable",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    logger.info("auto_user_created", user_id=str(user_id))
    return user
