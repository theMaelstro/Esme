from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import CONN
from data.mappings.custom.tables import (
    Discord
)

class DiscordBuilder():
    """Query builder class for Discord table."""
    def __init__(self) -> None:
        self.db = CONN

    async def check_id(self, session, discord_id: str):
        """Check if discord id is registered."""
        stmt = select(Discord).options(
            load_only(Discord.id)
        ).where(Discord.discord_id == discord_id)
        discord = await self.db.select_object(session, stmt)
        return discord

    async def select_discord_user(self, session, discord_id: str):
        """Check if discord id is registered."""
        stmt = select(Discord).options(
            load_only(Discord.id, Discord.user_id, Discord.character_id)
        ).where(Discord.discord_id == discord_id)
        discord = await self.db.select_object(session, stmt)
        return discord

    async def bind_user_old(
        self,
        session,
        user_id: int,
        discord_id: str
    ) -> (int | None):
        """Update user_id for existing user."""
        stmt = (
            update(Discord)
            .where(Discord.discord_id == discord_id)
            .values(user_id=user_id)
        )
        return await self.db.update_objects(session, stmt)

    async def bind_user_new(self, session, user_id: int, discord_id: str):
        """Register new user."""
        values = [
            Discord(discord_id=discord_id, user_id=user_id)
        ]
        await self.db.insert_objects(session, values)

    async def update_character(
        self,
        session,
        character_id: int,
        discord_id: str
    ) -> (int | None):
        """Update active character_id for existing user."""
        stmt = (
            update(Discord)
            .where(Discord.discord_id == discord_id)
            .values(character_id=character_id)
        )
        return await self.db.update_objects(session, stmt)
