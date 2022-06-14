from typing import cast

from core.context import request_context
from core.db.base import AsyncSession, async_session


async def init_db() -> AsyncSession:
    """Store db session in the context var and reset it"""
    db = async_session()
    request_context.set("db", db)
    try:
        yield db
    finally:
        # Release the connection
        await db.close()


def get_db() -> AsyncSession:
    """Fetch db session from the context var"""
    session = cast(AsyncSession, request_context.get("db"))
    if session is None:
        raise Exception("Missing session")
    return session
