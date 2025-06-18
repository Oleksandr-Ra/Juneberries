from asyncio import current_task

from sqlalchemy.ext.asyncio import (create_async_engine, AsyncEngine, async_sessionmaker,
                                    AsyncSession, async_scoped_session)

from config import DatabaseConfig


class DatabaseHelper:
    def __init__(
            self,
            url: str,
            echo: bool = False,
            echo_pool: bool = False,
            pool_size: int = 5,
            max_overflow: int = 10,
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def session_dependency(self) -> AsyncSession:
        async with self.session_factory() as session:
            yield session
            await session.close()

    async def scoped_session_dependency(self) -> AsyncSession:
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.remove()


def create_db_helper(config: DatabaseConfig) -> DatabaseHelper:
    return DatabaseHelper(
        url=str(config.url),
        echo=config.echo,
        echo_pool=config.echo_pool,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
    )
