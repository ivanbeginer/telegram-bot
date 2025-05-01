
from pydantic import Secret, PostgresDsn
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
class DataBase:
    def __init__(self,dsn: Secret[PostgresDsn], declarative_base:DeclarativeBase):
        self._engine = create_async_engine(str(dsn))
        self._async_session = async_sessionmaker(self._engine)
        self._declarative_base = declarative_base



    async def shutdown(self)->None:
        await self._engine.dispose()

    async def create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(self._declarative_base.metadata.create_all)



    @asynccontextmanager
    async def session(self)->AsyncGenerator[AsyncSession,None]:
        session: AsyncSession = self._async_session()

        async with session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

