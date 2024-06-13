"""Table mappings module"""
import datetime

from sqlalchemy import LargeBinary, String
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..base_mapping import Base

class Guilds(Base):
    """Guild table object"""
    __tablename__ = "guilds"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(24))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now()) # pylint: disable=[not-callable]
    leader_id: Mapped[int]
    main_motto: Mapped[int]
    rank_rp: Mapped[int]
    comment: Mapped[str] = mapped_column(String(255))
    icon: Mapped[bytes] = mapped_column(LargeBinary())
    sub_motto: Mapped[int]
    item_box: Mapped[bytes] = mapped_column(LargeBinary())
    event_rp: Mapped[int]
    pugi_name_1: Mapped[str] = mapped_column(String(12))
    pugi_name_2: Mapped[str] = mapped_column(String(12))
    pugi_name_3: Mapped[str] = mapped_column(String(12))
    recruiting: Mapped[bool]
    pugi_outfit_1: Mapped[int]
    pugi_outfit_2: Mapped[int]
    pugi_outfit_3: Mapped[int]
    pugi_outfits: Mapped[int]
    tower_mission_page: Mapped[int]
    tower_rp: Mapped[int]
    room_rp: Mapped[int]
    room_expiry: Mapped[datetime.datetime]