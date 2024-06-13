"""Table mappings module"""
import datetime

from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Users(Base):
    """Users table object"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    item_box: Mapped[bytes] = mapped_column(LargeBinary())
    rights: Mapped[int]
    last_character: Mapped[int]
    last_login: Mapped[datetime.datetime]
    gacha_premium: Mapped[int]
    gacha_trial: Mapped[int]
    frontier_points: Mapped[int]
    psn_id: Mapped[str]
    wiiu_key: Mapped[str]
    discord_token: Mapped[str]
    discord_id: Mapped[str]
    op: Mapped[bool]
