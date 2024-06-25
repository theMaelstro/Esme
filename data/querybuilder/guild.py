from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import CONN
from data.mappings.erupe import (
    Guilds
)
from data.mappings.custom.views import (
    GuildCharactersByGuildId
)
class GuildBuilder():
    def __init__(self) -> None:
        self.db = CONN

    async def select_guilds(self, session):
        """Select Guild rows"""
        stmt = select(Guilds).options(
            load_only(Guilds.id, Guilds.name)
        ).order_by(Guilds.id)
        #).order_by(Guilds.id).offset(0).limit(10)
        rows = await self.db.select_objects(session, stmt)
        return rows

    async def select_guild_characters_by_guild_id(self, session, guild_id):
        """Select guild characters by their guild id"""
        stmt = select(
            GuildCharactersByGuildId
        ).options(
            load_only(
                GuildCharactersByGuildId.id,
                GuildCharactersByGuildId.name,
                GuildCharactersByGuildId.joined_at_epoch
            )

        ).where(
            GuildCharactersByGuildId.guild_id == guild_id
        ).order_by(
            GuildCharactersByGuildId.id
        )

        rows = await self.db.select_objects(session, stmt)
        return rows


    async def update_guild_leader(self, session, guild_id, leader_id):
        stmt = (
            update(Guilds)
            .where(Guilds.id == guild_id)
            .values(leader_id=leader_id)
        )
        await self.db.update_objects(session, stmt)
