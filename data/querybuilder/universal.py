"""
Query Builder module for other tables related queries
that are not contextually tied to other builders.
"""
from sqlalchemy import select, update, delete
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import func

from data.connector import CONN
from data.mappings.erupe import (
    Servers
)

class UniversalBuilder():
    """Query builder class for other tables."""
    def __init__(self) -> None:
        self.db = CONN

    # Server players count
    async def get_players_online(self, session):
        """Select online players sum across all servers."""
        stmt = select(
            func.sum(Servers.current_players)
        )
        row = await self.db.select_object(session, stmt)
        return row

    async def get_players_online_per_land(self, session):
        """Select online players sum per land."""
        stmt = (
            select(
                Servers
            ).options(
                load_only(
                    Servers.world_name,
                    Servers.land,
                    Servers.current_players
                )
            ).order_by(
                Servers.server_id
            )
        )
        rows = await self.db.select_objects(session, stmt)
        return rows
