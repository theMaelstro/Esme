"""
PSQL Connector
"""
from __future__ import annotations
import os

from sqlalchemy import exc
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

# TODO: Move session manager to cogs, each cog opens session for itself and passes it to builder as an argument

class Connector:
    """Database Connection object."""
    def __init__(self) -> None:
        self.url_object = URL.create(
            "postgresql+asyncpg",
            username=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),  # plain (unescaped) text
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database="test",
        )
        self.engine = create_async_engine(self.url_object, echo=True)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def select_object(
        self,
        stmt,
    ) -> None:
        """Select all rows."""
        try:
            #async with self.engine.begin() as conn:
            #    await conn.run_sync(Base.metadata.create_all)

            async with self.async_session() as session:
                result = await session.execute(stmt)

            await self.engine.dispose()

            return result.scalar_one_or_none()
        except exc.SQLAlchemyError as e:
            print(e)

    async def select_objects(
        self,
        stmt,
    ) -> None:
        """Select all rows."""
        try:
            #async with self.engine.begin() as conn:
            #    await conn.run_sync(Base.metadata.create_all)

            async with self.async_session() as session:
                result = await session.execute(stmt)

            await self.engine.dispose()

            return result.scalars().all()
        except exc.SQLAlchemyError as e:
            print(e)

    async def update_objects(
        self,
        stmt
    ) -> None:
        """Update cell."""
        try:
            async with self.async_session() as session:
                await session.execute(stmt)
                await session.commit()
                await session.close()

            await self.engine.dispose()

        except exc.SQLAlchemyError as e:
            print(e)

    async def insert_objects(
        self,
        values
    ) -> None:
        """Insert values into table."""
        try:
            async with self.async_session() as session:
                session.add_all(values)
                await session.commit()
                await session.close()

            await self.engine.dispose()

        except exc.SQLAlchemyError as e:
            print(e)

"""
async def insert_objects(
    async_session: async_sessionmaker[AsyncSession]
) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    A(bs=[B(data="b1"), B(data="b2")], data="a1"),
                    A(bs=[], data="a2"),
                    A(bs=[B(data="b3"), B(data="b4")], data="a3"),
                ]
            )

async def select_and_update_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session:
        stmt = select(A).order_by(A.id).options(selectinload(A.bs))

        result = await session.execute(stmt)

        for a in result.scalars():
            print(a, a.data)
            print(f"created at: {a.create_date}")
            for b in a.bs:
                print(b, b.data)

        result = await session.execute(select(A).order_by(A.id).limit(1))

        a1 = result.scalars().one()

        a1.data = "new data"

        await session.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows
        print(a1.data)

        # alternatively, AsyncAttrs may be used to access any attribute
        # as an awaitable (new in 2.0.13)
        for b1 in await a1.awaitable_attrs.bs:
            print(b1, b1.data)

async def select_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session:
        stmt = select(FestaTrials).order_by(FestaTrials.id)

        result = await session.execute(stmt)

        for row in result.scalars():
            print(row.id, row.objective, row.goal_id, row.times_req, row.locale_req, row.reward)
"""
"""
async def async_main() -> None:
    engine = create_async_engine(url_object, echo=True)

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    #await insert_objects(async_session)
    #await select_and_update_objects(async_session)
    await select_objects(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()

asyncio.run(async_main())
"""
