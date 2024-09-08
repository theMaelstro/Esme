"""Query Builder module for Guild related queries."""
from sqlalchemy import select, update, delete
from sqlalchemy.orm import load_only
from sqlalchemy.sql.expression import func

from data.connector import CONN
from data.mappings.erupe import (
    Guilds,
    GuildApplications,
    GuildCharacters,
    Characters
)
from data.mappings.custom.tables import (
    Discord
)
from data.mappings.custom.views import (
    GuildCharactersByGuildId,
    GuildApplicationsDetails
)
class GuildBuilder():
    """Query builder class for Guild table."""
    def __init__(self) -> None:
        self.db = CONN

    # Guilds
    async def select_guild(self, session, guild_id: int):
        """Select guild id and name row where id = guild_id."""
        stmt = select(Guilds).options(
            load_only(Guilds.id, Guilds.name)
        ).where(
            Guilds.id == guild_id
        )
        rows = await self.db.select_object(session, stmt)
        return rows

    async def select_guilds(self, session):
        """Select Guild rows"""
        stmt = select(Guilds).options(
            load_only(Guilds.id, Guilds.name)
        ).order_by(Guilds.id)
        #).order_by(Guilds.id).offset(0).limit(10)
        rows = await self.db.select_objects(session, stmt)
        return rows

    async def update_guild_leader(
        self,
        session,
        guild_id,
        leader_id
    ) -> (int | None):
        """Update leader id"""
        stmt = (
            update(Guilds)
            .where(Guilds.id == guild_id)
            .values(leader_id=leader_id)
        )
        return await self.db.update_objects(session, stmt)

    async def select_poogie_outfits(self, session, guild_id: int):
        """Select guild poogie outfits where id = guild_id."""
        stmt = select(Guilds).options(
            load_only(Guilds.id, Guilds.pugi_outfits)
        ).where(
            Guilds.id == guild_id
        )
        rows = await self.db.select_object(session, stmt)
        return rows

    async def update_poogie_outfits(
        self,
        session,
        guild_id: int,
        pugi_outfits: int
    ) -> (int | None):
        """Update poogie outfits."""
        stmt = (
            update(Guilds)
            .where(Guilds.id == guild_id)
            .values(pugi_outfits=pugi_outfits)
        )
        return await self.db.update_objects(session, stmt)

    # Guild Applications


    # Views
    async def select_guild_characters_by_guild_id(self, session, guild_id):
        """Select guild characters by their guild id"""
        stmt = select(
            GuildCharactersByGuildId
        ).options(
            load_only(
                GuildCharactersByGuildId.name,
                GuildCharactersByGuildId.joined_at_epoch,
                GuildCharactersByGuildId.order_index
            )

        ).where(
            GuildCharactersByGuildId.guild_id == guild_id
        ).order_by(
            GuildCharactersByGuildId.order_index
        )

        rows = await self.db.select_objects(session, stmt)
        return rows

    async def select_guild_application_detail_by_id(self, session, application_id: int):
        """Select guild application detail by id"""
        stmt = select(
            GuildApplicationsDetails
        ).where(
            GuildApplicationsDetails.id == application_id
        )

        rows = await self.db.select_object(session, stmt)
        return rows

    async def select_guild_application_by_id(self, session, application_id: int):
        """Select guild application by id"""
        stmt = select(
            GuildApplications
        ).where(
            GuildApplications.id == application_id
        )

        rows = await self.db.select_object(session, stmt)
        return rows

    async def select_recruiter_discord_ids(self, session, guild_id: int):
        """Select guild recruiters."""
        # TODO: Break queries into corresponding builders
        # and use import from for needed methods
        stmt_leader = (
            select(
                Guilds
            )
            .options(
                load_only(Guilds.leader_id)
            )
            .where(
                Guilds.id == guild_id
            )
        )

        stmt_recruiters = (
            select(
                GuildCharacters
            )
            .options(
                load_only(GuildCharacters.character_id)
            )
            .where(
                GuildCharacters.recruiter is True
            )
            .where(
                GuildCharacters.guild_id == guild_id
            )
        )

        character_id_leader = await self.db.select_objects(session, stmt_leader)
        character_id_recruiters = await self.db.select_objects(session, stmt_recruiters)

        character_ids = []
        if character_id_leader is not None:
            for character in character_id_leader:
                character_ids.append(character.leader_id)

        if character_id_recruiters is not None:
            for character in character_id_recruiters:
                character_ids.append(character.character_id)

        if len(character_ids) == 0:
            return None

        stmt_users = (
            select(Characters)
            .options(
                load_only(Characters.user_id)
            )
            .where(Characters.id.in_(character_ids))
            .distinct()
        )

        users = await self.db.select_objects(session, stmt_users)

        if users is not None:
            stmt_discord_ids = (
                select(Discord)
                .options(
                    load_only(Discord.discord_id)
                )
                .where(Discord.user_id.in_([user.user_id for user in users]))
            )

            discord_ids = await self.db.select_objects(session, stmt_discord_ids)
            return [discord.discord_id for discord in discord_ids]
        return None

    async def insert_guild_member(
        self,
        session,
        guild_id: int,
        character_id: int
    ):
        """Insert guild member into guild table."""
        stmt = (
            select(
                func.max(GuildCharacters.order_index)
            ).where(
                GuildCharacters.guild_id == guild_id
            )
        )
        order_index = int(await self.db.select_object(session, stmt)) + 1
        values = [
            GuildCharacters(
                guild_id=guild_id,
                character_id=character_id,
                avoid_leadership=False,
                order_index=order_index,
                recruiter=False
            )
        ]
        await self.db.insert_objects(session, values)

    async def delete_guild_application(
        self,
        session,
        application_id: str
    ):
        """Delete guild application by id."""
        stmt = (
            delete(
                GuildApplications
            ).where(
                GuildApplications.id == application_id
            )
        )
        await self.db.execute_raw(session, stmt)
