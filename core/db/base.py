from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings


engine = create_async_engine(settings.DB_DSN, echo=settings.DB_ECHO, future=True, connect_args={"timeout": 15})

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, future=True)

metadata = MetaData()

Base = declarative_base(metadata=metadata)
