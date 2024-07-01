"""Table mappings module"""
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    TIMESTAMP
)

from ..base_mapping import Base

class GuildCharacters(Base):
    """Guild Characters table object"""
    __tablename__ = "guild_characters"
    id: Mapped[int] = mapped_column(primary_key=True)
    guild_id: Mapped[int]
    character_id: Mapped[int]
    joined_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(), # pylint: disable=[not-callable]
        nullable=True
    )
    avoid_leadership: Mapped[bool]
    order_index: Mapped[int]
    recruiter: Mapped[bool]
    souls: Mapped[int]
    rp_today: Mapped[int]
    rp_yesterday: Mapped[int]
    tower_mission_1: Mapped[int]
    tower_mission_2: Mapped[int]
    tower_mission_3: Mapped[int]
    box_claimed: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(), # pylint: disable=[not-callable]
        nullable=True
    )
    treasure_hunt: Mapped[int]
    trial_vote: Mapped[int]
