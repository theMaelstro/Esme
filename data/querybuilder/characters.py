"""Query Builder module for Characters related queries."""
from datetime import datetime, timezone

from sqlalchemy import (
    Sequence,
    select,
    and_,
    insert
)
from sqlalchemy.orm import load_only

from data.connector import CONN
from data.mappings.erupe import (
    Characters,
    Mail
)
from data.mappings.custom.views import (
    CharacterDetails
)

class CharactersBuilder():
    """Query builder class for Characters table."""
    def __init__(self) -> None:
        self.db = CONN

    async def create_character(self, session, user_id: int):
        """Create blank character"""
        stmt = insert(
            Characters
        ).values(
            user_id=user_id,
            is_female=False,
            is_new_character=True,
            name='',
            unk_desc_string='',
            hr=0,
            gr=0,
            weapon_type=0,
            last_login=datetime.now(timezone.utc).timestamp()
        )
        return await self.db.select_objects(session, stmt)

    async def select_characters_by_user_id(self, session, user_id: int):
        """Select characters by user id"""
        stmt = select(
            Characters
        ).options(
            load_only(
                Characters.id,
                Characters.name,
                Characters.last_login,
                Characters.hr,
                Characters.gr,
                # Characters.time_played,
                Characters.weapon_type,
                Characters.kouryou_point,
                Characters.gcp,
                Characters.netcafe_points
            )

        ).where(
            and_(
                Characters.user_id == user_id,
                Characters.deleted == False
            )
        ).order_by(
            Characters.id
        )

        rows = await self.db.select_objects(session, stmt)
        return rows

    async def select_character_by_id(self, session, character_id: int):
        """Select characters by user id"""
        stmt = select(
            Characters
        ).options(
            load_only(
                Characters.id,
                Characters.name,
                Characters.last_login,
                # Characters.time_played,
                Characters.hr,
                Characters.gr,
                Characters.weapon_type,
                Characters.kouryou_point,
                Characters.gcp,
                Characters.netcafe_points
            )

        ).where(
            Characters.id == character_id
        )

        rows = await self.db.select_object(session, stmt)
        return rows

    async def select_character_details_by_character_id(self, session, character_id):
        """Select guild characters details by their guild id"""
        stmt = select(
            CharacterDetails
        ).where(
            CharacterDetails.character_id == character_id
        )

        rows = await self.db.select_object(session, stmt)
        return rows

    async def select_characters_in_guild_details(self, session):
        """Select all character details"""
        stmt = select(
            CharacterDetails
        ).where(
            CharacterDetails.guild_id != None
        ).order_by(
            CharacterDetails.guild_id,
            CharacterDetails.order_index
        )

        rows = await self.db.select_objects(session, stmt)
        return rows

    async def insert_message(
        self,
        session,
        sender_id: int,
        recipient_id: int,
        subject: str = "Subject",
        body: str = "Message",
        read: bool = False,
        attached_item_received: bool = False,
        attached_item: int = 0,
        attached_item_amount: int = 0,
        is_guild_invite: bool = False,
        deleted: bool = False,
        locked: bool = False,
        is_sys_message: bool = False
    ):
        """Insert new mail to a user inbox."""
        values = [
            Mail(
                sender_id=sender_id,
                recipient_id=recipient_id,
                subject=subject,
                body=body,
                read=read,
                attached_item_received=attached_item_received,
                attached_item=attached_item,
                attached_item_amount=attached_item_amount,
                is_guild_invite=is_guild_invite,
                deleted=deleted,
                locked=locked,
                is_sys_message=is_sys_message
            )
        ]
        await self.db.insert_objects(session, values)
