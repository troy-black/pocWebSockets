from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from tdb.poc_websockets.server import config

engine = create_async_engine(
    str(config.settings.ASYNC_POSTGRES_URI),
    echo=config.settings.POSTGRES_ECHO,
    future=True,
    pool_size=max(5, config.settings.POSTGRES_POOL_SIZE),
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as _exception:
            await session.rollback()
            raise
        finally:
            await session.close()
