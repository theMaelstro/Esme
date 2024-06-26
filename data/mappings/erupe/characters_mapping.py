"""Table mappings module"""
import datetime
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    TEXT,
    BYTEA,
    VARCHAR,
    TIMESTAMP
)

from ..base_mapping import Base

class Characters(Base):
    """Characters table object"""
    __tablename__ = "characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=True)
    is_female: Mapped[bool] = mapped_column(nullable=True)
    is_new_character: Mapped[bool] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(VARCHAR(15))
    unk_desc_string: Mapped[str] = mapped_column(VARCHAR(31))
    gr: Mapped[int] = mapped_column(nullable=True)
    hrp: Mapped[int] = mapped_column(nullable=True)
    weapon_type: Mapped[int] = mapped_column(nullable=True)
    last_login: Mapped[int] = mapped_column(nullable=True)
    savedata: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    decomyset: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    hunternavi: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    otomoairou: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    partner: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    platebox: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    platedata: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    platemyset: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    rengokudata: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    savemercenary: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    restrict_guild_scout: Mapped[bool]
    minidata: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    gacha_items: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    daily_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
    house_info: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    login_boost: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    skin_hist: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    kouryou_point: Mapped[int] = mapped_column(nullable=True)
    gcp: Mapped[int] = mapped_column(nullable=True)
    guild_post_checked: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
    time_played: Mapped[int]
    weapon_id: Mapped[int]
    scenariodata: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    savefavoritequest: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    friends: Mapped[str] = mapped_column(TEXT)
    blocked: Mapped[str] = mapped_column(TEXT)
    deleted: Mapped[bool]
    cafe_time: Mapped[int] = mapped_column(nullable=True)
    netcafe_points: Mapped[int] = mapped_column(nullable=True)
    boost_time: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
    cafe_reset: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
    bonus_quests: Mapped[int]
    daily_quests: Mapped[int]
    promo_points: Mapped[int] 
    rasta_id: Mapped[int] = mapped_column(nullable=True)
    pact_id: Mapped[int] = mapped_column(nullable=True)
    stampcard: Mapped[int]
    mezfes: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
