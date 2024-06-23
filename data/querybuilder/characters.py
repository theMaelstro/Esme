from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import Connector
from data.mappings.erupe import (
    Characters
)

class CharactersBuilder():
    def __init__(self) -> None:
        self.db = Connector()

    async def select_characters_by_user_id(self, user_id: int):
        """Select characters by user id"""
        stmt = select(
            Characters
        ).options(
            load_only(
                Characters.id,
                Characters.name,
                Characters.last_login,
                # Characters.time_played,
                Characters.weapon_type,
                Characters.kouryou_point,
                Characters.gcp,
                Characters.netcafe_points
            )

        ).where(
            Characters.user_id == user_id
        ).order_by(
            Characters.id
        )

        rows = await self.db.select_objects(stmt)
        return rows
