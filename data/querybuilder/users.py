from sqlalchemy import select, update
from sqlalchemy.orm import load_only

from data.connector import CONN

from data.mappings.erupe import (
    Users
)
class UserBuilder():
    """User table query builder."""
    def __init__(self) -> None:
        self.db = CONN

    async def select_id_by_token(self, discord_token):
        """Select user_id by discord_token."""
        stmt = select(Users).options(
            load_only(Users.id)
        ).where(Users.discord_token == discord_token)
        user_id = await self.db.select_object(stmt)
        if user_id:
            print(user_id.id)
            return user_id.id
        return user_id

    async def select_user_by_username(self, username: str):
        """Select user id and password hash by username."""
        stmt = select(Users).options(
            load_only(Users.id, Users.password)
        ).where(Users.username == username)
        user = await self.db.select_object(stmt)
        return user

    async def clear_user_token(self, user_id: int):
        """Update user by setting discord token to NULL"""
        stmt = (
            update(Users)
            .where(Users.id == user_id)
            .values(discord_token=None)
        )
        await self.db.update_objects(stmt)
