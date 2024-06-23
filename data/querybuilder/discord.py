from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import CONN
from data.mappings.custom.tables import (
    Discord
)

class DiscordBuilder():
    def __init__(self) -> None:
        self.db = CONN

    async def check_id(self, session, discord_id: str):
        """Check if discord id is registered."""
        stmt = select(Discord).options(
            load_only(Discord.id)
        ).where(Discord.discord_id == discord_id)
        discord = await self.db.select_object(session, stmt)
        return discord

    async def bind_user_old(self, session, user_id: int, discord_id: str):
        stmt = (
            update(Discord)
            .where(Discord.discord_id == discord_id)
            .values(user_id=user_id)
        )
        await self.db.update_objects(session, stmt)

    async def bind_user_new(self, session, user_id: int, discord_id: str):
        values = [
            Discord(discord_id=discord_id, user_id=user_id)
        ]
        await self.db.insert_objects(session, values)
