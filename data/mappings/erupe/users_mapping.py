"""Table mappings module"""
import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    BYTEA,
    TEXT,
    TIMESTAMP
)

from ..base_mapping import Base

class Users(Base):
    """Users table object"""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(TEXT)
    password: Mapped[str] = mapped_column(TEXT)
    item_box: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    rights: Mapped[int] = mapped_column(default=12)
    last_character: Mapped[int] = mapped_column(default=0, nullable=True)
    last_login: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    return_expires: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    gacha_premium: Mapped[int] = mapped_column(nullable=True)
    gacha_trial: Mapped[int] = mapped_column(nullable=True)
    frontier_points: Mapped[int] = mapped_column(nullable=True)
    psn_id: Mapped[str] = mapped_column(TEXT, nullable=True)
    wiiu_key: Mapped[str] = mapped_column(TEXT, nullable=True)
    discord_token: Mapped[str] = mapped_column(TEXT, nullable=True)
    discord_id: Mapped[str] = mapped_column(TEXT, nullable=True)
    op: Mapped[bool] = mapped_column(nullable=True)
