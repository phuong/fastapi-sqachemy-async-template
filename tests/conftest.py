import asyncio
from typing import Generator

import pytest
from httpx import AsyncClient
from main import app
from sqlalchemy import event
from sqlalchemy.engine import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from core.context import request_context
from core.db.base import engine


@pytest.fixture(scope="session")
def event_loop(request) -> asyncio.AbstractEventLoopPolicy:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db() -> AsyncSession:
    connection = await engine.connect()
    session = AsyncSession(bind=connection, expire_on_commit=False, future=True)
    yield session
    await connection.close()


@pytest.fixture
def db_context(db: AsyncSession) -> None:
    token = request_context.init()
    request_context.set("db", db)
    yield
    request_context.reset(token)


@pytest.fixture
async def client(db) -> Generator[AsyncClient, None, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
