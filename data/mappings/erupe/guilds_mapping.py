"""Table mappings module"""
import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import (
    BYTEA,
    VARCHAR,
    TIMESTAMP,
)

from ..base_mapping import Base

class Guilds(Base):
    """Guild table object"""
    __tablename__ = "guilds"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(VARCHAR(24), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(), # pylint: disable=[not-callable]
        nullable=True
    ) 
    leader_id: Mapped[int]
    main_motto: Mapped[int] = mapped_column(nullable=True)
    rank_rp: Mapped[int]
    comment: Mapped[str] = mapped_column(VARCHAR(255))
    icon: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    sub_motto: Mapped[int] = mapped_column(nullable=True)
    item_box: Mapped[bytes] = mapped_column(BYTEA, nullable=True)
    event_rp: Mapped[int]
    pugi_name_1: Mapped[str] = mapped_column(VARCHAR(12), nullable=True)
    pugi_name_2: Mapped[str] = mapped_column(VARCHAR(12), nullable=True)
    pugi_name_3: Mapped[str] = mapped_column(VARCHAR(12), nullable=True)
    recruiting: Mapped[bool]
    pugi_outfit_1: Mapped[int]
    pugi_outfit_2: Mapped[int]
    pugi_outfit_3: Mapped[int]
    pugi_outfits: Mapped[int]
    tower_mission_page: Mapped[int]
    tower_rp: Mapped[int]
    room_rp: Mapped[int]
    room_expiry: Mapped[datetime.datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now()) # pylint: disable=[not-callable]
