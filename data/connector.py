"""
PSQL Connector
"""
from __future__ import annotations
import logging
import sys

from asyncpg.exceptions import DuplicateTableError
from sqlalchemy import exc, text
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)

from settings import CONFIG
from data.mappings import (
    Discord,
    GuildCharactersByGuildId,
    GuildApplicationsDetails
)

class Connector:
    """Database Connection object."""
    def __init__(self) -> None:
        self.url_object = None
        self.engine = None

    async def open_connection(self) -> None:
        """Estabilish connection with database."""
        try:
            # Init url object.
            self.url_object = URL.create(
                "postgresql+asyncpg",
                username=CONFIG.database.username,
                password=CONFIG.database.password,
                host=CONFIG.database.host,
                port=CONFIG.database.port,
                database=CONFIG.database.database,
            )

            # Create engine.
            self.engine = create_async_engine(self.url_object, echo=False, hide_parameters=True)

            # Connect to database
            async with self.engine.begin() as conn:
                # Attempt to create discord registration table.
                await conn.execute(text(GuildCharactersByGuildId.__query__))
                logging.info("Guild Characters View prepared.")
                await conn.commit()

            async with self.engine.begin() as conn:
                # Attempt to create discord registration table.
                await conn.execute(text(GuildApplicationsDetails.__query__))
                logging.info("Guild Applications View prepared.")
                await conn.commit()

            async with self.engine.begin() as conn:
                # Attempt to create discord registration table.
                logging.info("Checking if Discord table exists.")
                await conn.run_sync(Discord.__table__.create)
                logging.info("Discord Table created because it was not found.")
                await conn.commit()

        except exc.ProgrammingError as e:
            if isinstance(e.orig.__cause__, DuplicateTableError):
                logging.info("Discord table exists, skipping.")
            else:
                logging.error(e)

        except exc.SQLAlchemyError as e:
            logging.error(e)

        except Exception as e:
            logging.critical("Unhandled database error. Could not connect to postgres: %s", e)
            sys.exit(1)

        finally:
            await self.engine.dispose()

    async def execute_raw(
        self,
        session: async_sessionmaker[AsyncSession],
        stmt: text,
    ) -> None:
        """Execute raw query."""
        try:
            result = await session.execute(stmt)

        except exc.SQLAlchemyError as e:
            logging.error(e)

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
    ) -> (int | None):
        """Update cell."""
        try:
            result = await session.execute(stmt)
            return result.rowcount

        except exc.SQLAlchemyError as e:
            logging.error(e)
        return None

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
