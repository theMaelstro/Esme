"""Query Builder module for Discord related queries."""
from typing import Literal

from sqlalchemy import select, update, delete
from sqlalchemy.orm import load_only
from sqlalchemy.dialects.postgresql import (
    JSON
)

from data.connector import CONN
from data.mappings.custom.tables import (
    Discord,
    DiscordMeta
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
            load_only(
                Discord.id,
                Discord.user_id,
                Discord.character_id,
                Discord.terms
            )
        ).where(Discord.discord_id == discord_id)
        discord = await self.db.select_object(session, stmt)
        return discord

    async def delete_user(self, session, discord_pk: int):
        """Delete registered user from database."""
        stmt = (
            delete(
                Discord
            ).where(
                Discord.id == discord_pk
            ).returning(
                Discord.id
            )
        )
        result = await self.db.select_object(session, stmt)
        return result

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
            .values(
                user_id=user_id,
                character_id=None
            )
        )
        return await self.db.update_objects(session, stmt)

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

    async def get_cooldown(
        self,
        session,
        discord_id: int,
    ):
        """Get cooldown for discord user."""
        stmt = select(Discord).options(
            load_only(
                Discord.id,
                Discord.cd_backup
            )
        ).where(
            Discord.discord_id == str(discord_id)
        )
        return await self.db.select_object(session, stmt)

    async def update_cooldown(
        self,
        session,
        discord_id: int,
        cd_type: Literal["backup"],
        timestamp: int
    ) -> (int | None):
        """Update cooldown for discord user."""
        stmt = (
            update(
                Discord
            ).where(
                Discord.discord_id == str(discord_id)
            )
        )
        match cd_type:
            case "backup":
                stmt = stmt.values(cd_backup=timestamp)
        return await self.db.update_objects(session, stmt)

    async def update_user_terms(
        self,
        session,
        discord_id: str,
        terms: str
    ) -> (int | None):
        """Update user agreements."""
        stmt = (
            update(Discord)
            .where(Discord.discord_id == discord_id)
            .values(
                terms=terms
            )
        )
        return await self.db.update_objects(session, stmt)

    async def create_user_entry(
        self,
        session,
        discord_id: str,
        terms: str
    ):
        """Register new user."""
        values = [
            Discord(
                discord_id=discord_id,
                terms=terms
            )
        ]
        await self.db.insert_objects(session, values)

    async def get_terms_validated_users(
        self,
        session
    ):
        """Get list of users who accepted terms."""
        stmt = select(
            Discord
        ).options(
            load_only(
                Discord.discord_id,
                Discord.terms
            )

        ).where(
            Discord.terms is not None
        )

        rows = await self.db.select_objects(session, stmt)
        return rows

    async def select_meta(
            self,
            session,
            key: Literal[
                "terms"
            ],
        ) -> (JSON | None):
        """Select discord metadata."""
        stmt = select(
            DiscordMeta
        ).where(
            DiscordMeta.key == key
        )
        row = await self.db.select_object(session, stmt)
        if row:
            return row.data
        return None

    async def insert_meta(
            self,
            session,
            key: Literal[
                "terms"
            ],
            data: JSON
        ):
        """Create new discord metadata."""
        values = [
            DiscordMeta(
                key=key,
                data=data
            )
        ]
        await self.db.insert_objects(session, values)

    async def update_meta(
        self,
        session,
        key: Literal[
            "terms"
        ],
        data: JSON
    ) -> (int | None):
        """Update discord metadata."""
        stmt = (
            update(
                DiscordMeta
            )
            .where(
                DiscordMeta.key == key
            )
            .values(
                data=data
            )
        )
        return await self.db.update_objects(session, stmt)
