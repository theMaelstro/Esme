"""
PSQL Connector
"""
from __future__ import annotations
import os
import logging

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
            self.engine = create_async_engine(self.url_object, echo=False, hide_parameters=True)

            # Connect to database
            async with self.engine.begin() as conn:
                # Attempt to create discord registration table.
                logging.info("Checking if Discord table exists.")
                await conn.run_sync(Discord.__table__.create)
                logging.info("Discord Table created because it was not found.")

        except exc.ProgrammingError as e:
            if isinstance(e.orig.__cause__, DuplicateTableError):
                logging.info("Discord table exists, skipping.")
            else:
                logging.error(e)

        except exc.SQLAlchemyError as e:
            logging.error(e)

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
            logging.error(e)

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

        except exc.ProgrammingError as e:
            logging.error(e.orig.__cause__)

        except exc.SQLAlchemyError as e:
            logging.error(e)

    async def update_objects(
        self,
        session: async_sessionmaker[AsyncSession],
        stmt
    ) -> None:
        """Update cell."""
        try:
            await session.execute(stmt)

        except exc.SQLAlchemyError as e:
            logging.error(e)

    async def insert_objects(
        self,
        session: async_sessionmaker[AsyncSession],
        values
    ) -> None:
        """Insert values into table."""
        try:
            session.add_all(values)

        except exc.SQLAlchemyError as e:
            logging.error(e)

CONN = Connector()
