"""
PSQL Connector
"""
from __future__ import annotations
import os
from asyncpg.exceptions import DuplicateTableError

from sqlalchemy import exc
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from data.mappings import Discord

class Connector:
    """Database Connection object."""
    def __init__(self) -> None:
        self.url_object = URL.create(
            "postgresql+asyncpg",
            username=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
        )
        self.engine = None

    async def open_connection(self) -> None:
        """Estabilish connection with database."""
        try:
            # Create engine.
            self.engine = create_async_engine(self.url_object, echo=True)

            # Connect to database
            async with self.engine.begin() as conn:
                # Attempt to create discord registration table.
                print("INFO", "Checking if Discord table exists.")
                await conn.run_sync(Discord.__table__.create)
                print("INFO", "Discord Table created because it was not found.")

        except exc.ProgrammingError as e:
            if isinstance(e.orig.__cause__, DuplicateTableError):
                print("INFO", "Discord table exists, skipping.")
            else:
                print("ERROR: ", e)

        except exc.SQLAlchemyError as e:
            print("ERROR: ", e)

        finally:
            await self.engine.dispose()

    async def select_object(
        self,
        session: async_sessionmaker[AsyncSession],
        stmt,
    ) -> None:
        """Select all rows."""
        try:
            #async with self.engine.begin() as conn:
            #    await conn.run_sync(Base.metadata.create_all)

            result = await session.execute(stmt)
            return result.scalar_one_or_none()

        except exc.SQLAlchemyError as e:
            print(e)

    async def select_objects(
        self,
        session: async_sessionmaker[AsyncSession],
        stmt,
    ) -> None:
        """Select all rows."""
        try:
            #async with self.engine.begin() as conn:
            #    await conn.run_sync(Base.metadata.create_all)

            result = await session.execute(stmt)
            return result.scalars().all()

        except exc.SQLAlchemyError as e:
            print(e)

    async def update_objects(
        self,
        session: async_sessionmaker[AsyncSession],
        stmt
    ) -> None:
        """Update cell."""
        try:
            await session.execute(stmt)

        except exc.SQLAlchemyError as e:
            print(e)

    async def insert_objects(
        self,
        session: async_sessionmaker[AsyncSession],
        values
    ) -> None:
        """Insert values into table."""
        try:
            session.add_all(values)

        except exc.SQLAlchemyError as e:
            print(e)

CONN = Connector()

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
