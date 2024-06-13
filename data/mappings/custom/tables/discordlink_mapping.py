"""Table mappings module"""
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ...base_mapping import Base

class DiscordLink(Base):
    """Discord Link table object"""
    __tablename__ = "discordlink"
    id: Mapped[int] = mapped_column(primary_key=True)
    discordname: Mapped[str]
    user_id: Mapped[int]
